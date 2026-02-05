"""Unit tests for RunService — state machine transitions and validation.

Mocks the repository layer to test pure service logic without a database.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from intelli.core.exceptions import NotFoundError, ValidationError
from intelli.db.models.runs import RunStatus
from intelli.services.runs.run_service import RunService

pytestmark = pytest.mark.unit


def _make_run(status: str = RunStatus.PENDING.value, run_id=None):
    """Create a mock Run object."""
    run = MagicMock()
    run.id = run_id or uuid4()
    run.status = status
    run.run_type = "agent_chat"
    run.config = {}
    return run


class TestCreateRun:
    @pytest.mark.asyncio
    async def test_creates_run_via_repo(self):
        session = AsyncMock()
        service = RunService(session)
        expected_run = _make_run()
        service.repo.create_run = AsyncMock(return_value=expected_run)

        run = await service.create_run(run_type="agent_chat", name="Test")
        assert run is expected_run
        service.repo.create_run.assert_awaited_once()


class TestGetRun:
    @pytest.mark.asyncio
    async def test_returns_run_when_found(self):
        session = AsyncMock()
        service = RunService(session)
        expected_run = _make_run()
        service.repo.get_by_id = AsyncMock(return_value=expected_run)

        run = await service.get_run(expected_run.id)
        assert run is expected_run

    @pytest.mark.asyncio
    async def test_raises_not_found_when_missing(self):
        session = AsyncMock()
        service = RunService(session)
        service.repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await service.get_run(uuid4())


class TestStartRun:
    @pytest.mark.asyncio
    async def test_starts_pending_run(self):
        session = AsyncMock()
        service = RunService(session)
        run = _make_run(RunStatus.PENDING.value)
        service.repo.get_by_id = AsyncMock(return_value=run)
        service.repo.start = AsyncMock(return_value=run)
        service.ledger.log_event = AsyncMock()

        await service.start_run(run.id)
        service.repo.start.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_rejects_non_pending_run(self):
        session = AsyncMock()
        service = RunService(session)
        run = _make_run(RunStatus.RUNNING.value)
        service.repo.get_by_id = AsyncMock(return_value=run)

        with pytest.raises(ValidationError):
            await service.start_run(run.id)


class TestPauseRun:
    @pytest.mark.asyncio
    async def test_pauses_running_run(self):
        session = AsyncMock()
        service = RunService(session)
        run = _make_run(RunStatus.RUNNING.value)
        service.repo.get_by_id = AsyncMock(return_value=run)
        service.repo.pause = AsyncMock(return_value=run)
        service.ledger.log_event = AsyncMock()

        await service.pause_run(run.id)
        service.repo.pause.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_rejects_non_running_run(self):
        session = AsyncMock()
        service = RunService(session)
        run = _make_run(RunStatus.PENDING.value)
        service.repo.get_by_id = AsyncMock(return_value=run)

        with pytest.raises(ValidationError):
            await service.pause_run(run.id)


class TestResumeRun:
    @pytest.mark.asyncio
    async def test_resumes_paused_run(self):
        session = AsyncMock()
        service = RunService(session)
        run = _make_run(RunStatus.PAUSED.value)
        service.repo.get_by_id = AsyncMock(return_value=run)
        service.repo.resume = AsyncMock(return_value=run)
        service.ledger.log_event = AsyncMock()

        await service.resume_run(run.id)
        service.repo.resume.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_rejects_non_paused_run(self):
        session = AsyncMock()
        service = RunService(session)
        run = _make_run(RunStatus.RUNNING.value)
        service.repo.get_by_id = AsyncMock(return_value=run)

        with pytest.raises(ValidationError):
            await service.resume_run(run.id)


class TestCompleteRun:
    @pytest.mark.asyncio
    async def test_completes_running_run(self):
        session = AsyncMock()
        service = RunService(session)
        run = _make_run(RunStatus.RUNNING.value)
        service.repo.get_by_id = AsyncMock(return_value=run)
        service.repo.complete = AsyncMock(return_value=run)
        service.ledger.log_event = AsyncMock()

        await service.complete_run(run.id, result={"ok": True})
        service.repo.complete.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_rejects_pending_run(self):
        session = AsyncMock()
        service = RunService(session)
        run = _make_run(RunStatus.PENDING.value)
        service.repo.get_by_id = AsyncMock(return_value=run)

        with pytest.raises(ValidationError):
            await service.complete_run(run.id)


class TestFailRun:
    @pytest.mark.asyncio
    async def test_fails_running_run(self):
        session = AsyncMock()
        service = RunService(session)
        run = _make_run(RunStatus.RUNNING.value)
        service.repo.get_by_id = AsyncMock(return_value=run)
        service.repo.fail = AsyncMock(return_value=run)
        service.ledger.log_event = AsyncMock()

        await service.fail_run(run.id, error={"type": "TestError"})
        service.repo.fail.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_rejects_completed_run(self):
        session = AsyncMock()
        service = RunService(session)
        run = _make_run(RunStatus.COMPLETED.value)
        service.repo.get_by_id = AsyncMock(return_value=run)

        with pytest.raises(ValidationError):
            await service.fail_run(run.id, error={"type": "Err"})

    @pytest.mark.asyncio
    async def test_rejects_failed_run(self):
        session = AsyncMock()
        service = RunService(session)
        run = _make_run(RunStatus.FAILED.value)
        service.repo.get_by_id = AsyncMock(return_value=run)

        with pytest.raises(ValidationError):
            await service.fail_run(run.id, error={"type": "Err"})


class TestCancelRun:
    @pytest.mark.asyncio
    async def test_cancels_running_run(self):
        session = AsyncMock()
        service = RunService(session)
        run = _make_run(RunStatus.RUNNING.value)
        service.repo.get_by_id = AsyncMock(return_value=run)
        service.repo.cancel = AsyncMock(return_value=run)
        service.ledger.log_event = AsyncMock()

        await service.cancel_run(run.id)
        service.repo.cancel.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_rejects_completed_run(self):
        session = AsyncMock()
        service = RunService(session)
        run = _make_run(RunStatus.COMPLETED.value)
        service.repo.get_by_id = AsyncMock(return_value=run)

        with pytest.raises(ValidationError):
            await service.cancel_run(run.id)


class TestListRuns:
    @pytest.mark.asyncio
    async def test_list_by_project(self):
        session = AsyncMock()
        service = RunService(session)
        service.repo.list_by_project = AsyncMock(return_value=[])

        project_id = uuid4()
        await service.list_runs(project_id=project_id)
        service.repo.list_by_project.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_list_by_status(self):
        session = AsyncMock()
        service = RunService(session)
        service.repo.list_by_status = AsyncMock(return_value=[])

        await service.list_runs(status="running")
        service.repo.list_by_status.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_list_recent_default(self):
        session = AsyncMock()
        service = RunService(session)
        service.repo.list_recent = AsyncMock(return_value=[])

        await service.list_runs()
        service.repo.list_recent.assert_awaited_once()
