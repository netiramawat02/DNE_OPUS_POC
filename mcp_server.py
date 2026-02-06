from mcp.server.fastmcp import FastMCP
from ingestion.pdf_loader import PDFLoader
from rag_engine.vector_store import RAGEngine
import os
import glob
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize FastMCP
mcp = FastMCP("Contract Chatbot")

# Global RAG Engine
# In a real app, this might need better state management
rag_engine = RAGEngine()

def index_samples():
    """Helper to index sample contracts on startup"""
    sample_dir = "sample_contracts"
    if not os.path.exists(sample_dir):
        return

    files = glob.glob(os.path.join(sample_dir, "*.pdf"))
    logger.info(f"Indexing {len(files)} sample contracts for MCP...")
    for f in files:
        try:
            text = PDFLoader.extract_text_from_file(f)
            rag_engine.index_documents(text, os.path.basename(f))
        except Exception as e:
            logger.error(f"Failed to index {f}: {e}")

# Index on load
index_samples()

@mcp.tool()
def query_contracts(question: str) -> str:
    """
    Answers a question about the contracts in the sample_contracts directory.
    Returns relevant context snippets.
    """
    logger.info(f"MCP Tool called with: {question}")
    docs = rag_engine.search(question)

    if not docs:
        return "No relevant information found in the contracts."

    context = ""
    for i, doc in enumerate(docs):
        source = doc.metadata.get('source', 'Unknown')
        context += f"--- Source: {source} ---\n{doc.page_content}\n\n"

    return f"Found the following context:\n{context}"

@mcp.resource("contracts://list")
def list_contracts() -> str:
    """Lists all indexed contracts."""
    sample_dir = "sample_contracts"
    if not os.path.exists(sample_dir):
        return "No contracts found."
    files = glob.glob(os.path.join(sample_dir, "*.pdf"))
    return "\n".join([os.path.basename(f) for f in files])

if __name__ == "__main__":
    # fastmcp run will handle execution, but we can also run directly
    mcp.run()
