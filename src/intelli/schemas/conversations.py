"""Pydantic schemas for Conversations and Messages."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Type aliases for status fields
ConversationStatus = Literal["active", "archived", "deleted"]
MessageRole = Literal["user", "assistant", "system", "tool"]
MessageStatus = Literal["pending", "streaming", "complete", "failed"]
FeedbackRating = Literal["positive", "negative"]


# ---------------------------------------------------------------------------
# Conversation schemas
# ---------------------------------------------------------------------------


class ConversationCreate(BaseModel):
    """Request to create a new conversation."""

    scope_type: str = Field(default="tenant", description="Scope level binding")
    scope_id: UUID | None = Field(None, description="Scope entity ID (null for tenant-level)")
    module: str | None = Field(None, description="Module context: research, analysis, etc.")
    title: str | None = Field(None, description="Conversation title (auto-generated if absent)")
    session_id: UUID | None = Field(None, description="Session to bind this conversation to")
    config_snapshot: dict = Field(default_factory=dict, description="Resolved config snapshot")

    model_config = ConfigDict(extra="forbid")


class ConversationUpdate(BaseModel):
    """Request to update a conversation."""

    title: str | None = None
    status: ConversationStatus | None = Field(None, description="Conversation status")

    model_config = ConfigDict(extra="forbid")


class ConversationResponse(BaseModel):
    """Conversation in API responses."""

    id: UUID
    tenant_id: UUID
    user_id: UUID
    scope_type: str
    scope_id: UUID | None
    module: str | None
    title: str | None
    status: ConversationStatus
    message_count: int
    total_input_tokens: int
    total_output_tokens: int
    total_cost_micros: int
    session_id: UUID | None
    run_id: UUID | None
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    """Paginated list of conversations."""

    items: list[ConversationResponse]
    total: int


# ---------------------------------------------------------------------------
# Message schemas
# ---------------------------------------------------------------------------


class MessageResponse(BaseModel):
    """Message in API responses."""

    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str | None
    parts: dict | None
    input_tokens: int | None
    output_tokens: int | None
    cost_micros: int | None
    latency_ms: int | None
    model_id: str | None
    status: MessageStatus
    parent_message_id: UUID | None
    sequence_number: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageListResponse(BaseModel):
    """Paginated list of messages."""

    items: list[MessageResponse]
    total: int


# ---------------------------------------------------------------------------
# Feedback schemas
# ---------------------------------------------------------------------------


class FeedbackCreate(BaseModel):
    """Request to add feedback to a message."""

    rating: FeedbackRating = Field(..., description="Feedback rating")
    content: str | None = Field(None, description="Optional explanation")

    model_config = ConfigDict(extra="forbid")


class FeedbackResponse(BaseModel):
    """Feedback in API responses."""

    id: UUID
    message_id: UUID
    user_id: UUID
    rating: FeedbackRating
    content: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Branch schemas
# ---------------------------------------------------------------------------


class BranchCreate(BaseModel):
    """Request to branch from a message."""

    message_id: UUID = Field(..., description="Message to branch from")

    model_config = ConfigDict(extra="forbid")


class BranchResponse(BaseModel):
    """Response after creating a branch."""

    conversation_id: UUID
    branch_point_message_id: UUID
    new_sequence_number: int


class SiblingResponse(BaseModel):
    """Response containing sibling messages."""

    items: list[MessageResponse]
    total: int
    current_index: int
