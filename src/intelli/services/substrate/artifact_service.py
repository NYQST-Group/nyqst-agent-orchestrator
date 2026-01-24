"""Service for artifact operations."""

import hashlib
from dataclasses import dataclass
from typing import BinaryIO
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from intelli.core.exceptions import NotFoundError
from intelli.db.models.substrate import Artifact
from intelli.repositories.artifacts import ArtifactRepository
from intelli.storage import StorageBackend, get_storage_backend


@dataclass
class ArtifactUploadResult:
    """Result of an artifact upload operation."""

    sha256: str
    size_bytes: int
    storage_uri: str
    is_duplicate: bool
    content_url: str | None = None


class ArtifactService:
    """Service for artifact business logic.

    Handles artifact upload (with deduplication), retrieval,
    and content-addressed storage operations.
    """

    def __init__(
        self,
        session: AsyncSession,
        storage: StorageBackend | None = None,
    ):
        """Initialize artifact service.

        Args:
            session: Database session
            storage: Storage backend (defaults to configured backend)
        """
        self.repo = ArtifactRepository(session)
        self.storage = storage or get_storage_backend()

    async def upload_artifact(
        self,
        content: BinaryIO | bytes,
        filename: str | None = None,
        media_type: str = "application/octet-stream",
        created_by: UUID | None = None,
        generate_url: bool = False,
    ) -> ArtifactUploadResult:
        """Upload an artifact with deduplication.

        Computes SHA-256 hash of content. If artifact with same hash
        already exists, increments reference count instead of re-uploading.

        Args:
            content: File content (file-like or bytes)
            filename: Original filename
            media_type: MIME type
            created_by: Principal ID of uploader
            generate_url: Whether to generate a pre-signed URL

        Returns:
            Upload result with SHA-256 and metadata
        """
        # Read content and compute hash
        if isinstance(content, bytes):
            data = content
        else:
            data = content.read()

        sha256 = hashlib.sha256(data).hexdigest()
        size_bytes = len(data)

        # Check for duplicate
        existing = await self.repo.get_by_sha256(sha256)
        if existing:
            # Increment reference count
            await self.repo.increment_reference_count(sha256)

            # Generate URL if requested
            content_url = None
            if generate_url:
                content_url = await self.storage.generate_presigned_url(sha256)

            return ArtifactUploadResult(
                sha256=sha256,
                size_bytes=size_bytes,
                storage_uri=existing.storage_uri,
                is_duplicate=True,
                content_url=content_url,
            )

        # Upload to storage
        storage_uri = await self.storage.put(
            key=sha256,
            content=data,
            content_type=media_type,
            metadata={"filename": filename} if filename else None,
        )

        # Create database record
        await self.repo.create_artifact(
            sha256=sha256,
            media_type=media_type,
            size_bytes=size_bytes,
            storage_uri=storage_uri,
            filename=filename,
            created_by=created_by,
        )

        # Generate URL if requested
        content_url = None
        if generate_url:
            content_url = await self.storage.generate_presigned_url(sha256)

        return ArtifactUploadResult(
            sha256=sha256,
            size_bytes=size_bytes,
            storage_uri=storage_uri,
            is_duplicate=False,
            content_url=content_url,
        )

    async def get_artifact(self, sha256: str) -> Artifact:
        """Get artifact by SHA-256.

        Args:
            sha256: Artifact hash

        Returns:
            Artifact model

        Raises:
            NotFoundError: If artifact doesn't exist
        """
        artifact = await self.repo.get_by_sha256(sha256)
        if not artifact:
            raise NotFoundError(resource_type="artifact", identifier=sha256)
        return artifact

    async def get_content(self, sha256: str) -> bytes:
        """Get artifact content.

        Args:
            sha256: Artifact hash

        Returns:
            Content bytes

        Raises:
            NotFoundError: If artifact doesn't exist
        """
        # Verify artifact exists in DB
        artifact = await self.get_artifact(sha256)

        # Get content from storage
        return await self.storage.get_bytes(sha256)

    async def get_content_url(
        self,
        sha256: str,
        expiration_seconds: int = 3600,
    ) -> str:
        """Get pre-signed URL for artifact content.

        Args:
            sha256: Artifact hash
            expiration_seconds: URL validity duration

        Returns:
            Pre-signed URL

        Raises:
            NotFoundError: If artifact doesn't exist
        """
        # Verify artifact exists
        await self.get_artifact(sha256)

        return await self.storage.generate_presigned_url(
            key=sha256,
            expiration_seconds=expiration_seconds,
        )

    async def exists(self, sha256: str) -> bool:
        """Check if artifact exists.

        Args:
            sha256: Artifact hash

        Returns:
            True if exists
        """
        return await self.repo.exists(sha256)

    async def delete_artifact(
        self,
        sha256: str,
        force: bool = False,
    ) -> bool:
        """Delete artifact if not referenced.

        Args:
            sha256: Artifact hash
            force: Delete even if referenced

        Returns:
            True if deleted

        Raises:
            NotFoundError: If artifact doesn't exist
        """
        artifact = await self.get_artifact(sha256)

        if not force and artifact.reference_count > 0:
            return False

        # Delete from storage
        await self.storage.delete(sha256)

        # Delete from database
        await self.repo.delete(artifact)

        return True

    async def list_artifacts(
        self,
        media_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Artifact]:
        """List artifacts with optional filters.

        Args:
            media_type: Filter by MIME type
            limit: Maximum records
            offset: Skip count

        Returns:
            List of artifacts
        """
        if media_type:
            return await self.repo.list_by_media_type(media_type, limit, offset)
        return await self.repo.list_all(limit, offset)
