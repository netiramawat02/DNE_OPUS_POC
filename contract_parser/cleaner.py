import re

class TextCleaner:
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans extracted text by removing excessive whitespace and common artifacts.
        """
        # Replace multiple newlines with a single newline
        text = re.sub(r'\n\s*\n', '\n', text)
        # Replace multiple spaces with single space
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
