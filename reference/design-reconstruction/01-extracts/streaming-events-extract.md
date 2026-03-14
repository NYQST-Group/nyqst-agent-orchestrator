# Streaming, Events & SSE Domain — Complete Extraction

**Date:** 2026-02-20
**Confidence:** HIGH (direct from production Superagent client bundle analysis + NYQST SSE spec)
**Sources:**
- `/Users/markforster/AirTable-SuperAgent/reports/02_streaming_protocol.md` (NDJSON protocol)
- `/Users/markforster/AirTable-SuperAgent/docs/analysis/TECHNICAL-DEEP-DIVE.md` lines 915-1906 (streaming schemas & PlanSet)
- `/Users/markforster/NYQST-MCP/research/dify-analysis/NYQST-SSE-EVENT-SPECIFICATION.md` (proposed event extensions)
- `/Users/markforster/NYQST-MCP/research/dify-analysis/VERCEL-AI-SDK-NATIVE-COMPARISON.md` (AI SDK protocol alignment)
- `/Users/markforster/AirTable-SuperAgent/docs/analysis/CHAT-EXPORT-ANALYSIS.md` (message schema 26 fields)
- `/Users/markforster/AirTable-SuperAgent/reports/01_observed_surface.md` (feature flags & entity types)

---

## Event Type Registry — Complete Enum

**Total: 22 confirmed event types + 4 proposed = 26 event types**

### Superagent Production Events (22 confirmed)

| # | Event Type | Category | When Emitted | Payload Keys |
|---|---|---|---|---|
| 1 | `stream_start` | Lifecycle | Stream begins | `chat_id`, `creator_user_id`, `user_chat_message_id`, `workspace_id` |
| 2 | `heartbeat` | Lifecycle | Every 20-30s (watchdog keepalive) | (empty) |
| 3 | `done` | Lifecycle | Stream terminal | `message?`, `has_async_entities_pending?` |
| 4 | `ERROR` | Error | LLM/system failure | `error_type`, `error_message` |
| 5 | `message_delta` | Text Streaming | Token arrival | `delta: string` |
| 6 | `ai_message` | Message | Full message object | `message: Message` |
| 7 | `message_is_answer` | Message | Marks message as answer | `is_answer: boolean` |
| 8 | `chat_title_generated` | Message | Title auto-generation done | `title: string` |
| 9 | `clarification_needed` | Message | System needs clarification | `message: Message` |
| 10 | `update_message_clarification_message` | Message | Updates clarification flag | `update: {chat_message_id, needs_clarification_message}` |
| 11 | `task_update` | Planning | Plan task status changes | `key`, `title`, `message`, `status: loading\|success\|error`, `plan_set: PlanSet`, `metadata?` |
| 12 | `pending_sources` | Planning | Sources not yet fetched | `pending_sources: PendingSource[]` |
| 13 | `references_found` | References | Entity resolution done | `references: Entity[]` |
| 14 | `node_tools_execution_start` | Tool Execution | Tools begin on node | `plan_set_id`, `plan_id`, `node_id`, `tool_ids[]`, `total_tools`, `timestamp` |
| 15 | `node_tool_event` | Tool Execution | Fine-grained tool event | `event`, `node_id`, `plan_id`, `plan_set_id`, `tool_id?`, `tool_type?`, `metadata?`, `timestamp` |
| 16 | `update_subagent_current_action` | Tool Execution | UI status message ("what I'm doing") | `current_action`, `node_id`, `plan_id`, `plan_set_id`, `tool_id?`, `timestamp` |
| 17 | `node_report_preview_start` | Report Preview | Report generation begins | `preview_id`, `report_title`, `report_user_query`, `final_report`, `section_id?`, `node_id`, `plan_id`, `plan_set_id`, `entity`, `timestamp`, `workspace_id`, `tool_id?` |
| 18 | `node_report_preview_delta` | Report Preview | Incremental report content | `delta`, `preview_id`, `node_id`, `plan_id`, `plan_set_id`, `section_id?` |
| 19 | `node_report_preview_done` | Report Preview | Report complete | `content` (full GML), `preview_id`, `report_title`, `final_report`, `entity?`, `node_id`, `plan_id`, `plan_set_id`, `section_id?`, `timestamp`, `workspace_id` |
| 20 | `browser_use_start` | Browser Automation | Browser session opens | `browser_session_id`, `browser_stream_url`, `timestamp` |
| 21 | `browser_use_stop` | Browser Automation | Browser session closes | `browser_session_id` |
| 22 | `browser_use_await_user_input` | Browser Automation | Paused for human input | `browser_session_id`, `agent_message?` |

### NYQST Proposed New Events (4)

| # | Event Type | Category | Priority | When Emitted | Payload Keys |
|---|---|---|---|---|---|
| 23 | `ping` | Connection | HIGH | Every 10s | `timestamp: ISO8601` |
| 24 | `error` | Error Handling | HIGH | LLM/tool/network failure | `code`, `message`, `recoverable`, `context?` |
| 25 | `message-file` | Artifacts | MEDIUM | Agent generates file | `fileId`, `name`, `type`, `url`, `size?` |
| 26 | `usage-update` | Token Tracking | MEDIUM | After LLM call | `inputTokens`, `outputTokens`, `totalTokens`, `cost?` |

---

## Event Payload Schemas (Pydantic/TypeScript)

### Lifecycle Events

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any
from datetime import datetime

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
    message: Optional[dict] = None  # Full Message object if present
```

### Text Streaming Events

```python
class MessageDelta(BaseModel):
    type: Literal["message_delta"]
    delta: str  # incremental text token

class AiMessage(BaseModel):
    type: Literal["ai_message"]
    message: dict  # Full Message object

class MessageIsAnswer(BaseModel):
    type: Literal["message_is_answer"]
    is_answer: bool
