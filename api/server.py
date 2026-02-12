from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
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
from api.auth import get_api_key, get_admin_key, add_api_key
from langchain_community.embeddings import FakeEmbeddings
from langchain_community.chat_models import FakeListChatModel

logger = setup_logger(__name__)

app = FastAPI(title="AI Contract Chatbot API")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up API Server...")

    # Validate OpenAI API Key
    try:
        # Attempt a simple embedding to verify the key
        logger.info("Validating OpenAI API Key...")
        state.rag_engine.embeddings.embed_query("test")
        logger.info("OpenAI API Key is valid.")
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Incorrect API key" in error_msg:
            logger.error(f"OpenAI API Key validation failed: {error_msg}")
            logger.warning("----------------------------------------------------------------")
            logger.warning("WARNING: INVALID OPENAI API KEY DETECTED")
            logger.warning("The application will run in MOCK MODE.")
            logger.warning("You will NOT get real answers based on your PDF.")
            logger.warning("Please check your .env file and update OPENAI_API_KEY.")
            logger.warning("----------------------------------------------------------------")

            # Switch to Mock Mode
            fake_embeddings = FakeEmbeddings(size=1536)
            fake_llm = FakeListChatModel(responses=[
                "I am running in MOCK MODE because a valid OpenAI API Key was not found. "
                "I cannot analyze the PDF content, but the system is functional for demonstration purposes. "
                "Please update your OPENAI_API_KEY to use the full features."
            ])

            # Replace global state engines with mock versions
            state.rag_engine = RAGEngine(embeddings=fake_embeddings)
            state.chat_engine = ChatEngine(state.rag_engine, llm=fake_llm)
        else:
            # If it's another error (e.g. network), we might still want to fail or warn
            logger.error(f"Error validating OpenAI API Key: {e}")
            # Optional: Decide if we want to fallback for other errors too. For now, only 401.

    # Check for OCR tools
    if not shutil.which("tesseract"):
        logger.warning("WARNING: 'tesseract' executable not found. OCR for scanned PDFs will fail. Install tesseract-ocr.")
    if not shutil.which("pdftoppm"): # pdftoppm is part of poppler-utils
        logger.warning("WARNING: 'pdftoppm' executable not found. OCR for scanned PDFs will fail. Install poppler-utils.")

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
    contract_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

class ContractResponse(BaseModel):
    id: str
    filename: str
    metadata: Optional[ContractMetadata]
    status: str = "processed"

class APIKeyResponse(BaseModel):
    api_key: str
    message: str

def process_contract_background(file_path: str, filename: str, contract_id: str):
    logger.info(f"Starting background processing for {filename} (ID: {contract_id})")
    try:
        # Ingest
        text = PDFLoader.extract_text_from_file(file_path)

        if not text:
            logger.warning(f"No text extracted for {filename}")
            if contract_id in state.processing_files:
                state.processing_files[contract_id]["status"] = "failed"
                state.processing_files[contract_id]["error"] = "No text extracted. The file might be an image-based PDF and OCR dependencies (tesseract-ocr, poppler-utils) are missing or not configured."
            return

        # Index
        indexed = state.rag_engine.index_documents(
            text,
            filename,
            metadata={"contract_id": contract_id}
        )

        if not indexed:
            logger.warning(f"Indexing failed for {filename} (empty content?)")
            if contract_id in state.processing_files:
                state.processing_files[contract_id]["status"] = "failed"
                state.processing_files[contract_id]["error"] = "Content extraction yielded no indexable text."

                # We do NOT add to metadata_store as processed
            return

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

@app.post("/api/admin/generate-key", response_model=APIKeyResponse)
def generate_api_key(admin_key: str = Depends(get_admin_key)):
    """
    Generates a new API key for clients.
    Protected by Admin Key.
    """
    new_key = str(uuid.uuid4())
    add_api_key(new_key)
    return {"api_key": new_key, "message": "API Key generated successfully"}

@app.post("/api/upload")
def upload_contract(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
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
def chat(request: ChatRequest, api_key: str = Depends(get_api_key)):
    try:
        response = state.chat_engine.process_query(request.query, contract_id=request.contract_id)

        # Extract sources names
        sources = []
        if response.get("source_documents"):
            sources = list(set([doc.metadata.get("source", "Unknown") for doc in response["source_documents"]]))

        return ChatResponse(
            answer=response["answer"],
            sources=sources
        )
    except Exception as e:
        logger.error(f"Chat failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contracts", response_model=List[ContractResponse])
def list_contracts(api_key: str = Depends(get_api_key)):
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
