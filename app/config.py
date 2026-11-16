import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "FraudShield AI Backend"
    database_url: str = "sqlite:///./fraudshield_dev.db"
    jwt_secret: str = ""
    token_minutes: int = 30
    cors_origins: tuple[str, ...] = ("http://127.0.0.1:5500", "http://localhost:5500", "http://localhost:8000")


@lru_cache

def settings() -> Settings:
    from dotenv import load_dotenv
    load_dotenv()
    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///./fraudshield_dev.db"),
        jwt_secret=os.getenv("JWT_SECRET", ""),
        token_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        cors_origins=tuple(s.strip() for s in os.getenv("CORS_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500,http://localhost:8000").split(",") if s.strip()),
    )
