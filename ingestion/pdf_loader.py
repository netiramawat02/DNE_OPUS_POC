from pypdf import PdfReader
from utils.logger import setup_logger
import io
import os

logger = setup_logger(__name__)

# Check for OCR dependencies
try:
    import pytesseract
    from pdf2image import convert_from_path, convert_from_bytes
    from pdf2image.exceptions import PDFInfoNotInstalledError
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

class PDFLoader:
    @staticmethod
    def extract_text_from_file(file_path: str, use_ocr_if_empty: bool = True) -> str:
        """
        Extracts text from a PDF file.
        If extracted text is empty and use_ocr_if_empty is True, tries OCR.
        """
        logger.info(f"Extracting text from {file_path}")
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            if not text.strip() and use_ocr_if_empty:
                logger.info("No text extracted using standard method. Attempting OCR...")
                return PDFLoader._ocr_extract_from_file(file_path)

            return text
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            raise e

    @staticmethod
    def extract_text_from_stream(file_stream, filename: str = "stream", use_ocr_if_empty: bool = True) -> str:
        """
        Extracts text from a file-like object (e.g. uploaded file).
        """
        logger.info(f"Extracting text from stream: {filename}")
        text = ""
        try:
            # pypdf expects a binary stream
            reader = PdfReader(file_stream)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            if not text.strip() and use_ocr_if_empty:
                logger.info("No text extracted using standard method. Attempting OCR...")
                # Reset stream position for OCR
                file_stream.seek(0)
                file_bytes = file_stream.read()
                return PDFLoader._ocr_extract_from_bytes(file_bytes)

            return text
        except Exception as e:
            logger.error(f"Error reading PDF stream {filename}: {e}")
            raise e

    @staticmethod
    def _ocr_extract_from_file(file_path: str) -> str:
        if not OCR_AVAILABLE:
            logger.warning("OCR requested but dependencies (pytesseract, pdf2image) not installed.")
            return ""

        try:
            images = convert_from_path(file_path)
            text = ""
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"
            return text
        except PDFInfoNotInstalledError:
            logger.error("OCR failed: Poppler not found. Please install poppler-utils (sudo apt-get install poppler-utils).")
            return ""
        except pytesseract.TesseractNotFoundError:
            logger.error("OCR failed: Tesseract not found. Please install tesseract-ocr (sudo apt-get install tesseract-ocr).")
            return ""
        except Exception as e:
            logger.error(f"OCR failed for {file_path}: {e}")
            return ""

    @staticmethod
    def _ocr_extract_from_bytes(file_bytes: bytes) -> str:
        if not OCR_AVAILABLE:
            logger.warning("OCR requested but dependencies not installed.")
            return ""

        try:
            images = convert_from_bytes(file_bytes)
            text = ""
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"
            return text
        except PDFInfoNotInstalledError:
            logger.error("OCR failed: Poppler not found. Please install poppler-utils.")
            return ""
        except pytesseract.TesseractNotFoundError:
            logger.error("OCR failed: Tesseract not found. Please install tesseract-ocr.")
            return ""
        except Exception as e:
            logger.error(f"OCR failed for bytes: {e}")
            return ""
