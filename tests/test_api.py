import unittest
from fastapi.testclient import TestClient
from api.server import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_list_contracts_empty(self):
        response = self.client.get("/api/contracts")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_chat_no_context(self):
        response = self.client.post("/api/chat", json={"query": "Hello"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("answer", data)

if __name__ == '__main__':
    unittest.main()
