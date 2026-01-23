"""Authentication and authorization models.

Enterprise-grade multi-tenant security:
- Tenants: Isolated organizational units
- Users: Human actors with roles
- API Keys: Machine credentials with scopes
- Audit Log: Immutable record of all actions
"""

import secrets
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from intelli.db.base import Base
from intelli.db.models.mixins import TimestampMixin


class TenantStatus(str, Enum):
    """Tenant lifecycle states."""
    active = "active"
    suspended = "suspended"
    pending = "pending"


class UserRole(str, Enum):
    """User roles within a tenant."""
    owner = "owner"      # Full control, billing, can delete tenant
    admin = "admin"      # Manage users, API keys, all resources
    member = "member"    # Read/write resources
    viewer = "viewer"    # Read-only access


class APIKeyScope(str, Enum):
    """API key permission scopes."""
    read = "read"                # Read artifacts, manifests, runs
    write = "write"              # Create/modify resources
    admin = "admin"              # Manage tenant settings
    agent = "agent"              # MCP tool access (runs, checkpoints)


class Tenant(Base, TimestampMixin):
    """Organizational unit for resource isolation.

    All resources (artifacts, manifests, pointers, runs) belong to a tenant.
    Provides hard isolation boundary for multi-tenancy.
    """
    __tablename__ = "tenants"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    status: Mapped[TenantStatus] = mapped_column(default=TenantStatus.active)

    # Quotas and limits
    storage_quota_bytes: Mapped[int] = mapped_column(default=10 * 1024**3)  # 10 GB
    run_quota_monthly: Mapped[int] = mapped_column(default=1000)

    # Settings
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Relationships
    users: Mapped[list["User"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    api_keys: Mapped[list["APIKey"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")


class User(Base, TimestampMixin):
    """Human user within a tenant."""
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    email: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(default=UserRole.member)

    # Auth - password hash for local auth, or external provider ID
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    external_id: Mapped[Optional[str]] = mapped_column(String(255))  # OAuth/SAML subject
    external_provider: Mapped[Optional[str]] = mapped_column(String(50))  # google, okta, etc.

    # Status
    is_active: Mapped[bool] = mapped_column(default=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column()

    # Relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="users")

    __table_args__ = (
        Index("ix_users_tenant_email", "tenant_id", "email", unique=True),
        Index("ix_users_external", "external_provider", "external_id"),
    )


class APIKey(Base, TimestampMixin):
    """Machine credential for API access.

    Keys are hashed - we only store the hash, not the plaintext.
    The plaintext is shown once at creation time.
    """
    __tablename__ = "api_keys"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    created_by_user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(12), nullable=False)  # First 8 chars for identification
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False)    # SHA-256 of full key

    # Permissions
    scopes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Constraints
    expires_at: Mapped[Optional[datetime]] = mapped_column()
    rate_limit_rpm: Mapped[int] = mapped_column(default=60)  # Requests per minute
    allowed_ips: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))  # IP allowlist

    # Status
    is_active: Mapped[bool] = mapped_column(default=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column()
    use_count: Mapped[int] = mapped_column(default=0)

    # Relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="api_keys")

    __table_args__ = (
        Index("ix_api_keys_prefix", "key_prefix"),
        Index("ix_api_keys_hash", "key_hash", unique=True),
    )

    @staticmethod
    def generate_key() -> tuple[str, str, str]:
        """Generate a new API key.

        Returns:
            Tuple of (full_key, prefix, hash)
            The full_key should be shown to user once, then discarded.
        """
        import hashlib

        # Format: int_xxxxxxxxxxxxxxxxxxxxxxxxxxxx (32 chars after prefix)
        random_part = secrets.token_hex(16)
        full_key = f"int_{random_part}"
        prefix = full_key[:12]
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()

        return full_key, prefix, key_hash

    @staticmethod
    def hash_key(key: str) -> str:
        """Hash an API key for comparison."""
        import hashlib
        return hashlib.sha256(key.encode()).hexdigest()


class AuditLog(Base):
    """Immutable audit trail of all significant actions.

    Append-only log for compliance, debugging, and security.
    Partitioned by timestamp for efficient querying and retention.
    """
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    # Actor
    tenant_id: Mapped[UUID] = mapped_column(nullable=False)
    user_id: Mapped[Optional[UUID]] = mapped_column()
    api_key_id: Mapped[Optional[UUID]] = mapped_column()

    # Action
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "artifact.create"
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "artifact"
    resource_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Context
    ip_address: Mapped[Optional[str]] = mapped_column(INET)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    request_id: Mapped[Optional[str]] = mapped_column(String(36))

    # Details
    details: Mapped[dict] = mapped_column(JSONB, default=dict)

    __table_args__ = (
        Index("ix_audit_tenant_time", "tenant_id", "timestamp"),
        Index("ix_audit_resource", "resource_type", "resource_id"),
        Index("ix_audit_action", "action", "timestamp"),
    )
