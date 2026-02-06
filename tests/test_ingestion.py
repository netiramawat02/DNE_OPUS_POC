import unittest
import os
from ingestion.pdf_loader import PDFLoader

class TestIngestion(unittest.TestCase):
    def test_pdf_extraction(self):
        # Use one of the generated samples
        sample_path = "sample_contracts/vendor_service_agreement.pdf"
        if not os.path.exists(sample_path):
            self.skipTest("Sample contract not found")

        text = PDFLoader.extract_text_from_file(sample_path)
        print(f"Extracted text length: {len(text)}")
        self.assertIn("IT Service Agreement", text)
        self.assertIn("TechSolutions Inc.", text)
        self.assertIn("Global Corp", text)

if __name__ == '__main__':
    unittest.main()
