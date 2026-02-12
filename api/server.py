from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import shutil
import os
import uuid
import io
import tempfile
import logging

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
    processing_files: Dict[str, dict] = {}

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
    status: str = "processed"

def process_contract_background(file_path: str, filename: str, contract_id: str):
    logger.info(f"Starting background processing for {filename} (ID: {contract_id})")
    try:
        # Ingest
        text = PDFLoader.extract_text_from_file(file_path)

        if not text:
            logger.warning(f"No text extracted for {filename}")
            if contract_id in state.processing_files:
                state.processing_files[contract_id]["status"] = "failed"
                state.processing_files[contract_id]["error"] = "No text extracted"
            return

        # Index
        state.rag_engine.index_documents(text, filename)

        # Extract Metadata
        extractor = MetadataExtractor()
        meta = extractor.extract(text)

        # Update state: Move from processing to metadata_store
        record = {
            "id": contract_id,
            "filename": filename,
            "metadata": meta,
            "status": "processed"
        }
        state.metadata_store.append(record)
        state.processed_files.add(filename)

        # Remove from processing_files
        if contract_id in state.processing_files:
            del state.processing_files[contract_id]

        logger.info(f"Successfully processed {filename}")

    except Exception as e:
        logger.error(f"Background processing failed for {filename}: {e}")
        if contract_id in state.processing_files:
            state.processing_files[contract_id]["status"] = "failed"
            state.processing_files[contract_id]["error"] = str(e)
    finally:
        # Cleanup temp file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/api/upload")
async def upload_contract(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    filename = file.filename
    # Check if already processed
    if filename in state.processed_files:
        return {"message": "File already processed", "filename": filename, "status": "processed"}

    # Check if currently processing
    for task in state.processing_files.values():
        if task["filename"] == filename and task["status"] == "processing":
             return {"message": "File is currently processing", "filename": filename, "status": "processing", "id": task["id"]}

    logger.info(f"Queuing upload: {filename}")
    contract_id = str(uuid.uuid4())

    # Save to temp file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
    except Exception as e:
        logger.error(f"Failed to save temp file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")

    # Add to processing queue
    state.processing_files[contract_id] = {
        "id": contract_id,
        "filename": filename,
        "status": "processing",
        "metadata": None
    }

    background_tasks.add_task(process_contract_background, tmp_path, filename, contract_id)

    return {"message": "Upload successful, processing started.", "id": contract_id, "status": "processing"}

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
    processed_list = []
    processed_ids = set()
    # Copy metadata_store to avoid modification issues if any (though append is atomic-ish)
    # Actually, iterate over a copy or just assume it's append-only
    for item in list(state.metadata_store):
        item_copy = item.copy()
        if "status" not in item_copy:
            item_copy["status"] = "processed"
        processed_list.append(item_copy)
        processed_ids.add(item["id"])

    # Create a copy of processing files to avoid runtime error during iteration
    processing_tasks = list(state.processing_files.values())

    processing_list = []
    for task in processing_tasks:
        # Avoid race condition duplicates
        if task["id"] in processed_ids:
            continue

        processing_list.append({
            "id": task["id"],
            "filename": task["filename"],
            "metadata": task["metadata"],
            "status": task["status"]
        })

    return processed_list + processing_list
