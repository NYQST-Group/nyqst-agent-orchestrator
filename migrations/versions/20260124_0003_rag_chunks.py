"""RAG chunks + embeddings (pgvector).

Revision ID: 20260124_0003
Revises: 20260123_0002
Create Date: 2026-01-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260124_0003"
down_revision: Union[str, None] = "20260123_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rag_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("artifact_sha256", sa.String(64), nullable=False, comment="Source artifact SHA-256"),
        sa.Column("chunk_index", sa.Integer(), nullable=False, comment="Chunk index within the artifact"),
        sa.Column("content", sa.Text(), nullable=False, comment="Chunk text content"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}", comment="Chunk metadata"),
        sa.Column("embedding_model", sa.String(100), nullable=False, comment="Embedding model used"),
        sa.Column("embedding_dimensions", sa.Integer(), nullable=False, comment="Embedding dimension"),
        sa.Column("embedding", Vector(), nullable=False, comment="Embedding vector"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rag_chunks")),
        sa.ForeignKeyConstraint(
            ["artifact_sha256"],
            ["artifacts.sha256"],
            name=op.f("fk_rag_chunks_artifact_sha256_artifacts"),
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "artifact_sha256",
            "chunk_index",
            "embedding_model",
            name="uq_rag_chunks_artifact_chunk_model",
        ),
    )
    op.create_index("ix_rag_chunks_artifact", "rag_chunks", ["artifact_sha256"])
    op.create_index("ix_rag_chunks_model", "rag_chunks", ["embedding_model"])


def downgrade() -> None:
    op.drop_index("ix_rag_chunks_model", table_name="rag_chunks")
    op.drop_index("ix_rag_chunks_artifact", table_name="rag_chunks")
    op.drop_table("rag_chunks")
