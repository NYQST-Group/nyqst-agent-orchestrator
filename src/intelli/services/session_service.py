"""Service for session lifecycle management."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from intelli.core.clock import utc_now
from intelli.core.exceptions import NotFoundError, ValidationError
from intelli.db.models.conversations import Session, SessionStatus
from intelli.repositories.sessions import SessionRepository
from intelli.services.usage.pricing import PRICE_TABLE_VERSION

# Valid state transitions (self-transitions are no-ops)
_TRANSITIONS: dict[str, set[str]] = {
    SessionStatus.active.value: {
        SessionStatus.active.value,
        SessionStatus.idle.value,
        SessionStatus.paused.value,
        SessionStatus.closed.value,
    },
    SessionStatus.idle.value: {
        SessionStatus.idle.value,
        SessionStatus.active.value,
        SessionStatus.closed.value,
    },
    SessionStatus.paused.value: {
        SessionStatus.paused.value,
        SessionStatus.active.value,
        SessionStatus.closed.value,
    },
    SessionStatus.closed.value: set(),  # terminal state
}


class SessionService:
    """Service for session lifecycle: start, idle, resume, close."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SessionRepository(session)

    @staticmethod
    def _merge_model_totals(model_totals: dict[str, dict[str, int]], token_usage: dict | None) -> None:
        if not isinstance(token_usage, dict):
            return
        for model, usage in token_usage.items():
            if not isinstance(usage, dict):
                continue
            bucket = model_totals.setdefault(
                model,
                {"input_tokens": 0, "output_tokens": 0, "cost_micros": 0},
            )
            bucket["input_tokens"] += int(usage.get("input_tokens", usage.get("input", 0)) or 0)
            bucket["output_tokens"] += int(usage.get("output_tokens", usage.get("output", 0)) or 0)
            bucket["cost_micros"] += int(usage.get("cost_micros", 0) or 0)

    async def start(
        self,
        tenant_id: UUID,
        user_id: UUID,
        *,
        scope_type: str = "tenant",
        scope_id: UUID | None = None,
        module: str | None = None,
        objective: str | None = None,
        config_snapshot: dict | None = None,
        idle_timeout_minutes: int = 30,
    ) -> Session:
        """Start a new session."""
        now = utc_now()
        return await self.repo.create(
            tenant_id=tenant_id,
            user_id=user_id,
            scope_type=scope_type,
            scope_id=scope_id,
            module=module,
            objective=objective,
            config_snapshot=config_snapshot or {},
            idle_timeout_minutes=idle_timeout_minutes,
            status=SessionStatus.active.value,
            started_at=now,
            last_active_at=now,
            updated_at=now,
        )

    async def get(self, session_id: UUID, tenant_id: UUID) -> Session:
        """Get session by ID, scoped to tenant."""
        sess = await self.repo.get_by_tenant(session_id, tenant_id)
        if not sess:
            raise NotFoundError(resource_type="session", identifier=str(session_id))
        return sess

    async def list_for_user(
        self,
        tenant_id: UUID,
        user_id: UUID,
        **filters,
    ) -> tuple[list[Session], int]:
        """List sessions for a user with count."""
        items = await self.repo.list_by_user(tenant_id, user_id, **filters)
        total = await self.repo.count_by_user(tenant_id, user_id)
        return items, total

    async def transition(
        self,
        session_id: UUID,
        tenant_id: UUID,
        new_status: str,
        close_reason: str | None = None,
    ) -> Session:
        """Transition a session to a new status."""
        sess = await self.get(session_id, tenant_id)
        allowed = _TRANSITIONS.get(sess.status, set())
        if new_status not in allowed:
            raise ValidationError(
                f"Cannot transition session from '{sess.status}' to '{new_status}'",
                field="status",
            )

        now = utc_now()
        sess.status = new_status
        sess.updated_at = now

        if new_status == SessionStatus.active.value:
            sess.last_active_at = now
        elif new_status == SessionStatus.closed.value:
            sess.closed_at = now
            sess.close_reason = close_reason or "user_ended"
            # Aggregate cost from conversations
            cost = await self.get_cost_breakdown(session_id, tenant_id)
            sess.total_cost_micros = cost["total_cost_micros"]

        await self.session.flush()
        return sess

    async def touch(self, session_id: UUID) -> None:
        """Update last_active_at (called by middleware on requests)."""
        sess = await self.repo.get_by_id(session_id)
        if sess and sess.status == SessionStatus.active.value:
            sess.last_active_at = utc_now()
            await self.session.flush()

    async def get_cost_breakdown(self, session_id: UUID, tenant_id: UUID) -> dict:
        """Get cost breakdown for a session."""
        await self.get(session_id, tenant_id)
        agg = await self.repo.aggregate_cost(session_id)
        runs = await self.repo.list_runs(session_id)

        # Get per-conversation breakdown
        from sqlalchemy import select

        from intelli.db.models.conversations import Conversation

        stmt = select(Conversation).where(Conversation.session_id == session_id)
        result = await self.session.execute(stmt)
        convs = result.scalars().all()

        non_chat_run_cost = 0
        non_chat_input_tokens = 0
        non_chat_output_tokens = 0
        model_totals: dict[str, dict[str, int]] = {}
        for run in runs:
            self._merge_model_totals(model_totals, run.token_usage)
            if run.run_type != "agent_chat":
                non_chat_input_tokens += sum(
                    int(usage.get("input_tokens", usage.get("input", 0)) or 0)
                    for usage in (run.token_usage or {}).values()
                    if isinstance(usage, dict)
                )
                non_chat_output_tokens += sum(
                    int(usage.get("output_tokens", usage.get("output", 0)) or 0)
                    for usage in (run.token_usage or {}).values()
                    if isinstance(usage, dict)
                )
                non_chat_run_cost += sum(
                    int(usage.get("cost_micros", 0) or 0)
                    for usage in (run.token_usage or {}).values()
                    if isinstance(usage, dict)
                )

        per_model = [
            {
                "model": model,
                "input_tokens": totals["input_tokens"],
                "output_tokens": totals["output_tokens"],
                "cost_micros": totals["cost_micros"],
            }
            for model, totals in sorted(
                model_totals.items(),
                key=lambda item: (-item[1]["cost_micros"], item[0]),
            )
        ]

        return {
            "session_id": session_id,
            "price_table_version": PRICE_TABLE_VERSION,
            "total_cost_micros": agg["total_cost_micros"] + non_chat_run_cost,
            "conversation_count": agg["conversation_count"],
            "total_input_tokens": agg["total_input_tokens"] + non_chat_input_tokens,
            "total_output_tokens": agg["total_output_tokens"] + non_chat_output_tokens,
            "models": per_model,
            "conversations": [
                {
                    "id": str(c.id),
                    "title": c.title,
                    "cost_micros": c.total_cost_micros,
                    "input_tokens": c.total_input_tokens,
                    "output_tokens": c.total_output_tokens,
                }
                for c in convs
            ],
        }

    async def idle_stale_sessions(self) -> int:
        """Find and idle stale sessions. Returns count of idled sessions."""
        stale = await self.repo.find_idle()
        count = 0
        for sess in stale:
            sess.status = SessionStatus.idle.value
            sess.updated_at = utc_now()
            count += 1
        if count:
            await self.session.flush()
        return count
