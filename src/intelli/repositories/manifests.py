"""Repository for Manifest operations."""

from uuid import UUID

from sqlalchemy import select

from intelli.db.models.substrate import Manifest
from intelli.repositories.base import BaseRepository


class ManifestRepository(BaseRepository[Manifest]):
    """Repository for Manifest CRUD operations."""

    model = Manifest

    async def get_by_sha256(self, sha256: str) -> Manifest | None:
        """Get manifest by SHA-256 hash.

        Args:
            sha256: SHA-256 hash of canonical JSON

        Returns:
            Manifest or None if not found
        """
        return await self.session.get(Manifest, sha256.lower())

    async def exists(self, sha256: str) -> bool:
        """Check if manifest exists.

        Args:
            sha256: SHA-256 hash

        Returns:
            True if manifest exists
        """
        manifest = await self.get_by_sha256(sha256)
        return manifest is not None

    async def create_manifest(
        self,
        sha256: str,
        tree: dict,
        entry_count: int,
        total_size_bytes: int,
        parent_sha256: str | None = None,
        message: str | None = None,
        created_by: UUID | None = None,
    ) -> Manifest:
        """Create a new manifest.

        Args:
            sha256: SHA-256 hash of canonical tree JSON
            tree: Tree structure with entries
            entry_count: Number of entries
            total_size_bytes: Total size of all artifacts
            parent_sha256: Parent manifest for history
            message: Commit message
            created_by: Creator principal ID

        Returns:
            Created manifest
        """
        return await self.create(
            sha256=sha256.lower(),
            tree=tree,
            entry_count=entry_count,
            total_size_bytes=total_size_bytes,
            parent_sha256=parent_sha256.lower() if parent_sha256 else None,
            message=message,
            created_by=created_by,
        )

    async def get_history(
        self,
        sha256: str,
        limit: int = 100,
    ) -> list[Manifest]:
        """Get manifest history by walking parent chain.

        Args:
            sha256: Starting manifest SHA-256
            limit: Maximum history depth

        Returns:
            List of manifests from newest to oldest
        """
        history = []
        current_sha = sha256.lower()

        while current_sha and len(history) < limit:
            manifest = await self.get_by_sha256(current_sha)
            if not manifest:
                break
            history.append(manifest)
            current_sha = manifest.parent_sha256

        return history

    async def get_children(self, sha256: str) -> list[Manifest]:
        """Get manifests that have this manifest as parent.

        Args:
            sha256: Parent manifest SHA-256

        Returns:
            List of child manifests
        """
        stmt = (
            select(Manifest)
            .where(Manifest.parent_sha256 == sha256.lower())
            .order_by(Manifest.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_recent(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Manifest]:
        """List most recent manifests.

        Args:
            limit: Maximum records
            offset: Skip count

        Returns:
            List of manifests ordered by creation time
        """
        stmt = (
            select(Manifest)
            .order_by(Manifest.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_roots(self, limit: int = 100) -> list[Manifest]:
        """List root manifests (no parent).

        Args:
            limit: Maximum records

        Returns:
            List of root manifests
        """
        stmt = (
            select(Manifest)
            .where(Manifest.parent_sha256.is_(None))
            .order_by(Manifest.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
