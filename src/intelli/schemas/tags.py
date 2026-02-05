"""Pydantic schemas for Tags."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Type alias for tag source
TagSource = Literal["manual", "agent_proposed", "system", "inherited"]


class TagCreate(BaseModel):
    """Request to create a tag."""

    entity_type: str = Field(..., description="Type of entity being tagged")
    entity_id: UUID = Field(..., description="ID of the entity being tagged")
    namespace: str = Field(..., description="Tag namespace (domain, asset_class, etc.)")
    key: str = Field(..., description="Tag key")
    value: str = Field(..., description="Tag value")
    source: TagSource = Field(default="manual", description="Tag source")
    confidence: float | None = Field(None, ge=0.0, le=1.0, description="Confidence (0-1)")

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_confidence(self) -> "TagCreate":
        """Ensure confidence is only set for agent_proposed source."""
        if self.source != "agent_proposed" and self.confidence is not None:
            raise ValueError("confidence is only valid for agent_proposed source")
        return self


class TagResponse(BaseModel):
    """Tag in API responses."""

    id: UUID
    tenant_id: UUID
    entity_type: str
    entity_id: UUID
    namespace: str
    key: str
    value: str
    source: TagSource
    confidence: float | None
    verified_by: UUID | None
    verified_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TagListResponse(BaseModel):
    """Paginated list of tags."""

    items: list[TagResponse]
    total: int


class TagSearchResult(BaseModel):
    """Result of cross-entity tag search."""

    entity_type: str
    entity_id: UUID
    tags: list[TagResponse]
