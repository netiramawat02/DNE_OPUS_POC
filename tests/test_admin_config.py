import os
import unittest
from unittest.mock import MagicMock, patch, mock_open
from fastapi.testclient import TestClient

# Import app and state
from api.server import app, state
from api.auth import valid_api_keys
from config.settings import settings

class TestAdminConfig(unittest.TestCase):
    def setUp(self):
        # Set admin key
        valid_api_keys.add("admin-secret-test")
        self.client = TestClient(app)
        self.client.headers = {"X-API-Key": "admin-secret-test"}

        # Save original settings and state
        self.original_openai_key = settings.OPENAI_API_KEY
        self.original_admin_key = settings.API_ADMIN_KEY
        self.original_rag_engine = state.rag_engine
        self.original_chat_engine = state.chat_engine

        # Override admin key for test
        settings.API_ADMIN_KEY = "admin-secret-test"

    def tearDown(self):
        # Restore settings
        settings.OPENAI_API_KEY = self.original_openai_key
        settings.API_ADMIN_KEY = self.original_admin_key
        os.environ["OPENAI_API_KEY"] = self.original_openai_key if self.original_openai_key else ""

        # Restore state
        state.rag_engine = self.original_rag_engine
        state.chat_engine = self.original_chat_engine

    @patch("api.server.RAGEngine")
    @patch("api.server.ChatEngine")
    @patch("builtins.open", new_callable=mock_open, read_data="OPENAI_API_KEY=old_key")
    @patch("os.path.exists", return_value=True)
    def test_set_openai_key(self, mock_exists, mock_file, mock_chat_engine, mock_rag_engine):
        # Setup mocks
        mock_rag_instance = MagicMock()
        mock_rag_engine.return_value = mock_rag_instance

        mock_chat_instance = MagicMock()
        mock_chat_engine.return_value = mock_chat_instance

        new_key = "sk-test-new-key-123"

        # Call the endpoint
        response = self.client.post(
            "/api/admin/set-openai-key",
            json={"api_key": new_key}
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertIn("re-initialized successfully", response.json()["message"])

        # Verify settings updated
        self.assertEqual(settings.OPENAI_API_KEY, new_key)
        self.assertEqual(os.environ["OPENAI_API_KEY"], new_key)

        # Verify file write
        # mock_file() returns the file object mock
        # We need to verify that write was called on it
        handle = mock_file()
        handle.write.assert_called()

        # Get the arguments passed to write
        # call_args_list might have multiple writes?
        # The code does: f.write(content) once.
        written_content = handle.write.call_args[0][0]
        self.assertIn(f"OPENAI_API_KEY={new_key}", written_content)

        # Verify engines re-initialized
        mock_rag_engine.assert_called()
        mock_chat_engine.assert_called_with(mock_rag_instance)

        # Verify state updated
        self.assertEqual(state.rag_engine, mock_rag_instance)
        self.assertEqual(state.chat_engine, mock_chat_instance)

    @patch("api.server.RAGEngine")
    @patch("api.server.ChatEngine")
    @patch("builtins.open", new_callable=mock_open, read_data="FOO=bar")
    @patch("os.path.exists", return_value=True)
    def test_set_openai_key_append(self, mock_exists, mock_file, mock_chat_engine, mock_rag_engine):
        mock_rag_instance = MagicMock()
        mock_rag_engine.return_value = mock_rag_instance
        mock_chat_engine.return_value = MagicMock()

        new_key = "sk-test-append"

        response = self.client.post(
            "/api/admin/set-openai-key",
            json={"api_key": new_key}
        )
        self.assertEqual(response.status_code, 200)

        handle = mock_file()
        written_content = handle.write.call_args[0][0]
        self.assertIn(f"\nOPENAI_API_KEY={new_key}", written_content)
        self.assertIn("FOO=bar", written_content)

    def test_set_openai_key_empty(self):
        response = self.client.post(
            "/api/admin/set-openai-key",
            json={"api_key": ""}
        )
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
