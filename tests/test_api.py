import os
import unittest
from unittest.mock import MagicMock

# Set env var for clean import
os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-testing"
os.environ["API_ADMIN_KEY"] = "admin-secret-test"

# Also patch settings in case it was already imported by another test
try:
    from config.settings import settings
    settings.OPENAI_API_KEY = "sk-dummy-key-for-testing"
    settings.API_ADMIN_KEY = "admin-secret-test"
except ImportError:
    pass

from fastapi.testclient import TestClient
# Now import app, which initializes global state
from api.server import app, state
# Import auth to update valid keys
from api.auth import valid_api_keys

class TestAPI(unittest.TestCase):
    def setUp(self):
        # Ensure the test key is valid
        valid_api_keys.add("admin-secret-test")
        self.client = TestClient(app)
        self.client.headers = {"X-API-Key": "admin-secret-test"}

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

    def test_generate_key(self):
        response = self.client.post("/api/admin/generate-key")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("api_key", data)

        # Verify the new key works
        new_key = data["api_key"]
        client2 = TestClient(app)
        client2.headers = {"X-API-Key": new_key}
        response = client2.get("/api/contracts")
        self.assertEqual(response.status_code, 200)

    def test_public_access_no_key(self):
        """Test that endpoints are accessible without API Key."""
        client_no_auth = TestClient(app)
        # Should succeed
        response = client_no_auth.get("/api/contracts")
        self.assertEqual(response.status_code, 200)

        # Chat should also work
        original_process_query = state.chat_engine.process_query
        state.chat_engine.process_query = MagicMock(return_value={
            "answer": "Public access working.",
            "source_documents": []
        })
        try:
            response = client_no_auth.post("/api/chat", json={"query": "Hello"})
            self.assertEqual(response.status_code, 200)
        finally:
            state.chat_engine.process_query = original_process_query

if __name__ == '__main__':
    unittest.main()
