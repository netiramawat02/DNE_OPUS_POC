import unittest
from unittest.mock import MagicMock
from langchain_community.chat_models import FakeListChatModel
from langchain_community.llms import FakeListLLM
from chat_engine.core import ChatEngine
from rag_engine.vector_store import RAGEngine
from langchain_core.documents import Document

class TestMockModeChat(unittest.TestCase):
    def test_fake_list_llm_success(self):
        """
        Demonstrates that FakeListLLM works because ChatEngine handles string responses gracefully.
        """
        # Mock RAG Engine
        rag_engine = MagicMock()
        rag_engine.is_empty = True

        # This mirrors the behavior of FakeListLLM returning a string
        fake_llm = FakeListLLM(responses=["I am a mock response"])

        # Initialize ChatEngine with the fake LLM
        chat_engine = ChatEngine(rag_engine, llm=fake_llm)

        # When process_query is called, it calls llm.invoke() which returns a string.
        result = chat_engine.process_query("Hello")

        # Should succeed
        self.assertEqual(result["answer"], "I am a mock response")

    def test_fake_list_chat_model_success(self):
        """
        Demonstrates that FakeListChatModel works correctly because it returns
        an AIMessage object which has .content.
        """
        # Mock RAG Engine
        rag_engine = MagicMock()
        rag_engine.is_empty = True

        # This uses the correct mock model for ChatEngine
        fake_llm = FakeListChatModel(responses=["I am a mock response"])

        chat_engine = ChatEngine(rag_engine, llm=fake_llm)

        result = chat_engine.process_query("Hello")

        # Should succeed
        self.assertEqual(result["answer"], "I am a mock response")

if __name__ == '__main__':
    unittest.main()
