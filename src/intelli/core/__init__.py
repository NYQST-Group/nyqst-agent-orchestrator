"""Core cross-cutting concerns."""

from intelli.core.exceptions import (
    IntelliError,
    NotFoundError,
    ConflictError,
    ValidationError,
    StorageError,
)

__all__ = [
    "IntelliError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "StorageError",
]