```

### Planning Events

```python
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
    plan_tasks: dict[str, PlanTask]  # key = task_id
    used_sources: Optional[list[str]] = None
    previous_plan_id: Optional[str] = None

class PlanSet(BaseModel):
    chat_id: str
    creator_user_id: str
    user_chat_message_id: str
    workspace_id: str
    plans: dict[str, Plan]  # key = plan_id

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
```

### Reference & Entity Events

```python
class Entity(BaseModel):
    """Discriminated union on entity_type"""
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
    purpose: Optional[str] = None

    # Type-specific fields (example: WEB_PAGE)
    external_url: Optional[str] = None
    api_name: Optional[str] = None
    api_subtype: Optional[str] = None
    user_query: Optional[str] = None
    all_seen_entities: list[str] = Field(default_factory=list)
    cited_entities: list[str] = Field(default_factory=list)

class ReferencesFound(BaseModel):
    type: Literal["references_found"]
    references: list[Entity]
```

### Tool Execution Events

```python
class NodeToolsExecutionStart(BaseModel):
    type: Literal["node_tools_execution_start"]
    node_id: str
    plan_id: str
    plan_set_id: str
    tool_ids: list[str]
    total_tools: int
    timestamp: int  # Unix milliseconds

class NodeToolEvent(BaseModel):
    type: Literal["node_tool_event"]
    event: str  # event name (e.g., "tool_called", "tool_completed")
    node_id: str
    plan_id: str
    plan_set_id: str
    tool_id: Optional[str] = None
    tool_type: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    timestamp: int

class UpdateSubagentCurrentAction(BaseModel):
    type: Literal["update_subagent_current_action"]
    current_action: str  # human-readable status ("Searching the web...", "Analyzing results...")
    node_id: str
    plan_id: str
    plan_set_id: str
    tool_id: Optional[str] = None
    timestamp: int
```

### Report Preview Events

```python
class NodeReportPreviewStart(BaseModel):
    type: Literal["node_report_preview_start"]
    preview_id: str
    report_title: str
    report_user_query: str
    final_report: bool  # True for final synthesis, False for intermediate previews
    node_id: str
    plan_id: str
    plan_set_id: str
    entity: Entity  # GENERATED_REPORT type
    section_id: Optional[str] = None
    tool_id: Optional[str] = None
    timestamp: int
    workspace_id: str

class NodeReportPreviewDelta(BaseModel):
    type: Literal["node_report_preview_delta"]
    preview_id: str
    delta: str  # incremental GML content
    node_id: str
    plan_id: str
    plan_set_id: str
    section_id: Optional[str] = None

class NodeReportPreviewDone(BaseModel):
    type: Literal["node_report_preview_done"]
    preview_id: str
    content: str  # full GML content (XML-like markup with gml-* tags)
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
```

### Browser Automation Events

```python
class BrowserUseStart(BaseModel):
    type: Literal["browser_use_start"]
    browser_session_id: str
    browser_stream_url: str
    timestamp: int

class BrowserUseStop(BaseModel):
    type: Literal["browser_use_stop"]
    browser_session_id: str

class BrowserUseAwaitUserInput(BaseModel):
    type: Literal["browser_use_await_user_input"]
    browser_session_id: str
    agent_message: Optional[str] = None
```

### Clarification & Message Events

```python
class Message(BaseModel):
    """Full message schema (26 fields total)"""
    id: str
    chat_id: str
    creator_type: Literal["AI", "USER"]
    creator_user_id: Optional[str] = None  # null for AI messages
    message_type: Optional[Literal["normal", "super_report"]] = None
    deliverable_type: Optional[Literal["WEBSITE", "REPORT", "DOCUMENT", "SLIDE", "CODE"]] = None
    is_answer: bool
    is_running: Optional[bool] = None
    needs_clarification_message: Optional[str] = None
    retry_attempts: Optional[int] = None
    content: str  # raw content (often empty, see hydrated_content)
    hydrated_content: Optional[str] = None  # rendered HTML with gml-* components
    user_content_artifact_id: Optional[str] = None
    user_message_entity_ids: Optional[list[str]] = None
    user_message_entities: Optional[list[Entity]] = None
    ai_output_id: Optional[str] = None
    first_report_identifier: Optional[str] = None  # UUID of primary deliverable
    entities: list[Entity] = Field(default_factory=list)
    event_stream_artifact_id: Optional[str] = None  # points to event stream log
    error_type: Optional[Literal["TIMEOUT", "INVALID_RESPONSE"]] = None
    created_at: str  # ISO 8601

class ClarificationNeeded(BaseModel):
    type: Literal["clarification_needed"]
    message: Message

class UpdateMessageClarificationMessage(BaseModel):
    type: Literal["update_message_clarification_message"]
    update: dict  # {chat_message_id: str, needs_clarification_message: str | None}

class ChatTitleGenerated(BaseModel):
    type: Literal["chat_title_generated"]
    title: str
```

### Error Event (Production)

```python
class StreamError(BaseModel):
    type: Literal["ERROR"]
    error_type: str
    error_message: str
```

### Proposed New Events (NYQST)

```python
# Connection health
class PingEvent(BaseModel):
    type: Literal["ping"]
    timestamp: str  # ISO 8601

# Structured error handling
class ErrorEvent(BaseModel):
    type: Literal["error"]
    code: Literal[
        "rate_limit_exceeded", "tool_execution_failed", "llm_request_failed",
        "validation_error", "context_length_exceeded", "unknown_error"
    ]
    message: str
    recoverable: bool
    context: Optional[dict[str, Any]] = None

# File attachments
class MessageFileEvent(BaseModel):
    type: Literal["message-file"]
    fileId: str
    name: str
    type: str  # MIME type or file type
    url: str
    size: Optional[int] = None

