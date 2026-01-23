"""Repository for Pointer operations."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, and_

from intelli.core.clock import utc_now
from intelli.db.models.substrate import Pointer, PointerHistory
from intelli.repositories.base import BaseRepository


class PointerRepository(BaseRepository[Pointer]):
    """Repository for Pointer CRUD operations."""

    model = Pointer

    async def get_by_name(
        self,
        namespace: str,
        name: str,
    ) -> Pointer | None:
        """Get pointer by namespace and name.

        Args:
            namespace: Pointer namespace
            name: Pointer name

        Returns:
            Pointer or None if not found
        """
        stmt = select(Pointer).where(
            and_(
                Pointer.namespace == namespace,
                Pointer.name == name,
                Pointer.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_pointer(
        self,
        namespace: str,
        name: str,
        pointer_type: str = "bundle",
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
            manifest_sha256: Initial manifest SHA-256
            description: Human-readable description
            metadata: Additional metadata
            created_by: Creator principal ID

        Returns:
            Created pointer
        """
        pointer = await self.create(
            namespace=namespace,
            name=name,
            pointer_type=pointer_type,
            manifest_sha256=manifest_sha256.lower() if manifest_sha256 else None,
            description=description,
            metadata=metadata or {},
            created_by=created_by,
        )

        # Record creation in history
        await self._record_history(
            pointer_id=pointer.id,
            old_sha256=None,
            new_sha256=manifest_sha256,
            operation="create",
            changed_by=created_by,
            reason="Pointer created",
        )

        return pointer

    async def advance(
        self,
        pointer: Pointer,
        new_sha256: str,
        expected_sha256: str | None = None,
        reason: str | None = None,
        changed_by: UUID | None = None,
    ) -> tuple[bool, str | None]:
        """Advance pointer HEAD to a new manifest.

        Uses optimistic locking if expected_sha256 is provided.

        Args:
            pointer: Pointer to advance
            new_sha256: New manifest SHA-256
            expected_sha256: Expected current SHA-256 (for optimistic locking)
            reason: Reason for the change
            changed_by: Who made the change

        Returns:
            Tuple of (success, old_sha256)
        """
        old_sha256 = pointer.manifest_sha256

        # Check optimistic lock
        if expected_sha256 is not None:
            if old_sha256 != expected_sha256.lower() if expected_sha256 else old_sha256 is not None:
                return False, old_sha256

        # Update pointer
        pointer.manifest_sha256 = new_sha256.lower()
        pointer.updated_at = utc_now()
        await self.session.flush()

        # Record in history
        await self._record_history(
            pointer_id=pointer.id,
            old_sha256=old_sha256,
            new_sha256=new_sha256,
            operation="advance",
            changed_by=changed_by,
            reason=reason,
        )

        return True, old_sha256

    async def reset(
        self,
        pointer: Pointer,
        target_sha256: str | None,
        reason: str | None = None,
        changed_by: UUID | None = None,
    ) -> str | None:
        """Reset pointer HEAD to a specific manifest (or null).

        Args:
            pointer: Pointer to reset
            target_sha256: Target manifest SHA-256 (or None to clear)
            reason: Reason for the reset
            changed_by: Who made the change

        Returns:
            Previous manifest SHA-256
        """
        old_sha256 = pointer.manifest_sha256

        # Update pointer
        pointer.manifest_sha256 = target_sha256.lower() if target_sha256 else None
        pointer.updated_at = utc_now()
        await self.session.flush()

        # Record in history
        await self._record_history(
            pointer_id=pointer.id,
            old_sha256=old_sha256,
            new_sha256=target_sha256,
            operation="reset",
            changed_by=changed_by,
            reason=reason,
        )

        return old_sha256

    async def soft_delete(
        self,
        pointer: Pointer,
        deleted_by: UUID | None = None,
    ) -> None:
        """Soft delete a pointer.

        Args:
            pointer: Pointer to delete
            deleted_by: Who deleted it
        """
        pointer.deleted_at = utc_now()
        await self.session.flush()

        # Record in history
        await self._record_history(
            pointer_id=pointer.id,
            old_sha256=pointer.manifest_sha256,
            new_sha256=None,
            operation="delete",
            changed_by=deleted_by,
            reason="Pointer deleted",
        )

    async def list_by_namespace(
        self,
        namespace: str,
        pointer_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Pointer]:
        """List pointers in a namespace.

        Args:
            namespace: Namespace to filter by
            pointer_type: Optional type filter
            limit: Maximum records
            offset: Skip count

        Returns:
            List of pointers
        """
        conditions = [
            Pointer.namespace == namespace,
            Pointer.deleted_at.is_(None),
        ]
        if pointer_type:
            conditions.append(Pointer.pointer_type == pointer_type)

        stmt = (
            select(Pointer)
            .where(and_(*conditions))
            .order_by(Pointer.name)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_all_active(
        self,
        pointer_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Pointer]:
        """List all active (non-deleted) pointers.

        Args:
            pointer_type: Optional type filter
            limit: Maximum records
            offset: Skip count

        Returns:
            List of pointers
        """
        conditions = [Pointer.deleted_at.is_(None)]
        if pointer_type:
            conditions.append(Pointer.pointer_type == pointer_type)

        stmt = (
            select(Pointer)
            .where(and_(*conditions))
            .order_by(Pointer.namespace, Pointer.name)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_history(
        self,
        pointer_id: UUID,
        limit: int = 100,
    ) -> list[PointerHistory]:
        """Get pointer change history.

        Args:
            pointer_id: Pointer ID
            limit: Maximum records

        Returns:
            List of history entries, newest first
        """
        stmt = (
            select(PointerHistory)
            .where(PointerHistory.pointer_id == pointer_id)
            .order_by(PointerHistory.changed_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def _record_history(
        self,
        pointer_id: UUID,
        old_sha256: str | None,
        new_sha256: str | None,
        operation: str,
        changed_by: UUID | None,
        reason: str | None,
    ) -> PointerHistory:
        """Record a pointer change in history.

        Args:
            pointer_id: Pointer ID
            old_sha256: Previous manifest SHA-256
            new_sha256: New manifest SHA-256
            operation: Operation type
            changed_by: Who made the change
            reason: Reason for the change

        Returns:
            Created history entry
        """
        history = PointerHistory(
            pointer_id=pointer_id,
            old_sha256=old_sha256.lower() if old_sha256 else None,
            new_sha256=new_sha256.lower() if new_sha256 else None,
            operation=operation,
            changed_by=changed_by,
            changed_at=utc_now(),
            reason=reason,
        )
        self.session.add(history)
        await self.session.flush()
        return history
