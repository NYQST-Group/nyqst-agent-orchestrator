"""Domain exceptions for the Intelli platform."""


class IntelliError(Exception):
    """Base exception for all Intelli errors."""

    def __init__(self, message: str, code: str | None = None) -> None:
        self.message = message
        self.code = code or "INTELLI_ERROR"
        super().__init__(message)


class NotFoundError(IntelliError):
    """Resource not found."""

    def __init__(self, resource_type: str, identifier: str) -> None:
        self.resource_type = resource_type
        self.identifier = identifier
        super().__init__(
            message=f"{resource_type} not found: {identifier}",
            code="NOT_FOUND",
        )


class ConflictError(IntelliError):
    """Resource conflict (e.g., concurrent modification)."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="CONFLICT")


class ValidationError(IntelliError):
    """Input validation failed."""

    def __init__(self, message: str, field: str | None = None) -> None:
        self.field = field
        super().__init__(message=message, code="VALIDATION_ERROR")


class StorageError(IntelliError):
    """Storage backend error."""

    def __init__(self, message: str, operation: str | None = None) -> None:
        self.operation = operation
        super().__init__(message=message, code="STORAGE_ERROR")
