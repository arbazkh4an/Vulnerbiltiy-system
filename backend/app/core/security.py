"""
SentinelAI — Authentication & Security
JWT token verification and user extraction for API endpoints.
"""

from fastapi import Depends, Request
from jose import JWTError, jwt

from app.config import Settings, get_settings
from app.core.exceptions import AuthenticationError
from app.logging import get_logger

logger = get_logger(__name__)


def _extract_token(request: Request) -> str:
    """Extract Bearer token from the Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise AuthenticationError("Missing or invalid Authorization header")
    token = auth_header[7:].strip()
    if not token:
        raise AuthenticationError("Empty bearer token")
    return token


async def get_current_user(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> str:
    """
    FastAPI dependency: extract and verify user identity from JWT.

    Returns the user_id (sub claim) from the token.
    """
    token = _extract_token(request)

    # If no JWT secret is configured, accept the token as a raw user_id
    # This supports the case where the Next.js frontend acts as the auth gate
    # and passes the user_id directly
    if not settings.JWT_SECRET:
        logger.warning("jwt_secret_not_configured", msg="Accepting token as raw user_id")
        return token

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as exc:
        logger.warning("jwt_decode_failed", error=str(exc))
        raise AuthenticationError("Invalid or expired token")

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Token missing 'sub' claim")

    return user_id
