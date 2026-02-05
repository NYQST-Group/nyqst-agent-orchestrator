"""Pydantic schemas for lightweight RAG (index + ask)."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RagIndexRequest(BaseModel):
    """Index all artifacts in a manifest/pointer for semantic search."""

    pointer_id: UUID | None = Field(default=None, description="Pointer to index (preferred)")
    manifest_sha256: str | None = Field(default=None, description="Manifest to index")
    force: bool = Field(default=False, description="Rebuild index even if chunks exist")

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_target(self) -> "RagIndexRequest":
        if not self.pointer_id and not self.manifest_sha256:
            raise ValueError("Provide pointer_id or manifest_sha256")
        return self


class RagIndexResponse(BaseModel):
    run_id: UUID
    manifest_sha256: str
    embedding_model: str
    artifacts_total: int
    artifacts_indexed: int
    artifacts_skipped: int
    chunks_created: int

    model_config = ConfigDict(extra="forbid")


class RagAskRequest(BaseModel):
    """Ask a question scoped to a manifest/pointer."""

    pointer_id: UUID | None = Field(default=None, description="Pointer to query (preferred)")
    manifest_sha256: str | None = Field(default=None, description="Manifest to query")
    question: str = Field(..., min_length=1, description="User question")
    top_k: int = Field(default=8, ge=1, le=50, description="Number of chunks to retrieve")

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_target(self) -> "RagAskRequest":
        if not self.pointer_id and not self.manifest_sha256:
            raise ValueError("Provide pointer_id or manifest_sha256")
        return self


class RagSource(BaseModel):
    chunk_id: UUID
    score: float
    artifact_sha256: str
    path: str | None = None
    chunk_index: int
    content: str

    model_config = ConfigDict(extra="forbid")


class RagAskResponse(BaseModel):
    run_id: UUID
    model: str
    answer: str
    sources: list[RagSource]

    model_config = ConfigDict(extra="forbid")
