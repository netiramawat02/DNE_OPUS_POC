from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

# In-memory store for valid keys
# Initialize with the admin key if it exists
valid_api_keys = {settings.API_ADMIN_KEY} if settings.API_ADMIN_KEY else set()

def add_api_key(key: str):
    """Adds a new API key to the valid keys set."""
    valid_api_keys.add(key)
    logger.info(f"Added new API key: {key[:4]}...{key[-4:]}")

def get_api_key(api_key_header: str = Security(api_key_header)):
    """Validates the X-API-Key header against the set of valid keys."""
    if api_key_header in valid_api_keys:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
    )

def get_admin_key(api_key_header: str = Security(api_key_header)):
    """Validates the X-API-Key header matches the ADMIN key."""
    if api_key_header == settings.API_ADMIN_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin privileges required",
    )
