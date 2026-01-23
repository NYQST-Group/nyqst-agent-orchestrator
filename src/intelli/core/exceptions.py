"""Application exception hierarchy.

Provides structured exceptions that map cleanly to HTTP responses
and carry context for logging and debugging.
"""

from typing import Any, Optional


class IntelliError(Exception):
    """Base exception for all Intelli errors.

    Attributes:
        message: Human-readable error message
        code: Machine-readable error code
        status_code: HTTP status code to return
        details: Additional context for debugging
    """

    message: str = "An error occurred"
    code: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message or self.__class__.message
        self.code = code or self.__class__.code
        self.status_code = status_code or self.__class__.status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON response."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


# ============================================================================
# Client Errors (4xx)
# ============================================================================

class ValidationError(IntelliError):
    """Invalid input data."""
    message = "Validation failed"
    code = "VALIDATION_ERROR"
    status_code = 400

    def __init__(self, message: str = None, field: str = None, **kwargs):
        super().__init__(message=message, **kwargs)
        if field:
            self.details["field"] = field


class AuthenticationError(IntelliError):
    """Authentication failed."""
    message = "Authentication required"
    code = "AUTHENTICATION_ERROR"
    status_code = 401


class AuthorizationError(IntelliError):
    """Authorization failed."""
    message = "Permission denied"
    code = "AUTHORIZATION_ERROR"
    status_code = 403


class NotFoundError(IntelliError):
    """Resource not found."""
    message = "Resource not found"
    code = "NOT_FOUND"
    status_code = 404

    def __init__(
        self,
        resource_type: str = None,
        identifier: str = None,
        message: str = None,
        **kwargs,
    ):
        if resource_type and identifier:
            message = message or f"{resource_type} not found: {identifier}"
            kwargs.setdefault("details", {})
            kwargs["details"]["resource_type"] = resource_type
            kwargs["details"]["identifier"] = identifier
        super().__init__(message=message, **kwargs)


class ConflictError(IntelliError):
    """Resource conflict (e.g., duplicate, version mismatch)."""
    message = "Resource conflict"
    code = "CONFLICT"
    status_code = 409


class RateLimitError(IntelliError):
    """Rate limit exceeded."""
    message = "Rate limit exceeded"
    code = "RATE_LIMIT_EXCEEDED"
    status_code = 429

    def __init__(
        self,
        limit: int = 60,
        reset_after: int = 60,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.limit = limit
        self.reset_after = reset_after
        self.details = {
            "limit": limit,
            "reset_after_seconds": reset_after,
        }


# ============================================================================
# Resource-Specific Errors
# ============================================================================

class ArtifactNotFoundError(NotFoundError):
    """Artifact not found."""
    code = "ARTIFACT_NOT_FOUND"

    def __init__(self, sha256: str, **kwargs):
        super().__init__(
            resource_type="Artifact",
            identifier=sha256[:16] + "...",
            details={"sha256": sha256},
            **kwargs,
        )


class ManifestNotFoundError(NotFoundError):
    """Manifest not found."""
    code = "MANIFEST_NOT_FOUND"

    def __init__(self, sha256: str, **kwargs):
        super().__init__(
            resource_type="Manifest",
            identifier=sha256[:16] + "...",
            details={"sha256": sha256},
            **kwargs,
        )


class PointerNotFoundError(NotFoundError):
    """Pointer not found."""
    code = "POINTER_NOT_FOUND"

    def __init__(self, namespace: str = None, name: str = None, pointer_id: str = None, **kwargs):
        if namespace and name:
            identifier = f"{namespace}/{name}"
        else:
            identifier = pointer_id or "unknown"
        super().__init__(
            resource_type="Pointer",
            identifier=identifier,
            details={"namespace": namespace, "name": name, "pointer_id": pointer_id},
            **kwargs,
        )


class RunNotFoundError(NotFoundError):
    """Run not found."""
    code = "RUN_NOT_FOUND"

    def __init__(self, run_id: str, **kwargs):
        super().__init__(
            resource_type="Run",
            identifier=run_id,
            details={"run_id": run_id},
            **kwargs,
        )


class VersionConflictError(ConflictError):
    """Version mismatch during optimistic locking."""
    code = "VERSION_CONFLICT"

    def __init__(self, expected: int, actual: int, **kwargs):
        super().__init__(
            message=f"Version conflict: expected {expected}, got {actual}",
            details={"expected_version": expected, "actual_version": actual},
            **kwargs,
        )


class DuplicateResourceError(ConflictError):
    """Resource already exists."""
    code = "DUPLICATE_RESOURCE"


# ============================================================================
# Server Errors (5xx)
# ============================================================================

class StorageError(IntelliError):
    """Storage backend error."""
    message = "Storage operation failed"
    code = "STORAGE_ERROR"
    status_code = 500

    def __init__(self, message: str = None, operation: str = None, **kwargs):
        super().__init__(message=message, **kwargs)
        if operation:
            self.details["operation"] = operation


class DatabaseError(IntelliError):
    """Database operation failed."""
    message = "Database operation failed"
    code = "DATABASE_ERROR"
    status_code = 500


class ExternalServiceError(IntelliError):
    """External service (LLM, etc.) failed."""
    message = "External service error"
    code = "EXTERNAL_SERVICE_ERROR"
    status_code = 502
