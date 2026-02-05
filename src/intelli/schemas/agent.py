"""Agent API schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class AgentChatMessage(BaseModel):
    """A single chat message."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class AgentChatRequest(BaseModel):
    """Request body for agent chat endpoint."""

    messages: list[AgentChatMessage] = Field(
        ..., description="Conversation history including the new user message"
    )
    pointer_id: UUID | None = Field(None, description="Pointer ID for document context (notebook)")
    manifest_sha256: str | None = Field(
        None, description="Direct manifest SHA256 for document context"
    )
    conversation_id: UUID | None = Field(
        None, description="Existing conversation ID for multi-turn chat"
    )
    session_id: UUID | None = Field(None, description="Session ID for grouping conversations")

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [{"role": "user", "content": "What are the key terms in this lease?"}],
                "pointer_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        }


class AgentChatResponse(BaseModel):
    """Non-streaming response for agent chat (used for errors)."""

    run_id: UUID = Field(..., description="Run ID for this chat interaction")
    message: str = Field(..., description="Response message")
    sources: list[dict] = Field(default_factory=list, description="Retrieved sources")
