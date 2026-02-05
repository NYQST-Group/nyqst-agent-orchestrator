"""Background session idle monitor.

Periodically checks for active sessions that have been idle past their
timeout threshold and transitions them to idle status.
"""

import asyncio
import logging

from intelli.config import settings
from intelli.db.engine import get_session as db_get_session
from intelli.services.session_service import SessionService

logger = logging.getLogger(__name__)

_task: asyncio.Task | None = None


async def _monitor_loop() -> None:
    """Background loop that checks for stale sessions."""
    while True:
        try:
            await asyncio.sleep(settings.session_monitor_interval_seconds)
            async for session in db_get_session():
                service = SessionService(session)
                count = await service.idle_stale_sessions()
                if count:
                    logger.info("sessions_idled", extra={"count": count})
        except asyncio.CancelledError:
            break
        except Exception:
            logger.exception("session_monitor_error")


async def start_session_monitor() -> None:
    """Start the background session monitor task."""
    global _task
    if _task is None:
        _task = asyncio.create_task(_monitor_loop())
        logger.info("session_monitor_started")


async def stop_session_monitor() -> None:
    """Stop the background session monitor task."""
    global _task
    if _task is not None:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
        _task = None
        logger.info("session_monitor_stopped")
