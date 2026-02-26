"""
Backend Configuration
Pydantic-based settings management for FastAPI application
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    
    DATABASE_URL: str = "postgresql://scanner:scanner@localhost:5432/scannerdb"
    REDIS_URL: str = "redis://localhost:6379/0"
    GROQ_API_KEY: Optional[str] = None
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    MAX_SCANS_PER_HOUR: int = 10


settings = Settings()
