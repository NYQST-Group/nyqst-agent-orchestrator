"""Service for conversation and message operations."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from intelli.core.clock import utc_now
from intelli.core.exceptions import ConflictError, NotFoundError
from intelli.db.models.conversations import (
    Conversation,
    ConversationStatus,
    Message,
    MessageFeedback,
)
from intelli.repositories.conversations import ConversationRepository
from intelli.repositories.messages import MessageRepository


class ConversationService:
    """Service for conversation lifecycle and message management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.conv_repo = ConversationRepository(session)
        self.msg_repo = MessageRepository(session)

    # -----------------------------------------------------------------------
    # Conversations
    # -----------------------------------------------------------------------

    async def create(
        self,
        tenant_id: UUID,
        user_id: UUID,
        *,
        scope_type: str = "tenant",
        scope_id: UUID | None = None,
        module: str | None = None,
        title: str | None = None,
        session_id: UUID | None = None,
        config_snapshot: dict | None = None,
    ) -> Conversation:
        """Create a new conversation."""
        return await self.conv_repo.create(
            tenant_id=tenant_id,
            user_id=user_id,
            scope_type=scope_type,
            scope_id=scope_id,
            module=module,
            title=title,
            session_id=session_id,
            config_snapshot=config_snapshot or {},
        )

    async def get(self, conversation_id: UUID, tenant_id: UUID) -> Conversation:
        """Get a conversation by ID, scoped to tenant."""
        conv = await self.conv_repo.get_by_tenant(conversation_id, tenant_id)
        if not conv:
            raise NotFoundError(resource_type="conversation", identifier=str(conversation_id))
        return conv

    async def list_for_user(
        self,
        tenant_id: UUID,
        user_id: UUID,
        **filters,
    ) -> tuple[list[Conversation], int]:
        """List conversations for a user with count."""
        items = await self.conv_repo.list_by_user(tenant_id, user_id, **filters)
        total = await self.conv_repo.count_by_user(tenant_id, user_id, status=filters.get("status"))
        return items, total

    async def update(
        self,
        conversation_id: UUID,
        tenant_id: UUID,
        **kwargs,
    ) -> Conversation:
        """Update conversation metadata."""
        conv = await self.get(conversation_id, tenant_id)
        return await self.conv_repo.update(conv, **kwargs)

    async def archive(self, conversation_id: UUID, tenant_id: UUID) -> Conversation:
        """Archive a conversation."""
        conv = await self.get(conversation_id, tenant_id)
        conv.status = ConversationStatus.archived.value
        conv.updated_at = utc_now()
        await self.session.flush()
        return conv

    async def soft_delete(self, conversation_id: UUID, tenant_id: UUID) -> None:
        """Soft-delete a conversation."""
        conv = await self.get(conversation_id, tenant_id)
        conv.status = ConversationStatus.deleted.value
        conv.updated_at = utc_now()
        await self.session.flush()

    # -----------------------------------------------------------------------
    # Messages
    # -----------------------------------------------------------------------

    async def save_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str | None = None,
        *,
        parts: dict | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        cost_micros: int | None = None,
        latency_ms: int | None = None,
        model_id: str | None = None,
        parent_message_id: UUID | None = None,
        run_event_id: UUID | None = None,
    ) -> Message:
        """Save a message and update conversation totals."""
        seq = await self.msg_repo.get_next_sequence(conversation_id)

        message = await self.msg_repo.create(
            conversation_id=conversation_id,
            role=role,
            content=content,
            parts=parts,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_micros=cost_micros,
            latency_ms=latency_ms,
            model_id=model_id,
            parent_message_id=parent_message_id,
            run_event_id=run_event_id,
            sequence_number=seq,
        )

        # Update conversation totals
        conv = await self.conv_repo.get_by_id(conversation_id)
        if conv:
            conv.message_count = (conv.message_count or 0) + 1
            conv.last_message_at = utc_now()
            conv.updated_at = utc_now()
            if input_tokens:
                conv.total_input_tokens = (conv.total_input_tokens or 0) + input_tokens
            if output_tokens:
                conv.total_output_tokens = (conv.total_output_tokens or 0) + output_tokens
            if cost_micros:
                conv.total_cost_micros = (conv.total_cost_micros or 0) + cost_micros
            await self.session.flush()

        return message

    async def get_messages(
        self,
        conversation_id: UUID,
        *,
        limit: int = 100,
        before_seq: int | None = None,
    ) -> tuple[list[Message], int]:
        """Get messages for a conversation with count."""
        items = await self.msg_repo.list_by_conversation(
            conversation_id,
            limit=limit,
            before_seq=before_seq,
        )
        total = await self.msg_repo.count_by_conversation(conversation_id)
        return items, total

    # -----------------------------------------------------------------------
    # Feedback
    # -----------------------------------------------------------------------

    async def add_feedback(
        self,
        message_id: UUID,
        user_id: UUID,
        rating: str,
        content: str | None = None,
    ) -> MessageFeedback:
        """Add feedback to a message. Raises ConflictError on duplicate."""
        from sqlalchemy import and_, select

        # Check for existing feedback
        stmt = select(MessageFeedback).where(
            and_(
                MessageFeedback.message_id == message_id,
                MessageFeedback.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none():
            raise ConflictError(message="Feedback already exists for this message")

        feedback = MessageFeedback(
            message_id=message_id,
            user_id=user_id,
            rating=rating,
            content=content,
        )
        self.session.add(feedback)
        await self.session.flush()
        return feedback

    # -----------------------------------------------------------------------
    # Branching
    # -----------------------------------------------------------------------

    async def branch_from_message(
        self,
        conversation_id: UUID,
        message_id: UUID,
    ) -> dict:
        """Create a branch point from a message.

        Returns info about the branch: the new sequence number to continue from.
        """
        msg = await self.msg_repo.get_by_id(message_id)
        if not msg or msg.conversation_id != conversation_id:
            raise NotFoundError(resource_type="message", identifier=str(message_id))

        next_seq = await self.msg_repo.get_next_sequence(conversation_id)
        return {
            "conversation_id": conversation_id,
            "branch_point_message_id": message_id,
            "new_sequence_number": next_seq,
        }

    async def get_siblings(
        self,
        conversation_id: UUID,
        message_id: UUID,
    ) -> tuple[list[Message], int, int]:
        """Get sibling messages (messages that share the same parent).

        Returns (siblings, total, current_index).
        """
        msg = await self.msg_repo.get_by_id(message_id)
        if not msg or msg.conversation_id != conversation_id:
            raise NotFoundError(resource_type="message", identifier=str(message_id))

        # Get all messages with the same parent
        if msg.parent_message_id is None:
            # No parent means no siblings (root message)
            return [msg], 1, 0

        siblings = await self.msg_repo.get_branch_siblings(msg.parent_message_id)

        # Find the index of the current message
        current_index = next(
            (i for i, sibling in enumerate(siblings) if sibling.id == message_id),
            0,
        )

        return siblings, len(siblings), current_index

    # -----------------------------------------------------------------------
    # Cost tracking
    # -----------------------------------------------------------------------

    async def update_cost_totals(
        self,
        conversation_id: UUID,
        input_tokens: int,
        output_tokens: int,
        cost_micros: int,
    ) -> None:
        """Update cost totals on a conversation (idempotent add)."""
        conv = await self.conv_repo.get_by_id(conversation_id)
        if conv:
            conv.total_input_tokens = (conv.total_input_tokens or 0) + input_tokens
            conv.total_output_tokens = (conv.total_output_tokens or 0) + output_tokens
            conv.total_cost_micros = (conv.total_cost_micros or 0) + cost_micros
            conv.updated_at = utc_now()
            await self.session.flush()
