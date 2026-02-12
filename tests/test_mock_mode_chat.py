import unittest
from unittest.mock import MagicMock
from langchain_community.chat_models import FakeListChatModel
from langchain_community.llms import FakeListLLM
from chat_engine.core import ChatEngine
from rag_engine.vector_store import RAGEngine
from langchain_core.documents import Document

class TestMockModeChat(unittest.TestCase):
    def test_fake_list_llm_failure(self):
        """
        Demonstrates that FakeListLLM fails because it returns a string,
        and ChatEngine expects an object with .content.
        """
        # Mock RAG Engine
        rag_engine = MagicMock()
        rag_engine.is_empty = True

        # This mirrors the behavior of FakeListLLM returning a string
        # Note: In real execution, FakeListLLM returns a string directly when invoked.
        # But ChatEngine expects a message object.

        # To reproduce the exact behavior inside ChatEngine, we use FakeListLLM directly.
        fake_llm = FakeListLLM(responses=["I am a mock response"])

        # Initialize ChatEngine with the fake LLM
        chat_engine = ChatEngine(rag_engine, llm=fake_llm)

        # When process_query is called, it calls llm.invoke() which returns a string.
        # Then it tries to access .content on that string, raising AttributeError.
        result = chat_engine.process_query("Hello")

        # Check that the error was caught and returned in the answer
        self.assertTrue(result["answer"].startswith("Error generating answer"))
        self.assertIn("'str' object has no attribute 'content'", result["answer"])

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
