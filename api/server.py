from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os
import uuid
import io

# Re-use existing engines
from ingestion.pdf_loader import PDFLoader
from rag_engine.vector_store import RAGEngine
from metadata_extractor.extractor import MetadataExtractor, ContractMetadata
from chat_engine.core import ChatEngine
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(title="Jules AI Contract Chatbot API")

# Allow CORS for React Frontend (usually runs on port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State (In-Memory)
class AppState:
    rag_engine = RAGEngine()
    chat_engine = ChatEngine(rag_engine)
    metadata_store: List[dict] = []
    processed_files = set()

state = AppState()

# Request Models
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

class ContractResponse(BaseModel):
    id: str
    filename: str
    metadata: Optional[ContractMetadata]

@app.post("/api/upload")
async def upload_contract(file: UploadFile = File(...)):
    filename = file.filename
    if filename in state.processed_files:
        return {"message": "File already processed", "filename": filename}

    logger.info(f"Processing upload: {filename}")

    # Save temp file or process stream directly
    # PDFLoader expects stream or path.
    # To handle potential large files or OCR, writing to temp might be safer,
    # but for simplicity/in-memory requirement, let's try stream.

    try:
        # Read file into bytes first to allow seeking if needed by PDFLoader/OCR
        content = await file.read()
        file_like = io.BytesIO(content)

        # Ingest
        text = PDFLoader.extract_text_from_stream(file_like, filename)

        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")

        # Index
        state.rag_engine.index_documents(text, filename)

        # Extract Metadata
        extractor = MetadataExtractor()
        meta = extractor.extract(text)

        contract_id = str(uuid.uuid4())
        record = {
            "id": contract_id,
            "filename": filename,
            "metadata": meta
        }
        state.metadata_store.append(record)
        state.processed_files.add(filename)

        return {"message": "Processed successfully", "id": contract_id, "metadata": meta}

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = state.chat_engine.process_query(request.query)

        # Extract sources names
        sources = []
        if response.get("source_documents"):
            sources = list(set([doc.metadata.get("source", "Unknown") for doc in response["source_documents"]]))

        return ChatResponse(
            answer=response["answer"],
            sources=sources
        )
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contracts", response_model=List[ContractResponse])
async def list_contracts():
    return state.metadata_store
