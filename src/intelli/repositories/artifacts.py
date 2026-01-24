"""Repository for Artifact operations."""

from uuid import UUID

from sqlalchemy import select, update

from intelli.db.models.substrate import Artifact
from intelli.repositories.base import BaseRepository


class ArtifactRepository(BaseRepository[Artifact]):
    """Repository for Artifact CRUD operations."""

    model = Artifact

    async def get_by_sha256(self, sha256: str) -> Artifact | None:
        """Get artifact by SHA-256 hash.

        Args:
            sha256: SHA-256 hash of artifact content

        Returns:
            Artifact or None if not found
        """
        return await self.session.get(Artifact, sha256.lower())

    async def exists(self, sha256: str) -> bool:
        """Check if artifact exists.

        Args:
            sha256: SHA-256 hash

        Returns:
            True if artifact exists
        """
        artifact = await self.get_by_sha256(sha256)
        return artifact is not None

    async def create_artifact(
        self,
        sha256: str,
        media_type: str,
        size_bytes: int,
        storage_uri: str,
        filename: str | None = None,
        storage_class: str = "STANDARD",
        created_by: UUID | None = None,
    ) -> Artifact:
        """Create a new artifact.

        Args:
            sha256: SHA-256 hash of content
            media_type: MIME type
            size_bytes: Content size
            storage_uri: Storage location URI
            filename: Original filename
            storage_class: Storage class
            created_by: Creator principal ID

        Returns:
            Created artifact
        """
        return await self.create(
            sha256=sha256.lower(),
            media_type=media_type,
            size_bytes=size_bytes,
            storage_uri=storage_uri,
            filename=filename,
            storage_class=storage_class,
            created_by=created_by,
        )

    async def increment_reference_count(self, sha256: str) -> None:
        """Increment artifact reference count.

        Called when a manifest references this artifact.

        Args:
            sha256: SHA-256 hash
        """
        stmt = (
            update(Artifact)
            .where(Artifact.sha256 == sha256.lower())
            .values(reference_count=Artifact.reference_count + 1)
        )
        await self.session.execute(stmt)

    async def decrement_reference_count(self, sha256: str) -> int:
        """Decrement artifact reference count.

        Called when a manifest is removed.

        Args:
            sha256: SHA-256 hash

        Returns:
            New reference count
        """
        stmt = (
            update(Artifact)
            .where(Artifact.sha256 == sha256.lower())
            .values(reference_count=Artifact.reference_count - 1)
            .returning(Artifact.reference_count)
        )
        result = await self.session.execute(stmt)
        row = result.first()
        return row[0] if row else 0

    async def list_by_media_type(
        self,
        media_type: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Artifact]:
        """List artifacts by media type.

        Args:
            media_type: MIME type to filter by
            limit: Maximum records
            offset: Skip count

        Returns:
            List of artifacts
        """
        stmt = (
            select(Artifact)
            .where(Artifact.media_type == media_type)
            .order_by(Artifact.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_unreferenced(self, limit: int = 100) -> list[Artifact]:
        """List artifacts with zero references (candidates for cleanup).

        Args:
            limit: Maximum records

        Returns:
            List of unreferenced artifacts
        """
        stmt = (
            select(Artifact)
            .where(Artifact.reference_count <= 0)
            .order_by(Artifact.created_at)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
