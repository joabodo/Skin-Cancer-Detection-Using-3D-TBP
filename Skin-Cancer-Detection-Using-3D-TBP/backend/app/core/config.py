import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://skinuser:sk!npass@db/skinapp")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change_me")
    MODEL_PATH: str = os.getenv("MODEL_PATH", "/app/model/best_model.pth")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/app/uploads")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    RATE_LIMIT_PER_MIN: int = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))
    class Config:
        env_file = ".env"

settings = Settings()
