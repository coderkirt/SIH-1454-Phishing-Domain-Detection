"""Configuration settings for the PHISHEYE standalone RAG service."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Service settings
    HOST: str = "127.0.0.1"
    PORT: int = 8001
    DEBUG: bool = False

    # Directories
    BASE_DIR: Path = BASE_DIR
    CORPUS_DIR: Path = BASE_DIR / "corpus"
    DATA_DIR: Path = BASE_DIR / "data"
    CHROMA_PERSIST_DIR: Path = BASE_DIR / "data" / "chroma"

    # Chroma collection settings
    COLLECTION_NAME: str = "phishing_knowledge"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_VERSION: str = "v1.0.0"

    # Backup & retention settings
    BACKUP_DIR: Path = BASE_DIR / "backups"
    BACKUP_RETENTION_DAYS: int = 30

    # Hybrid retrieval settings
    RRF_K: int = 60  # Standard Reciprocal Rank Fusion constant
    TOP_K: int = 4
    DENSE_WEIGHT: float = 0.6
    SPARSE_WEIGHT: float = 0.4

    # Cache settings
    CACHE_SIZE: int = 512
    CACHE_TTL_SECONDS: int = 3600

    # LLM settings
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gemini-1.5-flash"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
