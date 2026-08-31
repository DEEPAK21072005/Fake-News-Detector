import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

IS_VERCEL = (
    bool(os.getenv("VERCEL"))
    or bool(os.getenv("NOW_REGION"))
    or bool(os.getenv("VERCEL_REGION"))
    or bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
    or bool(os.getenv("LAMBDA_TASK_ROOT"))
)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# In serverless environments, writable directories must be in /tmp
if IS_VERCEL or not os.access(str(BASE_DIR), os.W_OK):
    DATA_DIR = Path("/tmp/data")
    MODELS_DIR = Path("/tmp/models")
else:
    DATA_DIR = BASE_DIR / "data"
    MODELS_DIR = BASE_DIR / "models"


CHECKPOINTS_DIR = MODELS_DIR / "checkpoints"
EVIDENCE_DIR = DATA_DIR / "evidence"
UPLOADS_DIR = DATA_DIR / "uploads"

# Ensure directories exist safely
for directory in [DATA_DIR, MODELS_DIR, CHECKPOINTS_DIR, EVIDENCE_DIR, UPLOADS_DIR]:
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


class Settings(BaseSettings):
    APP_NAME: str = "VeritasAI"
    APP_ENV: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "*",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{str(DATA_DIR / 'veritas.db').replace(chr(92), '/')}"
    SYNC_DATABASE_URL: str = f"sqlite:///{str(DATA_DIR / 'veritas.db').replace(chr(92), '/')}"
    
    # Inference Modes: FAST | BALANCED | RESEARCH | CLOUD_ENHANCED
    DEFAULT_INFERENCE_MODE: str = "BALANCED"
    
    # Embedding Configuration
    EMBEDDING_PROVIDER: str = "sentence-transformers"  # sentence-transformers | compact-tfidf | api
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    MAX_ARTICLE_TOKENS: int = 1024
    CHUNK_SIZE_TOKENS: int = 256
    CHUNK_OVERLAP_TOKENS: int = 32
    
    # Vision & OCR
    ENABLE_OCR: bool = True
    VISION_MODEL_NAME: str = "mobilenet_v3_small"
    
    # Optional Cloud LLM (Gemini / OpenAI / Null fallback)
    LLM_PROVIDER: str = "gemini" if os.getenv("GEMINI_API_KEY") else "null"  # null | gemini | openai | local
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # Security
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_IMAGE_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "webp", "bmp"]
    SCRAPER_TIMEOUT_SECONDS: int = 10
    MAX_SCRAPED_CHARS: int = 50000
    
    # Paths
    BASE_PATH: Path = BASE_DIR
    DATA_PATH: Path = DATA_DIR
    MODELS_PATH: Path = MODELS_DIR
    CHECKPOINTS_PATH: Path = CHECKPOINTS_DIR
    EVIDENCE_PATH: Path = EVIDENCE_DIR
    UPLOADS_PATH: Path = UPLOADS_DIR
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
