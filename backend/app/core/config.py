from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    APP_NAME: str = "CodeNexus"
    VERSION: str = "1.0.0"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # AI Settings
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    EMBEDDING_MODEL: str = "text-embedding-004"
    LLM_MODEL: str = "gemini-2.5-flash"
    
    # Scanning Limits
    MAX_FILE_SIZE_BYTES: int = 1024 * 1024  # 1MB per file
    MAX_TOTAL_FILES: int = 5000
    
    # Embedding Cache Path
    CACHE_DIR: str = ".codenexus_cache"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

