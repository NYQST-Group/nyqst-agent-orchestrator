---
document_id: EVENT-CONTRACT-V1
version: 1
date: 2026-03-14
status: locked
phase: Phase 0 deliverable
gap: GAP-079
---

# Event Contract v1 — NYQST DocuIntelli SSE Streaming Protocol

> **Purpose**: Formal specification of all SSE event types emitted by the NYQST DocuIntelli backend. This is the authoritative contract that BL-001 (research orchestrator) must produce and BL-002 (RunEvent schema extensions) must persist. Frontend SSE consumers must conform to this contract.
>
> **Source**: Derived from `streaming-events-extract.md` (22 confirmed Superagent event types) plus NYQST-proposed extensions. Grounded in direct Superagent JS bundle analysis.
>
> **LangGraph binding**: Section 3 specifies which LangGraph lifecycle hooks map to which SSE event types.

---

## 1. Transport Layer

All events are emitted via the existing PostgreSQL LISTEN/NOTIFY SSE endpoint:

```
GET /api/v1/streams/runs/{run_id}
Content-Type: text/event-stream
```

Each event is a JSON-encoded SSE `data:` line:

```
data: {"type": "stream_start", "chat_id": "...", ...}

data: {"type": "message_delta", "delta": "Hello"}

data: {"type": "done"}

```

The NDJSON envelope is **not used** — NYQST uses the SSE `data:` field directly (per DEC-020, DEC-021).

---

## 2. Complete Event Type Registry

**Total: 22 confirmed production events (from Superagent) + 2 NYQST additions = 24 events**

### 2.1 Lifecycle Events

| Event Type | When Emitted | Required Fields | Optional Fields |
|---|---|---|---|
| `stream_start` | Stream begins | `type`, `chat_id`, `creator_user_id`, `user_chat_message_id`, `workspace_id` | — |
| `heartbeat` | Every 20–30s (keepalive watchdog) | `type` | — |
| `done` | Stream terminal (final event) | `type` | `has_async_entities_pending: bool`, `message: Message` |
| `ERROR` | System/LLM failure | `type`, `error_type: str`, `error_message: str` | — |

**Note on `done`**: When `has_async_entities_pending: true`, the frontend must poll or await a subsequent `references_found` event (emitted by the arq background job after entity creation completes).

### 2.2 Text Streaming Events

| Event Type | When Emitted | Required Fields | Optional Fields |
|---|---|---|---|
| `message_delta` | Each token arrival from LLM | `type`, `delta: str` | — |
| `ai_message` | Full message object ready | `type`, `message: Message` | — |
| `message_is_answer` | Message marked as final answer | `type`, `is_answer: bool` | — |
| `chat_title_generated` | Auto-title generation completes | `type`, `title: str` | — |
| `clarification_needed` | Graph paused at interrupt | `type`, `message: Message` | — |
| `update_message_clarification_message` | Clarification flag updated | `type`, `update: {chat_message_id: str, needs_clarification_message: str\|null}` | — |

### 2.3 Planning Events

| Event Type | When Emitted | Required Fields | Optional Fields |
|---|---|---|---|
| `task_update` | Plan task status changes (LOADING/SUCCESS/ERROR) | `type`, `key: str`, `title: str`, `message: str`, `status: "loading"\|"success"\|"error"`, `plan_set: PlanSet` | `metadata: dict` |
| `pending_sources` | Sources queued but not yet fetched | `type`, `pending_sources: PendingSource[]` | — |

### 2.4 Reference Events

| Event Type | When Emitted | Required Fields | Optional Fields |
|---|---|---|---|
| `references_found` | Entity resolution completes | `type`, `references: Entity[]` | — |

### 2.5 Tool Execution Events

| Event Type | When Emitted | Required Fields | Optional Fields |
|---|---|---|---|
| `node_tools_execution_start` | Tool batch begins on a node | `type`, `plan_set_id`, `plan_id`, `node_id`, `tool_ids: str[]`, `total_tools: int`, `timestamp: int` (Unix ms) | — |
| `node_tool_event` | Fine-grained tool lifecycle event | `type`, `event: str`, `node_id`, `plan_id`, `plan_set_id`, `timestamp: int` | `tool_id`, `tool_type`, `metadata: dict` |
| `update_subagent_current_action` | UI status label update ("Searching the web...") | `type`, `current_action: str`, `node_id`, `plan_id`, `plan_set_id`, `timestamp: int` | `tool_id` |

**`node_tool_event` event values** (the `event` field):

