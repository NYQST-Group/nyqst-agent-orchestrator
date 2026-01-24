"""Core cross-cutting concerns."""

from intelli.core.exceptions import (
    IntelliError,
    NotFoundError,
    ConflictError,
    ValidationError,
    StorageError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    ArtifactNotFoundError,
    ManifestNotFoundError,
    PointerNotFoundError,
    RunNotFoundError,
    VersionConflictError,
    DatabaseError,
    ExternalServiceError,
)
from intelli.core.logging import get_logger, setup_logging, get_correlation_id, set_correlation_id

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
