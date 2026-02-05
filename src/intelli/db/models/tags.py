"""Universal tagging system.

Tags provide classification for any entity in the system:
artifacts, pointers, conversations, insights, tools, projects, etc.
Supports manual, agent-proposed, system, and inherited provenance.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Float, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from intelli.db.base import Base


class Tag(Base):
    """Universal tag for any entity."""

    __tablename__ = "tags"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    # What is tagged
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

    # The tag itself
    namespace: Mapped[str] = mapped_column(String(100), nullable=False)
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)

    # Provenance
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    verified_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    verified_at: Mapped[datetime | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "entity_type",
            "entity_id",
            "namespace",
            "key",
            "value",
            name="uq_tags_entity_tag",
        ),
        Index("ix_tags_entity", "entity_type", "entity_id"),
        Index("ix_tags_lookup", "tenant_id", "namespace", "key", "value"),
        Index(
            "ix_tags_unverified",
            "tenant_id",
            "source",
            "verified_at",
            postgresql_where="verified_at IS NULL",
        ),
    )
