"""Substrate models: Artifact, Manifest, Pointer, PointerHistory.

These form the immutable backbone of the platform:
- Artifacts are content-addressed (SHA-256) immutable blobs
- Manifests are immutable trees of artifact/manifest references
- Pointers are mutable HEAD references (like Git branches)
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from intelli.db.base import Base, SoftDeleteMixin, TimestampMixin


class Artifact(Base, TimestampMixin):
    """Immutable content-addressed artifact (file/blob).

    Primary key is SHA-256 hash of content, ensuring deduplication.
    Actual content is stored in object storage (S3/MinIO).
    """

    __tablename__ = "artifacts"

    # Content-addressable: SHA-256 of content
    sha256: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        comment="SHA-256 hash of artifact content",
    )

    # Metadata
    media_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="MIME type (e.g., application/pdf)",
    )
    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="Content size in bytes",
    )
    filename: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
        comment="Original filename",
    )

    # Storage location
    storage_uri: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
        comment="Storage URI (e.g., s3://bucket/key)",
    )
    storage_class: Mapped[str] = mapped_column(
        String(50),
        default="STANDARD",
        comment="Storage class (STANDARD, GLACIER, etc.)",
    )

    # Tracking
    created_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        comment="Principal ID who created this artifact",
    )

    # Deduplication stats
    reference_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        comment="Number of manifests referencing this artifact",
    )

    __table_args__ = (
        CheckConstraint("sha256 ~ '^[a-f0-9]{64}$'", name="sha256_format"),
        Index("ix_artifacts_media_type", "media_type"),
        Index("ix_artifacts_created_at", "created_at"),
    )


class Manifest(Base, TimestampMixin):
    """Immutable tree snapshot (bundle/corpus/run output).

    Content-addressed by SHA-256 of canonical JSON representation.
    Forms a DAG via parent_sha256 for history tracking.
    """

    __tablename__ = "manifests"

    # Content-addressable: SHA-256 of canonical JSON
    sha256: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        comment="SHA-256 hash of canonical JSON tree",
    )

    # Tree structure (schema-on-read)
    tree: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Tree structure with entries and metadata",
    )

    # Parent manifest for history (null = root)
    parent_sha256: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("manifests.sha256"),
        nullable=True,
        comment="Parent manifest SHA-256 for history chain",
    )

    # Statistics (denormalized for query efficiency)
    entry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Number of entries in this manifest",
    )
    total_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="Total size of all referenced artifacts",
    )

    # Tracking
    created_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        comment="Principal ID who created this manifest",
    )
    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Commit message describing this snapshot",
    )

    # Relationships
    parent: Mapped["Manifest | None"] = relationship(
        "Manifest",
        remote_side=[sha256],
        backref="children",
    )

    __table_args__ = (
        CheckConstraint("sha256 ~ '^[a-f0-9]{64}$'", name="sha256_format"),
        Index("ix_manifests_parent", "parent_sha256"),
        Index("ix_manifests_created_at", "created_at"),
        Index("ix_manifests_tree", "tree", postgresql_using="gin"),
    )


class Pointer(Base, TimestampMixin, SoftDeleteMixin):
    """Mutable HEAD reference to a manifest.

    Pointers are like Git branches - they track a current manifest
    and can be advanced atomically. Types:
    - bundle: working set, freely mutable
    - corpus: governed, requires approval for changes
    - snapshot: point-in-time freeze
    """

    __tablename__ = "pointers"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Naming (scoped by namespace)
    namespace: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="default",
        comment="Namespace for pointer (e.g., project ID)",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Pointer name within namespace",
    )

    # Current HEAD (null = empty pointer)
    manifest_sha256: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("manifests.sha256"),
        nullable=True,
        comment="Current HEAD manifest SHA-256",
    )

    # Pointer type for governance
    pointer_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="bundle",
        comment="Type: bundle, corpus, snapshot",
    )

    # Metadata
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Human-readable description",
    )
    meta: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
        comment="Additional metadata",
    )

    # Tracking
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Last update timestamp",
    )
    created_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        comment="Principal ID who created this pointer",
    )

    # Relationships
    manifest: Mapped[Manifest | None] = relationship("Manifest")
    history: Mapped[list["PointerHistory"]] = relationship(
        "PointerHistory",
        back_populates="pointer",
        order_by="desc(PointerHistory.changed_at)",
    )

    __table_args__ = (
        UniqueConstraint("namespace", "name", "deleted_at", name="uq_pointer_name"),
        Index("ix_pointers_namespace", "namespace", postgresql_where="deleted_at IS NULL"),
        Index("ix_pointers_type", "pointer_type", postgresql_where="deleted_at IS NULL"),
        Index("ix_pointers_manifest", "manifest_sha256"),
    )


class PointerHistory(Base):
    """Audit trail for pointer HEAD changes."""

    __tablename__ = "pointer_history"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    pointer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("pointers.id"),
        nullable=False,
    )

    # State change
    old_sha256: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="Previous manifest SHA-256",
    )
    new_sha256: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="New manifest SHA-256",
    )

    # Context
    operation: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Operation: create, advance, reset, revert",
    )
    changed_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        comment="Principal ID who made the change",
    )
    changed_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )
    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Reason for the change",
    )

    # Relationships
    pointer: Mapped[Pointer] = relationship("Pointer", back_populates="history")

    __table_args__ = (
        Index("ix_pointer_history_pointer", "pointer_id", "changed_at"),
    )
