"""
SentinelAI — Configuration
Pydantic Settings-based configuration with environment variable loading.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")

    # AI Provider
    GROQ_API_KEY: str = Field(default="", description="Groq API key for LLM")
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key (fallback)")
    AI_MODEL: str = Field(default="llama-3.3-70b-versatile", description="LLM model name")

    # NVD API
    NVD_API_KEY: str = Field(default="", description="NVD API key for higher rate limits")

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="Allowed CORS origins",
    )

    # Scanning
    SCAN_TIMEOUT: int = Field(default=30, description="Per-scanner timeout in seconds")
    TOTAL_SCAN_TIMEOUT: int = Field(default=90, description="Total scan time budget")

    # Worker
    WORKER_POLL_INTERVAL: int = Field(default=5, description="Worker poll interval in seconds")

    # Rate Limiting
    RATE_LIMIT_MAX: int = Field(default=5, description="Max scans per user per window")
    RATE_LIMIT_WINDOW_HOURS: int = Field(default=1, description="Rate limit window in hours")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Server
    HOST: str = Field(default="0.0.0.0", description="Server bind host")
    PORT: int = Field(default=5000, description="Server bind port")

    # JWT (for validating frontend tokens)
    JWT_SECRET: str = Field(default="", description="JWT secret for token validation")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance. Call once at startup."""
    return Settings()
