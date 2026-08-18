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

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
