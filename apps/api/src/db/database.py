import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

try:
    from src.core.config import settings  # type: ignore
except Exception:
    settings = None  # type: ignore


def _db_url() -> str:
    # 1) Prefer env var from docker-compose
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # 2) Fallback to Settings (support both styles)
    if settings is not None:
        if hasattr(settings, "DATABASE_URL"):
            return getattr(settings, "DATABASE_URL")
        if hasattr(settings, "database_url"):
            return getattr(settings, "database_url")

    # 3) Last resort default for compose network
    return "postgresql+psycopg://amazonlite:amazonlite@postgres:5432/amazonlite"


engine = create_engine(_db_url(), pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
