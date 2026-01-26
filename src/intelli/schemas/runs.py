"""Pydantic schemas for Runs and Run Events."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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


# ============================================
# Run Schemas
# ============================================


class RunCreate(BaseModel):
    """Schema for creating a new run."""

    run_type: str = Field(..., description="Type of run (document_parse, research, analysis)")
    name: str | None = Field(None, description="Human-readable name")
    config: dict = Field(default_factory=dict, description="Run configuration")
    input_manifest_sha256: str | None = Field(None, description="Input manifest SHA-256")
    project_id: UUID | None = Field(None, description="Project this run belongs to")
    session_id: UUID | None = Field(None, description="Session this run belongs to")
    parent_run_id: UUID | None = Field(None, description="Parent run for nested execution")

    model_config = ConfigDict(extra="forbid")


class RunUpdate(BaseModel):
    """Schema for updating a run."""

    status: RunStatus | None = Field(None, description="New status")
    result: dict | None = Field(None, description="Run result (on completion)")
    error: dict | None = Field(None, description="Error details (on failure)")
    output_manifest_sha256: str | None = Field(None, description="Output manifest SHA-256")

    model_config = ConfigDict(extra="forbid")


class RunResponse(BaseModel):
    """Schema for run response."""

    id: UUID = Field(..., description="Run ID")
    run_type: str = Field(..., description="Run type")
    name: str | None = Field(None, description="Run name")
    status: str = Field(..., description="Current status")
    started_at: datetime | None = Field(None, description="Start timestamp")
    completed_at: datetime | None = Field(None, description="Completion timestamp")
    input_manifest_sha256: str | None = Field(None, description="Input manifest")
    output_manifest_sha256: str | None = Field(None, description="Output manifest")
    config: dict = Field(default_factory=dict, description="Configuration")
    result: dict | None = Field(None, description="Result")
    error: dict | None = Field(None, description="Error details")
    token_usage: dict = Field(default_factory=dict, description="Token usage")
    cost_cents: int = Field(default=0, description="Estimated cost")
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by: UUID | None = Field(None, description="Creator principal ID")
    project_id: UUID | None = Field(None, description="Project ID")
    session_id: UUID | None = Field(None, description="Session ID")
    parent_run_id: UUID | None = Field(None, description="Parent run ID")

    model_config = ConfigDict(from_attributes=True)


class RunListResponse(BaseModel):
    """Paginated list of runs."""

    items: list[RunResponse] = Field(..., description="List of runs")
    total: int = Field(..., description="Total count")
    limit: int = Field(..., description="Page size")
    offset: int = Field(..., description="Page offset")


# ============================================
# Run Event Schemas
# ============================================


class RunEventCreate(BaseModel):
    """Schema for creating a run event."""

    event_type: RunEventType = Field(..., description="Event type")
    payload: dict = Field(..., description="Event payload")
    duration_ms: int | None = Field(None, description="Duration in milliseconds")

    model_config = ConfigDict(extra="forbid")


class RunEventResponse(BaseModel):
    """Schema for run event response."""

    id: int = Field(..., description="Event ID")
    run_id: UUID = Field(..., description="Run ID")
    event_type: str = Field(..., description="Event type")
    payload: dict = Field(..., description="Event payload")
    timestamp: datetime = Field(..., description="Event timestamp")
    duration_ms: int | None = Field(None, description="Duration")
    sequence_num: int = Field(..., description="Sequence number")

    model_config = ConfigDict(from_attributes=True)


class RunEventListResponse(BaseModel):
    """List of run events."""

    items: list[RunEventResponse] = Field(..., description="List of events")
    run_id: UUID = Field(..., description="Run ID")
    total: int = Field(..., description="Total count")


# ============================================
# Convenience Event Payloads
# ============================================


class StepStartPayload(BaseModel):
    """Payload for step_started events."""

    step_name: str = Field(..., description="Name of the step")
    input_data: dict | None = Field(None, description="Input to the step")


class StepCompletePayload(BaseModel):
    """Payload for step_completed events."""

    step_name: str = Field(..., description="Name of the step")
    output_data: dict | None = Field(None, description="Output from the step")
    success: bool = Field(default=True, description="Whether step succeeded")


class ToolCallPayload(BaseModel):
    """Payload for tool_call events."""

    tool_name: str = Field(..., description="Name of the tool")
    tool_version: str | None = Field(None, description="Tool version")
    arguments: dict = Field(default_factory=dict, description="Tool arguments")
    result: dict | None = Field(None, description="Tool result (for completed)")


class LLMInteractionPayload(BaseModel):
    """Payload for LLM request/response events."""

    model: str = Field(..., description="Model ID")
    messages: list[dict] | None = Field(None, description="Input messages (for request)")
    response: dict | None = Field(None, description="Response content (for response)")
    input_tokens: int | None = Field(None, description="Input token count")
    output_tokens: int | None = Field(None, description="Output token count")


class CheckpointPayload(BaseModel):
    """Payload for checkpoint events."""

    state: dict = Field(..., description="Serialized state")
    resumable: bool = Field(default=True, description="Whether run can be resumed")
    checkpoint_id: str | None = Field(None, description="Checkpoint identifier")
