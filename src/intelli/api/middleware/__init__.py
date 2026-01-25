"""API middleware components."""

from intelli.api.middleware.auth import (
    AdminContext,
    AgentContext,
    AuthContext,
    OptionalAuthContext,
    WriteContext,
    authenticate,
    authenticate_optional,
    require_admin,
    require_scope,
)
from intelli.api.middleware.correlation import CorrelationMiddleware
from intelli.api.middleware.error_handler import ErrorHandlerMiddleware, intelli_exception_handler

__all__ = [
    # Auth dependencies
    "authenticate",
    "authenticate_optional",
    "require_scope",
    "require_admin",
    "AuthContext",
    "OptionalAuthContext",
    "WriteContext",
    "AdminContext",
    "AgentContext",
    # Middleware classes
    "CorrelationMiddleware",
    "ErrorHandlerMiddleware",
    "intelli_exception_handler",
]
