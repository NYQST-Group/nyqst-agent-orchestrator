"""Service for manifest operations."""

import hashlib
import json
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from intelli.core.exceptions import NotFoundError, ValidationError
from intelli.db.models.substrate import Manifest
from intelli.repositories.artifacts import ArtifactRepository
from intelli.repositories.manifests import ManifestRepository
from intelli.schemas.substrate import ManifestEntry


@dataclass
class ManifestBuildResult:
    """Result of manifest build operation."""

    sha256: str
    entry_count: int
    total_size_bytes: int
    is_duplicate: bool


@dataclass
class ManifestDiff:
    """Diff between two manifests."""

    old_sha256: str
    new_sha256: str
    added: list[ManifestEntry]
    removed: list[ManifestEntry]
    modified: list[dict]  # {"path": ..., "old": ..., "new": ...}


class ManifestService:
    """Service for manifest business logic.

    Handles manifest creation, tree building, history tracking,
    and diff generation.
    """

    def __init__(self, session: AsyncSession):
        """Initialize manifest service.

        Args:
            session: Database session
        """
        self.repo = ManifestRepository(session)
        self.artifact_repo = ArtifactRepository(session)

    async def build_manifest(
        self,
        entries: list[ManifestEntry],
        parent_sha256: str | None = None,
        message: str | None = None,
        metadata: dict | None = None,
        created_by: UUID | None = None,
    ) -> ManifestBuildResult:
        """Build a new manifest from entries.

        Creates an immutable manifest with computed SHA-256.
        If manifest with same hash exists, returns existing.

        Args:
            entries: List of manifest entries
            parent_sha256: Parent manifest for history chain
            message: Commit message
            metadata: Additional metadata
            created_by: Creator principal ID

        Returns:
            Build result with SHA-256

        Raises:
            ValidationError: If referenced artifacts don't exist
            NotFoundError: If parent manifest doesn't exist
        """
        # Validate parent exists if specified
        if parent_sha256:
            parent = await self.repo.get_by_sha256(parent_sha256)
            if not parent:
                raise NotFoundError(resource_type="manifest", identifier=parent_sha256)

        # Validate all referenced artifacts exist and compute total size
        total_size = 0
        for entry in entries:
            artifact = await self.artifact_repo.get_by_sha256(entry.artifact_sha256)
            if not artifact:
                raise ValidationError(
                    message=f"Artifact not found: {entry.artifact_sha256}",
                    field=f"entries[{entry.path}].artifact_sha256",
                )
            total_size += artifact.size_bytes

        # Build tree structure
        tree = {
            "entries": [
                {
                    "path": e.path,
                    "artifact_sha256": e.artifact_sha256.lower(),
                    "metadata": e.metadata or {},
                }
                for e in entries
            ],
            "metadata": metadata or {},
        }

        # Compute SHA-256 of canonical JSON
        canonical_json = json.dumps(tree, sort_keys=True, separators=(",", ":"))
        sha256 = hashlib.sha256(canonical_json.encode()).hexdigest()

        # Check for duplicate
        existing = await self.repo.get_by_sha256(sha256)
        if existing:
            return ManifestBuildResult(
                sha256=sha256,
                entry_count=len(entries),
                total_size_bytes=total_size,
                is_duplicate=True,
            )

        # Create manifest
        await self.repo.create_manifest(
            sha256=sha256,
            tree=tree,
            entry_count=len(entries),
            total_size_bytes=total_size,
            parent_sha256=parent_sha256,
            message=message,
            created_by=created_by,
        )

        # Increment reference counts for all artifacts
        for entry in entries:
            await self.artifact_repo.increment_reference_count(entry.artifact_sha256)

        return ManifestBuildResult(
            sha256=sha256,
            entry_count=len(entries),
            total_size_bytes=total_size,
            is_duplicate=False,
        )

    async def get_manifest(self, sha256: str) -> Manifest:
        """Get manifest by SHA-256.

        Args:
            sha256: Manifest hash

        Returns:
            Manifest model

        Raises:
            NotFoundError: If manifest doesn't exist
        """
        manifest = await self.repo.get_by_sha256(sha256)
        if not manifest:
            raise NotFoundError(resource_type="manifest", identifier=sha256)
        return manifest

    async def get_entries(self, sha256: str) -> list[ManifestEntry]:
        """Get entries from a manifest.

        Args:
            sha256: Manifest hash

        Returns:
            List of manifest entries

        Raises:
            NotFoundError: If manifest doesn't exist
        """
        manifest = await self.get_manifest(sha256)
        return [
            ManifestEntry(
                path=e["path"],
                artifact_sha256=e["artifact_sha256"],
                metadata=e.get("metadata"),
            )
            for e in manifest.tree.get("entries", [])
        ]

    async def get_history(
        self,
        sha256: str,
        limit: int = 100,
    ) -> list[Manifest]:
        """Get manifest history by walking parent chain.

        Args:
            sha256: Starting manifest hash
            limit: Maximum history depth

        Returns:
            List of manifests from newest to oldest

        Raises:
            NotFoundError: If manifest doesn't exist
        """
        # Verify manifest exists
        await self.get_manifest(sha256)
        return await self.repo.get_history(sha256, limit)

    async def diff_manifests(
        self,
        old_sha256: str,
        new_sha256: str,
    ) -> ManifestDiff:
        """Compute diff between two manifests.

        Args:
            old_sha256: Old manifest hash
            new_sha256: New manifest hash

        Returns:
            ManifestDiff with added, removed, and modified entries

        Raises:
            NotFoundError: If either manifest doesn't exist
        """
        old_entries = await self.get_entries(old_sha256)
        new_entries = await self.get_entries(new_sha256)

        # Build lookup maps
        old_by_path = {e.path: e for e in old_entries}
        new_by_path = {e.path: e for e in new_entries}

        added = []
        removed = []
        modified = []

        # Find added and modified
        for path, new_entry in new_by_path.items():
            if path not in old_by_path:
                added.append(new_entry)
            elif old_by_path[path].artifact_sha256 != new_entry.artifact_sha256:
                modified.append({
                    "path": path,
                    "old": old_by_path[path],
                    "new": new_entry,
                })

        # Find removed
        for path, old_entry in old_by_path.items():
            if path not in new_by_path:
                removed.append(old_entry)

        return ManifestDiff(
            old_sha256=old_sha256,
            new_sha256=new_sha256,
            added=added,
            removed=removed,
            modified=modified,
        )

    async def exists(self, sha256: str) -> bool:
        """Check if manifest exists.

        Args:
            sha256: Manifest hash

        Returns:
            True if exists
        """
        return await self.repo.exists(sha256)

    async def list_manifests(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Manifest]:
        """List recent manifests.

        Args:
            limit: Maximum records
            offset: Skip count

        Returns:
            List of manifests
        """
        return await self.repo.list_recent(limit, offset)
