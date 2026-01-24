"""Service for run operations."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from intelli.core.exceptions import NotFoundError, ValidationError
from intelli.db.models.runs import Run, RunStatus
from intelli.repositories.runs import RunRepository
from intelli.services.runs.ledger_service import LedgerService


class RunService:
    """Service for run lifecycle management.

    Handles run creation, status transitions, and completion.
    """

    def __init__(self, session: AsyncSession):
        """Initialize run service.

        Args:
            session: Database session
        """
        self.repo = RunRepository(session)
        self.ledger = LedgerService(session)

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
            parent_run_id: Parent run ID
            created_by: Creator principal ID

        Returns:
            Created run
        """
        run = await self.repo.create_run(
            run_type=run_type,
            name=name,
            config=config,
            input_manifest_sha256=input_manifest_sha256,
            project_id=project_id,
            session_id=session_id,
            parent_run_id=parent_run_id,
            created_by=created_by,
        )

        return run

    async def get_run(self, run_id: UUID) -> Run:
        """Get run by ID.

        Args:
            run_id: Run UUID

        Returns:
            Run model

        Raises:
            NotFoundError: If run doesn't exist
        """
        run = await self.repo.get_by_id(run_id)
        if not run:
            raise NotFoundError(resource_type="run", identifier=str(run_id))
        return run

    async def start_run(self, run_id: UUID) -> Run:
        """Start a pending run.

        Args:
            run_id: Run UUID

        Returns:
            Updated run

        Raises:
            NotFoundError: If run doesn't exist
            ValidationError: If run is not in pending state
        """
        run = await self.get_run(run_id)

        if run.status != RunStatus.PENDING.value:
            raise ValidationError(
                f"Cannot start run in state: {run.status}",
                field="status",
            )

        run = await self.repo.start(run)

        # Log event
        await self.ledger.log_event(
            run_id=run_id,
            event_type="run_started",
            payload={"run_type": run.run_type, "config": run.config},
        )

        return run

    async def pause_run(self, run_id: UUID) -> Run:
        """Pause a running run.

        Args:
            run_id: Run UUID

        Returns:
            Updated run

        Raises:
            NotFoundError: If run doesn't exist
            ValidationError: If run is not running
        """
        run = await self.get_run(run_id)

        if run.status != RunStatus.RUNNING.value:
            raise ValidationError(
                f"Cannot pause run in state: {run.status}",
                field="status",
            )

        run = await self.repo.pause(run)

        # Log event
        await self.ledger.log_event(
            run_id=run_id,
            event_type="run_paused",
            payload={},
        )

        return run

    async def resume_run(self, run_id: UUID) -> Run:
        """Resume a paused run.

        Args:
            run_id: Run UUID

        Returns:
            Updated run

        Raises:
            NotFoundError: If run doesn't exist
            ValidationError: If run is not paused
        """
        run = await self.get_run(run_id)

        if run.status != RunStatus.PAUSED.value:
            raise ValidationError(
                f"Cannot resume run in state: {run.status}",
                field="status",
            )

        run = await self.repo.resume(run)

        # Log event
        await self.ledger.log_event(
            run_id=run_id,
            event_type="run_resumed",
            payload={},
        )

        return run

    async def complete_run(
        self,
        run_id: UUID,
        result: dict | None = None,
        output_manifest_sha256: str | None = None,
    ) -> Run:
        """Mark run as completed.

        Args:
            run_id: Run UUID
            result: Run result
            output_manifest_sha256: Output manifest

        Returns:
            Updated run

        Raises:
            NotFoundError: If run doesn't exist
            ValidationError: If run is not in a completable state
        """
        run = await self.get_run(run_id)

        if run.status not in [RunStatus.RUNNING.value, RunStatus.PAUSED.value]:
            raise ValidationError(
                f"Cannot complete run in state: {run.status}",
                field="status",
            )

        run = await self.repo.complete(run, result, output_manifest_sha256)

        # Log event
        await self.ledger.log_event(
            run_id=run_id,
            event_type="run_completed",
            payload={
                "result": result,
                "output_manifest_sha256": output_manifest_sha256,
            },
        )

        return run

    async def fail_run(
        self,
        run_id: UUID,
        error: dict,
    ) -> Run:
        """Mark run as failed.

        Args:
            run_id: Run UUID
            error: Error details

        Returns:
            Updated run

        Raises:
            NotFoundError: If run doesn't exist
            ValidationError: If run is already completed
        """
        run = await self.get_run(run_id)

        if run.status in [RunStatus.COMPLETED.value, RunStatus.FAILED.value, RunStatus.CANCELLED.value]:
            raise ValidationError(
                f"Cannot fail run in state: {run.status}",
                field="status",
            )

        run = await self.repo.fail(run, error)

        # Log event
        await self.ledger.log_event(
            run_id=run_id,
            event_type="run_failed",
            payload={"error": error},
        )

        return run

    async def cancel_run(self, run_id: UUID) -> Run:
        """Cancel a run.

        Args:
            run_id: Run UUID

        Returns:
            Updated run

        Raises:
            NotFoundError: If run doesn't exist
            ValidationError: If run is already completed
        """
        run = await self.get_run(run_id)

        if run.status in [RunStatus.COMPLETED.value, RunStatus.FAILED.value, RunStatus.CANCELLED.value]:
            raise ValidationError(
                f"Cannot cancel run in state: {run.status}",
                field="status",
            )

        run = await self.repo.cancel(run)

        # Log event
        await self.ledger.log_event(
            run_id=run_id,
            event_type="run_cancelled",
            payload={},
        )

        return run

    async def list_runs(
        self,
        status: str | list[str] | None = None,
        run_type: str | None = None,
        project_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Run]:
        """List runs with optional filters.

        Args:
            status: Filter by status
            run_type: Filter by type
            project_id: Filter by project
            limit: Maximum records
            offset: Skip count

        Returns:
            List of runs
        """
        if project_id:
            return await self.repo.list_by_project(project_id, limit, offset)
        if status:
            return await self.repo.list_by_status(status, limit, offset)
        return await self.repo.list_recent(run_type, limit, offset)
