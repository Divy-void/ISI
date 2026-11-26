import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "IS-Assist"
    ENVIRONMENT: str = "demo"
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'storage' / 'is_assist_demo.db'}"
    STORAGE_DIR: str = str(BASE_DIR / "storage" / "uploads")
    MAX_UPLOAD_SIZE_MB: int = 20
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(Path(settings.DATABASE_URL.replace("sqlite:///", "")).parent, exist_ok=True)
