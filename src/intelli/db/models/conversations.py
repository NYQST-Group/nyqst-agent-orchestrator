"""Conversation, Message, MessageFeedback, and Session models.

Phase 1 of the Knowledge, Context & Organisational Intelligence System.
Provides persistent chat with history, sessions, feedback, branching, and cost tracking.
"""

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from intelli.db.base import Base, TimestampMixin

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ConversationStatus(StrEnum):
    """Conversation lifecycle states."""

    active = "active"
    archived = "archived"
    deleted = "deleted"


class MessageRole(StrEnum):
    """Message roles."""

    user = "user"
    assistant = "assistant"
    system = "system"
    tool = "tool"


class MessageStatus(StrEnum):
    """Message delivery states."""

    pending = "pending"
    streaming = "streaming"
    complete = "complete"
    failed = "failed"


class FeedbackRating(StrEnum):
    """Feedback rating values."""

    positive = "positive"
    negative = "negative"


class SessionStatus(StrEnum):
    """Session lifecycle states."""

    active = "active"
    idle = "idle"
    paused = "paused"
    closed = "closed"


VALID_SCOPE_TYPES = (
    "tenant",
    "environment",
    "project",
    "objective",
    "workflow",
    "task",
    "pointer",
    "user",
)


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------


class Session(Base, TimestampMixin):
    """Environment lifecycle from start to finish.

    Contains conversations, runs, and workspace state.
    Pre-VM: bounded by inactivity gates.
    """

    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Polymorphic scope binding
    scope_type: Mapped[str] = mapped_column(String(50), nullable=False, default="tenant")
    scope_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    # Module context
    module: Mapped[str | None] = mapped_column(String(50), nullable=True)
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Resolved config snapshot
    config_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Resource mounts
    mounted_pointers: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    mounted_kbs: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    pinned_artifacts: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    # Agent binding
    agent_definition_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Lifecycle
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=SessionStatus.active.value,
    )
    started_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    last_active_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    idle_timeout_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    closed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    close_reason: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Workspace state
    workspace: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Cost tracking
    total_cost_micros: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    # Updated at
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="session",
        order_by="Conversation.created_at",
    )

    __table_args__ = (
        CheckConstraint(
            f"scope_type IN {VALID_SCOPE_TYPES!r}",
            name="sessions_scope_check",
        ),
        Index("ix_sessions_tenant_status", "tenant_id", "status"),
        Index("ix_sessions_tenant_user", "tenant_id", "user_id"),
        Index("ix_sessions_scope", "scope_type", "scope_id"),
        Index(
            "ix_sessions_active",
            "status",
            "last_active_at",
            postgresql_where="status = 'active'",
        ),
    )


# ---------------------------------------------------------------------------
# Conversation
# ---------------------------------------------------------------------------


class Conversation(Base, TimestampMixin):
    """Container for a chat interaction.

    Scoped to a level in the org hierarchy. Config frozen at creation.
    conversation.id == LangGraph thread_id for checkpoint mapping.
    """

    __tablename__ = "conversations"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Polymorphic scope binding
    scope_type: Mapped[str] = mapped_column(String(50), nullable=False, default="tenant")
    scope_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    # Module context
    module: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Resolved config snapshot (frozen at creation)
    config_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Metadata
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ConversationStatus.active.value,
    )
    message_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_cost_micros: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    # Agent binding
    agent_definition_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Run ledger link
    run_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("runs.id"),
        nullable=True,
    )

    # Session link
    session_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sessions.id"),
        nullable=True,
    )

    # Timestamps
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    last_message_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        order_by="Message.sequence_number",
        cascade="all, delete-orphan",
    )
    session: Mapped["Session | None"] = relationship(
        "Session",
        back_populates="conversations",
    )

    __table_args__ = (
        CheckConstraint(
            f"scope_type IN {VALID_SCOPE_TYPES!r}",
            name="conversations_scope_check",
        ),
        Index("ix_conversations_tenant", "tenant_id"),
        Index("ix_conversations_scope", "scope_type", "scope_id"),
        Index("ix_conversations_tenant_user", "tenant_id", "user_id"),
        Index("ix_conversations_run", "run_id", postgresql_where="run_id IS NOT NULL"),
        Index("ix_conversations_session", "session_id", postgresql_where="session_id IS NOT NULL"),
    )


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------


class Message(Base):
    """Individual exchange within a conversation.

    Supports branching via parent_message_id for tree-structured conversations.
    """

    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Content
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    parts: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Metrics
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_micros: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=MessageStatus.complete.value,
    )
    error: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Provenance links
    run_event_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    parent_message_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("messages.id"),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Ordering
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages",
    )
    feedback: Mapped[list["MessageFeedback"]] = relationship(
        "MessageFeedback",
        back_populates="message",
        cascade="all, delete-orphan",
    )
    parent_message: Mapped["Message | None"] = relationship(
        "Message",
        remote_side=[id],
        backref="child_messages",
    )

    __table_args__ = (
        Index("ix_messages_conversation_seq", "conversation_id", "sequence_number"),
        Index("ix_messages_run_event", "run_event_id", postgresql_where="run_event_id IS NOT NULL"),
        Index(
            "ix_messages_parent",
            "parent_message_id",
            postgresql_where="parent_message_id IS NOT NULL",
        ),
    )


# ---------------------------------------------------------------------------
# MessageFeedback
# ---------------------------------------------------------------------------


class MessageFeedback(Base):
    """User feedback (thumbs up/down) on a message."""

    __tablename__ = "message_feedback"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    message_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    rating: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    message: Mapped["Message"] = relationship("Message", back_populates="feedback")

    __table_args__ = (UniqueConstraint("message_id", "user_id", name="uq_message_feedback_user"),)
