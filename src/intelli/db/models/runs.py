"""Run and Run Ledger models.

Runs represent execution instances (agentic, deterministic, hybrid).
The Run Ledger is an append-only event stream for full reproducibility.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from intelli.db.base import Base, TimestampMixin


class RunStatus(str, Enum):
    """Run lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunEventType(str, Enum):
    """Types of events in the run ledger."""

    # Lifecycle
    RUN_STARTED = "run_started"
    RUN_PAUSED = "run_paused"
    RUN_RESUMED = "run_resumed"
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"
    RUN_CANCELLED = "run_cancelled"

    # Steps
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"

    # Tool calls
    TOOL_CALL_STARTED = "tool_call_started"
    TOOL_CALL_COMPLETED = "tool_call_completed"

    # LLM interactions
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"

    # Retrieval
    RETRIEVAL_QUERY = "retrieval_query"
    RETRIEVAL_RESULT = "retrieval_result"

    # Artifacts and manifests
    ARTIFACT_EMITTED = "artifact_emitted"
    MANIFEST_CREATED = "manifest_created"
    POINTER_MOVED = "pointer_moved"

    # State management
    CHECKPOINT = "checkpoint"
    STATE_UPDATE = "state_update"

    # Human interaction
    USER_INPUT = "user_input"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    COMMENT_ADDED = "comment_added"

    # Errors
    ERROR = "error"
    WARNING = "warning"


class Run(Base, TimestampMixin):
    """Execution instance (agentic, deterministic, hybrid).

    Tracks inputs, outputs, status, and links to the run ledger events.
    """

    __tablename__ = "runs"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Run identification
    run_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Run type: document_parse, research, analysis, etc.",
    )
    name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Human-readable run name",
    )

    # Lifecycle
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=RunStatus.PENDING.value,
        comment="Current run status",
    )
    started_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        comment="When the run started executing",
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        comment="When the run completed (success or failure)",
    )

    # Input/output manifest references
    input_manifest_sha256: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("manifests.sha256"),
        nullable=True,
        comment="Input manifest SHA-256",
    )
    output_manifest_sha256: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("manifests.sha256"),
        nullable=True,
        comment="Output manifest SHA-256",
    )

    # Configuration and results
    config: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Run configuration",
    )
    result: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Run result (on success)",
    )
    error: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Error details (on failure)",
    )

    # Metrics
    token_usage: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Token usage by model",
    )
    cost_cents: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Estimated cost in cents",
    )

    # Tracking
    created_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        comment="Principal ID who created this run",
    )

    # Context (for future phases)
    project_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        comment="Project this run belongs to",
    )
    session_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        comment="Session this run belongs to",
    )
    parent_run_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("runs.id"),
        nullable=True,
        comment="Parent run for nested executions",
    )

    # Relationships
    events: Mapped[list["RunEvent"]] = relationship(
        "RunEvent",
        back_populates="run",
        order_by="RunEvent.sequence_num",
    )
    parent_run: Mapped["Run | None"] = relationship(
        "Run",
        remote_side=[id],
        backref="child_runs",
    )

    __table_args__ = (
        Index("ix_runs_status", "status"),
        Index("ix_runs_type", "run_type"),
        Index("ix_runs_created_at", "created_at"),
        Index("ix_runs_project", "project_id", postgresql_where="project_id IS NOT NULL"),
    )


class RunEvent(Base):
    """Append-only event log entry for a run.

    Forms the run ledger - complete audit trail of what happened.
    """

    __tablename__ = "run_events"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Monotonic event ID",
    )
    run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("runs.id"),
        nullable=False,
        index=True,
    )

    # Event details
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Event type from RunEventType enum",
    )

    # Event data (schema varies by type)
    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Event-specific payload data",
    )

    # Timing
    timestamp: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
        comment="When the event occurred",
    )
    duration_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Duration in milliseconds (for completed events)",
    )

    # Sequence within run (for ordering)
    sequence_num: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Sequence number within the run",
    )

    # Relationships
    run: Mapped[Run] = relationship("Run", back_populates="events")

    __table_args__ = (
        UniqueConstraint("run_id", "sequence_num", name="uq_run_event_sequence"),
        Index("ix_run_events_run", "run_id", "sequence_num"),
        Index("ix_run_events_type", "event_type"),
        Index("ix_run_events_timestamp", "timestamp"),
    )