| Value | Meaning |
|---|---|
| `tool_called` | Tool invocation dispatched |
| `tool_completed` | Tool returned result |
| `tool_failed` | Tool raised exception |
| `fallback_used` | Primary tool failed; secondary provider tried |
| `all_tools_failed` | All fallback options exhausted |

### 2.6 Report Preview Events

| Event Type | When Emitted | Required Fields | Optional Fields |
|---|---|---|---|
| `node_report_preview_start` | Report generation begins for a section or full report | `type`, `preview_id`, `report_title`, `report_user_query`, `final_report: bool`, `node_id`, `plan_id`, `plan_set_id`, `entity: Entity`, `timestamp: int`, `workspace_id` | `section_id`, `tool_id` |
| `node_report_preview_delta` | Incremental GML content chunk during generation | `type`, `preview_id`, `delta: str`, `node_id`, `plan_id`, `plan_set_id` | `section_id` |
| `node_report_preview_done` | Complete GML content for a report section or full report | `type`, `preview_id`, `content: str` (full GML), `report_title`, `final_report: bool`, `node_id`, `plan_id`, `plan_set_id`, `timestamp: int`, `workspace_id` | `entity: Entity`, `section_id`, `tool_id` |

**`content` field**: The full GML string wrapped in `<answer>...</answer>`. Frontend must extract using the pre-processing step defined in GML-RENDERING-ANALYSIS Section 7.

### 2.7 Browser Automation Events (v1.5, deferred)

| Event Type | When Emitted | Required Fields |
|---|---|---|
| `browser_use_start` | Browser session opens | `type`, `browser_session_id`, `browser_stream_url`, `timestamp: int` |
| `browser_use_stop` | Browser session closes | `type`, `browser_session_id` |
| `browser_use_await_user_input` | Session paused for human input | `type`, `browser_session_id` |

### 2.8 NYQST Additions

| Event Type | When Emitted | Required Fields | Status |
|---|---|---|---|
| `ping` | Every 10s (connection health) | `type`, `timestamp: str` (ISO 8601) | v1 |
| `usage_update` | After each LLM call completes | `type`, `input_tokens: int`, `output_tokens: int`, `total_tokens: int` | v1 |

---

## 3. LangGraph Hook → SSE Event Mapping

This table specifies which LangGraph lifecycle callback maps to which SSE event type and what LangGraph state fields are read for the payload.

| LangGraph Callback | SSE Event Type | LangGraph State Fields Read | Notes |
|---|---|---|---|
| `on_chain_start` (graph entry) | `stream_start` | `configurable.thread_id` (→ `chat_id`), `configurable.user_id`, `configurable.workspace_id` | Emitted once at the start of graph execution |
| `on_chain_start` (planner node) | `task_update` (status=loading, key="planning") | `state.plan_set` | Emitted when planner node begins |
| `on_chain_end` (planner node) | `task_update` (status=success) + `pending_sources` | `state.plan_set`, `state.pending_sources` | Emitted when planner outputs PlanSet |
| `on_chain_start` (worker node) | `task_update` (status=loading, key=task_id) + `update_subagent_current_action` | `state.current_task.id`, `state.current_task.title` | One event per Send() dispatch |
| `on_tool_start` | `node_tools_execution_start` + `node_tool_event` (event="tool_called") | `state.current_task.node_id`, tool name/id | `on_tool_start` fires for each tool call |
| `on_tool_end` | `node_tool_event` (event="tool_completed") | tool output, node context | Includes `metadata` with result summary |
| `on_chat_model_stream` | `message_delta` | `chunk.content` (delta string) | Only emitted for synthesis/generator nodes, not planner/worker nodes |
| `on_chain_end` (worker node) | `task_update` (status=success, key=task_id) + `references_found` | `state.current_task.result`, `state.current_task.citations` | `references_found` includes resolved Entity objects |
| `on_chain_start` (synthesis node) | `task_update` (status=loading, key="synthesis") | `state.plan_set` | |
| `on_chain_start` (generator node) | `node_report_preview_start` | `state.preview_id`, `state.report_title`, `state.run_id` | |
| `on_chat_model_stream` (generator node) | `node_report_preview_delta` | `chunk.content`, `state.preview_id` | Delta streaming of GML content |
| `on_chain_end` (generator node) | `node_report_preview_done` | `state.report_content`, `state.preview_id`, `state.report_entity` | Full GML in `content` field |
| `on_chain_end` (graph exit, success) | `ai_message` + `done` | `state.final_message`, `state.has_async_entities_pending` | |
| `on_chain_end` (graph exit, error) | `ERROR` + `done` | exception details | |

