"""API middleware components."""

from intelli.api.middleware.auth import (
    authenticate,
    authenticate_optional,
    require_scope,
    require_admin,
    AuthContext,
    OptionalAuthContext,
    WriteContext,
    AdminContext,
    AgentContext,
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
