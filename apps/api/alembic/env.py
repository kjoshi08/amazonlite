from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your Base + models so Alembic can autogenerate
from src.db import models  # noqa: F401,E402  (ensures models are imported)
from src.db.base import Base  # noqa: E402

target_metadata = Base.metadata


def get_db_url() -> str:
    # Prefer env var from docker-compose
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # Optional fallback to settings if present
    try:
        from src.core.config import settings  # type: ignore
        if hasattr(settings, "DATABASE_URL"):
            return getattr(settings, "DATABASE_URL")
        if hasattr(settings, "database_url"):
            return getattr(settings, "database_url")
    except Exception:
        pass

    # Last resort default for compose network
    return "postgresql+psycopg://amazonlite:amazonlite@postgres:5432/amazonlite"


def run_migrations_offline() -> None:
    url = get_db_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_db_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
