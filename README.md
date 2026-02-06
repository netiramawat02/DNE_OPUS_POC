# AI Contract Chatbot for IT Admin Team

A PDF-based chatbot that reads contracts, extracts metadata, and answers questions using RAG (Retrieval-Augmented Generation) without persistent database storage.

## Features

- **PDF Ingestion**: Upload multiple PDF contracts (digital or scanned/OCR).
- **Metadata Extraction**: Automatically extracts Title, Vendor, Dates, and Renewal Terms.
- **Chat Interface**: React-based UI to ask natural language questions about the contracts.
- **No Database**: All processing is in-memory for security and simplicity.
- **MCP Integration**: Exposes contract querying as an MCP tool.

## Architecture

- **Backend**: FastAPI (Python)
- **Frontend**: React (JS)
- **RAG Engine**: LangChain + FAISS + OpenAI

## Folder Structure

```
project/
├── api/                # FastAPI backend endpoints
├── frontend/           # React frontend application
├── ingestion/          # PDF loading and text extraction
├── contract_parser/    # Text cleaning
├── metadata_extractor/ # LLM-based metadata extraction
├── rag_engine/         # Vector store and retrieval (FAISS)
├── chat_engine/        # Q&A logic
├── utils/              # Logging and helpers
├── config/             # Configuration settings
├── tests/              # Unit tests
└── main.py             # Entry point
```

## Setup

### 1. Backend Setup

1. **Prerequisites**:
   - Python 3.10+
   - Tesseract OCR (optional, for scanned PDFs): `sudo apt-get install tesseract-ocr`

2. **Installation**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**:
   - Copy `.env.example` to `.env` (or set environment variables).
   - Set `OPENAI_API_KEY`.

4. **Run Server**:
   ```bash
   python main.py server
   ```
   The API runs on `http://localhost:8000`. API Docs at `http://localhost:8000/docs`.

### 2. Frontend Setup

1. **Navigate to frontend**:
   ```bash
   cd frontend
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Run UI**:
   ```bash
   npm start
   ```
   The app runs on `http://localhost:3000`. It proxies API requests to port 8000.

### 3. MCP Server (Optional)
```bash
python main.py mcp
```

## Testing

Run unit tests:
```bash
python -m unittest discover tests
```
