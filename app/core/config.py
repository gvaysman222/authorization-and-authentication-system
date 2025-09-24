from pydantic import BaseModel
import os

class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    TOKEN_TTL_HOURS: int = int(os.getenv("TOKEN_TTL_HOURS", "24"))
    CORS_ORIGINS: list[str] = ["*"]

    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

settings = Settings()
