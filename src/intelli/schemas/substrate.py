"""Pydantic schemas for substrate objects: Artifacts, Manifests, Pointers."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PointerType(str, Enum):
    """Types of pointers with different governance levels."""

    BUNDLE = "bundle"  # Working set, freely mutable
    CORPUS = "corpus"  # Governed, requires approval
    SNAPSHOT = "snapshot"  # Point-in-time freeze


# ============================================
# Artifact Schemas
# ============================================


class ArtifactCreate(BaseModel):
    """Schema for creating an artifact (metadata only, content via upload)."""

    filename: str | None = Field(None, description="Original filename")
    media_type: str = Field(..., description="MIME type")

    model_config = ConfigDict(extra="forbid")


class ArtifactResponse(BaseModel):
    """Schema for artifact response."""

    sha256: str = Field(..., description="SHA-256 hash of content")
    media_type: str = Field(..., description="MIME type")
    size_bytes: int = Field(..., description="Content size in bytes")
    filename: str | None = Field(None, description="Original filename")
    storage_uri: str = Field(..., description="Storage location")
    storage_class: str = Field(..., description="Storage class")
    reference_count: int = Field(..., description="Reference count")
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by: UUID | None = Field(None, description="Creator principal ID")

    model_config = ConfigDict(from_attributes=True)


class ArtifactUploadResponse(BaseModel):
    """Response from artifact upload."""

    sha256: str = Field(..., description="SHA-256 hash of uploaded content")
    size_bytes: int = Field(..., description="Content size in bytes")
    is_duplicate: bool = Field(..., description="Whether this was a duplicate upload")
    content_url: str | None = Field(None, description="Pre-signed URL for content access")

    model_config = ConfigDict(extra="forbid")


# ============================================
# Manifest Schemas
# ============================================


class ManifestEntry(BaseModel):
    """Single entry in a manifest tree."""

    path: str = Field(..., description="Path within the manifest tree")
    artifact_sha256: str = Field(..., description="SHA-256 of the referenced artifact")
    metadata: dict | None = Field(default_factory=dict, description="Entry-specific metadata")

    @field_validator("artifact_sha256")
    @classmethod
    def validate_sha256(cls, v: str) -> str:
        """Validate SHA-256 format."""
        if not v or len(v) != 64:
            raise ValueError("artifact_sha256 must be a 64-character hex string")
        try:
            int(v, 16)
        except ValueError:
            raise ValueError("artifact_sha256 must be a valid hex string")
        return v.lower()


class ManifestTree(BaseModel):
    """The tree structure stored in a manifest."""

    entries: list[ManifestEntry] = Field(default_factory=list, description="List of manifest entries")
    metadata: dict | None = Field(default_factory=dict, description="Tree-level metadata")


class ManifestCreate(BaseModel):
    """Schema for creating a new manifest."""

    entries: list[ManifestEntry] = Field(..., description="List of entries in the manifest")
    parent_sha256: str | None = Field(None, description="Parent manifest for history chain")
    message: str | None = Field(None, description="Commit message")
    metadata: dict | None = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(extra="forbid")

    @field_validator("parent_sha256")
    @classmethod
    def validate_parent_sha256(cls, v: str | None) -> str | None:
        """Validate parent SHA-256 format if provided."""
        if v is None:
            return v
        if len(v) != 64:
            raise ValueError("parent_sha256 must be a 64-character hex string")
        try:
            int(v, 16)
        except ValueError:
            raise ValueError("parent_sha256 must be a valid hex string")
        return v.lower()


class ManifestResponse(BaseModel):
    """Schema for manifest response."""

    sha256: str = Field(..., description="SHA-256 hash of canonical tree")
    tree: ManifestTree = Field(..., description="Manifest tree structure")
    parent_sha256: str | None = Field(None, description="Parent manifest SHA-256")
    entry_count: int = Field(..., description="Number of entries")
    total_size_bytes: int = Field(..., description="Total size of referenced artifacts")
    message: str | None = Field(None, description="Commit message")
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by: UUID | None = Field(None, description="Creator principal ID")

    model_config = ConfigDict(from_attributes=True)


class ManifestDiff(BaseModel):
    """Diff between two manifests."""

    old_sha256: str = Field(..., description="Old manifest SHA-256")
    new_sha256: str = Field(..., description="New manifest SHA-256")
    added: list[ManifestEntry] = Field(default_factory=list, description="Added entries")
    removed: list[ManifestEntry] = Field(default_factory=list, description="Removed entries")
    modified: list[dict] = Field(default_factory=list, description="Modified entries (old, new)")


# ============================================
# Pointer Schemas
# ============================================


class PointerCreate(BaseModel):
    """Schema for creating a new pointer."""

    namespace: str = Field(default="default", description="Namespace for the pointer")
    name: str = Field(..., description="Pointer name within namespace")
    pointer_type: PointerType = Field(default=PointerType.BUNDLE, description="Pointer type")
    manifest_sha256: str | None = Field(None, description="Initial manifest SHA-256")
    description: str | None = Field(None, description="Human-readable description")
    metadata: dict | None = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(extra="forbid")


class PointerResponse(BaseModel):
    """Schema for pointer response."""

    id: UUID = Field(..., description="Pointer ID")
    namespace: str = Field(..., description="Namespace")
    name: str = Field(..., description="Pointer name")
    pointer_type: str = Field(..., description="Pointer type")
    manifest_sha256: str | None = Field(None, description="Current HEAD manifest")
    description: str | None = Field(None, description="Description")
    metadata: dict = Field(default_factory=dict, description="Metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: UUID | None = Field(None, description="Creator principal ID")

    model_config = ConfigDict(from_attributes=True)


class PointerAdvance(BaseModel):
    """Schema for advancing a pointer to a new manifest."""

    manifest_sha256: str = Field(..., description="New manifest SHA-256 to point to")
    expected_sha256: str | None = Field(
        None, description="Expected current SHA-256 for optimistic locking"
    )
    reason: str | None = Field(None, description="Reason for the advance")

    model_config = ConfigDict(extra="forbid")

    @field_validator("manifest_sha256", "expected_sha256")
    @classmethod
    def validate_sha256(cls, v: str | None) -> str | None:
        """Validate SHA-256 format."""
        if v is None:
            return v
        if len(v) != 64:
            raise ValueError("SHA-256 must be a 64-character hex string")
        try:
            int(v, 16)
        except ValueError:
            raise ValueError("SHA-256 must be a valid hex string")
        return v.lower()


class PointerAdvanceResponse(BaseModel):
    """Response from pointer advance operation."""

    success: bool = Field(..., description="Whether the advance succeeded")
    old_sha256: str | None = Field(None, description="Previous manifest SHA-256")
    new_sha256: str = Field(..., description="New manifest SHA-256")
    conflict: bool = Field(default=False, description="Whether a conflict was detected")

    model_config = ConfigDict(extra="forbid")


class PointerHistoryEntry(BaseModel):
    """Single entry in pointer history."""

    id: UUID = Field(..., description="History entry ID")
    old_sha256: str | None = Field(None, description="Previous manifest SHA-256")
    new_sha256: str | None = Field(None, description="New manifest SHA-256")
    operation: str = Field(..., description="Operation type")
    changed_by: UUID | None = Field(None, description="Who made the change")
    changed_at: datetime = Field(..., description="When the change was made")
    reason: str | None = Field(None, description="Reason for change")

    model_config = ConfigDict(from_attributes=True)
