"""Unit tests for LedgerService — event logging delegation and payload structure.

Mocks the repository layer to verify correct event types and payloads.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from intelli.services.runs.ledger_service import LedgerService

pytestmark = pytest.mark.unit


def _make_event(event_type="test", payload=None):
    """Create a mock RunEvent."""
    event = MagicMock()
    event.id = 1
    event.run_id = uuid4()
    event.event_type = event_type
    event.payload = payload or {}
    event.timestamp = MagicMock()
    event.timestamp.isoformat.return_value = "2025-01-01T00:00:00"
    event.duration_ms = None
    event.sequence_num = 1
    return event


class TestLogEvent:
    @pytest.mark.asyncio
    async def test_delegates_to_repo(self):
        session = AsyncMock()
        service = LedgerService(session, publish_events=False)
        event = _make_event()
        service.repo.append_event = AsyncMock(return_value=event)

        run_id = uuid4()
        await service.log_event(run_id, "test_event", {"key": "value"})
        service.repo.append_event.assert_awaited_once_with(
            run_id=run_id,
            event_type="test_event",
            payload={"key": "value"},
            duration_ms=None,
        )

    @pytest.mark.asyncio
    async def test_publishes_event_when_enabled(self):
        session = AsyncMock()
        service = LedgerService(session, publish_events=True)
        event = _make_event()
        service.repo.append_event = AsyncMock(return_value=event)
        # Mock the session.execute for pg_notify
        session.execute = AsyncMock()

        await service.log_event(uuid4(), "test", {})
        # pg_notify should have been called
        session.execute.assert_awaited()

    @pytest.mark.asyncio
    async def test_skips_publish_when_disabled(self):
        session = AsyncMock()
        service = LedgerService(session, publish_events=False)
        event = _make_event()
        service.repo.append_event = AsyncMock(return_value=event)

        await service.log_event(uuid4(), "test", {})
        # session.execute should NOT have been called for pg_notify
        session.execute.assert_not_awaited()


class TestConvenienceMethods:
    @pytest.mark.asyncio
    async def test_log_step_start(self):
        session = AsyncMock()
        service = LedgerService(session, publish_events=False)
        event = _make_event()
        service.repo.append_event = AsyncMock(return_value=event)

        run_id = uuid4()
        await service.log_step_start(run_id, "retrieve", {"query": "test"})
        call_kwargs = service.repo.append_event.call_args.kwargs
        assert call_kwargs["event_type"] == "step_started"
        assert call_kwargs["payload"]["step_name"] == "retrieve"

    @pytest.mark.asyncio
    async def test_log_step_complete(self):
        session = AsyncMock()
        service = LedgerService(session, publish_events=False)
        event = _make_event()
        service.repo.append_event = AsyncMock(return_value=event)

        run_id = uuid4()
        await service.log_step_complete(run_id, "retrieve", {"chunks": 5}, success=True)
        call_kwargs = service.repo.append_event.call_args.kwargs
        assert call_kwargs["event_type"] == "step_completed"
        assert call_kwargs["payload"]["success"] is True

    @pytest.mark.asyncio
    async def test_log_tool_call_start(self):
        session = AsyncMock()
        service = LedgerService(session, publish_events=False)
        event = _make_event()
        service.repo.append_event = AsyncMock(return_value=event)

        run_id = uuid4()
        await service.log_tool_call_start(run_id, "search", {"q": "test"})
        call_kwargs = service.repo.append_event.call_args.kwargs
        assert call_kwargs["event_type"] == "tool_call_started"
        assert call_kwargs["payload"]["tool_name"] == "search"

    @pytest.mark.asyncio
    async def test_log_error(self):
        session = AsyncMock()
        service = LedgerService(session, publish_events=False)
        event = _make_event()
        service.repo.append_event = AsyncMock(return_value=event)

        run_id = uuid4()
        await service.log_error(run_id, "RuntimeError", "boom")
        call_kwargs = service.repo.append_event.call_args.kwargs
        assert call_kwargs["event_type"] == "error"
        assert call_kwargs["payload"]["message"] == "boom"

    @pytest.mark.asyncio
    async def test_log_checkpoint(self):
        session = AsyncMock()
        service = LedgerService(session, publish_events=False)
        event = _make_event()
        service.repo.append_event = AsyncMock(return_value=event)

        run_id = uuid4()
        await service.log_checkpoint(run_id, state={"step": 3}, resumable=True)
        call_kwargs = service.repo.append_event.call_args.kwargs
        assert call_kwargs["event_type"] == "checkpoint"
        assert call_kwargs["payload"]["resumable"] is True


class TestGetEvents:
    @pytest.mark.asyncio
    async def test_delegates_to_repo(self):
        session = AsyncMock()
        service = LedgerService(session, publish_events=False)
        service.repo.get_events_for_run = AsyncMock(return_value=[])

        run_id = uuid4()
        await service.get_events(run_id, event_types=["step_started"])
        service.repo.get_events_for_run.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_count_events(self):
        session = AsyncMock()
        service = LedgerService(session, publish_events=False)
        service.repo.count_by_run = AsyncMock(return_value=42)

        count = await service.count_events(uuid4())
        assert count == 42
