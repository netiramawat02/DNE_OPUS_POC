import os
import unittest
from unittest.mock import MagicMock

# Set env var for clean import
os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-testing"

# Also patch settings in case it was already imported by another test
try:
    from config.settings import settings
    settings.OPENAI_API_KEY = "sk-dummy-key-for-testing"
except ImportError:
    pass

from fastapi.testclient import TestClient
# Now import app, which initializes global state
from api.server import app, state

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_list_contracts_empty(self):
        response = self.client.get("/api/contracts")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_chat_no_context(self):
        # Mock the chat engine query processing
        original_process_query = state.chat_engine.process_query
        state.chat_engine.process_query = MagicMock(return_value={
            "answer": "I cannot find this information.",
            "source_documents": []
        })

        try:
            response = self.client.post("/api/chat", json={"query": "Hello"})
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("answer", data)
        finally:
            state.chat_engine.process_query = original_process_query

if __name__ == '__main__':
    unittest.main()
