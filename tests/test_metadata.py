import unittest
from unittest.mock import MagicMock
from metadata_extractor.extractor import MetadataExtractor, ContractMetadata

class TestMetadata(unittest.TestCase):
    def test_extraction(self):
        # Mock LLM
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = """
        {
            "title": "Service Agreement",
            "vendor": "Acme Inc",
            "client": "Beta Corp",
            "start_date": "2023-01-01",
            "end_date": "2024-01-01",
            "renewal_terms": "Auto-renew",
            "contract_id": "12345"
        }
        """
        mock_llm.invoke.return_value = mock_response

        extractor = MetadataExtractor(llm=mock_llm)
        metadata = extractor.extract("Some contract text...")

        self.assertEqual(metadata.title, "Service Agreement")
        self.assertEqual(metadata.vendor, "Acme Inc")
        self.assertEqual(metadata.start_date, "2023-01-01")

if __name__ == '__main__':
    unittest.main()
