"""Service for pointer operations."""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from intelli.core.exceptions import ConflictError, NotFoundError
from intelli.db.models.substrate import Pointer, PointerHistory
from intelli.repositories.manifests import ManifestRepository
from intelli.repositories.pointers import PointerRepository
from intelli.schemas.substrate import PointerType


@dataclass
class PointerAdvanceResult:
    """Result of pointer advance operation."""

    success: bool
    old_sha256: str | None
    new_sha256: str
    conflict: bool = False


class PointerService:
    """Service for pointer business logic.

    Handles pointer creation, resolution, advancement,
    and history tracking.
    """

    def __init__(self, session: AsyncSession):
        """Initialize pointer service.

        Args:
            session: Database session
        """
        self.repo = PointerRepository(session)
        self.manifest_repo = ManifestRepository(session)

    async def create_pointer(
        self,
        namespace: str,
        name: str,
        pointer_type: PointerType = PointerType.BUNDLE,
        manifest_sha256: str | None = None,
        description: str | None = None,
        metadata: dict | None = None,
        created_by: UUID | None = None,
    ) -> Pointer:
        """Create a new pointer.

        Args:
            namespace: Namespace for the pointer
            name: Pointer name
            pointer_type: Type (bundle, corpus, snapshot)
            manifest_sha256: Initial manifest hash
            description: Human-readable description
            metadata: Additional metadata
            created_by: Creator principal ID

        Returns:
            Created pointer

        Raises:
            ConflictError: If pointer with same name exists in namespace
            NotFoundError: If specified manifest doesn't exist
        """
        # Check for existing pointer
        existing = await self.repo.get_by_name(namespace, name)
        if existing:
            raise ConflictError(
                f"Pointer already exists: {namespace}/{name}"
            )

        # Validate manifest if specified
        if manifest_sha256:
            manifest = await self.manifest_repo.get_by_sha256(manifest_sha256)
            if not manifest:
                raise NotFoundError(resource_type="manifest", identifier=manifest_sha256)

        return await self.repo.create_pointer(
            namespace=namespace,
            name=name,
            pointer_type=pointer_type.value,
            manifest_sha256=manifest_sha256,
            description=description,
            metadata=metadata,
            created_by=created_by,
        )

    async def get_pointer(
        self,
        namespace: str,
        name: str,
    ) -> Pointer:
        """Get pointer by namespace and name.

        Args:
            namespace: Pointer namespace
            name: Pointer name

        Returns:
            Pointer model

        Raises:
            NotFoundError: If pointer doesn't exist
        """
        pointer = await self.repo.get_by_name(namespace, name)
        if not pointer:
            raise NotFoundError(
                resource_type="pointer",
                identifier=f"{namespace}/{name}",
            )
        return pointer

    async def get_pointer_by_id(self, pointer_id: UUID) -> Pointer:
        """Get pointer by ID.

        Args:
            pointer_id: Pointer UUID

        Returns:
            Pointer model

        Raises:
            NotFoundError: If pointer doesn't exist
        """
        pointer = await self.repo.get_by_id(pointer_id)
        if not pointer or pointer.deleted_at:
            raise NotFoundError(
                resource_type="pointer",
                identifier=str(pointer_id),
            )
        return pointer

    async def resolve(
        self,
        namespace: str,
        name: str,
    ) -> str | None:
        """Resolve pointer to current manifest SHA-256.

        Args:
            namespace: Pointer namespace
            name: Pointer name

        Returns:
            Current manifest SHA-256 or None if empty

        Raises:
            NotFoundError: If pointer doesn't exist
        """
        pointer = await self.get_pointer(namespace, name)
        return pointer.manifest_sha256

    async def advance(
        self,
        pointer_id: UUID,
        new_sha256: str,
        expected_sha256: str | None = None,
        reason: str | None = None,
        changed_by: UUID | None = None,
    ) -> PointerAdvanceResult:
        """Advance pointer HEAD to a new manifest.

        Uses optimistic locking if expected_sha256 is provided.

        Args:
            pointer_id: Pointer UUID
            new_sha256: New manifest SHA-256
            expected_sha256: Expected current SHA-256
            reason: Reason for the change
            changed_by: Who made the change

        Returns:
            Advance result

        Raises:
            NotFoundError: If pointer or manifest doesn't exist
        """
        pointer = await self.get_pointer_by_id(pointer_id)

        # Validate new manifest exists
        manifest = await self.manifest_repo.get_by_sha256(new_sha256)
        if not manifest:
            raise NotFoundError(resource_type="manifest", identifier=new_sha256)

        success, old_sha256 = await self.repo.advance(
            pointer=pointer,
            new_sha256=new_sha256,
            expected_sha256=expected_sha256,
            reason=reason,
            changed_by=changed_by,
        )

        return PointerAdvanceResult(
            success=success,
            old_sha256=old_sha256,
            new_sha256=new_sha256,
            conflict=not success,
        )

    async def reset(
        self,
        pointer_id: UUID,
        target_sha256: str | None,
        reason: str | None = None,
        changed_by: UUID | None = None,
    ) -> str | None:
        """Reset pointer HEAD to a specific manifest or clear it.

        Args:
            pointer_id: Pointer UUID
            target_sha256: Target manifest SHA-256 (or None to clear)
            reason: Reason for reset
            changed_by: Who made the change

        Returns:
            Previous manifest SHA-256

        Raises:
            NotFoundError: If pointer or target manifest doesn't exist
        """
        pointer = await self.get_pointer_by_id(pointer_id)

        # Validate target manifest if specified
        if target_sha256:
            manifest = await self.manifest_repo.get_by_sha256(target_sha256)
            if not manifest:
                raise NotFoundError(resource_type="manifest", identifier=target_sha256)

        return await self.repo.reset(
            pointer=pointer,
            target_sha256=target_sha256,
            reason=reason,
            changed_by=changed_by,
        )

    async def delete_pointer(
        self,
        pointer_id: UUID,
        deleted_by: UUID | None = None,
    ) -> None:
        """Soft delete a pointer.

        Args:
            pointer_id: Pointer UUID
            deleted_by: Who deleted it

        Raises:
            NotFoundError: If pointer doesn't exist
        """
        pointer = await self.get_pointer_by_id(pointer_id)
        await self.repo.soft_delete(pointer, deleted_by)

    async def get_history(
        self,
        pointer_id: UUID,
        limit: int = 100,
    ) -> list[PointerHistory]:
        """Get pointer change history.

        Args:
            pointer_id: Pointer UUID
            limit: Maximum records

        Returns:
            List of history entries, newest first

        Raises:
            NotFoundError: If pointer doesn't exist
        """
        await self.get_pointer_by_id(pointer_id)
        return await self.repo.get_history(pointer_id, limit)

    async def list_pointers(
        self,
        namespace: str | None = None,
        pointer_type: PointerType | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Pointer]:
        """List pointers with optional filters.

        Args:
            namespace: Filter by namespace
            pointer_type: Filter by type
            limit: Maximum records
            offset: Skip count

        Returns:
            List of pointers
        """
        type_value = pointer_type.value if pointer_type else None

        if namespace:
            return await self.repo.list_by_namespace(
                namespace, type_value, limit, offset
            )
        return await self.repo.list_all_active(type_value, limit, offset)
