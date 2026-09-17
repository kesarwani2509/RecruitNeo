from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Defaults to a local SQLite file so the app runs out-of-the-box.
    # For production, set DATABASE_URL to a PostgreSQL connection string,
    # e.g. postgresql://user:pass@host:5432/resume_matcher
    database_url: str = "sqlite:///./resume_matcher.db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    gemini_api_key: Optional[str] = None
    upload_dir: str = "./uploads"
    project_name: str = "Resume Relevance Check System"
    environment: str = "development"
    chroma_persist_dir: str = "./chroma_db"
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
