"""Repository for Session operations."""

from uuid import UUID

from sqlalchemy import and_, func, select

from intelli.core.clock import utc_now
from intelli.db.models.conversations import Conversation, Session
from intelli.repositories.base import BaseRepository


class SessionRepository(BaseRepository[Session]):
    """Repository for Session CRUD operations."""

    model = Session

    async def list_by_user(
        self,
        tenant_id: UUID,
        user_id: UUID,
        *,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Session]:
        """List sessions for a user."""
        conditions = [
            Session.tenant_id == tenant_id,
            Session.user_id == user_id,
        ]
        if status:
            conditions.append(Session.status == status)

        stmt = (
            select(Session)
            .where(and_(*conditions))
            .order_by(Session.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(
        self,
        tenant_id: UUID,
        user_id: UUID,
    ) -> int:
        """Count sessions for a user."""
        stmt = (
            select(func.count())
            .select_from(Session)
            .where(
                and_(
                    Session.tenant_id == tenant_id,
                    Session.user_id == user_id,
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_by_tenant(
        self,
        session_id: UUID,
        tenant_id: UUID,
    ) -> Session | None:
        """Get a session scoped to a tenant."""
        stmt = select(Session).where(
            and_(
                Session.id == session_id,
                Session.tenant_id == tenant_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_for_user(
        self,
        tenant_id: UUID,
        user_id: UUID,
    ) -> Session | None:
        """Get the active session for a user (if any)."""
        stmt = (
            select(Session)
            .where(
                and_(
                    Session.tenant_id == tenant_id,
                    Session.user_id == user_id,
                    Session.status == "active",
                )
            )
            .order_by(Session.last_active_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_idle(self, threshold_minutes: int | None = None) -> list[Session]:
        """Find active sessions that have been idle past their timeout."""
        now = utc_now()
        # Use SQL expression for per-session timeout
        stmt = select(Session).where(
            and_(
                Session.status == "active",
                Session.last_active_at
                < now - func.make_interval(0, 0, 0, 0, 0, Session.idle_timeout_minutes),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def aggregate_cost(self, session_id: UUID) -> dict:
        """Aggregate cost from all conversations in a session."""
        stmt = select(
            func.count(Conversation.id).label("count"),
            func.coalesce(func.sum(Conversation.total_input_tokens), 0).label("input_tokens"),
            func.coalesce(func.sum(Conversation.total_output_tokens), 0).label("output_tokens"),
            func.coalesce(func.sum(Conversation.total_cost_micros), 0).label("cost_micros"),
        ).where(Conversation.session_id == session_id)
        result = await self.session.execute(stmt)
        row = result.one()
        return {
            "conversation_count": row.count,
            "total_input_tokens": row.input_tokens,
            "total_output_tokens": row.output_tokens,
            "total_cost_micros": row.cost_micros,
        }
