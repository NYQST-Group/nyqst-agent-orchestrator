"""Time abstraction for testability."""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return current UTC timestamp."""
    return datetime.now(UTC)
