"""Repository for Tag operations."""

from uuid import UUID

from sqlalchemy import and_, func, select

from intelli.db.models.tags import Tag
from intelli.repositories.base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    """Repository for Tag CRUD operations."""

    model = Tag

    async def get_entity_tags(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID,
    ) -> list[Tag]:
        """Get all tags for a specific entity within a tenant."""
        stmt = (
            select(Tag)
            .where(
                and_(
                    Tag.tenant_id == tenant_id,
                    Tag.entity_type == entity_type,
                    Tag.entity_id == entity_id,
                )
            )
            .order_by(Tag.namespace, Tag.key)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_tag(
        self,
        tenant_id: UUID,
        *,
        namespace: str | None = None,
        key: str | None = None,
        value: str | None = None,
        entity_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Tag]:
        """Search tags by namespace/key/value within a tenant."""
        conditions = [Tag.tenant_id == tenant_id]
        if namespace:
            conditions.append(Tag.namespace == namespace)
        if key:
            conditions.append(Tag.key == key)
        if value:
            conditions.append(Tag.value == value)
        if entity_type:
            conditions.append(Tag.entity_type == entity_type)

        stmt = (
            select(Tag)
            .where(and_(*conditions))
            .order_by(Tag.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_search(
        self,
        tenant_id: UUID,
        *,
        namespace: str | None = None,
        key: str | None = None,
        value: str | None = None,
        entity_type: str | None = None,
    ) -> int:
        """Count tags matching search criteria."""
        conditions = [Tag.tenant_id == tenant_id]
        if namespace:
            conditions.append(Tag.namespace == namespace)
        if key:
            conditions.append(Tag.key == key)
        if value:
            conditions.append(Tag.value == value)
        if entity_type:
            conditions.append(Tag.entity_type == entity_type)

        stmt = select(func.count()).select_from(Tag).where(and_(*conditions))
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def find_duplicate(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID,
        namespace: str,
        key: str,
        value: str,
    ) -> Tag | None:
        """Check if a tag already exists (for upsert logic)."""
        stmt = select(Tag).where(
            and_(
                Tag.tenant_id == tenant_id,
                Tag.entity_type == entity_type,
                Tag.entity_id == entity_id,
                Tag.namespace == namespace,
                Tag.key == key,
                Tag.value == value,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
