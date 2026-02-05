"""Repository for Message operations."""

from uuid import UUID

from sqlalchemy import and_, func, select

from intelli.db.models.conversations import Message
from intelli.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """Repository for Message CRUD operations."""

    model = Message

    async def list_by_conversation(
        self,
        conversation_id: UUID,
        *,
        limit: int = 100,
        before_seq: int | None = None,
    ) -> list[Message]:
        """List messages for a conversation, paginated by sequence_number."""
        conditions = [Message.conversation_id == conversation_id]
        if before_seq is not None:
            conditions.append(Message.sequence_number < before_seq)

        stmt = (
            select(Message)
            .where(and_(*conditions))
            .order_by(Message.sequence_number.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_conversation(self, conversation_id: UUID) -> int:
        """Count messages in a conversation."""
        stmt = (
            select(func.count())
            .select_from(Message)
            .where(Message.conversation_id == conversation_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_next_sequence(self, conversation_id: UUID) -> int:
        """Get the next sequence number for a conversation."""
        stmt = select(func.coalesce(func.max(Message.sequence_number), 0)).where(
            Message.conversation_id == conversation_id
        )
        result = await self.session.execute(stmt)
        return (result.scalar() or 0) + 1

    async def get_branch_siblings(self, parent_message_id: UUID) -> list[Message]:
        """Get all messages that share the same parent (branch siblings)."""
        stmt = (
            select(Message)
            .where(Message.parent_message_id == parent_message_id)
            .order_by(Message.sequence_number.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_thread(self, message_id: UUID) -> list[Message]:
        """Walk the parent chain from a message to the root.

        Returns messages in root-first order.
        """
        messages = []
        current_id = message_id
        while current_id:
            msg = await self.get_by_id(current_id)
            if not msg:
                break
            messages.append(msg)
            current_id = msg.parent_message_id
        messages.reverse()
        return messages
