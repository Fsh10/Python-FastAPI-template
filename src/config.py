from __future__ import annotations

import os

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class CustomBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Config(CustomBaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB_TEST: str

    SMTP_USER: str
    SMTP_PASSWORD: str

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    BASE_API_PATH: str
    SECRET_AUTH: str
    DOMAIN_NAME: str

    DATABASE_URL: PostgresDsn
    DATABASE_ASYNC_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 10
    DATABASE_POOL_TTL: int = 60 * 20
    DATABASE_POOL_PRE_PING: bool = True
    DATABASE_MAX_OVERFLOW: int = 20

    MODE: str
    ENVIRONMENT: str
    SENTRY_DSN: str | None = None

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: list[str] = ["*"]

    APP_VERSION: str = "0.1"
    TEST_API_URL_ADDRESS: str = "http://127.0.0.1:8000"

    DATABASE_URL: PostgresDsn | None = None
    DATABASE_URL_TEST: PostgresDsn | None = None
    DATABASE_ASYNC_URL: PostgresDsn | None = None

    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    S3_ENDPOINT_URL: str
    S3_BUCKET_NAME: str
    S3_REGION: str

    RABBITMQ_HOST: str
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_SSL: bool = False
    RABBITMQ_PORT: int = 5672

    REDIS_URL: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not self.DATABASE_URL:
            self.DATABASE_URL = PostgresDsn.build(
                scheme="postgresql",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=f"{self.POSTGRES_DB}",
            )

        if not self.DATABASE_ASYNC_URL:
            self.DATABASE_ASYNC_URL = PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=f"{self.POSTGRES_DB}",
            )

        if not self.DATABASE_URL_TEST:
            self.DATABASE_URL_TEST = PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=f"{self.POSTGRES_DB_TEST}",
            )


settings = Config()
