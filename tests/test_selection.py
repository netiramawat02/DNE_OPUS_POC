import os
import unittest
from unittest.mock import MagicMock, patch
import sys

# Set dummy env vars BEFORE importing api.server
os.environ["PERPLEXITY_API_KEY"] = "pplx-test"
os.environ["API_ADMIN_KEY"] = "admin-secret"

# Mock HuggingFace embeddings
sys.modules["langchain_huggingface"] = MagicMock()

# Mock specific classes
mock_embeddings = MagicMock()
mock_embeddings.embed_documents.return_value = [[0.1] * 384]
mock_embeddings.embed_query.return_value = [0.1] * 384

mock_chat = MagicMock()
mock_chat.invoke.return_value.content = "This is a mocked answer."



# Mock FAISS
sys.modules["langchain_community.vectorstores"] = MagicMock()
mock_vectorstore = MagicMock()
sys.modules["langchain_community.vectorstores"].FAISS.from_documents.return_value = mock_vectorstore
mock_vectorstore.similarity_search.return_value = [
    MagicMock(page_content="Contract A content", metadata={"source": "contractA.pdf", "contract_id": "1"})
]

from fastapi.testclient import TestClient
from api.server import app, state

client = TestClient(app)

class TestSelection(unittest.TestCase):
    def setUp(self):
        # Reset state
        state.rag_engine.vector_store = None
        state.metadata_store = []
        state.processed_files = set()
        state.processing_files = {}
        # Reset mocks
        mock_vectorstore.reset_mock()
        # Re-apply default return value because reset_mock clears it
        mock_vectorstore.similarity_search.return_value = [
             MagicMock(page_content="Contract A content", metadata={"source": "contractA.pdf", "contract_id": "1"})
        ]

    def test_chat_filtering(self):
        # 1. Setup RAG engine with a mocked vector store
        state.rag_engine.vector_store = mock_vectorstore

        # 2. Chat with contract_id
        contract_id = "12345"
        response = client.post("/api/chat", json={"query": "What is this?", "contract_id": contract_id})

        self.assertEqual(response.status_code, 200)

        # Verify that search was called with the correct filter
        mock_vectorstore.similarity_search.assert_called_with("What is this?", k=3, filter={"contract_id": contract_id})

    def test_chat_no_filtering(self):
        # 1. Setup RAG engine with a mocked vector store
        state.rag_engine.vector_store = mock_vectorstore

        # 2. Chat without contract_id
        response = client.post("/api/chat", json={"query": "What is this?"})

        self.assertEqual(response.status_code, 200)

        # Verify that search was called without filter (or None)
        mock_vectorstore.similarity_search.assert_called_with("What is this?", k=3, filter=None)

if __name__ == "__main__":
    unittest.main()