**Implementation approach**: Use `astream_events(v="v2")` from the LangGraph `CompiledGraph`. This yields `RunLogPatch` events. Filter by `event.name` and `event.metadata.langgraph_node` to map to SSE types.

---

## 4. Payload Schemas (Python / Pydantic v2)

### Core Data Models

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any
from datetime import datetime

class Entity(BaseModel):
    entity_type: Literal[
        "WEB_PAGE", "EXTERNAL_API_DATA", "GENERATED_CONTENT",
        "USER_QUERY_PART", "GENERATED_REPORT", "GENERATED_PRESENTATION",
        "INTRA_ENTITY_SEARCH_RESULT", "EXTRACTED_ENTITY", "SEARCH_PLAN",
        "KNOWLEDGE_BASE", "WEBSITE", "GENERATED_DOCUMENT"
    ]
    identifier: str
    title: Optional[str] = None
    description: Optional[str] = None
    file_name: str
    mimetype: str
    workspace_id: str
    stored_entity_id: Optional[str] = None
    content_artifact_id: Optional[str] = None
    content_length: Optional[int] = None
    created_at: Optional[str] = None
    external_url: Optional[str] = None
    citation_identifier: Optional[str] = None  # UUID for GML citation binding

class PlanTask(BaseModel):
    id: str
    title: str
    message: str
    plan_id: str
    status: Literal["LOADING", "SUCCESS", "ERROR"]
    previous_task_id: Optional[str] = None

class Plan(BaseModel):
    id: str
    plan_set_id: str
    title: Optional[str] = None
    summary: Optional[str] = None
    status: Literal["LOADING", "SUCCESS", "ERROR"]
    plan_tasks: dict[str, PlanTask]
    used_sources: Optional[list[str]] = None
    previous_plan_id: Optional[str] = None

class PlanSet(BaseModel):
    chat_id: str
    creator_user_id: str
    user_chat_message_id: str
    workspace_id: str
    plans: dict[str, Plan]
```

### Event Schemas

```python
# Lifecycle
class StreamStart(BaseModel):
    type: Literal["stream_start"]
    chat_id: str
    creator_user_id: str
    user_chat_message_id: str
    workspace_id: str

class Heartbeat(BaseModel):
    type: Literal["heartbeat"]

class DoneEvent(BaseModel):
    type: Literal["done"]
    has_async_entities_pending: Optional[bool] = None

class StreamError(BaseModel):
    type: Literal["ERROR"]
    error_type: str
    error_message: str

# Text streaming
class MessageDelta(BaseModel):
    type: Literal["message_delta"]
    delta: str

class AiMessage(BaseModel):
    type: Literal["ai_message"]
    message: dict

class MessageIsAnswer(BaseModel):
    type: Literal["message_is_answer"]
    is_answer: bool

class ChatTitleGenerated(BaseModel):
    type: Literal["chat_title_generated"]
    title: str

# Planning
class TaskUpdate(BaseModel):
    type: Literal["task_update"]
    key: str
    title: str
    message: str
    status: Literal["loading", "success", "error"]
    plan_set: PlanSet
    metadata: Optional[dict[str, Any]] = None

class PendingSource(BaseModel):
    plan_id: str
    plan_set_id: str
    plan_task_id: str
    title: str
    type: Literal["WEB", "DOCUMENT", "CODING_AGENT"]
    web_domain: Optional[str] = None

class PendingSources(BaseModel):
    type: Literal["pending_sources"]
    pending_sources: list[PendingSource]

# References
class ReferencesFound(BaseModel):
    type: Literal["references_found"]
    references: list[Entity]

# Tool execution
class NodeToolsExecutionStart(BaseModel):
    type: Literal["node_tools_execution_start"]
    plan_set_id: str
    plan_id: str
    node_id: str
    tool_ids: list[str]
    total_tools: int
    timestamp: int  # Unix milliseconds

class NodeToolEvent(BaseModel):
    type: Literal["node_tool_event"]
    event: str
    node_id: str
    plan_id: str
    plan_set_id: str
    tool_id: Optional[str] = None
    tool_type: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    timestamp: int

class UpdateSubagentCurrentAction(BaseModel):
    type: Literal["update_subagent_current_action"]
    current_action: str
    node_id: str
    plan_id: str
    plan_set_id: str
    tool_id: Optional[str] = None
    timestamp: int

