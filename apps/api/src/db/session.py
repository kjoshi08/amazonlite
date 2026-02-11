from __future__ import annotations

from typing import Generator
from sqlalchemy.orm import Session

from src.db.database import SessionLocal  # change if your sessionmaker name differs


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
