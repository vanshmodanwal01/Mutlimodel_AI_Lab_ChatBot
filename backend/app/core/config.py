import json
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    """Centralized application settings loaded from environment variables."""

    # Project Information
    PROJECT_NAME: str = "MindBridge AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Secure Multimodal Conversational AI Platform with RAG and Emotional Support Guardrails"

    # Environment & Server
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "8501"))

    # AI Model Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-004")

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/mindbridge_db")
    DB_AUTO_FALLBACK_SQLITE: bool = os.getenv("DB_AUTO_FALLBACK_SQLITE", "true").lower() in ("true", "1", "yes")
    SQLITE_FALLBACK_URL: str = f"sqlite:///{BASE_DIR / 'mindbridge.db'}"

    # File Upload & Storage
    UPLOAD_DIR: Path = BASE_DIR / os.getenv("UPLOAD_DIR", "backend/uploads")
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    ALLOWED_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp"}
    ALLOWED_DOCUMENT_EXTENSIONS: set = {".pdf", ".docx", ".txt"}
    ALLOWED_AUDIO_EXTENSIONS: set = {".wav", ".mp3", ".m4a", ".ogg"}

    # Security & Guardrails
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    ENABLE_SAFETY_GUARDRAILS: bool = os.getenv("ENABLE_SAFETY_GUARDRAILS", "true").lower() in ("true", "1", "yes")

    # CORS
    @property
    def cors_origins(self) -> List[str]:
        raw = os.getenv("CORS_ORIGINS", '["http://localhost:8501", "http://127.0.0.1:8501", "http://localhost:3000"]')
        try:
            return json.loads(raw)
        except Exception:
            return ["*"]


settings = Settings()

# Ensure uploads directory exists
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
