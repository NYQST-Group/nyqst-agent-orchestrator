"""MCP tools for run and ledger operations.

These tools enable agents to create runs, manage lifecycle, and log events
to the append-only run ledger for full reproducibility and auditability.
"""

import json
from typing import Any
from uuid import UUID

from mcp.server import Server
from mcp.types import Tool, TextContent

from intelli.db.engine import AsyncSessionLocal
from intelli.services.runs.run_service import RunService
from intelli.services.runs.ledger_service import LedgerService


# Tool definitions
RUN_TOOLS = [
    Tool(
        name="create_run",
        description="Create a new run (execution instance). Runs track agentic work with full provenance.",
        inputSchema={
            "type": "object",
            "properties": {
                "run_type": {
                    "type": "string",
                    "description": "Type of run (e.g., 'document_parse', 'research', 'analysis')",
                },
                "name": {
                    "type": "string",
                    "description": "Human-readable name for the run",
                },
                "config": {
                    "type": "object",
                    "description": "Run configuration parameters",
                },
                "input_manifest_sha256": {
                    "type": "string",
                    "description": "Input manifest SHA-256 (pins inputs for provenance)",
                },
            },
            "required": ["run_type"],
        },
    ),
    Tool(
        name="start_run",
        description="Start a pending run. Changes status from 'pending' to 'running'.",
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "Run UUID",
                },
            },
            "required": ["run_id"],
        },
    ),
    Tool(
        name="complete_run",
        description="Mark a run as completed with optional result and output manifest.",
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "Run UUID",
                },
                "result": {
                    "type": "object",
                    "description": "Run result data",
                },
                "output_manifest_sha256": {
                    "type": "string",
                    "description": "Output manifest SHA-256",
                },
            },
            "required": ["run_id"],
        },
    ),
    Tool(
        name="fail_run",
        description="Mark a run as failed with error details.",
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "Run UUID",
                },
                "error": {
                    "type": "object",
                    "description": "Error details",
                    "properties": {
                        "type": {"type": "string"},
                        "message": {"type": "string"},
                        "details": {"type": "object"},
                    },
                    "required": ["type", "message"],
                },
            },
            "required": ["run_id", "error"],
        },
    ),
    Tool(
        name="get_run",
        description="Get run details by ID.",
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "Run UUID",
                },
            },
            "required": ["run_id"],
        },
    ),
    Tool(
        name="list_runs",
        description="List runs with optional filters.",
        inputSchema={
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["pending", "running", "paused", "completed", "failed", "cancelled"],
                    "description": "Filter by status",
                },
                "run_type": {
                    "type": "string",
                    "description": "Filter by run type",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum runs to return",
                    "default": 50,
                },
            },
        },
    ),
    Tool(
        name="log_step",
        description="Log a step event (start or complete) to the run ledger.",
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "Run UUID",
                },
                "step_name": {
                    "type": "string",
                    "description": "Name of the step",
                },
                "event": {
                    "type": "string",
                    "enum": ["start", "complete"],
                    "description": "Whether step is starting or completing",
                },
                "data": {
                    "type": "object",
                    "description": "Input data (for start) or output data (for complete)",
                },
                "duration_ms": {
                    "type": "integer",
                    "description": "Duration in milliseconds (for complete)",
                },
                "success": {
                    "type": "boolean",
                    "description": "Whether step succeeded (for complete)",
                    "default": True,
                },
            },
            "required": ["run_id", "step_name", "event"],
        },
    ),
    Tool(
        name="log_tool_call",
        description="Log a tool call to the run ledger.",
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "Run UUID",
                },
                "tool_name": {
                    "type": "string",
                    "description": "Name of the tool",
                },
                "event": {
                    "type": "string",
                    "enum": ["start", "complete"],
                    "description": "Whether call is starting or completing",
                },
                "arguments": {
                    "type": "object",
                    "description": "Tool arguments (for start)",
                },
                "result": {
                    "type": "object",
                    "description": "Tool result (for complete)",
                },
                "duration_ms": {
                    "type": "integer",
                    "description": "Duration in milliseconds (for complete)",
                },
            },
            "required": ["run_id", "tool_name", "event"],
        },
    ),
    Tool(
        name="checkpoint",
        description="Save a checkpoint for run resumption.",
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "Run UUID",
                },
                "state": {
                    "type": "object",
                    "description": "Serialized state to save",
                },
                "checkpoint_id": {
                    "type": "string",
                    "description": "Optional checkpoint identifier",
                },
            },
            "required": ["run_id", "state"],
        },
    ),
    Tool(
        name="get_latest_checkpoint",
        description="Get the most recent checkpoint for a run (for resumption).",
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "Run UUID",
                },
            },
            "required": ["run_id"],
        },
    ),
    Tool(
        name="get_run_events",
        description="Get events from the run ledger.",
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "Run UUID",
                },
                "event_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by event types",
                },
                "since_sequence": {
                    "type": "integer",
                    "description": "Get events after this sequence number",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum events to return",
                    "default": 100,
                },
            },
            "required": ["run_id"],
        },
    ),
]