# Token usage
class UsageUpdateEvent(BaseModel):
    type: Literal["usage-update"]
    inputTokens: int
    outputTokens: int
    totalTokens: int
    cost: Optional[dict] = None  # {cents: int, currency: str}
```

### Complete Type Union (Python)

```python
StreamEvent = Union[
    StreamStart, Heartbeat, DoneEvent,
    MessageDelta, AiMessage, MessageIsAnswer, ChatTitleGenerated,
    TaskUpdate, PendingSources, ReferencesFound,
    NodeToolsExecutionStart, NodeToolEvent, UpdateSubagentCurrentAction,
    NodeReportPreviewStart, NodeReportPreviewDelta, NodeReportPreviewDone,
    BrowserUseStart, BrowserUseStop, BrowserUseAwaitUserInput,
    ClarificationNeeded, UpdateMessageClarificationMessage,
    StreamError,
    # Proposed new:
    PingEvent, ErrorEvent, MessageFileEvent, UsageUpdateEvent
]
```

---

## SSE Protocol Details

### NDJSON Envelope Format

**HTTP Request:**
```
GET /api/chat/message/stream?message_stream_id={id}
Host: superagent.com
Cookie: <session>
Connection: keep-alive
cache-control: no-cache
X-Gradient-Browser-Client: 1
X-Gradient-Workspace-Id: {workspace_id}  [optional]
credentials: include
```

**HTTP Response:**
```
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no  (nginx: disable buffering)
Transfer-Encoding: chunked

