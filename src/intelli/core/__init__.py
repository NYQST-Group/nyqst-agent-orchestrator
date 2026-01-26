"""Core cross-cutting concerns."""

from intelli.core.exceptions import (
    ArtifactNotFoundError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DatabaseError,
    ExternalServiceError,
    IntelliError,
    ManifestNotFoundError,
    NotFoundError,
    PointerNotFoundError,
    RateLimitError,
    RunNotFoundError,
    StorageError,
    ValidationError,
    VersionConflictError,
)
from intelli.core.logging import get_correlation_id, get_logger, set_correlation_id, setup_logging

__all__ = [
    # Exceptions
    "IntelliError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "StorageError",
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",
    "ArtifactNotFoundError",
    "ManifestNotFoundError",
    "PointerNotFoundError",
    "RunNotFoundError",
    "VersionConflictError",
    "DatabaseError",
    "ExternalServiceError",
    # Logging
    "get_logger",
    "setup_logging",
    "get_correlation_id",
    "set_correlation_id",
]
