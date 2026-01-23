"""Request context for tenant isolation and audit trails.

Provides a clean way to access the current tenant, user, and request
context from anywhere in the application without passing through all layers.
"""

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class RequestContext:
    """Context for the current request.

    Carries tenant isolation info and audit metadata through the request.
    """
    # Request identification
    request_id: str = field(default_factory=lambda: str(uuid4()))

    # Tenant isolation (required for all authenticated requests)
    tenant_id: Optional[UUID] = None

    # Actor info (mutually exclusive - either user or API key)
    user_id: Optional[UUID] = None
    api_key_id: Optional[UUID] = None

    # Authorization
    role: Optional[str] = None
    scopes: list[str] = field(default_factory=list)

    # Client info for audit
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    def is_authenticated(self) -> bool:
        """Check if request has valid authentication."""
        return self.tenant_id is not None

    def has_scope(self, scope: str) -> bool:
        """Check if current context has a specific scope."""
        return scope in self.scopes or "admin" in self.scopes

    def can_write(self) -> bool:
        """Check if current context has write permission."""
        return self.has_scope("write") or self.has_scope("admin") or self.has_scope("agent")

    def can_admin(self) -> bool:
        """Check if current context has admin permission."""
        return self.has_scope("admin") or self.role in ("owner", "admin")


# Context variable to hold the current request context
_request_context: ContextVar[Optional[RequestContext]] = ContextVar(
    "request_context", default=None
)


def get_context() -> RequestContext:
    """Get the current request context.

    Raises:
        RuntimeError: If no context is set
    """
    ctx = _request_context.get()
    if ctx is None:
        raise RuntimeError("No request context available")
    return ctx


def get_context_or_none() -> Optional[RequestContext]:
    """Get the current request context or None if not set."""
    return _request_context.get()


def set_context(ctx: RequestContext) -> None:
    """Set the request context for the current execution."""
    _request_context.set(ctx)


def clear_context() -> None:
    """Clear the request context."""
    _request_context.set(None)


def get_tenant_id() -> UUID:
    """Get the current tenant ID.

    Convenience function for common case.

    Raises:
        RuntimeError: If no context or tenant not set
    """
    ctx = get_context()
    if ctx.tenant_id is None:
        raise RuntimeError("No tenant in context")
    return ctx.tenant_id
