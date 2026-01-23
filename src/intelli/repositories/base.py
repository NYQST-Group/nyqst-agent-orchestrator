"""Base repository with common patterns."""

from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intelli.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Base repository with common CRUD operations."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def get_by_id(self, id_value: Any) -> ModelT | None:
        """Get a single record by primary key.

        Args:
            id_value: Primary key value

        Returns:
            Model instance or None if not found
        """
        return await self.session.get(self.model, id_value)

    async def create(self, **kwargs: Any) -> ModelT:
        """Create a new record.

        Args:
            **kwargs: Model field values

        Returns:
            Created model instance
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, instance: ModelT, **kwargs: Any) -> ModelT:
        """Update an existing record.

        Args:
            instance: Model instance to update
            **kwargs: Fields to update

        Returns:
            Updated model instance
        """
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        return instance

    async def delete(self, instance: ModelT) -> None:
        """Delete a record.

        Args:
            instance: Model instance to delete
        """
        await self.session.delete(instance)
        await self.session.flush()

    async def list_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ModelT]:
        """List all records with pagination.

        Args:
            limit: Maximum records to return
            offset: Number of records to skip

        Returns:
            List of model instances
        """
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        """Count total records.

        Returns:
            Total count
        """
        from sqlalchemy import func

        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar() or 0
