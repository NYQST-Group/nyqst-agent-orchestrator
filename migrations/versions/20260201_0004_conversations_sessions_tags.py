"""Conversations, sessions, messages, feedback, and tags.

Phase 1 of the Knowledge, Context & Organisational Intelligence System.

Revision ID: 20260201_0004
Revises: 20260124_0003
Create Date: 2026-02-01
"""

from typing import Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260201_0004"
down_revision: Union[str, None] = "20260124_0003"
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    # Sessions
    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scope_type", sa.String(50), nullable=False, server_default="tenant"),
        sa.Column("scope_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("module", sa.String(50), nullable=True),
        sa.Column("objective", sa.Text, nullable=True),
        sa.Column("config_snapshot", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("mounted_pointers", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("mounted_kbs", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("pinned_artifacts", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("agent_definition_id", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("idle_timeout_minutes", sa.Integer, nullable=False, server_default="30"),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("close_reason", sa.String(50), nullable=True),
        sa.Column("workspace", postgresql.JSONB, nullable=True),
        sa.Column("total_cost_micros", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint(
            "scope_type IN ('tenant','environment','project','objective','workflow','task','pointer','user')",
            name="sessions_scope_check",
        ),
    )
    op.create_index("ix_sessions_tenant_status", "sessions", ["tenant_id", "status"])
    op.create_index("ix_sessions_tenant_user", "sessions", ["tenant_id", "user_id"])
    op.create_index("ix_sessions_scope", "sessions", ["scope_type", "scope_id"])
    op.execute(
        "CREATE INDEX ix_sessions_active ON sessions (status, last_active_at) "
        "WHERE status = 'active'"
    )

    # Conversations
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scope_type", sa.String(50), nullable=False, server_default="tenant"),
        sa.Column("scope_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("module", sa.String(50), nullable=True),
        sa.Column("config_snapshot", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("title", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("message_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_input_tokens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_output_tokens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_cost_micros", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("agent_definition_id", sa.String(255), nullable=True),
        sa.Column("run_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("runs.id"), nullable=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("sessions.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "scope_type IN ('tenant','environment','project','objective','workflow','task','pointer','user')",
            name="conversations_scope_check",
        ),
    )
    op.create_index("ix_conversations_tenant", "conversations", ["tenant_id"])
    op.create_index("ix_conversations_scope", "conversations", ["scope_type", "scope_id"])
    op.create_index("ix_conversations_tenant_user", "conversations", ["tenant_id", "user_id"])
    op.execute(
        "CREATE INDEX ix_conversations_run ON conversations (run_id) WHERE run_id IS NOT NULL"
    )
    op.execute(
        "CREATE INDEX ix_conversations_session ON conversations (session_id) "
        "WHERE session_id IS NOT NULL"
    )

    # Messages
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("parts", postgresql.JSONB, nullable=True),
        sa.Column("input_tokens", sa.Integer, nullable=True),
        sa.Column("output_tokens", sa.Integer, nullable=True),
        sa.Column("cost_micros", sa.BigInteger, nullable=True),
        sa.Column("latency_ms", sa.Integer, nullable=True),
        sa.Column("model_id", sa.String(100), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="completed"),
        sa.Column("error", postgresql.JSONB, nullable=True),
        sa.Column("run_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("parent_message_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("messages.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("sequence_number", sa.Integer, nullable=False),
    )
    op.create_index("ix_messages_conversation_seq", "messages",
                    ["conversation_id", "sequence_number"])
    op.execute(
        "CREATE INDEX ix_messages_run_event ON messages (run_event_id) "
        "WHERE run_event_id IS NOT NULL"
    )
    op.execute(
        "CREATE INDEX ix_messages_parent ON messages (parent_message_id) "
        "WHERE parent_message_id IS NOT NULL"
    )

    # Message Feedback
    op.create_table(
        "message_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("message_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id"), nullable=False),
        sa.Column("rating", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("message_id", "user_id", name="uq_message_feedback_user"),
    )

    # Tags
    op.create_table(
        "tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("namespace", sa.String(100), nullable=False),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.String(500), nullable=False),
        sa.Column("source", sa.String(50), nullable=False, server_default="manual"),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("verified_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id"), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint(
            "tenant_id", "entity_type", "entity_id", "namespace", "key", "value",
            name="uq_tags_entity_tag",
        ),
    )
    op.create_index("ix_tags_entity", "tags", ["entity_type", "entity_id"])
    op.create_index("ix_tags_lookup", "tags", ["tenant_id", "namespace", "key", "value"])
    op.execute(
        "CREATE INDEX ix_tags_unverified ON tags (tenant_id, source, verified_at) "
        "WHERE verified_at IS NULL"
    )


def downgrade() -> None:
    op.drop_table("tags")
    op.drop_table("message_feedback")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("sessions")
