"""Authentication API endpoints.

Provides:
- Login (email/password -> JWT)
- API key management
- Current user/tenant info
"""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intelli.api.dependencies import get_session
from intelli.api.middleware.auth import AdminContext, AuthContext
from intelli.config import settings
from intelli.core.security import (
    create_access_token,
    generate_api_key,
    hash_password,
    verify_password,
)
from intelli.db.models.auth import APIKey, APIKeyScope, Tenant, TenantStatus, User, UserRole
from intelli.services.audit_service import AuditService

router = APIRouter(prefix="/auth", tags=["auth"])


# ============================================================================
# Schemas
# ============================================================================


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_slug: str = Field(..., description="Tenant identifier")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours
    tenant_id: str
    user_id: str


class CurrentUserResponse(BaseModel):
    user_id: str | None = None
    tenant_id: str
    tenant_name: str
    role: str | None = None
    scopes: list[str]
    api_key_id: str | None = None


class APIKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    scopes: list[APIKeyScope] = Field(default=[APIKeyScope.read])
    expires_in_days: int | None = Field(default=None, ge=1, le=365)
    rate_limit_rpm: int = Field(default=60, ge=1, le=1000)
    allowed_ips: list[str] | None = None


class APIKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    scopes: list[str]
    expires_at: datetime | None
    rate_limit_rpm: int
    is_active: bool
    last_used_at: datetime | None
    use_count: int
    created_at: datetime


class APIKeyCreatedResponse(APIKeyResponse):
    """Response when creating a new API key - includes the full key (shown once)."""

    full_key: str = Field(..., description="Full API key - save this, it won't be shown again!")


