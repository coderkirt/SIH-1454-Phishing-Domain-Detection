from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # App
    app_name: str = "CyberGuard"
    debug: bool = True

    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key")
    algorithm: str = "HS256"

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./threats.db")

    # RAG Intelligence Service
    rag_service_url: str = os.getenv("RAG_SERVICE_URL", "http://127.0.0.1:8001")
    rag_timeout_seconds: float = float(os.getenv("RAG_TIMEOUT_SECONDS", "8"))
    rag_enabled: bool = os.getenv("RAG_ENABLED", "true").lower() in ("true", "1", "yes")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
