import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
    PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "llama-2-70b-chat")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    API_ADMIN_KEY = os.getenv("API_ADMIN_KEY", "admin-secret")

settings = Settings()
