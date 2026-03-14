"""Repository for Run and RunEvent operations."""

from uuid import UUID

from sqlalchemy import and_, func, select

from intelli.core.clock import utc_now
from intelli.db.models.runs import Run, RunEvent, RunStatus
from intelli.repositories.base import BaseRepository


class RunRepository(BaseRepository[Run]):
    """Repository for Run CRUD operations."""

    model = Run

    async def create_run(
        self,
        run_type: str,
        name: str | None = None,
        config: dict | None = None,
        input_manifest_sha256: str | None = None,
        project_id: UUID | None = None,
        session_id: UUID | None = None,
        parent_run_id: UUID | None = None,
        created_by: UUID | None = None,
    ) -> Run:
        """Create a new run.

        Args:
            run_type: Type of run
            name: Human-readable name
            config: Run configuration
            input_manifest_sha256: Input manifest
            project_id: Project ID
            session_id: Session ID
            parent_run_id: Parent run for nested execution
            created_by: Creator principal ID

        Returns:
            Created run
        """
        return await self.create(
            run_type=run_type,
            name=name,
            config=config or {},
            input_manifest_sha256=input_manifest_sha256.lower() if input_manifest_sha256 else None,
            project_id=project_id,
            session_id=session_id,
            parent_run_id=parent_run_id,
            created_by=created_by,
        )

    async def start(self, run: Run) -> Run:
        """Mark run as started.

        Args:
            run: Run to start

        Returns:
            Updated run
        """
        run.status = RunStatus.RUNNING.value
        run.started_at = utc_now()
        await self.session.flush()
        return run

    async def pause(self, run: Run) -> Run:
        """Mark run as paused.

        Args:
            run: Run to pause

        Returns:
            Updated run
        """
        run.status = RunStatus.PAUSED.value
        await self.session.flush()
        return run

    async def resume(self, run: Run) -> Run:
        """Mark run as resumed (running).

        Args:
            run: Run to resume

        Returns:
            Updated run
        """
        run.status = RunStatus.RUNNING.value
        await self.session.flush()
        return run

    async def complete(
        self,
        run: Run,
        result: dict | None = None,
        output_manifest_sha256: str | None = None,
    ) -> Run:
        """Mark run as completed.

        Args:
            run: Run to complete
            result: Run result
            output_manifest_sha256: Output manifest

        Returns:
            Updated run
        """
        run.status = RunStatus.COMPLETED.value
        run.completed_at = utc_now()
        run.result = result
        if output_manifest_sha256:
            run.output_manifest_sha256 = output_manifest_sha256.lower()
        await self.session.flush()
        return run

    async def fail(
        self,
        run: Run,
        error: dict,
    ) -> Run:
        """Mark run as failed.

        Args:
            run: Run to fail
            error: Error details

        Returns:
            Updated run
        """
        run.status = RunStatus.FAILED.value
        run.completed_at = utc_now()
        run.error = error
        await self.session.flush()
        return run

    async def cancel(self, run: Run) -> Run:
        """Mark run as cancelled.

        Args:
            run: Run to cancel

        Returns:
            Updated run
        """
        run.status = RunStatus.CANCELLED.value
        run.completed_at = utc_now()
        await self.session.flush()
        return run

    async def update_token_usage(
        self,
        run: Run,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_micros: int = 0,
    ) -> Run:
        """Update token usage for a run.

        Args:
            run: Run to update
            model: Model ID
            input_tokens: Input token count
            output_tokens: Output token count

        Returns:
            Updated run
        """
        existing = run.token_usage.get(model, {})
        run.token_usage[model] = {
            "input_tokens": int(existing.get("input_tokens", existing.get("input", 0))) + input_tokens,
            "output_tokens": int(existing.get("output_tokens", existing.get("output", 0))) + output_tokens,
            "cost_micros": int(existing.get("cost_micros", 0)) + cost_micros,
        }

        total_cost_micros = sum(
            int(model_usage.get("cost_micros", 0))
            for model_usage in run.token_usage.values()
            if isinstance(model_usage, dict)
        )
        run.cost_cents = int(round(total_cost_micros / 10_000))
        await self.session.flush()
        return run

    async def list_by_status(
        self,
        status: str | list[str],
        limit: int = 100,
        offset: int = 0,
    ) -> list[Run]:
        """List runs by status.

        Args:
            status: Status or list of statuses
            limit: Maximum records
            offset: Skip count

        Returns:
            List of runs
        """
        if isinstance(status, str):
            status = [status]

        stmt = (
            select(Run)
            .where(Run.status.in_(status))
            .order_by(Run.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_project(
        self,
        project_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Run]:
        """List runs for a project.

        Args:
            project_id: Project ID
            limit: Maximum records
            offset: Skip count

        Returns:
            List of runs
        """
        stmt = (
            select(Run)
            .where(Run.project_id == project_id)
            .order_by(Run.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_recent(
        self,
        run_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Run]:
        """List recent runs.

        Args:
            run_type: Optional type filter
            limit: Maximum records
            offset: Skip count

        Returns:
            List of runs
        """
        conditions = []
        if run_type:
            conditions.append(Run.run_type == run_type)

        stmt = select(Run)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(Run.created_at.desc()).limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class RunEventRepository(BaseRepository[RunEvent]):
    """Repository for RunEvent operations."""

    model = RunEvent

    async def append_event(
        self,
        run_id: UUID,
        event_type: str,
        payload: dict,
        duration_ms: int | None = None,
    ) -> RunEvent:
        """Append an event to the run ledger.

        Args:
            run_id: Run ID
            event_type: Event type
            payload: Event payload
            duration_ms: Duration in milliseconds

        Returns:
            Created event
        """
        # Get next sequence number
        sequence_num = await self._get_next_sequence(run_id)

        event = RunEvent(
            run_id=run_id,
            event_type=event_type,
            payload=payload,
            duration_ms=duration_ms,
            sequence_num=sequence_num,
            timestamp=utc_now(),
        )
        self.session.add(event)
        await self.session.flush()
        return event

    async def get_events_for_run(
        self,
        run_id: UUID,
        event_types: list[str] | None = None,
        since_sequence: int | None = None,
        limit: int = 1000,
    ) -> list[RunEvent]:
        """Get events for a run.

        Args:
            run_id: Run ID
            event_types: Optional filter by event types
            since_sequence: Get events after this sequence number
            limit: Maximum records

        Returns:
            List of events
        """
        conditions = [RunEvent.run_id == run_id]

        if event_types:
            conditions.append(RunEvent.event_type.in_(event_types))
        if since_sequence is not None:
            conditions.append(RunEvent.sequence_num > since_sequence)

        stmt = (
            select(RunEvent).where(and_(*conditions)).order_by(RunEvent.sequence_num).limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_checkpoint(self, run_id: UUID) -> RunEvent | None:
        """Get the most recent checkpoint event.

        Args:
            run_id: Run ID

        Returns:
            Checkpoint event or None
        """
        stmt = (
            select(RunEvent)
            .where(
                and_(
                    RunEvent.run_id == run_id,
                    RunEvent.event_type == "checkpoint",
                )
            )
            .order_by(RunEvent.sequence_num.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_run(self, run_id: UUID) -> int:
        """Count events for a run.

        Args:
            run_id: Run ID

        Returns:
            Event count
        """
        stmt = select(func.count()).select_from(RunEvent).where(RunEvent.run_id == run_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def _get_next_sequence(self, run_id: UUID) -> int:
        """Get the next sequence number for a run.

        Args:
            run_id: Run ID

        Returns:
            Next sequence number
        """
        stmt = select(func.coalesce(func.max(RunEvent.sequence_num), 0)).where(
            RunEvent.run_id == run_id
        )
        result = await self.session.execute(stmt)
        current_max = result.scalar() or 0
        return current_max + 1
