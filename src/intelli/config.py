"""Application configuration using Pydantic settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Intelli Document Platform")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://intelli:intelli@localhost:5432/intelli"
    )
    db_pool_size: int = Field(default=10)
    db_max_overflow: int = Field(default=20)

    # Storage
    storage_backend: Literal["s3", "local"] = Field(default="s3")
    s3_endpoint_url: str | None = Field(default=None)
    s3_bucket: str = Field(default="intelli-artifacts")
    s3_access_key: str | None = Field(default=None)
    s3_secret_key: str | None = Field(default=None)
    s3_region: str = Field(default="us-east-1")
    local_storage_path: str = Field(default="/tmp/intelli-storage")

    # Embeddings
    embedding_model: str = Field(default="text-embedding-3-small")
    embedding_dimensions: int = Field(default=1536)
    openai_api_key: str | None = Field(default=None)

    # MCP Server
    mcp_transport: Literal["streamable-http", "stdio"] = Field(default="streamable-http")
    mcp_port: int = Field(default=8001)

    # Observability
    langfuse_enabled: bool = Field(default=False)
    langfuse_public_key: str | None = Field(default=None)
    langfuse_secret_key: str | None = Field(default=None)
    langfuse_host: str = Field(default="https://cloud.langfuse.com")


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


settings = get_settings()
