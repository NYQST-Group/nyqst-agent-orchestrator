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
        default="postgresql+asyncpg://intelli:intelli@localhost:5433/intelli_test"
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
    openai_base_url: str | None = Field(default=None)

    # LLM (for answer generation)
    chat_model: str = Field(default="gpt-5-nano")
    chat_model_temperature: float = Field(default=0.2, description="LLM temperature for chat/agent")
    chat_model_max_tokens: int = Field(
        default=4096, description="Max completion tokens (includes reasoning)"
    )
    chat_model_reasoning_effort: str | None = Field(
        default=None,
        description="Reasoning effort for o-series models: low, medium, high. None = not a reasoning model.",
    )

    # Indexing / search backend
    index_backend: Literal["pgvector", "opensearch"] = Field(default="pgvector")
    opensearch_url: str = Field(default="http://localhost:9200")
    opensearch_username: str | None = Field(default=None)
    opensearch_password: str | None = Field(default=None)
    opensearch_verify_certs: bool = Field(default=False)
    opensearch_chunks_index: str = Field(default="intelli-chunks-v1")

    # MCP Server
    mcp_transport: Literal["streamable-http", "stdio"] = Field(default="streamable-http")
    mcp_port: int = Field(default=8001)

    # Security
    secret_key: str = Field(
        default="CHANGE-ME-IN-PRODUCTION-use-openssl-rand-hex-32",
        description="Secret key for JWT signing. Generate with: openssl rand -hex 32",
    )
    jwt_expiry_hours: int = Field(default=24)
    cors_origins: list[str] = Field(default=["http://localhost:3000"])
    rate_limit_rpm: int = Field(default=60, description="Default rate limit requests per minute")

    # LangGraph checkpointer
    checkpointer_pool_size: int = Field(
        default=5, description="psycopg pool size for LangGraph checkpointer"
    )

    # Redis (optional - graceful fallback if not configured)
    redis_url: str | None = Field(
        default=None, description="Redis URL for caching and rate limiting"
    )

    # Session monitoring
    session_monitor_interval_seconds: int = Field(
        default=300,
        description="Interval in seconds between session idle checks (default: 5 minutes)",
    )

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
