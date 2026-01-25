"""RAG models for lightweight document Q&A.

Phase 1-ish support for:
- Chunking artifact text
- Storing embeddings in Postgres (pgvector)
- Similarity search by manifest/pointer scope
"""

from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from intelli.db.base import Base, TimestampMixin
from intelli.db.models.substrate import Artifact


class RagChunk(Base, TimestampMixin):
    """A text chunk derived from an Artifact plus its embedding."""

    __tablename__ = "rag_chunks"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    artifact_sha256: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("artifacts.sha256", ondelete="CASCADE"),
        nullable=False,
        comment="Source artifact SHA-256",
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Chunk index within the artifact",
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Chunk text content",
    )

    meta: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
        comment="Chunk metadata (path hints, offsets, etc.)",
    )

    embedding_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Embedding model used for this chunk",
    )

    embedding_dimensions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Embedding dimension (for traceability)",
    )

    embedding: Mapped[list[float]] = mapped_column(
        Vector(),
        nullable=False,
        comment="Embedding vector",
    )

    artifact: Mapped[Artifact] = relationship("Artifact")

    __table_args__ = (
        UniqueConstraint(
            "artifact_sha256",
            "chunk_index",
            "embedding_model",
            name="uq_rag_chunks_artifact_chunk_model",
        ),
        Index("ix_rag_chunks_artifact", "artifact_sha256"),
        Index("ix_rag_chunks_model", "embedding_model"),
    )
