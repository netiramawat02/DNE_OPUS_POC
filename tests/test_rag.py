import unittest
from rag_engine.vector_store import RAGEngine
from langchain_core.embeddings import Embeddings
from typing import List

class FakeEmbeddings(Embeddings):
    def __init__(self, size=1536):
        self.size = size

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.1] * self.size for _ in texts]

    def embed_query(self, text: str) -> List[float]:
        return [0.1] * self.size

class TestRAG(unittest.TestCase):
    def test_indexing_and_search(self):
        rag = RAGEngine(embeddings=FakeEmbeddings())

        text = """
        This is a contract.
        Term: 2 years.
        Vendor: Acme Corp.
        """
        rag.index_documents(text, "doc1.pdf")

        # Verify store is populated
        self.assertIsNotNone(rag.vector_store)

        # Search
        results = rag.search("Who is the vendor?", k=1)
        self.assertEqual(len(results), 1)
        self.assertIn("Acme Corp", results[0].page_content)

if __name__ == '__main__':
    unittest.main()
