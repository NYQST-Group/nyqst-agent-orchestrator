"""LangGraph checkpoint persistence using PostgreSQL.

Provides AsyncPostgresSaver backed by a separate psycopg connection pool.
This pool uses psycopg (not asyncpg) because LangGraph's checkpoint format
requires psycopg-native wire protocol features.

The checkpointer stores full agent state as binary blobs, enabling
multi-turn conversation, state replay, and time-travel debugging.

This module uses a class-based singleton pattern to avoid module-level
mutable state, making it easier to test and reset between tests.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from intelli.config import settings

if TYPE_CHECKING:
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)


class CheckpointerManager:
    """Manages the LangGraph checkpointer lifecycle.

    This class provides a singleton-like interface without module-level state,
    making it easier to test and integrate with FastAPI's lifespan events.
    """

    def __init__(self) -> None:
        self._checkpointer: AsyncPostgresSaver | None = None
        self._pool: AsyncConnectionPool | None = None

    @staticmethod
    def _get_psycopg_conninfo() -> str:
        """Convert the asyncpg database URL to a psycopg-compatible conninfo string."""
        url = str(settings.database_url)
        # asyncpg URL: postgresql+asyncpg://user:pass@host:port/db
        # psycopg needs: postgresql://user:pass@host:port/db
        if "+asyncpg" in url:
            url = url.replace("+asyncpg", "")
        return url

    async def get_checkpointer(self) -> AsyncPostgresSaver:
        """Get or create the AsyncPostgresSaver.

        On first call, creates the psycopg connection pool and LangGraph
        checkpoint tables. Subsequent calls return the cached instance.
        """
        if self._checkpointer is not None:
            return self._checkpointer

        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        from psycopg_pool import AsyncConnectionPool

        conninfo = self._get_psycopg_conninfo()
        self._pool = AsyncConnectionPool(
            conninfo=conninfo,
            min_size=2,
            max_size=settings.checkpointer_pool_size,
            open=False,
            kwargs={
                "autocommit": True,
                "prepare_threshold": 0,
            },
        )
        await self._pool.open()

        self._checkpointer = AsyncPostgresSaver(self._pool)
        await self._checkpointer.setup()

        logger.info(
            "langgraph_checkpointer_initialized",
            extra={"pool_size": settings.checkpointer_pool_size},
        )
        return self._checkpointer

    async def close_checkpointer(self) -> None:
        """Close the checkpointer connection pool. Called on app shutdown."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
            self._checkpointer = None
            logger.info("langgraph_checkpointer_closed")


# Global instance for the application
_manager = CheckpointerManager()


async def get_checkpointer() -> AsyncPostgresSaver:
    """Get the AsyncPostgresSaver instance.

    This is the main entry point for the application to access the checkpointer.
    """
    return await _manager.get_checkpointer()


async def close_checkpointer() -> None:
    """Close the checkpointer connection pool.

    Called during FastAPI shutdown. This delegates to the manager instance.
    """
    await _manager.close_checkpointer()
