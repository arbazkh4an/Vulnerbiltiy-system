"""
SentinelAI — Custom Exceptions
Structured error types for the API layer.
"""

from fastapi import HTTPException, status


class InvalidURLException(HTTPException):
    """Raised when the submitted URL is malformed or uses a disallowed protocol."""

    def __init__(self, detail: str = "Invalid or unsupported URL"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class PrivateIPBlocked(HTTPException):
    """Raised when the URL resolves to a private/internal IP address."""

    def __init__(self, detail: str = "Scanning private or internal networks is not allowed"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class RateLimitExceeded(HTTPException):
    """Raised when the user has exceeded the scan rate limit."""

    def __init__(self, detail: str = "Rate limit exceeded. Try again later."):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


class ScanFailed(HTTPException):
    """Raised when a scan fails during execution."""

    def __init__(self, detail: str = "Scan execution failed"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class ScanNotFound(HTTPException):
    """Raised when a scan ID does not exist or the user lacks access."""

    def __init__(self, detail: str = "Scan not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class AuthenticationError(HTTPException):
    """Raised when the request lacks valid authentication."""

    def __init__(self, detail: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
