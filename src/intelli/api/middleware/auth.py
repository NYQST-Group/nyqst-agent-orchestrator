"""Authentication middleware for FastAPI.

Handles:
- API key authentication (X-API-Key header)
- JWT bearer token authentication
- Rate limiting
- Request context setup
- Audit logging
"""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from intelli.api.dependencies import get_session
from intelli.core.context import RequestContext, set_context
from intelli.core.security import decode_access_token, hash_api_key, rate_limiter
from intelli.db.models.auth import APIKey, Tenant, User

# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)


async def get_api_key_auth(
    session: AsyncSession,
    api_key: str,
    request: Request,
) -> RequestContext | None:
    """Authenticate via API key.

    Returns RequestContext if valid, None otherwise.
    """
    # Hash the key and look it up
    key_hash = hash_api_key(api_key)

    result = await session.execute(
        select(APIKey, Tenant)
        .join(Tenant, APIKey.tenant_id == Tenant.id)
        .where(APIKey.key_hash == key_hash)
        .where(APIKey.is_active)
        .where(Tenant.status == "active")
    )
    row = result.first()

    if not row:
        return None

    api_key_obj, tenant = row

    # Check expiry
    if api_key_obj.expires_at and api_key_obj.expires_at < datetime.now(UTC):
        return None

    # Check IP allowlist
    client_ip = request.client.host if request.client else None
    if api_key_obj.allowed_ips and client_ip not in api_key_obj.allowed_ips:
        return None

    # Check rate limit
    if not rate_limiter.is_allowed(
        str(api_key_obj.id),
        api_key_obj.rate_limit_rpm,
        window_seconds=60,
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(api_key_obj.rate_limit_rpm),
                "X-RateLimit-Remaining": "0",
                "Retry-After": "60",
            },
        )

    # Update last used
    await session.execute(
        update(APIKey)
        .where(APIKey.id == api_key_obj.id)
        .values(
            last_used_at=datetime.now(UTC),
            use_count=APIKey.use_count + 1,
        )
    )

    return RequestContext(
        tenant_id=tenant.id,
        api_key_id=api_key_obj.id,
        scopes=api_key_obj.scopes or [],
        ip_address=client_ip,
        user_agent=request.headers.get("user-agent"),
    )


async def get_bearer_auth(
    session: AsyncSession,
    token: str,
    request: Request,
) -> RequestContext | None:
    """Authenticate via JWT bearer token.

    Returns RequestContext if valid, None otherwise.
    """
    payload = decode_access_token(token)
    if not payload:
        return None

    # Validate tenant still exists and is active
    tenant_id = UUID(payload["tid"])
    result = await session.execute(
        select(Tenant).where(Tenant.id == tenant_id).where(Tenant.status == "active")
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        return None

    # Validate user still exists and is active
    user_id = UUID(payload["sub"])
    result = await session.execute(
        select(User)
        .where(User.id == user_id)
        .where(User.tenant_id == tenant_id)
        .where(User.is_active)
    )
    user = result.scalar_one_or_none()

    if not user:
        return None

    client_ip = request.client.host if request.client else None

    return RequestContext(
        tenant_id=tenant_id,
        user_id=user_id,
        role=payload.get("role"),
        scopes=["read", "write"] if user.role in ("owner", "admin", "member") else ["read"],
        ip_address=client_ip,
        user_agent=request.headers.get("user-agent"),
    )


async def authenticate(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    bearer: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
) -> RequestContext:
    """Authenticate the request and return context.

    Tries API key first, then bearer token.
    Raises 401 if neither is valid.
    """
    context: RequestContext | None = None

    # Try API key first
    if x_api_key:
        context = await get_api_key_auth(session, x_api_key, request)

    # Fall back to bearer token
    if not context and bearer:
        context = await get_bearer_auth(session, bearer.credentials, request)

    if not context:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Set context for the rest of the request
    set_context(context)

    return context


async def authenticate_optional(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    bearer: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
) -> RequestContext | None:
    """Optionally authenticate the request.

    Returns None if no valid auth provided (doesn't raise).
    Used for public endpoints that behave differently when authenticated.
    """
    context: RequestContext | None = None

    if x_api_key:
        try:
            context = await get_api_key_auth(session, x_api_key, request)
        except HTTPException:
            pass  # Rate limit - still return None for optional auth

    if not context and bearer:
        context = await get_bearer_auth(session, bearer.credentials, request)

    if context:
        set_context(context)

    return context


def require_scope(scope: str):
    """Dependency to require a specific scope."""
    async def check_scope(ctx: Annotated[RequestContext, Depends(authenticate)]):
        if not ctx.has_scope(scope):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scope: {scope}",
            )
        return ctx
    return check_scope


def require_admin():
    """Dependency to require admin access."""
    async def check_admin(ctx: Annotated[RequestContext, Depends(authenticate)]):
        if not ctx.can_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )
        return ctx
    return check_admin


# Type aliases for dependency injection
AuthContext = Annotated[RequestContext, Depends(authenticate)]
OptionalAuthContext = Annotated[RequestContext | None, Depends(authenticate_optional)]
WriteContext = Annotated[RequestContext, Depends(require_scope("write"))]
AdminContext = Annotated[RequestContext, Depends(require_admin())]
AgentContext = Annotated[RequestContext, Depends(require_scope("agent"))]
