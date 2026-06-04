"""
Security module for verifying incoming client requests.
Implements X-Aegis-API-Key header verification.
"""

from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings

# Header name used for authorization
API_KEY_HEADER_NAME = "X-Aegis-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)


async def get_api_key(
    api_key_header_value: str = Security(api_key_header)
) -> str | None:
    """
    Dependency to validate the incoming API key header.
    
    If AEGIS_API_KEY is not configured in the application settings, 
    authorization is bypassed (disabled). If configured, incoming requests 
    must supply a matching key in the X-Aegis-API-Key header.
    """
    # Bypass authorization if no key is configured on the backend
    if not settings.AEGIS_API_KEY:
        return None

    # Raise unauthorized if key is missing or incorrect
    if not api_key_header_value or api_key_header_value != settings.AEGIS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or missing API key in '{API_KEY_HEADER_NAME}' header."
        )

    return api_key_header_value
