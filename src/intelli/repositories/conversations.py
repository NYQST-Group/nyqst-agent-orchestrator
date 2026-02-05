"""Repository for Conversation operations."""

from uuid import UUID

from sqlalchemy import and_, func, select

from intelli.db.models.conversations import Conversation
from intelli.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """Repository for Conversation CRUD operations."""

    model = Conversation

    async def list_by_user(
        self,
        tenant_id: UUID,
        user_id: UUID,
        *,
        scope_type: str | None = None,
        scope_id: str | None = None,
        module: str | None = None,
        status: str | None = None,
        session_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Conversation]:
        """List conversations for a user with optional filters."""
        conditions = [
            Conversation.tenant_id == tenant_id,
            Conversation.user_id == user_id,
        ]
        if scope_type:
            conditions.append(Conversation.scope_type == scope_type)
        if scope_id:
            conditions.append(Conversation.scope_id == scope_id)
        if module:
            conditions.append(Conversation.module == module)
        if status:
            conditions.append(Conversation.status == status)
        else:
            conditions.append(Conversation.status != "deleted")
        if session_id:
            conditions.append(Conversation.session_id == session_id)

        stmt = (
            select(Conversation)
            .where(and_(*conditions))
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(
        self,
        tenant_id: UUID,
        user_id: UUID,
        status: str | None = None,
    ) -> int:
        """Count conversations for a user."""
        conditions = [
            Conversation.tenant_id == tenant_id,
            Conversation.user_id == user_id,
        ]
        if status:
            conditions.append(Conversation.status == status)
        else:
            conditions.append(Conversation.status != "deleted")

        stmt = select(func.count()).select_from(Conversation).where(and_(*conditions))
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_by_tenant(
        self,
        conversation_id: UUID,
        tenant_id: UUID,
    ) -> Conversation | None:
        """Get a conversation scoped to a tenant."""
        stmt = select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.tenant_id == tenant_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