def register(server: Server) -> None:
    """Register run tools with the MCP server."""

    # Note: Tools are registered via the substrate_tools module which handles
    # the list_tools and call_tool decorators. This module provides the tool
    # definitions and handlers that get merged in.
    pass


async def handle_run_tool(session: Any, name: str, arguments: dict[str, Any]) -> dict:
    """Handle a run tool call."""

    run_service = RunService(session)
    ledger_service = LedgerService(session)

    if name == "create_run":
        run = await run_service.create_run(
            run_type=arguments["run_type"],
            name=arguments.get("name"),
            config=arguments.get("config"),
            input_manifest_sha256=arguments.get("input_manifest_sha256"),
        )
        return {
            "run_id": str(run.id),
            "run_type": run.run_type,
            "status": run.status,
            "created_at": run.created_at.isoformat(),
        }

    elif name == "start_run":
        run = await run_service.start_run(UUID(arguments["run_id"]))
        return {
            "run_id": str(run.id),
            "status": run.status,
            "started_at": run.started_at.isoformat() if run.started_at else None,
        }

    elif name == "complete_run":
        run = await run_service.complete_run(
            run_id=UUID(arguments["run_id"]),
            result=arguments.get("result"),
            output_manifest_sha256=arguments.get("output_manifest_sha256"),
        )
        return {
            "run_id": str(run.id),
            "status": run.status,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        }

    elif name == "fail_run":
        run = await run_service.fail_run(
            run_id=UUID(arguments["run_id"]),
            error=arguments["error"],
        )
        return {
            "run_id": str(run.id),
            "status": run.status,
            "error": run.error,
        }

    elif name == "get_run":
        run = await run_service.get_run(UUID(arguments["run_id"]))
        return {
            "run_id": str(run.id),
            "run_type": run.run_type,
            "name": run.name,
            "status": run.status,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            "input_manifest_sha256": run.input_manifest_sha256,
            "output_manifest_sha256": run.output_manifest_sha256,
            "config": run.config,
            "result": run.result,
            "error": run.error,
        }

    elif name == "list_runs":
        runs = await run_service.list_runs(
            status=arguments.get("status"),
            run_type=arguments.get("run_type"),
            limit=arguments.get("limit", 50),
        )
        return {
            "runs": [
                {
                    "run_id": str(r.id),
                    "run_type": r.run_type,
                    "name": r.name,
                    "status": r.status,
                    "created_at": r.created_at.isoformat(),
                }
                for r in runs
            ]
        }

    elif name == "log_step":
        run_id = UUID(arguments["run_id"])
        if arguments["event"] == "start":
            event = await ledger_service.log_step_start(
                run_id=run_id,
                step_name=arguments["step_name"],
                input_data=arguments.get("data"),
            )
        else:
            event = await ledger_service.log_step_complete(
                run_id=run_id,
                step_name=arguments["step_name"],
                output_data=arguments.get("data"),
                duration_ms=arguments.get("duration_ms"),
                success=arguments.get("success", True),
            )
        return {"event_id": event.id, "sequence_num": event.sequence_num}

    elif name == "log_tool_call":
        run_id = UUID(arguments["run_id"])
        if arguments["event"] == "start":
            event = await ledger_service.log_tool_call_start(
                run_id=run_id,
                tool_name=arguments["tool_name"],
                arguments=arguments.get("arguments", {}),
            )
        else:
            event = await ledger_service.log_tool_call_complete(
                run_id=run_id,
                tool_name=arguments["tool_name"],
                result=arguments.get("result"),
                duration_ms=arguments.get("duration_ms"),
            )
        return {"event_id": event.id, "sequence_num": event.sequence_num}

    elif name == "checkpoint":
        event = await ledger_service.log_checkpoint(
            run_id=UUID(arguments["run_id"]),
            state=arguments["state"],
            checkpoint_id=arguments.get("checkpoint_id"),
        )
        return {"event_id": event.id, "sequence_num": event.sequence_num}

    elif name == "get_latest_checkpoint":
        event = await ledger_service.get_latest_checkpoint(UUID(arguments["run_id"]))
        if not event:
            return {"has_checkpoint": False}
        return {
            "has_checkpoint": True,
            "event_id": event.id,
            "sequence_num": event.sequence_num,
            "state": event.payload.get("state"),
            "checkpoint_id": event.payload.get("checkpoint_id"),
            "timestamp": event.timestamp.isoformat(),
        }

    elif name == "get_run_events":
        events = await ledger_service.get_events(
            run_id=UUID(arguments["run_id"]),
            event_types=arguments.get("event_types"),
            since_sequence=arguments.get("since_sequence"),
            limit=arguments.get("limit", 100),
        )
        return {
            "events": [
                {
                    "event_id": e.id,
                    "sequence_num": e.sequence_num,
                    "event_type": e.event_type,
                    "payload": e.payload,
                    "timestamp": e.timestamp.isoformat(),
                    "duration_ms": e.duration_ms,
                }
                for e in events
            ]
        }

    else:
        return {"error": f"Unknown tool: {name}"}
