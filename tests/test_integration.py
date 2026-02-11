import unittest
from unittest.mock import MagicMock
from ingestion.pdf_loader import PDFLoader
from rag_engine.vector_store import RAGEngine
from chat_engine.core import ChatEngine
from langchain_core.embeddings import Embeddings
from typing import List
import os

class FakeEmbeddings(Embeddings):
    def __init__(self, size=1536):
        self.size = size

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.1] * self.size for _ in texts]

    def embed_query(self, text: str) -> List[float]:
        return [0.1] * self.size

class TestIntegration(unittest.TestCase):
    def test_full_flow(self):
        # 1. Ingestion
        sample_path = "sample_contracts/vendor_service_agreement.pdf"
        if not os.path.exists(sample_path):
            print("Skipping integration test: sample contract not found")
            return

        text = PDFLoader.extract_text_from_file(sample_path)
        self.assertTrue(len(text) > 0, "Text extraction failed")

        # 2. RAG Indexing
        # Provide FakeEmbeddings to RAGEngine constructor to avoid API key requirement
        rag = RAGEngine(embeddings=FakeEmbeddings())
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