# Report preview
class NodeReportPreviewStart(BaseModel):
    type: Literal["node_report_preview_start"]
    preview_id: str
    report_title: str
    report_user_query: str
    final_report: bool
    node_id: str
    plan_id: str
    plan_set_id: str
    entity: Entity
    section_id: Optional[str] = None
    tool_id: Optional[str] = None
    timestamp: int
    workspace_id: str

class NodeReportPreviewDelta(BaseModel):
    type: Literal["node_report_preview_delta"]
    preview_id: str
    delta: str
    node_id: str
    plan_id: str
    plan_set_id: str
    section_id: Optional[str] = None

class NodeReportPreviewDone(BaseModel):
    type: Literal["node_report_preview_done"]
    preview_id: str
    content: str  # full GML string (includes <answer> wrapper)
    report_title: str
    final_report: bool
    node_id: str
    plan_id: str
    plan_set_id: str
    entity: Optional[Entity] = None
    section_id: Optional[str] = None
    tool_id: Optional[str] = None
    timestamp: int
    workspace_id: str

# NYQST additions
class PingEvent(BaseModel):
    type: Literal["ping"]
    timestamp: str  # ISO 8601

class UsageUpdate(BaseModel):
    type: Literal["usage_update"]
    input_tokens: int
    output_tokens: int
    total_tokens: int

# Discriminated union
StreamEvent = (
    StreamStart | Heartbeat | DoneEvent | StreamError |
    MessageDelta | AiMessage | MessageIsAnswer | ChatTitleGenerated |
    TaskUpdate | PendingSources | ReferencesFound |
    NodeToolsExecutionStart | NodeToolEvent | UpdateSubagentCurrentAction |
    NodeReportPreviewStart | NodeReportPreviewDelta | NodeReportPreviewDone |
    PingEvent | UsageUpdate
)
```

---

## 5. Event Sequence for a Standard Research Run

```
→ stream_start
→ task_update (key="planning", status=loading)
→ task_update (key="planning", status=success)    # planner produced PlanSet
→ pending_sources                                  # N sources queued
→ [For each parallel worker task:]
  → task_update (key=task_id, status=loading)
  → node_tools_execution_start
  → update_subagent_current_action
  → node_tool_event (event="tool_called")
  → node_tool_event (event="tool_completed")       # repeated per tool
  → references_found                               # entities for this task
  → task_update (key=task_id, status=success)
→ task_update (key="synthesis", status=loading)
→ task_update (key="synthesis", status=success)
→ node_report_preview_start (final_report=true)
→ [N × node_report_preview_delta]
→ node_report_preview_done (content = full GML)
→ message_delta [optional: prose summary in chat]
→ ai_message
→ done (has_async_entities_pending=true)
--- [async, after background job] ---
→ references_found (entity creation complete)
→ done (has_async_entities_pending=false)
```

---

## 6. Run Ledger Persistence

Each SSE event must be persisted as a `RunEvent` record in the `runs_events` table (BL-002). Key mapping:

| SSE Event | `RunEventType` enum value | Stored in `payload` |
|---|---|---|
| `stream_start` | `RUN_STARTED` | chat context |
| `task_update` (planning) | `PLAN_CREATED` | PlanSet |
| `task_update` (task loading) | `TASK_STARTED` | task metadata |
| `task_update` (task success) | `TASK_COMPLETED` | TaskResult |
| `task_update` (task error) | `TASK_FAILED` | error details |
| `node_report_preview_done` | `REPORT_DRAFT_READY` | preview metadata (not full GML — store GML as Artifact) |
| `references_found` | `SOURCES_RESOLVED` | Entity list |
| `done` | `RUN_COMPLETED` | completion metadata |
| `ERROR` | `RUN_FAILED` | error details |

**Note on GML storage**: The full GML content from `node_report_preview_done.content` is stored as an `Artifact` (SHA-256 addressed, media_type `application/vnd.nyqst.gml+xml`), not inline in the RunEvent payload. The `REPORT_DRAFT_READY` RunEvent stores the artifact SHA-256 reference.

---

## 7. Versioning

This is **Event Contract v1**. Changes to event schemas require:
1. A new version of this document
2. A corresponding ADR or DEC entry in DECISION-REGISTER
3. Backward-compatible changes only until v2 major revision

---

## Revision Log

| Date | Author | Change |
|------|--------|--------|
| 2026-03-14 | Agent (claude-sonnet-4-6) | v1 created from streaming-events-extract.md + orchestration-extract.md (GAP-079 resolution) |
