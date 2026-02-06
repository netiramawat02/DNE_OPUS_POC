import unittest
from unittest.mock import MagicMock
from chat_engine.core import ChatEngine
from langchain_core.documents import Document

class TestChat(unittest.TestCase):
    def test_process_query(self):
        # Mock RAG Engine
        mock_rag = MagicMock()
        mock_rag.search.return_value = [
            Document(page_content="The contract expires on 2025-12-31.", metadata={"source": "contract.pdf"})
        ]

        # Mock LLM
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "The contract expires on 2025-12-31."
        mock_llm.invoke.return_value = mock_response

        chat = ChatEngine(rag_engine=mock_rag, llm=mock_llm)
        result = chat.process_query("When does it expire?")

        self.assertEqual(result["answer"], "The contract expires on 2025-12-31.")
        self.assertEqual(len(result["source_documents"]), 1)
        mock_rag.search.assert_called_with("When does it expire?")

if __name__ == '__main__':
    unittest.main()
