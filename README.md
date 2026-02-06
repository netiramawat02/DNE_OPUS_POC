# AI Contract Chatbot for IT Admin Team

A PDF-based chatbot that reads contracts, extracts metadata, and answers questions using RAG (Retrieval-Augmented Generation) without persistent database storage.

## Features

- **PDF Ingestion**: Upload multiple PDF contracts (digital or scanned/OCR).
- **Metadata Extraction**: Automatically extracts Title, Vendor, Dates, and Renewal Terms.
- **Chat Interface**: Ask natural language questions about the contracts.
- **No Database**: All processing is in-memory for security and simplicity.
- **MCP Integration**: Exposes contract querying as an MCP tool.

## Folder Structure

```
project/
├── ingestion/          # PDF loading and text extraction
├── contract_parser/    # Text cleaning
├── metadata_extractor/ # LLM-based metadata extraction
├── rag_engine/         # Vector store and retrieval (FAISS)
├── chat_engine/        # Q&A logic
├── ui/                 # Streamlit application
├── utils/              # Logging and helpers
├── config/             # Configuration settings
├── tests/              # Unit tests
└── main.py             # Entry point
```

## Setup

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

## Usage

### Run the UI (Streamlit)
```bash
python main.py ui
# OR
streamlit run ui/app.py
```

### Run the MCP Server
```bash
python main.py mcp
```
The MCP server indexes PDF files located in `sample_contracts/` directory on startup.

## Testing

Run unit tests:
```bash
python -m unittest discover tests
```

## Generated Samples

The project includes a script `create_samples.py` to generate dummy contracts for testing.
```bash
python create_samples.py
```
