"""Unit tests for run MCP tools."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from intelli.mcp.tools.run_tools import handle_run_tool

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


def _make_run(run_id=None, status="pending", run_type="test_run"):
    """Create a mock Run object."""
    run = MagicMock()
    run.id = run_id or uuid4()
    run.run_type = run_type
    run.name = "Test run"
    run.status = status
    run.created_at = datetime.now()
    run.started_at = datetime.now() if status != "pending" else None
    run.completed_at = datetime.now() if status in ["completed", "failed"] else None
    run.input_manifest_sha256 = None
    run.output_manifest_sha256 = None
    run.config = {}
    run.result = None
    run.error = None
    return run


def _make_event(event_id=None, sequence_num=1):
    """Create a mock LedgerEvent object."""
    event = MagicMock()
    event.id = event_id or uuid4()
    event.sequence_num = sequence_num
    event.event_type = "step_start"
    event.payload = {}
    event.timestamp = datetime.now()
    event.duration_ms = None
    return event


class TestCreateRun:
    async def test_create_run_returns_run_id(self):
        """Test create_run returns run ID and metadata."""
        session = AsyncMock()
        run = _make_run()

        with patch("intelli.mcp.tools.run_tools.RunService") as mock_run_service_cls:
            run_service = mock_run_service_cls.return_value
            run_service.create_run = AsyncMock(return_value=run)

            result = await handle_run_tool(
                session,
                "create_run",
                {
                    "run_type": "document_parse",
                    "name": "Parse document",
                    "config": {"model": "gpt-4"},
                },
            )

            assert result["run_id"] == str(run.id)
            assert result["run_type"] == "test_run"
            assert result["status"] == "pending"
            run_service.create_run.assert_awaited_once()


class TestStartRun:
    async def test_start_run_changes_status(self):
        """Test start_run changes status to running."""
        session = AsyncMock()
        run = _make_run(status="running")

        with patch("intelli.mcp.tools.run_tools.RunService") as mock_run_service_cls:
            run_service = mock_run_service_cls.return_value
            run_service.start_run = AsyncMock(return_value=run)

            result = await handle_run_tool(
                session,
                "start_run",
                {"run_id": str(run.id)},
            )

            assert result["run_id"] == str(run.id)
            assert result["status"] == "running"
            assert result["started_at"] is not None
            run_service.start_run.assert_awaited_once()


class TestCompleteRun:
    async def test_complete_run_records_result(self):
        """Test complete_run records result and output manifest."""
        session = AsyncMock()
        run = _make_run(status="completed")
        run.result = {"success": True}
        run.output_manifest_sha256 = "output_sha"

        with patch("intelli.mcp.tools.run_tools.RunService") as mock_run_service_cls:
            run_service = mock_run_service_cls.return_value
            run_service.complete_run = AsyncMock(return_value=run)

            result = await handle_run_tool(
                session,
                "complete_run",
                {
                    "run_id": str(run.id),
                    "result": {"success": True},
                    "output_manifest_sha256": "output_sha",
                },
            )

            assert result["run_id"] == str(run.id)
            assert result["status"] == "completed"
            assert result["completed_at"] is not None
            run_service.complete_run.assert_awaited_once()


class TestFailRun:
    async def test_fail_run_records_error(self):
        """Test fail_run records error details."""
        session = AsyncMock()
        run = _make_run(status="failed")
        run.error = {"type": "ValidationError", "message": "Invalid input"}

        with patch("intelli.mcp.tools.run_tools.RunService") as mock_run_service_cls:
            run_service = mock_run_service_cls.return_value
            run_service.fail_run = AsyncMock(return_value=run)

            result = await handle_run_tool(
                session,
                "fail_run",
                {
                    "run_id": str(run.id),
                    "error": {"type": "ValidationError", "message": "Invalid input"},
                },
            )

            assert result["run_id"] == str(run.id)
            assert result["status"] == "failed"
            assert result["error"]["type"] == "ValidationError"
            run_service.fail_run.assert_awaited_once()


class TestGetRun:
    async def test_get_run_returns_full_details(self):
        """Test get_run returns complete run information."""
        session = AsyncMock()
        run = _make_run()

        with patch("intelli.mcp.tools.run_tools.RunService") as mock_run_service_cls:
            run_service = mock_run_service_cls.return_value
            run_service.get_run = AsyncMock(return_value=run)

            result = await handle_run_tool(
                session,
                "get_run",
                {"run_id": str(run.id)},
            )

            assert result["run_id"] == str(run.id)
            assert result["run_type"] == "test_run"
            assert result["name"] == "Test run"
            assert result["status"] == "pending"
            assert "config" in result
            assert "result" in result
            run_service.get_run.assert_awaited_once()


class TestListRuns:
    async def test_list_runs_with_filters(self):
        """Test list_runs applies filters."""
        session = AsyncMock()
        runs = [_make_run() for _ in range(3)]

        with patch("intelli.mcp.tools.run_tools.RunService") as mock_run_service_cls:
            run_service = mock_run_service_cls.return_value
            run_service.list_runs = AsyncMock(return_value=runs)

            result = await handle_run_tool(
                session,
                "list_runs",
                {"status": "running", "run_type": "document_parse", "limit": 10},
            )

            assert "runs" in result
            assert len(result["runs"]) == 3
            run_service.list_runs.assert_awaited_once_with(
                status="running",
                run_type="document_parse",
                limit=10,
            )


class TestLogStep:
    async def test_log_step_start_delegates_to_ledger(self):
        """Test log_step with event='start' logs step start."""
        session = AsyncMock()
        run_id = uuid4()
        event = _make_event()

        with patch("intelli.mcp.tools.run_tools.LedgerService") as mock_ledger_service_cls:
            ledger_service = mock_ledger_service_cls.return_value
            ledger_service.log_step_start = AsyncMock(return_value=event)

            result = await handle_run_tool(
                session,
                "log_step",
                {
                    "run_id": str(run_id),
                    "step_name": "parse_document",
                    "event": "start",
                    "data": {"input": "test.pdf"},
                },
            )

            assert result["event_id"] == event.id
            assert result["sequence_num"] == 1
            ledger_service.log_step_start.assert_awaited_once_with(
                run_id=run_id,
                step_name="parse_document",
                input_data={"input": "test.pdf"},
            )

    async def test_log_step_complete(self):
        """Test log_step with event='complete' logs step completion."""
        session = AsyncMock()
        run_id = uuid4()
        event = _make_event(sequence_num=2)

        with patch("intelli.mcp.tools.run_tools.LedgerService") as mock_ledger_service_cls:
            ledger_service = mock_ledger_service_cls.return_value
            ledger_service.log_step_complete = AsyncMock(return_value=event)

            result = await handle_run_tool(
                session,
                "log_step",
                {
                    "run_id": str(run_id),
                    "step_name": "parse_document",
                    "event": "complete",
                    "data": {"pages": 10},
                    "duration_ms": 1500,
                    "success": True,
                },
            )

            assert result["sequence_num"] == 2
            ledger_service.log_step_complete.assert_awaited_once()


class TestLogToolCall:
    async def test_log_tool_call_start(self):
        """Test log_tool_call with event='start'."""
        session = AsyncMock()
        run_id = uuid4()
        event = _make_event()

        with patch("intelli.mcp.tools.run_tools.LedgerService") as mock_ledger_service_cls:
            ledger_service = mock_ledger_service_cls.return_value
            ledger_service.log_tool_call_start = AsyncMock(return_value=event)

            result = await handle_run_tool(
                session,
                "log_tool_call",
                {
                    "run_id": str(run_id),
                    "tool_name": "resolve_pointer",
                    "event": "start",
                    "arguments": {"namespace": "default", "name": "test"},
                },
            )

            assert result["event_id"] == event.id
            ledger_service.log_tool_call_start.assert_awaited_once()

    async def test_log_tool_call_complete(self):
        """Test log_tool_call with event='complete'."""
        session = AsyncMock()
        run_id = uuid4()
        event = _make_event()

        with patch("intelli.mcp.tools.run_tools.LedgerService") as mock_ledger_service_cls:
            ledger_service = mock_ledger_service_cls.return_value
            ledger_service.log_tool_call_complete = AsyncMock(return_value=event)

            result = await handle_run_tool(
                session,
                "log_tool_call",
                {
                    "run_id": str(run_id),
                    "tool_name": "resolve_pointer",
                    "event": "complete",
                    "result": {"manifest_sha256": "abc123"},
                    "duration_ms": 50,
                },
            )

            assert result["event_id"] == event.id
            ledger_service.log_tool_call_complete.assert_awaited_once()


class TestCheckpoint:
    async def test_checkpoint_saves_state(self):
        """Test checkpoint saves serialized state."""
        session = AsyncMock()
        run_id = uuid4()
        event = _make_event()

        with patch("intelli.mcp.tools.run_tools.LedgerService") as mock_ledger_service_cls:
            ledger_service = mock_ledger_service_cls.return_value
            ledger_service.log_checkpoint = AsyncMock(return_value=event)

            result = await handle_run_tool(
                session,
                "checkpoint",
                {
                    "run_id": str(run_id),
                    "state": {"step": 3, "context": "parsing"},
                    "checkpoint_id": "checkpoint_1",
                },
            )

            assert result["event_id"] == event.id
            ledger_service.log_checkpoint.assert_awaited_once_with(
                run_id=run_id,
                state={"step": 3, "context": "parsing"},
                checkpoint_id="checkpoint_1",
            )


class TestGetLatestCheckpoint:
    async def test_get_latest_checkpoint_found(self):
        """Test get_latest_checkpoint when checkpoint exists."""
        session = AsyncMock()
        run_id = uuid4()
        event = _make_event()
        event.payload = {
            "state": {"step": 3, "context": "parsing"},
            "checkpoint_id": "checkpoint_1",
        }

        with patch("intelli.mcp.tools.run_tools.LedgerService") as mock_ledger_service_cls:
            ledger_service = mock_ledger_service_cls.return_value
            ledger_service.get_latest_checkpoint = AsyncMock(return_value=event)

            result = await handle_run_tool(
                session,
                "get_latest_checkpoint",
                {"run_id": str(run_id)},
            )

            assert result["has_checkpoint"] is True
            assert result["event_id"] == event.id
            assert result["state"] == {"step": 3, "context": "parsing"}
            assert result["checkpoint_id"] == "checkpoint_1"

    async def test_get_latest_checkpoint_not_found(self):
        """Test get_latest_checkpoint when no checkpoint exists."""
        session = AsyncMock()
        run_id = uuid4()

        with patch("intelli.mcp.tools.run_tools.LedgerService") as mock_ledger_service_cls:
            ledger_service = mock_ledger_service_cls.return_value
            ledger_service.get_latest_checkpoint = AsyncMock(return_value=None)

            result = await handle_run_tool(
                session,
                "get_latest_checkpoint",
                {"run_id": str(run_id)},
            )

            assert result["has_checkpoint"] is False


class TestGetRunEvents:
    async def test_get_run_events_returns_event_list(self):
        """Test get_run_events returns filtered events."""
        session = AsyncMock()
        run_id = uuid4()
        events = [_make_event(sequence_num=i) for i in range(1, 4)]

        with patch("intelli.mcp.tools.run_tools.LedgerService") as mock_ledger_service_cls:
            ledger_service = mock_ledger_service_cls.return_value
            ledger_service.get_events = AsyncMock(return_value=events)

            result = await handle_run_tool(
                session,
                "get_run_events",
                {
                    "run_id": str(run_id),
                    "event_types": ["step_start", "step_complete"],
                    "since_sequence": 0,
                    "limit": 100,
                },
            )

            assert "events" in result
            assert len(result["events"]) == 3
            assert result["events"][0]["sequence_num"] == 1
            ledger_service.get_events.assert_awaited_once()


class TestUnknownTool:
    async def test_unknown_tool_returns_error(self):
        """Test that unknown tool name returns error."""
        session = AsyncMock()

        result = await handle_run_tool(
            session,
            "nonexistent_tool",
            {},
        )

        assert "error" in result
        assert "Unknown tool" in result["error"]
