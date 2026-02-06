import unittest
from unittest.mock import MagicMock
from ingestion.pdf_loader import PDFLoader
from rag_engine.vector_store import RAGEngine
from chat_engine.core import ChatEngine
import os

class TestIntegration(unittest.TestCase):
    def test_full_flow(self):
        # 1. Ingestion
        sample_path = "sample_contracts/vendor_service_agreement.pdf"
        if not os.path.exists(sample_path):
            print("Skipping integration test: sample contract not found")
            return

        text = PDFLoader.extract_text_from_file(sample_path)
        self.assertTrue(len(text) > 0, "Text extraction failed")

        # 2. RAG Indexing (Mock Embeddings to avoid API call)
        # We need to patch RAGEngine to use fake embeddings or mock it
        # For integration test without API key, we have to mock the components that call API.

        rag = RAGEngine()
        # Mocking embeddings internal call or using a fake one if we could inject it easily.
        # Since RAGEngine constructor does logic, let's use the one we designed that accepts embeddings.
        from tests.test_rag import FakeEmbeddings
        rag.embeddings = FakeEmbeddings()
        rag.index_documents(text, "test_doc")

        results = rag.search("payment")
        self.assertTrue(len(results) > 0, "Indexing/Search failed")

        # 3. Chat (Mock LLM)
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = "Payment terms are Net 30."

        chat = ChatEngine(rag, llm=mock_llm)
        response = chat.process_query("What are payment terms?")

        self.assertIn("Payment terms are Net 30", response["answer"])
        self.assertTrue(len(response["source_documents"]) > 0)

if __name__ == '__main__':
    unittest.main()
