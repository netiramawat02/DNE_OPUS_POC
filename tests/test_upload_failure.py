import os
import unittest
from unittest.mock import MagicMock, patch
from api.server import app, state, process_contract_background
from fastapi.testclient import TestClient
from langchain_community.embeddings import FakeEmbeddings

class TestUploadFailure(unittest.TestCase):
    def setUp(self):
        # Reset state
        state.rag_engine.vector_store = None
        state.metadata_store = []
        state.processed_files = set()
        state.processing_files = {}

        # Use Fake Embeddings
        state.rag_engine.embeddings = FakeEmbeddings(size=1536)

        # Mock Chat Engine LLM
        self.mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Hello! I am ready to help you with your contracts."
        self.mock_llm.invoke.return_value = mock_response
        state.chat_engine.llm = self.mock_llm

    @patch("ingestion.pdf_loader.PDFLoader.extract_text_from_file")
    def test_upload_failure_empty_text(self, mock_extract):
        mock_extract.return_value = "   " # Whitespace only

        client = TestClient(app)

        # Mocking file upload process manually to control background task execution
        # But here we can simulate background task directly

        contract_id = "test-id"
        filename = "empty.pdf"
        file_path = "/tmp/empty.pdf"

        # Add to processing
        state.processing_files[contract_id] = {
            "id": contract_id,
            "filename": filename,
            "status": "processing",
            "metadata": None
        }

        # Create dummy file
        with open(file_path, "w") as f:
            f.write("dummy")

        process_contract_background(file_path, filename, contract_id)

        # Check status
        self.assertEqual(state.processing_files[contract_id]["status"], "failed")
        self.assertIn("content", state.processing_files[contract_id].get("error", "").lower())

        # Check chat response
        chat_response = client.post("/api/chat", json={"query": "hello"})
        self.assertEqual(chat_response.status_code, 200)
        # Ensure we get a response, even if no contracts are indexed (conversational fallback)
        self.assertTrue(len(chat_response.json()["answer"]) > 0)
        self.assertNotIn("No contracts have been indexed", chat_response.json()["answer"])

if __name__ == "__main__":
    unittest.main()
