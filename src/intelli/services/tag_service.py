"""Service for tag operations."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from intelli.core.exceptions import ConflictError, NotFoundError
from intelli.db.models.tags import Tag
from intelli.repositories.tags import TagRepository


class TagService:
    """Service for universal tagging system."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = TagRepository(session)

    async def add_tag(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID,
        namespace: str,
        key: str,
        value: str,
        *,
        source: str = "manual",
        confidence: float | None = None,
    ) -> Tag:
        """Add a tag. Raises ConflictError if duplicate."""
        existing = await self.repo.find_duplicate(
            tenant_id,
            entity_type,
            entity_id,
            namespace,
            key,
            value,
        )
        if existing:
            raise ConflictError(message="Tag already exists")

        return await self.repo.create(
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_id=entity_id,
            namespace=namespace,
            key=key,
            value=value,
            source=source,
            confidence=confidence,
        )

    async def remove_tag(self, tag_id: UUID, tenant_id: UUID) -> None:
        """Remove a tag by ID."""
        tag = await self.repo.get_by_id(tag_id)
        if not tag or tag.tenant_id != tenant_id:
            raise NotFoundError(resource_type="tag", identifier=str(tag_id))
        await self.repo.delete(tag)

    async def list_tags(
        self,
        tenant_id: UUID,
        *,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        namespace: str | None = None,
        key: str | None = None,
        value: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Tag], int]:
        """List/filter tags."""
        if entity_type and entity_id:
            items = await self.repo.get_entity_tags(tenant_id, entity_type, entity_id)
            return items, len(items)

        items = await self.repo.search_by_tag(
            tenant_id,
            namespace=namespace,
            key=key,
            value=value,
            entity_type=entity_type,
            limit=limit,
            offset=offset,
        )
        total = await self.repo.count_by_search(
            tenant_id,
            namespace=namespace,
            key=key,
            value=value,
            entity_type=entity_type,
        )
        return items, total

    async def search_entities_by_tag(
        self,
        tenant_id: UUID,
        *,
        namespace: str | None = None,
        key: str | None = None,
        value: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Cross-entity tag search. Returns grouped results by entity."""
        tags = await self.repo.search_by_tag(
            tenant_id,
            namespace=namespace,
            key=key,
            value=value,
            limit=limit,
        )

        # Group by entity
        entities: dict[tuple[str, UUID], list[Tag]] = {}
        for tag in tags:
            ek = (tag.entity_type, tag.entity_id)
            entities.setdefault(ek, []).append(tag)

        return [
            {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "tags": entity_tags,
            }
            for (entity_type, entity_id), entity_tags in entities.items()
        ]
