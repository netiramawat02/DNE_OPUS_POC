import os
import unittest
from unittest.mock import MagicMock, patch

# Set env var BEFORE importing app
os.environ["OPENAI_API_KEY"] = "sk-dummy"

from fastapi.testclient import TestClient
from api.server import app, state

class TestAsyncUpload(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Clear state
        state.metadata_store = []
        state.processed_files = set()
        if hasattr(state, 'processing_files'):
            state.processing_files = {}

    @patch('api.server.process_contract_background')
    def test_upload_returns_processing_status(self, mock_process):
        # Create a dummy PDF content
        files = {'file': ('test.pdf', b'%PDF-1.4 dummy content', 'application/pdf')}

        response = self.client.post("/api/upload", files=files)

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['status'], 'processing')
        self.assertIn('id', data)

        # Verify background task was called
        mock_process.assert_called_once()

    def test_list_contracts_includes_processing(self):
        # Manually add a processing task
        state.processing_files = {
            "123": {"id": "123", "filename": "pending.pdf", "status": "processing", "metadata": None}
        }

        response = self.client.get("/api/contracts")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Should see the pending contract
        pending = next((c for c in data if c['id'] == "123"), None)
        self.assertIsNotNone(pending)
        self.assertEqual(pending['status'], 'processing')

if __name__ == '__main__':
    unittest.main()
