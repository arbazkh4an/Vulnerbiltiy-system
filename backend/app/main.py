"""
SentinelAI — FastAPI Application Entry Point
Initializes the application, middleware, routers, and lifecycle events.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes_health import router as health_router
from app.api.routes_history import router as history_router
from app.api.routes_scan import router as scan_router
from app.config import get_settings
from app.core.exceptions import (
    AuthenticationError,
    InvalidURLException,
    PrivateIPBlocked,
    RateLimitExceeded,
    ScanFailed,
    ScanNotFound,
)
from app.db.session import close_pool, create_pool
from app.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    settings = get_settings()
    setup_logging(settings.LOG_LEVEL)
    logger.info("app_starting", version="1.0.0")

    # Initialize database pool
    await create_pool()
    logger.info("app_started")

    yield

    # Shutdown
    await close_pool()
    logger.info("app_stopped")


app = FastAPI(
    title="SentinelAI API",
    description="AI-powered OWASP web security scanner",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS Middleware ──────────────────────────────────────────────────────────

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Global Exception Handlers ───────────────────────────────────────────────


@app.exception_handler(InvalidURLException)
async def invalid_url_handler(request: Request, exc: InvalidURLException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "invalid_url", "detail": exc.detail},
    )


@app.exception_handler(PrivateIPBlocked)
async def private_ip_handler(request: Request, exc: PrivateIPBlocked):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "private_ip_blocked", "detail": exc.detail},
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "rate_limit_exceeded", "detail": exc.detail},
    )


@app.exception_handler(ScanNotFound)
async def scan_not_found_handler(request: Request, exc: ScanNotFound):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "scan_not_found", "detail": exc.detail},
    )


@app.exception_handler(ScanFailed)
async def scan_failed_handler(request: Request, exc: ScanFailed):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "scan_failed", "detail": exc.detail},
    )


@app.exception_handler(AuthenticationError)
async def auth_error_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "authentication_error", "detail": exc.detail},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "detail": "An unexpected error occurred"},
    )


# ─── Routers ─────────────────────────────────────────────────────────────────

app.include_router(scan_router, prefix="/api", tags=["Scans"])
app.include_router(history_router, prefix="/api", tags=["History"])
app.include_router(health_router, prefix="/api", tags=["Health"])