class DevBootstrapRequest(BaseModel):
    """Development-only bootstrap helper.

    Creates (or reuses) a tenant + user and returns a JWT.
    Only available when DEBUG=true.
    """

    tenant_slug: str = Field(default="demo", min_length=1, max_length=50)
    tenant_name: str = Field(default="Demo Tenant", min_length=1, max_length=100)
    email: EmailStr = Field(default="demo@example.com")
    user_name: str = Field(default="Demo User", min_length=1, max_length=100)
    password: str = Field(default="demo", min_length=1)


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Authenticate with email/password and receive a JWT token."""
    # Find tenant
    result = await session.execute(
        select(Tenant).where(Tenant.slug == data.tenant_slug).where(Tenant.status == "active")
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Find user
    result = await session.execute(
        select(User)
        .where(User.tenant_id == tenant.id)
        .where(User.email == data.email)
        .where(User.is_active)
    )
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Verify password
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Update last login
    user.last_login_at = datetime.now(UTC)
    await session.commit()

    # Create token
    token = create_access_token(
        subject=str(user.id),
        tenant_id=str(tenant.id),
        role=user.role.value,
    )

    return LoginResponse(
        access_token=token,
        tenant_id=str(tenant.id),
        user_id=str(user.id),
    )


@router.post("/dev-bootstrap", response_model=LoginResponse)
async def dev_bootstrap(
    data: DevBootstrapRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Create/reuse a demo tenant + user (development only) and return a JWT."""
    if not settings.debug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    # Find or create tenant
    result = await session.execute(select(Tenant).where(Tenant.slug == data.tenant_slug))
    tenant = result.scalar_one_or_none()
    if not tenant:
        tenant = Tenant(
            name=data.tenant_name,
            slug=data.tenant_slug,
            status=TenantStatus.active,
        )
        session.add(tenant)
        await session.flush()
    elif tenant.status != TenantStatus.active:
        tenant.status = TenantStatus.active
        await session.flush()

    # Find or create user
    result = await session.execute(
        select(User).where(User.tenant_id == tenant.id).where(User.email == data.email)
    )
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            tenant_id=tenant.id,
            email=data.email,
            name=data.user_name,
            role=UserRole.owner,
            password_hash=hash_password(data.password),
            is_active=True,
            last_login_at=datetime.now(UTC),
        )
        session.add(user)
        await session.flush()
    else:
        if not user.password_hash:
            user.password_hash = hash_password(data.password)
        if not user.is_active:
            user.is_active = True
        user.role = UserRole.owner
        user.last_login_at = datetime.now(UTC)
        await session.flush()

    await session.commit()

    token = create_access_token(
        subject=str(user.id),
        tenant_id=str(tenant.id),
        role=user.role.value,
    )

    return LoginResponse(
        access_token=token,
        expires_in=settings.jwt_expiry_hours * 3600,
        tenant_id=str(tenant.id),
        user_id=str(user.id),
    )


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user(
    ctx: AuthContext,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Get information about the current authenticated user/key."""
    # Get tenant info
    result = await session.execute(select(Tenant).where(Tenant.id == ctx.tenant_id))
    tenant = result.scalar_one()

    return CurrentUserResponse(
        user_id=str(ctx.user_id) if ctx.user_id else None,
        tenant_id=str(ctx.tenant_id),
        tenant_name=tenant.name,
        role=ctx.role,
        scopes=ctx.scopes,
        api_key_id=str(ctx.api_key_id) if ctx.api_key_id else None,
    )


@router.get("/keys", response_model=list[APIKeyResponse])
async def list_api_keys(
    ctx: AdminContext,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """List all API keys for the current tenant (admin only)."""
    result = await session.execute(
        select(APIKey).where(APIKey.tenant_id == ctx.tenant_id).order_by(APIKey.created_at.desc())
    )
    keys = result.scalars().all()

    return [
        APIKeyResponse(
            id=str(key.id),
            name=key.name,
            key_prefix=key.key_prefix,
            scopes=key.scopes or [],
            expires_at=key.expires_at,
            rate_limit_rpm=key.rate_limit_rpm,
            is_active=key.is_active,
            last_used_at=key.last_used_at,
            use_count=key.use_count,
            created_at=key.created_at,
        )
        for key in keys
    ]


@router.post("/keys", response_model=APIKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    data: APIKeyCreate,
    ctx: AdminContext,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Create a new API key (admin only).

    The full key is only shown once in the response. Store it securely.
    """
    # Generate key
    full_key, prefix, key_hash = generate_api_key()

    # Calculate expiry
    expires_at = None
    if data.expires_in_days:
        from datetime import timedelta

        expires_at = datetime.now(UTC) + timedelta(days=data.expires_in_days)

    # Create API key record
    api_key = APIKey(
        tenant_id=ctx.tenant_id,
        created_by_user_id=ctx.user_id,
        name=data.name,
        key_prefix=prefix,
        key_hash=key_hash,
        scopes=[s.value for s in data.scopes],
        expires_at=expires_at,
        rate_limit_rpm=data.rate_limit_rpm,
        allowed_ips=data.allowed_ips,
    )

    session.add(api_key)
    await session.flush()

    # Audit log
    audit = AuditService(session)
    await audit.log_api_key_create(api_key.id, data.name, api_key.scopes)

    await session.commit()

    return APIKeyCreatedResponse(
        id=str(api_key.id),
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        scopes=api_key.scopes or [],
        expires_at=api_key.expires_at,
        rate_limit_rpm=api_key.rate_limit_rpm,
        is_active=api_key.is_active,
        last_used_at=api_key.last_used_at,
        use_count=api_key.use_count,
        created_at=api_key.created_at,
        full_key=full_key,
    )


@router.delete("/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: UUID,
    ctx: AdminContext,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Revoke (deactivate) an API key (admin only)."""
    result = await session.execute(
        select(APIKey).where(APIKey.id == key_id).where(APIKey.tenant_id == ctx.tenant_id)
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    api_key.is_active = False

    # Audit log
    audit = AuditService(session)
    await audit.log_api_key_revoke(api_key.id, api_key.name)

    await session.commit()
