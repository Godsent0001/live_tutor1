# app/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from .env
    """

    # ----------------------------
    # APP
    # ----------------------------
    APP_NAME: str = "Live Tutor API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ----------------------------
    # GEMINI
    # ----------------------------
    GEMINI_API_KEY: str = ""

    # ----------------------------
    # JWT
    # ----------------------------
    JWT_SECRET: str = "super-secret-key"
    JWT_ALGORITHM: str = "HS256"

    # ----------------------------
    # MONGODB
    # ----------------------------
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "live_tutor"

    # ----------------------------
    # STORAGE
    # ----------------------------
    STORAGE_PATH: str = "app/storage"

    # ----------------------------
    # FILE UPLOADS
    # ----------------------------
    UPLOAD_PATH: str = "app/storage/uploads"

    # ----------------------------
    # TTS
    # ----------------------------
    TTS_API_KEY: str = ""
    TTS_BASE_URL: str = ""

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()