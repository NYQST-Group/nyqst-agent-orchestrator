"""Async database engine and session management."""

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from intelli.config import settings


@lru_cache
def get_engine() -> AsyncEngine:
    """Create and cache the async database engine."""
    return create_async_engine(
        str(settings.database_url),
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        echo=settings.debug,
    )


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create and cache the session factory."""
    return async_sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


# Alias for direct usage
AsyncSessionLocal = get_session_factory()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields database sessions."""
    async with get_session_factory()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