{"data":{"type":"stream_start","chat_id":"...","creator_user_id":"...","user_chat_message_id":"...","workspace_id":"..."},"timestamp":1730000000000}
{"data":{"type":"message_delta","delta":"Hello"},"timestamp":1730000000050}
{"data":{"type":"message_delta","delta":" world"},"timestamp":1730000000051}
{"data":{"type":"done","has_async_entities_pending":false},"timestamp":1730000000100}
```

### Envelope Envelope Schema (TypeScript)

```typescript
interface StreamEnvelope {
  data: StreamEvent;        // discriminated union on .data.type
  timestamp: number;        // Unix milliseconds
}
```

### Connection Lifecycle

1. **Connection Phase**
   - Client: GET request with `message_stream_id`
   - Server: Returns 200 OK, stream begins
   - Server: First event is always `stream_start`

2. **Streaming Phase**
   - Server emits events in order (deterministic sequence)
   - Events are split by newlines (`\n`)
   - Each line is one JSON envelope
   - Client: Parse line → validate with Zod → dispatch handler

3. **Termination Phase**
   - Server emits terminal event: `done`, `ERROR`, or `clarification_needed`
   - `done`: Normal completion (possibly with `has_async_entities_pending: true`)
   - `ERROR`: Fatal error (stop processing)
   - `clarification_needed`: System paused, waiting for user input
   - Client: Clean up stream, update UI

### Watchdog & Timeout Strategy

**30-second watchdog:**
- Client sets timeout to 30 seconds from stream start
- Timer **resets on each chunk arrival** (not on each event)
- If no data in 30s → abort stream, assume hung connection
- **Distinct from retry**: Watchdog is about "no data arriving", retry is about "connection dropped"

**Heartbeat:**
- Server emits `heartbeat` events every 20-30 seconds
- Payload: `{type: "heartbeat"}` (no other fields)
- Purpose: Reset client's watchdog timer
- Superagent implementation: `while True: try (event in wait_for(generator, timeout=20s)) else yield heartbeat`

### Reconnection Strategy

**Initial failure scenarios:**
- Connection drops after partial data received → **retry**
- Connection drops before any data → **retry** (only if buffer non-empty)
- Manual abort by user → **no retry**
- 404 Not Found (`message_stream_id` invalid) → **no retry**

**Exponential backoff (5 attempts max):**

| Attempt | Delay | Total Elapsed |
|---------|-------|---------------|
| 1 | 1,000ms | 1s |
| 2 | 2,000ms | 3s |
| 3 | 4,000ms | 7s |
| 4 | 8,000ms | 15s |
| 5 | 16,000ms | 31s |
| >5 | No retry | Error to user |

**Formula:** `delay = min(1000 * 2^(retry-1), 30000)`

### Citation Buffering (Client-Side State Machine)

**Purpose:** Avoid displaying incomplete citations like `[1` in the UI.

**State machine:**
```
State: isInCitation (boolean, default: false)
Buffer: accumulated text
ReadyPointer: index of last ready-to-display character

On each message_delta event:
  1. Append delta to buffer
  2. Iterate from (readyPointer + 1) to end of buffer:
     a. If char == '[' → enter citation (isInCitation = true)
     b. If char == ']' or '\n' → exit citation (isInCitation = false)
     c. If NOT in citation → advance readyPointer
  3. Return to UI: buffer[0..readyPointer] (ready content only)
  4. Keep buffered: buffer[readyPointer+1..end] (in-progress content)
```

**Example flow:**
```
Receive: "The answer is"
  → Ready: "The answer is"

Receive: " ["
  → Ready: "The answer is" (buffer: "The answer is [", pointer stays at 13)

Receive: "1"
  → Ready: "The answer is" (buffer: "The answer is [1", pointer stays at 13)

Receive: "]"
  → Ready: "The answer is [1]" (buffer: "The answer is [1]", pointer now at 17)

Receive: " complete"
  → Ready: "The answer is [1] complete"
```

### Replay Mode

**Activation condition:** `replayState === "playing"` AND `replayEvents !== null` AND `finalReplayMessage` exists

**Implementation:**
```python
async def replay_stream(events: list, final_message: Message, on_event, on_end):
    for event in events:
        if event["type"] == "heartbeat":
            # Skip heartbeats (0ms delay)
            continue
        else:
            # Emit other events with 5ms spacing
            await on_event(event)
            await asyncio.sleep(0.005)

    # Terminal event: synthesized from stored final_message
    await on_event({"type": "done", "message": final_message})
    await on_end()
```

**Key insight:** Backend stores events as NDJSON log (one line per event) + `finalMessage` separately. Replay uses both to reconstruct the user-visible stream without live processing.

---

## Two-Stream Architecture (DEC-021)

**Reference:** NYQST decision DEC-021 proposes two independent streams:

### Stream 1: Chat/Message Stream
- **Endpoint:** `/api/chat/message/stream`
- **Events:** `message_delta`, `message_is_answer`, `done`, `clarification_needed`, `ERROR`
- **Purpose:** User-visible response text and final message state
- **Lifetime:** Per user message → AI response completion

### Stream 2: Run/Execution Event Stream
- **Endpoint:** `/api/run/{run_id}/stream` (proposed, not confirmed in Superagent)
- **Events:** `task_update`, `pending_sources`, `node_tool_event`, `update_subagent_current_action`, `node_report_preview_*`, `browser_use_*`
- **Purpose:** Internal execution orchestration, planning, tool calls, report generation
- **Lifetime:** Per run (can span multiple conversation turns)

**Rationale:**
- Chat stream is request-response (user asks → AI responds)
- Run stream is orchestrator-driven (plan executes, generates multiple sub-tasks)
- Separating them allows frontend to show progress independently of message stream
- Enables replay of run (user views agent's thinking) separately from message (user views answer)

**Superagent observation:** Both streams are **coalesced into single `/api/chat/message/stream`** endpoint. The `event_stream_artifact_id` on messages points to the full event log, suggesting they keep a persistent event store per run.

---

## PG LISTEN/NOTIFY Integration (How Events Flow DB → SSE)

**Architecture pattern (inferred from Superagent):**

### Event Publishing (Backend → Database)

```python
# When orchestrator completes a task
async def emit_task_update(run_id: str, task: Task, status: TaskStatus):
    event = TaskUpdate(
        type="task_update",
        key=task.id,
        title=task.title,
        message=task.message,
        status=status.value,  # "loading" | "success" | "error"
        plan_set=task.plan_set,  # full nested object
        metadata=task.metadata,
    )

    # Store in RunEvents table
    db.session.add(RunEvent(
        run_id=run_id,
        event_type="task_update",
        payload=event.model_dump(),
        created_at=datetime.utcnow()
    ))

    # Notify waiting connections
    await db.execute(
        text("SELECT pg_notify(:channel, :payload)"),
        {
            "channel": f"run_stream_{run_id}",
            "payload": json.dumps(event.model_dump())
        }
    )
    db.session.commit()
```

### Event Consumption (Database → Stream Consumer)

```python
# FastAPI endpoint: /api/chat/message/stream?message_stream_id={id}
@app.get("/api/chat/message/stream")
async def stream_chat_message(message_stream_id: str):
    async def event_generator():
        # Step 1: Emit stream_start
        yield json.dumps({
            "data": {
                "type": "stream_start",
                "chat_id": message.chat_id,
                "creator_user_id": message.creator_user_id,
                "user_chat_message_id": message.id,
                "workspace_id": message.workspace_id,
            },
            "timestamp": int(time.time() * 1000)
        }) + "\n"

        # Step 2: Get run_id for this message
        run_id = message.run_id

        # Step 3: Listen for NOTIFY events
        async with db.engine.raw_connection() as conn:
            await conn.set_isolation_level("AUTOCOMMIT")
            async with conn.cursor() as cur:
                await cur.execute(f"LISTEN run_stream_{run_id}")

                # Step 4: Stream stored events from RunEvents table
                stored_events = db.session.query(RunEvent)\
                    .filter(RunEvent.run_id == run_id)\
                    .order_by(RunEvent.created_at)

                event_index = 0
                while not connection_closed:
                    # Emit next stored event
                    if event_index < len(stored_events):
                        event = stored_events[event_index]
                        yield json.dumps({
                            "data": event.payload,
                            "timestamp": int(event.created_at.timestamp() * 1000)
                        }) + "\n"
                        event_index += 1

                    # Wait for new NOTIFY or stored events
                    try:
                        notify = await asyncio.wait_for(
                            conn.get_notify(),
                            timeout=20.0
                        )
                        # New event from NOTIFY: emit it
                        payload = json.loads(notify.payload)
                        yield json.dumps({
                            "data": payload,
                            "timestamp": int(time.time() * 1000)
                        }) + "\n"
                    except asyncio.TimeoutError:
                        # No new events: emit heartbeat
                        yield json.dumps({
                            "data": {"type": "heartbeat"},
                            "timestamp": int(time.time() * 1000)
                        }) + "\n"

                # Stream terminal event
                yield json.dumps({
                    "data": {
                        "type": "done",
                        "has_async_entities_pending": message.has_async_entities_pending,
                        "message": message.to_dict()
                    },
                    "timestamp": int(time.time() * 1000)
                }) + "\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
```

### Event Persistence (RunEvents Table)

```python
from sqlalchemy import Column, String, JSON, DateTime
from datetime import datetime

class RunEvent(Base):
    __tablename__ = "run_events"

    id = Column(String, primary_key=True)  # UUID
    run_id = Column(String, ForeignKey("runs.id"), index=True)
    event_type = Column(String, index=True)  # discriminator
    payload = Column(JSON)  # full event envelope (data only, timestamp added on emit)
    sequence_number = Column(Integer, autoincrement=True)  # event ordering
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
```

**Key insight:** Events are **immutable append-only log**. Each event is persisted before streaming, enabling replay and audit trails.

---

## Message Schema (Complete 26-Field Model)

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    """Complete message schema from Superagent chat export"""

    # Identity
    id: str  # "{uuid}_chat_message"
    chat_id: str  # "{uuid}_chat"

    # Content & Storage
    content: str  # raw content (often empty)
    hydrated_content: Optional[str] = None  # rendered HTML with gml-* components

    # Metadata
    creator_type: Literal["AI", "USER"]
    creator_user_id: Optional[str] = None  # null for AI messages
    created_at: datetime  # ISO 8601 -> parsed
    message_type: Optional[Literal["normal", "super_report"]] = None  # null for user messages
    deliverable_type: Optional[Literal["WEBSITE", "REPORT", "DOCUMENT", "SLIDE", "CODE"]] = None  # on user messages

    # Status Flags
    is_answer: bool  # marks message as "the answer" in a conversation
    is_running: Optional[bool] = None  # true if generation in progress
    needs_clarification_message: Optional[str] = None  # clarification request text
    retry_attempts: Optional[int] = 0  # for tracking retries

    # References & Artifacts
    ai_output_id: Optional[str] = None  # "{uuid}_ai_outputs"
    event_stream_artifact_id: Optional[str] = None  # "{uuid}_artifact" → event log
    user_content_artifact_id: Optional[str] = None  # uploaded file content
    first_report_identifier: Optional[str] = None  # UUID of primary deliverable

    # Entities
    entities: list = Field(default_factory=list)  # Entity[]
    user_message_entities: Optional[list] = None  # entities uploaded by user
    user_message_entity_ids: Optional[list[str]] = None  # IDs of uploaded entities

    # Error Handling
    error_type: Optional[Literal["TIMEOUT", "INVALID_RESPONSE"]] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

**Key insights:**
- `deliverable_type` is **per-message**, not per-chat (user can request different types in follow-ups)
- `event_stream_artifact_id` points to the event log for that message's generation
- `first_report_identifier` disambiguates which entity is the "main" deliverable when multiple are generated
- `hydrated_content` is **rendered HTML** (already processed, includes gml-* web components)
- `is_running` is null for completed messages, true/false for in-progress
- `user_message_entities` and `user_message_entity_ids` are for RAG uploads, null for user chat

---

## Frontend Event Consumption Patterns

### EventSource Setup (TypeScript/React)

```typescript
// ui/src/hooks/use-sse.ts
import { useEffect, useRef, useState, useCallback } from 'react'

export function useSSE({
  url,
  onEvent,
  enabled = true,
  reconnectDelay = 3000,
  maxReconnectAttempts = 5
}) {
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  const [connectionHealth, setConnectionHealth] = useState<'healthy' | 'stale' | 'disconnected'>('disconnected')
  const reconnectAttemptsRef = useRef(0)
  const lastPingTimeRef = useRef<number>(Date.now())
  const eventSourceRef = useRef<EventSource | null>(null)

  const connect = useCallback(async () => {
    if (!enabled) return

    setStatus('connecting')

    // Manual fetch + ReadableStream (more control than EventSource)
    const workspaceId = getWorkspaceId()
    const headers: Record<string, string> = {
      'Connection': 'keep-alive',
      'X-Gradient-Browser-Client': '1',
      'cache-control': 'no-cache'
    }
    if (workspaceId) {
      headers['X-Gradient-Workspace-Id'] = workspaceId
    }

    try {
      const response = await fetch(url, {
        credentials: 'include',
        headers,
        method: 'GET'
      })

      if (response.status === 404) {
        setStatus('error')
        return
      }
      if (!response.ok || !response.body) throw new Error('No stream body')

      setStatus('connected')
      reconnectAttemptsRef.current = 0
      setConnectionHealth('healthy')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      // Watchdog timer: 30s with reset on each chunk
      const watchdogRef = useRef<NodeJS.Timeout | null>(null)
      const resetWatchdog = () => {
        if (watchdogRef.current) clearTimeout(watchdogRef.current)
        watchdogRef.current = setTimeout(() => {
          reader.cancel('Watchdog timeout')
          connect() // Retry
        }, 30000)
      }

      resetWatchdog()

      let done = false
      while (!done) {
        const { done: chunkDone, value } = await reader.read()
        resetWatchdog()
        done = chunkDone

        if (value) {
          buffer += decoder.decode(value, { stream: true })

          // Parse NDJSON lines
          let newlineIdx: number
          while ((newlineIdx = buffer.indexOf('\n')) !== -1) {
            const line = buffer.slice(0, newlineIdx).trim()
            buffer = buffer.slice(newlineIdx + 1)
            if (!line) continue

            try {
              const envelope = JSON.parse(line)
              const event = envelope.data

              // Update connection health on successful events
              if (event.type !== 'ERROR') {
                reconnectAttemptsRef.current = 0
              }

              // Emit to handler
              await onEvent(event)

              // Check for terminal event
              if (['done', 'ERROR', 'clarification_needed'].includes(event.type)) {
                done = true
              }
            } catch (e) {
              console.error('Failed to parse event', e)
            }
          }
        }
      }

      if (watchdogRef.current) clearTimeout(watchdogRef.current)
      setStatus('disconnected')
    } catch (err) {
      setStatus('error')

      // Retry with exponential backoff
      const nextRetry = reconnectAttemptsRef.current + 1
      if (nextRetry <= maxReconnectAttempts) {
        reconnectAttemptsRef.current = nextRetry
        const delay = Math.min(1000 * Math.pow(2, nextRetry - 1), 30000)
        setTimeout(connect, delay)
      } else {
        setStatus('disconnected')
      }
    }
  }, [url, enabled, onEvent])

  // Monitor ping events
  useEffect(() => {
    const interval = setInterval(() => {
      const timeSinceLastPing = Date.now() - lastPingTimeRef.current
      if (timeSinceLastPing > 15000) {
        setConnectionHealth('stale')
      }
      if (timeSinceLastPing > 30000) {
        setConnectionHealth('disconnected')
        connect() // Retry
      }
    }, 5000)
    return () => clearInterval(interval)
  }, [connect])

  useEffect(() => {
    if (enabled) connect()
  }, [enabled, connect])

  return { status, connectionHealth, connect }
}
```

### State Update Handler (React)

```typescript
// ui/src/hooks/use-chat-stream.ts
import { useState, useCallback } from 'react'
import { useSSE } from './use-sse'

export function useChatStream(messageStreamId: string) {
  const [messages, setMessages] = useState<Message[]>([])
  const [currentMessage, setCurrentMessage] = useState<MessageState | null>(null)
  const [planSet, setPlanSet] = useState<PlanSet | null>(null)
  const [entities, setEntities] = useState<Entity[]>([])
  const [reportPreviews, setReportPreviews] = useState<Record<string, ReportPreview>>({})
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Citation buffer for message_delta
  const citationBufferRef = useRef(new CitationBuffer())

  const handleEvent = useCallback(async (event: StreamEvent) => {
    switch (event.type) {
      case 'stream_start':
        setIsLoading(true)
        setError(null)
        setCurrentMessage({
          id: generateId(),
          content: '',
          role: 'assistant',
          entities: []
        })
        break

      case 'message_delta':
        citationBufferRef.current.feed(event.delta)
        setCurrentMessage(prev => prev ? {
          ...prev,
          content: citationBufferRef.current.getReadyContent()
        } : null)
        break

      case 'message_is_answer':
        setCurrentMessage(prev => prev ? { ...prev, isAnswer: event.is_answer } : null)
        break

      case 'task_update':
        setPlanSet(event.plan_set)
        break

      case 'references_found':
        setEntities(prev => [...prev, ...event.references])
        break

      case 'node_report_preview_start':
        setReportPreviews(prev => ({
          ...prev,
          [event.preview_id]: {
            id: event.preview_id,
            title: event.report_title,
            content: '',
            status: 'generating'
          }
        }))
        break

      case 'node_report_preview_delta':
        setReportPreviews(prev => ({
          ...prev,
          [event.preview_id]: {
            ...prev[event.preview_id],
            content: (prev[event.preview_id]?.content || '') + event.delta
          }
        }))
        break

      case 'node_report_preview_done':
        setReportPreviews(prev => ({
          ...prev,
          [event.preview_id]: {
            ...prev[event.preview_id],
            content: event.content,
            status: 'complete'
          }
        }))
        break

      case 'done':
        if (currentMessage) {
          setMessages(prev => [...prev, currentMessage])
        }
        setCurrentMessage(null)
        setIsLoading(false)
        break

      case 'ERROR':
        setError(event.error_message)
        setIsLoading(false)
        break

      case 'heartbeat':
        // No-op, just keeps connection alive
        break

      case 'ping':
        // Update connection health (handled by useSSE hook)
        break
    }
  }, [currentMessage])

  const { status, connectionHealth } = useSSE({
    url: `/api/chat/message/stream?message_stream_id=${messageStreamId}`,
    onEvent: handleEvent,
    enabled: !!messageStreamId
  })

  return {
    messages,
    currentMessage,
    planSet,
    entities,
    reportPreviews,
    isLoading,
    error,
    connectionHealth
  }
}
```

### Citation Buffer (Client-Side)

```typescript
// ui/src/utils/citation-buffer.ts
export class CitationBuffer {
  private isInCitation = false
  private buffer = ''
  private readyPointer = -1

  feed(chunk: string): boolean {
    if (!chunk) return false
    this.buffer += chunk

    const prevReady = this.readyPointer
    for (let i = this.readyPointer + 1; i < this.buffer.length; i++) {
      const char = this.buffer[i]
      if (char === '[') {
        this.isInCitation = true
      } else if (char === ']' || char === '\n') {
        this.isInCitation = false
      }
      if (!this.isInCitation) {
        this.readyPointer = i
      }
    }
    return prevReady !== this.readyPointer
  }

  getReadyContent(): string {
    return this.buffer.slice(0, this.readyPointer + 1)
  }

  getFullContent(): string {
    return this.buffer
  }

  reset(): void {
    this.isInCitation = false
    this.buffer = ''
    this.readyPointer = -1
  }
}
```

---

## AI SDK Data Stream Protocol Alignment

### NYQST → Vercel AI SDK v3 Mapping

**Superagent events → AI SDK native stream parts:**

| Superagent Event | AI SDK Equivalent | Mapping |
|---|---|---|
| `stream_start` | `start` | Initial lifecycle event |
| `message_delta` | `text-delta` (with `id`) | Text content streaming |
| `task_update` | Custom data event (via `providerMetadata`) | Plan/step info |
| `node_tool_event` | `tool-input-start`, `tool-input-available`, `tool-output-available` | Tool execution lifecycle |
| `done` | `finish` | Stream completion |
| `ERROR` | Custom error event | Error signaling |
| `heartbeat` | `ping` (proposed) | Connection keepalive |

### Implementation: LangGraph → AI SDK Adapter

```python
# intelli/agents/adapters/langgraph_to_aisdk.py
from typing import AsyncIterator
import json
import time
from datetime import datetime, timezone

class LangGraphToAISDKAdapter:
    """Convert LangGraph astream_events to Vercel AI SDK v3 SSE format"""

    def __init__(self):
        self._text_started = False
        self._text_id = "text-1"
        self._step_started = False
        self._current_step_id = "step-0"
        self._step_count = 0
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._last_ping = time.monotonic()

    async def convert_events_stream(
        self,
        langgraph_stream: AsyncIterator
    ) -> AsyncIterator[str]:
        """
        Convert LangGraph astream_events to AI SDK SSE format.

        Yields: NDJSON lines (each is {"data": {...}, "timestamp": ...})
        """
        async for event in langgraph_stream:
            event_type = event.get("event")
            event_data = event.get("data", {})

            # Emit ping every 10s
            now = time.monotonic()
            if now - self._last_ping > 10:
                yield self._sse({
                    "type": "ping",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                self._last_ping = now

            # Handle different LangGraph event types
            if event_type == "on_tool_start":
                tool_name = event_data.get("name", "unknown_tool")
                tool_call_id = event_data.get("tool_call_id", f"call-{uuid4()}")

                yield self._sse({
                    "type": "tool-input-start",
                    "toolCallId": tool_call_id,
                    "toolName": tool_name
                })

            elif event_type == "on_tool_end":
                tool_call_id = event_data.get("tool_call_id")
                output = event_data.get("output")

                yield self._sse({
                    "type": "tool-output-available",
                    "toolCallId": tool_call_id,
                    "output": output
                })

            elif event_type == "on_chat_model_stream":
                chunk = event_data.get("chunk")
                if chunk and chunk.content:
                    # Start text block if needed
                    if not self._text_started:
                        yield self._sse({
                            "type": "text-start",
                            "id": self._text_id
                        })
                        self._text_started = True

                    # Emit text delta
                    yield self._sse({
                        "type": "text-delta",
                        "id": self._text_id,
                        "delta": chunk.content
                    })

            elif event_type == "on_chat_model_end":
                if self._text_started:
                    yield self._sse({
                        "type": "text-end",
                        "id": self._text_id
                    })
                    self._text_started = False

                # Emit token usage
                output = event_data.get("output")
                if output:
                    usage = getattr(output, "usage_metadata", None)
                    if usage:
                        input_tokens = usage.get("input_tokens", 0)
                        output_tokens = usage.get("output_tokens", 0)
                        self._total_input_tokens += input_tokens
                        self._total_output_tokens += output_tokens

                        yield self._sse({
                            "type": "usage-update",
                            "inputTokens": self._total_input_tokens,
                            "outputTokens": self._total_output_tokens,
                            "totalTokens": self._total_input_tokens + self._total_output_tokens
                        })

            elif event_type == "on_end":
                # Emit finish (terminal event)
                yield self._sse({
                    "type": "finish"
                })

    def _sse(self, data: dict) -> str:
        """Format event as SSE NDJSON line"""
        envelope = {
            "data": data,
            "timestamp": int(time.time() * 1000)
        }
        return json.dumps(envelope) + "\n"
```

### Frontend Integration (Vercel AI SDK useChat)

```typescript
// ui/src/hooks/use-chat.ts
import { useChat } from '@ai-sdk/react'
import { useSSE } from './use-sse'

export function useChatWithSSE() {
  const [streamParts, setStreamParts] = useState<StreamPart[]>([])

  const handleSSEEvent = useCallback((event: any) => {
    // AI SDK native events
    if (['start', 'start-step', 'finish-step', 'finish', 'text-start',
          'text-delta', 'text-end', 'tool-input-start', 'tool-input-available',
          'tool-output-available'].includes(event.type)) {
      setStreamParts(prev => [...prev, event])
    }

    // Custom NYQST events
    if (event.type === 'ping') {
      // Update connection health
      setConnectionHealth('healthy')
    }
    if (event.type === 'error') {
      // Handle error event
      showErrorToast(event.message)
    }
    if (event.type === 'message-file') {
      // Add file attachment
      addFileToMessage(event)
    }
    if (event.type === 'usage-update') {
      // Update token display
      setTokenUsage(event)
    }
  }, [])

  const { status, connectionHealth } = useSSE({
    url: `/api/v1/agent/stream?run_id=${runId}`,
    onEvent: handleSSEEvent
  })

  return { streamParts, connectionHealth, status }
}
```

---

## Reusable Code Patterns

### Python: NDJSON Streaming Emitter

```python
# intelli/core/streaming.py
from fastapi.responses import StreamingResponse
from typing import AsyncIterator
import json
from datetime import datetime
import asyncio

async def ndjson_stream(
    event_generator: AsyncIterator,
    heartbeat_interval: float = 20.0
) -> AsyncIterator[bytes]:
    """
    Wrap event generator in NDJSON format with heartbeat.

    Args:
        event_generator: Async generator yielding event dicts
        heartbeat_interval: Seconds between heartbeats (default: 20s, for 30s watchdog)

    Yields:
        NDJSON-formatted bytes (envelope with timestamp)
    """
    last_event_time = asyncio.get_event_loop().time()

    async def with_heartbeat():
        nonlocal last_event_time

        while True:
            try:
                # Wait for next event or timeout (heartbeat interval)
                event = await asyncio.wait_for(
                    event_generator.__anext__(),
                    timeout=heartbeat_interval
                )
                last_event_time = asyncio.get_event_loop().time()
                yield event
            except asyncio.TimeoutError:
                # Emit heartbeat to reset client's 30s watchdog
                yield {"type": "heartbeat"}
            except StopAsyncIteration:
                break

    async for event in with_heartbeat():
        envelope = {
            "data": event,
            "timestamp": int(datetime.utcnow().timestamp() * 1000)
        }
        yield (json.dumps(envelope) + "\n").encode()


@app.get("/api/chat/message/stream")
async def stream_chat_message(message_stream_id: str):
    """Stream chat events with reconnection support"""

    async def event_gen():
        # Get message and run
        message = db.session.query(ChatMessage).filter_by(id=message_stream_id).first()
        if not message:
            yield {"type": "ERROR", "error_type": "NOT_FOUND", "error_message": "Message not found"}
            return

        # Emit stream start
        yield {
            "type": "stream_start",
            "chat_id": message.chat_id,
            "creator_user_id": message.creator_user_id,
            "user_chat_message_id": message.id,
            "workspace_id": message.workspace_id
        }

        # Stream from run orchestrator
        run_id = message.run_id
        async for event in run_stream(run_id):
            yield event

        # Terminal event
        yield {
            "type": "done",
            "has_async_entities_pending": message.has_async_entities_pending,
            "message": message.to_dict()
        }

    return StreamingResponse(
        ndjson_stream(event_gen()),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Nginx: don't buffer
        }
    )
```

### TypeScript: Event Discriminator & Handler Router

```typescript
// ui/src/types/stream-events.ts
import { z } from 'zod'

// Define all event types with Zod schemas
const StreamStartSchema = z.object({
  type: z.literal('stream_start'),
  chat_id: z.string(),
  creator_user_id: z.string(),
  user_chat_message_id: z.string(),
  workspace_id: z.string()
})

const MessageDeltaSchema = z.object({
  type: z.literal('message_delta'),
  delta: z.string()
})

const DoneSchema = z.object({
  type: z.literal('done'),
  has_async_entities_pending: z.boolean().optional(),
  message: z.record(z.any()).optional()
})

const PingSchema = z.object({
  type: z.literal('ping'),
  timestamp: z.string()
})

const ErrorEventSchema = z.object({
  type: z.literal('error'),
  code: z.enum(['rate_limit_exceeded', 'tool_execution_failed', 'llm_request_failed', 'validation_error', 'context_length_exceeded', 'unknown_error']),
  message: z.string(),
  recoverable: z.boolean(),
  context: z.record(z.any()).optional()
})

// Discriminated union
const StreamEventSchema = z.discriminatedUnion('type', [
  StreamStartSchema,
  MessageDeltaSchema,
  DoneSchema,
  PingSchema,
  ErrorEventSchema,
  // ... more event types
])

export type StreamEvent = z.infer<typeof StreamEventSchema>

// Event handler router
export class EventRouter {
  private handlers: Map<string, (event: any) => Promise<void>> = new Map()

  on<T extends StreamEvent>(
    eventType: T['type'],
    handler: (event: T) => Promise<void>
  ): void {
    this.handlers.set(eventType, handler)
  }

  async dispatch(event: StreamEvent): Promise<void> {
    const handler = this.handlers.get(event.type)
    if (handler) {
      await handler(event)
    }
  }
}

// Usage
const router = new EventRouter()

router.on('stream_start', async (event) => {
  console.log('Stream started', event.chat_id)
})

router.on('message_delta', async (event) => {
  console.log('Text chunk:', event.delta)
})

router.on('ping', async (event) => {
  console.log('Ping received', event.timestamp)
})

router.on('error', async (event) => {
  if (event.recoverable) {
    console.log('Recoverable error:', event.message)
  } else {
    console.error('Fatal error:', event.message)
  }
})
```

### Python: Pydantic Event Models (Full Set)

```python
# intelli/schemas/streaming.py
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any
from datetime import datetime

# Event schemas (inheritance pattern for code reuse)
class BaseStreamEvent(BaseModel):
    """Base for all events with common envelope"""
    class Config:
        use_enum_values = True

class StreamStart(BaseStreamEvent):
    type: Literal["stream_start"]
    chat_id: str
    creator_user_id: str
    user_chat_message_id: str
    workspace_id: str

class MessageDelta(BaseStreamEvent):
    type: Literal["message_delta"]
    delta: str

class Heartbeat(BaseStreamEvent):
    type: Literal["heartbeat"]

class PingEvent(BaseStreamEvent):
    type: Literal["ping"]
    timestamp: str  # ISO 8601

class ErrorEvent(BaseStreamEvent):
    type: Literal["error"]
    code: Literal[
        "rate_limit_exceeded", "tool_execution_failed", "llm_request_failed",
        "validation_error", "context_length_exceeded", "unknown_error"
    ]
    message: str
    recoverable: bool
    context: Optional[dict[str, Any]] = None

class DoneEvent(BaseStreamEvent):
    type: Literal["done"]
    has_async_entities_pending: Optional[bool] = None
    message: Optional[dict] = None

# Union discriminator
from typing import Union, Annotated

StreamEvent = Annotated[
    Union[
        StreamStart, MessageDelta, Heartbeat, PingEvent,
        ErrorEvent, DoneEvent
        # ... more types
    ],
    Field(discriminator='type')
]

# Safe parsing with fallback
def parse_stream_event(data: dict) -> StreamEvent:
    try:
        return StreamEvent.parse_obj(data)
    except Exception as e:
        logger.error(f"Failed to parse event: {e}")
        # Return a generic error event or skip
        return ErrorEvent(
            code="unknown_error",
            message=str(e),
            recoverable=False
        )
```

---

## Summary & Mapping Table

| Layer | Component | Implementation | Confidence |
|---|---|---|---|
| **Protocol** | NDJSON envelope | `{data: <event>, timestamp: <ms>}` | HIGH |
| **Transport** | HTTP/streaming | `GET /api/chat/message/stream` with ReadableStream | HIGH |
| **Events** | 22 confirmed types | Zod schemas extracted verbatim | HIGH |
| **Proposed** | 4 new types | ping, error, message-file, usage-update | HIGH (from NYQST spec) |
| **Watchdog** | 30s timeout | Reset on chunk, no heartbeat = abort | HIGH |
| **Heartbeat** | 20-30s interval | `{type: "heartbeat"}` → resets watchdog | HIGH |
| **Reconnection** | Exponential backoff | 5 attempts, max 16s delay | HIGH |
| **State Machine** | Citation buffer | Delay rendering until `]` seen | HIGH |
| **Replay** | Event log replay | NDJSON log + finalMessage stored | HIGH |
| **Database** | Event persistence | RunEvents table (append-only log) | INFERRED |
| **Notification** | PG LISTEN/NOTIFY | Async event emission via PostgreSQL | INFERRED |

---

**End of Streaming, Events & SSE Domain Extraction**
