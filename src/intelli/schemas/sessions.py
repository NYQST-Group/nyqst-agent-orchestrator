"""Pydantic schemas for Sessions."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Type aliases for status fields
SessionStatus = Literal["active", "idle", "paused", "closed"]


class SessionCreate(BaseModel):
    """Request to create a new session."""

    scope_type: str = Field(default="tenant", description="Scope level binding")
    scope_id: UUID | None = Field(None, description="Scope entity ID")
    module: str | None = Field(None, description="Module context")
    objective: str | None = Field(None, description="What the user is trying to accomplish")
    config_snapshot: dict = Field(default_factory=dict, description="Resolved config")
    idle_timeout_minutes: int = Field(default=30, description="Inactivity gate in minutes")

    model_config = ConfigDict(extra="forbid")


class SessionUpdate(BaseModel):
    """Request to update session status."""

    status: SessionStatus = Field(..., description="Session status")
    close_reason: str | None = Field(None, description="Reason for closing")

    model_config = ConfigDict(extra="forbid")


class SessionResponse(BaseModel):
    """Session in API responses."""

    id: UUID
    tenant_id: UUID
    user_id: UUID
    scope_type: str
    scope_id: UUID | None
    module: str | None
    objective: str | None
    status: SessionStatus
    started_at: datetime
    last_active_at: datetime
    idle_timeout_minutes: int
    closed_at: datetime | None
    close_reason: str | None
    total_cost_micros: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionListResponse(BaseModel):
    """Paginated list of sessions."""

    items: list[SessionResponse]
    total: int


class ConversationCostItem(BaseModel):
    """Cost breakdown for a single conversation within a session."""

    id: UUID
    title: str | None
    cost_micros: int
    input_tokens: int
    output_tokens: int


class SessionModelCostItem(BaseModel):
    """Cost breakdown for a model within a session."""

    model: str
    input_tokens: int
    output_tokens: int
    cost_micros: int


class SessionCostBreakdown(BaseModel):
    """Cost breakdown for a session."""

    session_id: UUID
    price_table_version: str
    total_cost_micros: int
    conversation_count: int
    total_input_tokens: int
    total_output_tokens: int
    models: list[SessionModelCostItem] = Field(default_factory=list)
    conversations: list[ConversationCostItem] = Field(default_factory=list)
