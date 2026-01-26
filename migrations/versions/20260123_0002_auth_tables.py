"""Add authentication and audit tables.

Revision ID: 20260123_0002
Revises: 20260123_0001
Create Date: 2026-01-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, INET, JSONB, UUID

revision: str = "20260123_0002"
down_revision: Union[str, None] = "20260123_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tenants table
    op.create_table(
        "tenants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(50), unique=True, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, default="active"),
        sa.Column("storage_quota_bytes", sa.BigInteger, nullable=False, default=10737418240),
        sa.Column("run_quota_monthly", sa.Integer, nullable=False, default=1000),
        sa.Column("settings", JSONB, nullable=False, default={}),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Users table
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, default="member"),
        sa.Column("password_hash", sa.String(255)),
        sa.Column("external_id", sa.String(255)),
        sa.Column("external_provider", sa.String(50)),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_tenant_email", "users", ["tenant_id", "email"], unique=True)
    op.create_index("ix_users_external", "users", ["external_provider", "external_id"])

    # API Keys table
    op.create_table(
        "api_keys",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("key_prefix", sa.String(12), nullable=False),
        sa.Column("key_hash", sa.String(64), nullable=False),
        sa.Column("scopes", ARRAY(sa.String), nullable=False, default=[]),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("rate_limit_rpm", sa.Integer, nullable=False, default=60),
        sa.Column("allowed_ips", ARRAY(sa.String)),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
        sa.Column("use_count", sa.Integer, nullable=False, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_api_keys_prefix", "api_keys", ["key_prefix"])
    op.create_index("ix_api_keys_hash", "api_keys", ["key_hash"], unique=True)

    # Audit Logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True)),
        sa.Column("api_key_id", UUID(as_uuid=True)),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String(255), nullable=False),
        sa.Column("ip_address", INET),
        sa.Column("user_agent", sa.String(500)),
        sa.Column("request_id", sa.String(36)),
        sa.Column("details", JSONB, nullable=False, default={}),
    )
    op.create_index("ix_audit_tenant_time", "audit_logs", ["tenant_id", "timestamp"])
    op.create_index("ix_audit_resource", "audit_logs", ["resource_type", "resource_id"])
    op.create_index("ix_audit_action", "audit_logs", ["action", "timestamp"])

    # Add tenant_id to existing tables for multi-tenancy
    # Note: This is a significant schema change - in production, would need data migration
    op.add_column("pointers", sa.Column("tenant_id", UUID(as_uuid=True)))
    op.create_index("ix_pointers_tenant", "pointers", ["tenant_id"])
    op.create_foreign_key("fk_pointers_tenant", "pointers", "tenants", ["tenant_id"], ["id"])

    op.add_column("runs", sa.Column("tenant_id", UUID(as_uuid=True)))
    op.create_index("ix_runs_tenant", "runs", ["tenant_id"])
    op.create_foreign_key("fk_runs_tenant", "runs", "tenants", ["tenant_id"], ["id"])


def downgrade() -> None:
    # Remove tenant_id from existing tables
    op.drop_constraint("fk_runs_tenant", "runs", type_="foreignkey")
    op.drop_index("ix_runs_tenant", "runs")
    op.drop_column("runs", "tenant_id")

    op.drop_constraint("fk_pointers_tenant", "pointers", type_="foreignkey")
    op.drop_index("ix_pointers_tenant", "pointers")
    op.drop_column("pointers", "tenant_id")

    # Drop new tables
    op.drop_index("ix_audit_action", "audit_logs")
    op.drop_index("ix_audit_resource", "audit_logs")
    op.drop_index("ix_audit_tenant_time", "audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_api_keys_hash", "api_keys")
    op.drop_index("ix_api_keys_prefix", "api_keys")
    op.drop_table("api_keys")

    op.drop_index("ix_users_external", "users")
    op.drop_index("ix_users_tenant_email", "users")
    op.drop_table("users")

    op.drop_table("tenants")
