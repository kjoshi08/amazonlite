from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str = "postgresql+psycopg://amazonlite:amazonlite@postgres:5432/amazonlite"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT (if you already have these, keep them)
    JWT_SECRET: str = "dev-secret-change-me"
    JWT_EXPIRE_MIN: int = 60


settings = Settings()
