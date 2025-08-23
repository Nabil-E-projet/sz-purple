from pydantic_settings import BaseSettings
from functools import lru_cache

class AppSettings(BaseSettings):
    ANALYSIS_USE_REMOTE_LLM: bool = False  # sécurité: OFF par défaut
    FEATURE_USE_TESSERACT: bool = False    # OCR off par défaut
    PII_SECRET: str = "dev-change-me"
    PII_PERSON_SCOPE: str = "document"     # or "global"
    ARTIFACTS_BASE_PATH: str = "./artifacts"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra environment variables

@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
