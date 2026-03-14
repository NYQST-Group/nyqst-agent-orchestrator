# NYQST SSE Event Type Specification
## Extending Event Coverage for Rich Agent & Workflow UIs

**Date:** 2026-02-04
**Author:** Claude Opus 4.5
**Context:** Based on Dify analysis (25+ event types) and NYQST current implementation (10 event types)
**Goal:** Balanced expansion to 12-15 event types maintaining Vercel AI SDK compatibility

---

## Executive Summary

NYQST currently emits **10 distinct event types** through the `LangGraphToAISDKAdapter`:
- Vercel AI SDK v3 events: `start`, `start-step`, `finish-step`, `finish`, `text-start`, `text-delta`, `text-end`, `reasoning-start`, `reasoning-delta`, `reasoning-end`
- Custom data events: `source-document`, `tool-input-start`, `tool-input-available`, `tool-output-available`

**Gap Analysis:**
- **Missing:** Connection keepalive (ping), workflow step lifecycle, error recovery signals, progress indicators, file attachments
- **Dify comparison:** 25+ events but many are workflow-engine-specific (node execution, iteration, loop, parallel branch)
- **Target:** 12-15 events total (add 2-5 new types)

**Design Principles:**
1. Vercel AI SDK compatibility is non-negotiable
2. Event types must map to frontend capabilities (no "future-proofing" waste)
3. Workflow orchestration happens in LangGraph, not SSE events
4. Adopt only Dify patterns that improve observability/UX

---

## 1. Current NYQST Event Catalog

### 1.1 Vercel AI SDK v3 Standard Events

| Event Type | When Emitted | Frontend Purpose |
|------------|--------------|------------------|
| `start` | First event when stream begins | Initialize UI state, show loading |
| `start-step` | Before each LangGraph node executes | Step boundary marker |
| `finish-step` | After each node completes | Close step UI, prepare for next |
| `finish` | Stream complete (includes metadata) | Close loading, show final state |
| `text-start` | Before text content streams | Start text accumulator |
| `text-delta` | Each text token | Append to message bubble |
| `text-end` | Text content complete | Close text block |
| `reasoning-start` | o1/o3/o4-mini models begin thinking | Show thinking indicator |
| `reasoning-delta` | Reasoning tokens stream | Append to collapsible think block |
| `reasoning-end` | Reasoning complete | Close think block |

**Format:**
```json
{"type": "text-delta", "id": "text-1", "delta": "Hello"}
```

### 1.2 Tool Execution Events

| Event Type | When Emitted | Payload |
|------------|--------------|---------|
| `tool-input-start` | Tool call begins (`on_tool_start`) | `{toolCallId, toolName}` |
| `tool-input-available` | Tool arguments ready | `{toolCallId, toolName, input: {}}` |
| `tool-output-available` | Tool execution complete (`on_tool_end`) | `{toolCallId, output: {...}}` |

**Format:**
```json
{"type": "tool-input-start", "toolCallId": "call-a1b2", "toolName": "kb_query"}
{"type": "tool-input-available", "toolCallId": "call-a1b2", "toolName": "kb_query", "input": {"query": "..."}}
{"type": "tool-output-available", "toolCallId": "call-a1b2", "output": {"sources": [...]}}
```

### 1.3 Source Document Events

| Event Type | When Emitted | Payload |
|------------|--------------|---------|
| `source-document` | RAG retrieval completes (`on_chain_end`) | `{sourceId, mediaType, title, providerMetadata}` |

**Format:**
```json
{
  "type": "source-document",
  "sourceId": "chunk-123",
  "mediaType": "text/plain",
  "title": "report_2023.pdf",
  "providerMetadata": {
    "custom": {
      "content": "...",
      "score": 0.89,
      "artifact_sha256": "a1b2c3...",
      "chunk_index": 5
    }
  }
}
```

### 1.4 Wire Format

All events are SSE (Server-Sent Events) with JSON payloads:
```
data: {"type":"text-delta","id":"text-1","delta":"Hello"}\n\n
data: {"type":"finish"}\n\n
```

---

## 2. Proposed Event Extensions

### 2.1 Connection Keepalive (HIGH PRIORITY)

**Event:** `ping`
**Interval:** 10 seconds
**Purpose:** Prevent proxy/CDN timeout, detect disconnections
**Payload:** `{timestamp: ISO8601}`

**Implementation:**
```python
# In LangGraphToAISDKAdapter
async def convert_events_stream(...):
    last_ping = time.monotonic()

    async for event in langgraph_events:
        # ... process events ...

        # Emit ping every 10s
        if time.monotonic() - last_ping > 10:
            yield self._sse({"type": "ping", "timestamp": datetime.now(timezone.utc).isoformat()})
            last_ping = time.monotonic()
```

**Frontend:**
```typescript
// In useSSE.ts
eventSource.addEventListener('ping', (e) => {
  // Update lastPingTime, reset stale connection warning
})
```

**Dify equivalent:** `ping` event (emitted every 10s via `MessageStreamManager.ping_thread`)

---

### 2.2 Error Events (HIGH PRIORITY)

**Event:** `error`
**When:** LLM errors, tool failures, rate limits, validation failures
**Payload:** `{code: string, message: string, recoverable: boolean, context?: {}}`

**Error Taxonomy:**
| Code | Scenario | Recoverable | Frontend Action |
|------|----------|-------------|-----------------|
| `rate_limit_exceeded` | LLM API quota hit | Yes | Show retry button after delay |
| `tool_execution_failed` | Tool raised exception | Yes | Show error in tool panel, continue |
| `llm_request_failed` | Network/API error | Yes | Show retry button |
| `validation_error` | Invalid tool arguments | No | Show error message, stop stream |
| `context_length_exceeded` | Input too long | No | Show error, suggest shorter input |
| `unknown_error` | Unhandled exception | No | Show generic error, log to Sentry |

**Implementation:**
```python
# In LangGraphToAISDKAdapter
async def convert_events_stream(...):
    try:
        async for event in langgraph_events:
            # ... process ...
    except RateLimitError as e:
        yield self._sse({
            "type": "error",
            "code": "rate_limit_exceeded",
            "message": str(e),
            "recoverable": True,
            "context": {"retry_after": e.retry_after}
        })
    except ToolExecutionError as e:
        yield self._sse({
            "type": "error",
            "code": "tool_execution_failed",
            "message": str(e),
            "recoverable": True,
            "context": {"tool_name": e.tool_name}
        })
```

**Frontend:**
```typescript
// In assistant-runtime.tsx
if (event.type === 'error') {
  if (event.recoverable) {
    setRetryAvailable(true)
    showToast({ title: event.message, variant: 'warning' })
  } else {
    showToast({ title: event.message, variant: 'destructive' })
    stopStream()
  }
}
```

**Dify equivalent:** `error` event with `status: 500, code: "internal_server_error"`

---

### 2.3 File Attachment Events (MEDIUM PRIORITY)

**Event:** `message-file`
**When:** Agent generates/references files (images, documents, data exports)
**Payload:** `{fileId: string, name: string, type: string, url: string, size?: number}`

**Use Cases:**
- Agent generates a chart image from data
- Agent creates a CSV export of query results
- Agent returns a PDF report

**Implementation:**
```python
# In LangGraphToAISDKAdapter
async def convert_events_stream(...):
    # When agent returns file metadata in tool output
    if "files" in tool_output:
        for file in tool_output["files"]:
            yield self._sse({
                "type": "message-file",
                "fileId": file["id"],
                "name": file["name"],
                "type": file["type"],
                "url": file["url"],
                "size": file.get("size")
            })
```

**Frontend:**
```typescript
// In message renderer
if (event.type === 'message-file') {
  addFile({
    id: event.fileId,
    name: event.name,
    type: event.type,
    url: event.url,
    size: event.size
  })
}
```

**Dify equivalent:** `message_file` event with `type: "image" | "video" | "audio" | "file"`

---

### 2.4 Token Usage & Cost Events (MEDIUM PRIORITY)

**Event:** `usage-update`
**When:** After each LLM call completes (`on_chat_model_end`)
**Payload:** `{inputTokens: number, outputTokens: number, totalTokens: number, cost?: {cents: number, currency: string}}`

**Purpose:**
- Real-time token usage display
- Cost tracking for operators
- Budget alerts

**Implementation:**
```python
# In LangGraphToAISDKAdapter
async def convert_events_stream(...):
    elif event_type == "on_chat_model_end":
        output = event_data.get("output")
        if output:
            usage_metadata = getattr(output, "usage_metadata", None)
            if usage_metadata:
                self._total_input_tokens += usage_metadata.get("input_tokens", 0)
                self._total_output_tokens += usage_metadata.get("output_tokens", 0)

                # Emit usage update
                yield self._sse({
                    "type": "usage-update",
                    "inputTokens": self._total_input_tokens,
                    "outputTokens": self._total_output_tokens,
                    "totalTokens": self._total_input_tokens + self._total_output_tokens
                })
```

**Frontend:**
```typescript
// In message metadata display
if (event.type === 'usage-update') {
  setTokenUsage({
    input: event.inputTokens,
    output: event.outputTokens,
    total: event.totalTokens
  })
}
```

**Dify equivalent:** Included in `message_end` metadata, not streamed incrementally

---

### 2.5 Workflow Step Events (LOW PRIORITY)

**Event:** `workflow-step-start` / `workflow-step-end`
**When:** LangGraph node boundaries (already emitted as `start-step` / `finish-step`)
**Payload:** `{stepId: string, stepName: string, stepType: string, status?: "success" | "failed"}`

**Rationale for LOW priority:**
- Vercel AI SDK already has `start-step` / `finish-step` for this purpose
- LangGraph orchestration is internal; frontend only needs high-level progress
- Node-level tracing belongs in the run ledger, not the streaming UI

**If implemented:**
```python
# In LangGraphToAISDKAdapter
def _start_new_step(self, node_name: str = None) -> str:
    out = ""
    if self._text_started:
        out += self._sse({"type": "text-end", "id": self._text_id})
        self._text_started = False
    if self._step_started:
        out += self._sse({
            "type": "workflow-step-end",
            "stepId": self._current_step_id,
            "status": "success"
        })
        out += self._sse({"type": "finish-step"})
        self._step_started = False

    self._step_count += 1
    self._current_step_id = f"step-{self._step_count}"

    if self._step_count == 1:
        out += self._sse({"type": "start"})

    out += self._sse({"type": "start-step"})

    if node_name:
        out += self._sse({
            "type": "workflow-step-start",
            "stepId": self._current_step_id,
            "stepName": node_name,
            "stepType": "langgraph_node"
        })

    self._step_started = True
    return out
```

**Dify equivalent:** `node_started` / `node_finished` / `node_retry` (workflow engine specific)

---

## 3. Event Mapping: Dify → NYQST

### 3.1 Adopted Events

| Dify Event | NYQST Equivalent | Adoption Status |
|------------|------------------|-----------------|
| `ping` | `ping` | **Adopt** (NEW) |
| `error` | `error` | **Adopt** (NEW) |
| `message_file` | `message-file` | **Adopt** (NEW) |
| `message` | `text-delta` | Already implemented (AI SDK v3 native) |
| `message_end` | `finish` | Already implemented (AI SDK v3 native) |
| `agent_thought` | `reasoning-delta` (o1/o3 models) OR implicit in tool events | Already implemented |
| `text_chunk` | `text-delta` | Already implemented |

### 3.2 Rejected Events (Workflow Engine Specific)

| Dify Event | Rationale for Rejection |
|------------|------------------------|
| `workflow_started` / `workflow_finished` | LangGraph orchestration is internal; frontend only needs `start` / `finish` |
| `node_started` / `node_finished` | Node execution is an implementation detail; use `start-step` / `finish-step` |
| `iteration_started` / `iteration_next` / `iteration_completed` | Loop constructs are internal to LangGraph; not exposed to UI |
| `loop_started` / `loop_next` / `loop_completed` | Loop constructs are internal to LangGraph; not exposed to UI |
| `parallel_branch_started` / `parallel_branch_finished` | Parallel execution is internal; no UI representation |
| `node_retry` | Retry logic is internal; errors surface via `error` event |

### 3.3 Rejected Events (Out of Scope)

| Dify Event | Rationale for Rejection |
|------------|------------------------|
| `tts_message` / `tts_message_end` | TTS not in scope for NYQST bootstrap |
| `message_replace` | Content moderation not in scope |
| `datasource_processing` / `datasource_completed` / `datasource_error` | Dataset indexing is synchronous in NYQST |
| `agent_log` | Debug logging belongs in run ledger, not streaming UI |

---

## 4. Vercel AI SDK Integration

### 4.1 AI SDK v3 Stream Parts

The Vercel AI SDK v3 defines standard stream part types in `@ai-sdk/provider`:

**Core protocol:**
```typescript
// Text streaming
type TextStreamPart =
  | { type: 'text-start', id: string }
  | { type: 'text-delta', id: string, delta: string }
  | { type: 'text-end', id: string }

// Tool calling
type ToolStreamPart =
  | { type: 'tool-input-start', toolCallId: string, toolName: string }
  | { type: 'tool-input-available', toolCallId: string, toolName: string, input: unknown }
  | { type: 'tool-output-available', toolCallId: string, output: unknown }

// Step boundaries
type StepStreamPart =
  | { type: 'start-step' }
  | { type: 'finish-step' }

// Lifecycle
type LifecycleStreamPart =
  | { type: 'start' }
  | { type: 'finish' }

// Reasoning (o1 models)
type ReasoningStreamPart =
  | { type: 'reasoning-start', id: string }
  | { type: 'reasoning-delta', id: string, delta: string }
  | { type: 'reasoning-end', id: string }
```

**Extension mechanism:**
- Custom events are allowed via `providerMetadata` on standard parts
- Or as standalone JSON events with custom `type` field

### 4.2 NYQST Extension Strategy

**Use AI SDK native types where possible:**
- `text-*`, `tool-*`, `reasoning-*`, `start-*`, `finish-*` events

**Add custom types for NYQST-specific concerns:**
- `ping`, `error`, `message-file`, `usage-update`, `source-document`

**Frontend adapter pattern:**
```typescript
// In assistant-runtime.tsx
const handleSSEEvent = (event: SSEEvent) => {
  // AI SDK native events pass through
  if (isAISDKNativeEvent(event.type)) {
    sdkStreamWriter.write(event)
  }

  // Custom events handled separately
  switch (event.type) {
    case 'ping':
      updateConnectionHealth()
      break
    case 'error':
      handleErrorEvent(event)
      break
    case 'message-file':
      addFileToMessage(event)
      break
    case 'usage-update':
      updateTokenUsage(event)
      break
  }
}
```

### 4.3 SSE Wire Format

All events use SSE `data:` lines with JSON payloads:

```
data: {"type":"start"}\n\n
data: {"type":"text-start","id":"text-1"}\n\n
data: {"type":"text-delta","id":"text-1","delta":"Hello"}\n\n
data: {"type":"text-delta","id":"text-1","delta":" world"}\n\n
data: {"type":"text-end","id":"text-1"}\n\n
data: {"type":"usage-update","inputTokens":50,"outputTokens":12,"totalTokens":62}\n\n
data: {"type":"finish"}\n\n
```

Named event types (non-data):
```
event: ping\n\n
event: error\n
data: {"code":"rate_limit_exceeded","message":"..."}\n\n
```

---

## 5. Frontend Event Handler Patterns

### 5.1 Event Handler Architecture

```typescript
// ui/src/providers/assistant-runtime.tsx
export function AssistantRuntimeProvider({ children }: { children: React.ReactNode }) {
  const [messages, setMessages] = useState<Message[]>([])
  const [currentMessage, setCurrentMessage] = useState<MessageState | null>(null)
  const [connectionHealth, setConnectionHealth] = useState<'healthy' | 'stale' | 'disconnected'>('healthy')

  const handleSSEEvent = useCallback((eventType: string, data: unknown) => {
    switch (eventType) {
      case 'start':
        setCurrentMessage({ id: generateId(), content: '', role: 'assistant' })
        break

      case 'text-delta':
        setCurrentMessage(prev => prev ? { ...prev, content: prev.content + data.delta } : null)
        break

      case 'text-end':
        setMessages(prev => [...prev, currentMessage!])
        setCurrentMessage(null)
        break

      case 'tool-input-start':
        // Show tool execution indicator
        break

      case 'tool-output-available':
        // Display tool result
        break

      case 'source-document':
        // Add citation to message
        break

      case 'reasoning-delta':
        // Append to think block
        break

      case 'ping':
        setConnectionHealth('healthy')
        break

      case 'error':
        handleErrorEvent(data as ErrorEvent)
        break

      case 'message-file':
        addFileToCurrentMessage(data as FileEvent)
        break

      case 'usage-update':
        setTokenUsage(data as UsageEvent)
        break
    }
  }, [currentMessage])

  // Connection health monitoring
  useEffect(() => {
    const interval = setInterval(() => {
      const timeSinceLastPing = Date.now() - lastPingTime
      if (timeSinceLastPing > 15000) {
        setConnectionHealth('stale')
      }
      if (timeSinceLastPing > 30000) {
        setConnectionHealth('disconnected')
      }
    }, 5000)
    return () => clearInterval(interval)
  }, [lastPingTime])

  return (
    <AssistantRuntimeContext.Provider value={{ messages, connectionHealth, ... }}>
      {children}
    </AssistantRuntimeContext.Provider>
  )
}
```

### 5.2 Error Event Handling

```typescript
// ui/src/components/chat/error-display.tsx
const handleErrorEvent = (event: ErrorEvent) => {
  const { code, message, recoverable, context } = event

  switch (code) {
    case 'rate_limit_exceeded':
      showToast({
        title: 'Rate limit reached',
        description: `Please wait ${context.retry_after} seconds before retrying`,
        variant: 'warning',
        action: <Button onClick={retryAfterDelay}>Retry</Button>
      })
      break

    case 'tool_execution_failed':
      addErrorToToolPanel(context.tool_name, message)
      break

    case 'llm_request_failed':
      showToast({
        title: 'Request failed',
        description: message,
        variant: 'destructive',
        action: recoverable ? <Button onClick={retry}>Retry</Button> : null
      })
      break

    case 'context_length_exceeded':
      showToast({
        title: 'Input too long',
        description: 'Please shorten your message and try again',
        variant: 'destructive'
      })
      stopStream()
      break

    default:
      showToast({
        title: 'An error occurred',
        description: message,
        variant: 'destructive'
      })
      logToSentry(event)
      break
  }
}
```

### 5.3 Tool Execution Display

```typescript
// ui/src/components/chat/tool-panel.tsx
export function ToolPanel({ toolCalls }: { toolCalls: ToolCall[] }) {
  return (
    <div className="space-y-2">
      {toolCalls.map(call => (
        <Collapsible key={call.id} defaultOpen={call.status === 'running'}>
          <CollapsibleTrigger className="flex items-center gap-2">
            {call.status === 'running' && <Spinner />}
            {call.status === 'success' && <CheckCircle className="text-green-600" />}
            {call.status === 'error' && <AlertCircle className="text-red-600" />}
            <span className="font-medium">{call.toolName}</span>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <div className="mt-2 space-y-2">
              <div>
                <div className="text-sm font-medium text-muted-foreground">Input</div>
                <pre className="text-xs bg-muted p-2 rounded overflow-x-auto">
                  {JSON.stringify(call.input, null, 2)}
                </pre>
              </div>
              {call.output && (
                <div>
                  <div className="text-sm font-medium text-muted-foreground">Output</div>
                  <pre className="text-xs bg-muted p-2 rounded overflow-x-auto">
                    {JSON.stringify(call.output, null, 2)}
                  </pre>
                </div>
              )}
              {call.error && (
                <div className="text-sm text-red-600">{call.error}</div>
              )}
            </div>
          </CollapsibleContent>
        </Collapsible>
      ))}
    </div>
  )
}
```

---

## 6. SSE Reconnection Strategy

### 6.1 Current Implementation (useSSE Hook)

```typescript
// ui/src/hooks/use-sse.ts
export function useSSE({ url, onEvent, enabled, reconnectDelay = 3000, maxReconnectAttempts = 5 }) {
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  const reconnectAttemptsRef = useRef(0)

  const connect = useCallback(() => {
    setStatus('connecting')
    const eventSource = new EventSource(url)

    eventSource.onopen = () => {
      setStatus('connected')
      reconnectAttemptsRef.current = 0
    }

    eventSource.onerror = (error) => {
      setStatus('error')

      // Exponential backoff reconnection
      if (reconnectAttemptsRef.current < maxReconnectAttempts) {
        reconnectAttemptsRef.current++
        const delay = reconnectDelay * Math.pow(2, reconnectAttemptsRef.current - 1)
        setTimeout(connect, delay)
      } else {
        disconnect()
      }
    }

    // ... event handlers ...
  }, [url])

  return { status, reconnect, disconnect }
}
```

### 6.2 Enhanced Strategy with Ping Events

**Add ping-based connection health monitoring:**

```typescript
export function useSSE({ ... }) {
  const [connectionHealth, setConnectionHealth] = useState<'healthy' | 'stale' | 'disconnected'>('disconnected')
  const lastPingTimeRef = useRef<number>(Date.now())

  // Monitor ping events
  useEffect(() => {
    const interval = setInterval(() => {
      const timeSinceLastPing = Date.now() - lastPingTimeRef.current

      if (timeSinceLastPing > 15000) {
        setConnectionHealth('stale')
      }
      if (timeSinceLastPing > 30000) {
        setConnectionHealth('disconnected')
        reconnect()
      }
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  // Update ping time on ping events
  eventSource.addEventListener('ping', () => {
    lastPingTimeRef.current = Date.now()
    setConnectionHealth('healthy')
  })

  return { status, connectionHealth, reconnect, disconnect }
}
```

**Connection health UI:**

```typescript
// ui/src/components/chat/connection-indicator.tsx
export function ConnectionIndicator({ health }: { health: 'healthy' | 'stale' | 'disconnected' }) {
  if (health === 'healthy') return null

  return (
    <div className={cn(
      "px-3 py-1 rounded-full text-xs font-medium",
      health === 'stale' && "bg-yellow-100 text-yellow-800",
      health === 'disconnected' && "bg-red-100 text-red-800"
    )}>
      {health === 'stale' && 'Connection unstable'}
      {health === 'disconnected' && 'Reconnecting...'}
    </div>
  )
}
```

### 6.3 Reconnection Backoff Strategy

| Attempt | Delay | Total Elapsed |
|---------|-------|---------------|
| 1 | 3s | 3s |
| 2 | 6s | 9s |
| 3 | 12s | 21s |
| 4 | 24s | 45s |
| 5 | 48s | 93s |

After 5 failed attempts, give up and show permanent error.

---

## 7. Complete Event Type Catalog (Final)

### 7.1 NYQST Event Types (14 total)

| Event Type | Category | Priority | Source |
|------------|----------|----------|--------|
| `start` | Lifecycle | Core | AI SDK v3 |
| `start-step` | Lifecycle | Core | AI SDK v3 |
| `finish-step` | Lifecycle | Core | AI SDK v3 |
| `finish` | Lifecycle | Core | AI SDK v3 |
| `text-start` | Text streaming | Core | AI SDK v3 |
| `text-delta` | Text streaming | Core | AI SDK v3 |
| `text-end` | Text streaming | Core | AI SDK v3 |
| `reasoning-start` | Reasoning (o1/o3) | Core | AI SDK v3 |
| `reasoning-delta` | Reasoning (o1/o3) | Core | AI SDK v3 |
| `reasoning-end` | Reasoning (o1/o3) | Core | AI SDK v3 |
| `tool-input-start` | Tool execution | Core | AI SDK v3 |
| `tool-input-available` | Tool execution | Core | AI SDK v3 |
| `tool-output-available` | Tool execution | Core | AI SDK v3 |
| `source-document` | RAG citations | Core | NYQST custom |
| **`ping`** | Connection health | **NEW** | Dify-inspired |
| **`error`** | Error handling | **NEW** | Dify-inspired |
| **`message-file`** | File attachments | **NEW** | Dify-inspired |
| **`usage-update`** | Token tracking | **NEW** | NYQST custom |

**Total: 18 event types (14 existing + 4 new)**

### 7.2 Event Schema Definitions

```typescript
// ui/src/types/sse-events.ts

// Lifecycle events
export type LifecycleEvent =
  | { type: 'start' }
  | { type: 'start-step' }
  | { type: 'finish-step' }
  | { type: 'finish' }

// Text streaming events
export type TextStreamEvent =
  | { type: 'text-start', id: string }
  | { type: 'text-delta', id: string, delta: string }
  | { type: 'text-end', id: string }

// Reasoning events (o1/o3/o4-mini models)
export type ReasoningEvent =
  | { type: 'reasoning-start', id: string }
  | { type: 'reasoning-delta', id: string, delta: string }
  | { type: 'reasoning-end', id: string }

// Tool execution events
export type ToolEvent =
  | { type: 'tool-input-start', toolCallId: string, toolName: string }
  | { type: 'tool-input-available', toolCallId: string, toolName: string, input: unknown }
  | { type: 'tool-output-available', toolCallId: string, output: unknown }

// Source document events (RAG citations)
export type SourceDocumentEvent = {
  type: 'source-document'
  sourceId: string
  mediaType: string
  title: string
  providerMetadata: {
    custom: {
      content: string
      score: number
      artifact_sha256: string
      chunk_index: number
    }
  }
}

// Connection health events
export type PingEvent = {
  type: 'ping'
  timestamp: string
}

// Error events
export type ErrorEvent = {
  type: 'error'
  code: 'rate_limit_exceeded' | 'tool_execution_failed' | 'llm_request_failed' | 'validation_error' | 'context_length_exceeded' | 'unknown_error'
  message: string
  recoverable: boolean
  context?: Record<string, unknown>
}

// File attachment events
export type MessageFileEvent = {
  type: 'message-file'
  fileId: string
  name: string
  type: string
  url: string
  size?: number
}

// Token usage events
export type UsageUpdateEvent = {
  type: 'usage-update'
  inputTokens: number
  outputTokens: number
  totalTokens: number
  cost?: {
    cents: number
    currency: string
  }
}

// Union of all event types
export type SSEEvent =
  | LifecycleEvent
  | TextStreamEvent
  | ReasoningEvent
  | ToolEvent
  | SourceDocumentEvent
  | PingEvent
  | ErrorEvent
  | MessageFileEvent
  | UsageUpdateEvent
```

---

## 8. Implementation Roadmap

### Phase 1: Connection Health (Week 1)
- [ ] Add `ping` event emission (10s interval) in `LangGraphToAISDKAdapter`
- [ ] Update `useSSE` hook with ping monitoring
- [ ] Add connection health indicator to chat UI
- [ ] Test reconnection strategy under network disruption

### Phase 2: Error Handling (Week 1)
- [ ] Define error taxonomy and codes
- [ ] Add error event emission for common failure scenarios
- [ ] Implement frontend error handler with retry logic
- [ ] Add error display components (toast, inline)

### Phase 3: Token Usage (Week 2)
- [ ] Add `usage-update` event emission after LLM calls
- [ ] Update message metadata display with token counts
- [ ] Add cost calculation (optional, requires rate card)
- [ ] Implement usage tracking in run ledger

### Phase 4: File Attachments (Week 2-3)
- [ ] Define file metadata schema
- [ ] Add `message-file` event emission for agent-generated files
- [ ] Implement file display components (image preview, download links)
- [ ] Update message renderer to show file attachments

### Phase 5: Testing & Documentation (Week 3)
- [ ] Unit tests for event emission
- [ ] Integration tests for SSE stream
- [ ] Frontend tests for event handlers
- [ ] Update API documentation with event catalog
- [ ] Update ADR-008 (MCP Tool Architecture) with event types

---

## 9. Testing Strategy

### 9.1 Backend Tests

**Unit tests for `LangGraphToAISDKAdapter`:**

```python
# tests/unit/agents/adapters/test_langgraph_to_aisdk_adapter.py

@pytest.mark.asyncio
async def test_ping_event_emission():
    adapter = LangGraphToAISDKAdapter()

    async def mock_stream():
        await asyncio.sleep(11)  # Force ping
        yield {"generate": {"messages": [{"content": "test"}]}}

    events = []
    async for chunk in adapter.convert_events_stream(mock_stream()):
        event = json.loads(chunk.replace("data: ", "").strip())
        events.append(event)

    ping_events = [e for e in events if e["type"] == "ping"]
    assert len(ping_events) >= 1
    assert "timestamp" in ping_events[0]

@pytest.mark.asyncio
async def test_error_event_emission():
    adapter = LangGraphToAISDKAdapter()

    async def mock_stream():
        raise RateLimitError("Quota exceeded", retry_after=60)

    events = []
    try:
        async for chunk in adapter.convert_events_stream(mock_stream()):
            event = json.loads(chunk.replace("data: ", "").strip())
            events.append(event)
    except:
        pass

    error_events = [e for e in events if e["type"] == "error"]
    assert len(error_events) == 1
    assert error_events[0]["code"] == "rate_limit_exceeded"
    assert error_events[0]["recoverable"] is True

@pytest.mark.asyncio
async def test_usage_update_emission():
    adapter = LangGraphToAISDKAdapter()

    async def mock_stream():
        # Simulate on_chat_model_end with usage metadata
        yield {
            "event": "on_chat_model_end",
            "data": {
                "output": MockLLMOutput(usage_metadata={"input_tokens": 50, "output_tokens": 12})
            }
        }

    events = []
    async for chunk in adapter.convert_events_stream(mock_stream()):
        event = json.loads(chunk.replace("data: ", "").strip())
        events.append(event)

    usage_events = [e for e in events if e["type"] == "usage-update"]
    assert len(usage_events) == 1
    assert usage_events[0]["inputTokens"] == 50
    assert usage_events[0]["outputTokens"] == 12
```

### 9.2 Frontend Tests

**React component tests:**

```typescript
// ui/src/components/chat/__tests__/error-display.test.tsx

describe('ErrorDisplay', () => {
  it('shows retry button for recoverable errors', () => {
    const errorEvent: ErrorEvent = {
      type: 'error',
      code: 'rate_limit_exceeded',
      message: 'Rate limit hit',
      recoverable: true,
      context: { retry_after: 60 }
    }

    const { getByText } = render(<ErrorDisplay event={errorEvent} />)
    expect(getByText('Retry')).toBeInTheDocument()
  })

  it('does not show retry button for non-recoverable errors', () => {
    const errorEvent: ErrorEvent = {
      type: 'error',
      code: 'context_length_exceeded',
      message: 'Input too long',
      recoverable: false
    }

    const { queryByText } = render(<ErrorDisplay event={errorEvent} />)
    expect(queryByText('Retry')).not.toBeInTheDocument()
  })
})
```

### 9.3 Integration Tests

**SSE contract test:**

```typescript
// ui/src/test/__tests__/sse-contract.test.ts

describe('SSE Stream Contract', () => {
  it('handles ping events correctly', async () => {
    const { result } = renderHook(() => useSSE({
      url: '/api/v1/agent/stream',
      onEvent: jest.fn()
    }))

    // Simulate ping event
    const pingEvent = new MessageEvent('ping', {
      data: JSON.stringify({ type: 'ping', timestamp: '2026-02-04T10:00:00Z' })
    })

    act(() => {
      window.dispatchEvent(pingEvent)
    })

    expect(result.current.connectionHealth).toBe('healthy')
  })

  it('detects stale connections', async () => {
    jest.useFakeTimers()

    const { result } = renderHook(() => useSSE({
      url: '/api/v1/agent/stream',
      onEvent: jest.fn()
    }))

    // Fast-forward 20 seconds (no ping received)
    act(() => {
      jest.advanceTimersByTime(20000)
    })

    expect(result.current.connectionHealth).toBe('stale')

    jest.useRealTimers()
  })
})
```

---

## 10. Summary & Recommendations

### 10.1 Final Event Count: 18 (+4 from current 14)

**New events to implement:**
1. `ping` — Connection keepalive (HIGH priority)
2. `error` — Structured error handling (HIGH priority)
3. `message-file` — File attachments (MEDIUM priority)
4. `usage-update` — Token tracking (MEDIUM priority)

**Rejected Dify events (11 total):**
- Workflow engine events: `workflow_started`, `workflow_finished`, `node_started`, `node_finished`, `node_retry`, `iteration_*`, `loop_*`, `parallel_branch_*`
- Out-of-scope: `tts_message`, `message_replace`, `datasource_*`, `agent_log`

### 10.2 Design Rationale

**Why 18 instead of 25+?**
- NYQST uses LangGraph for orchestration (internal), not a visual workflow builder (exposed)
- Node-level execution events belong in the run ledger, not the streaming UI
- Vercel AI SDK already provides step boundaries (`start-step` / `finish-step`)
- TTS, content moderation, and dataset indexing are out of scope for bootstrap

**Why these 4 new events?**
- `ping` — Essential for connection health monitoring and proxy timeout prevention
- `error` — Required for robust error handling and retry logic
- `message-file` — Enables agent-generated artifacts (charts, exports)
- `usage-update` — Critical for cost visibility and budget control

### 10.3 Vercel AI SDK Compatibility

**Preserved:**
- All AI SDK v3 native events continue to work unchanged
- Custom events are additive, not breaking changes
- Frontend can use standard `useChat` hook + custom event handlers

**Extended:**
- `source-document` event uses AI SDK's `providerMetadata` pattern
- Custom events follow AI SDK naming conventions (kebab-case, descriptive)
- All events are JSON-serializable and type-safe

### 10.4 Next Steps

1. **Draft ADR-011** (LangGraph-MCP Bridge) — specify event emission points in agent graph
2. **Update ADR-008** (MCP Tool Architecture) — add event catalog to Resources section
3. **Implement Phase 1** (Connection Health) — ping events + reconnection strategy
4. **Test in production** — monitor connection stability and error rates
5. **Iterate based on feedback** — add more events only if frontend needs them

---

## Appendix A: Event Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ LangGraph Agent                                             │
│                                                             │
│  retrieve_node → generate_node → tool_node → generate_node │
│       ↓              ↓              ↓              ↓        │
└───────┼──────────────┼──────────────┼──────────────┼────────┘
        │              │              │              │
        ↓              ↓              ↓              ↓
┌─────────────────────────────────────────────────────────────┐
│ LangGraphToAISDKAdapter                                     │
│                                                             │
│  Emit: start → start-step → text-start → text-delta... →   │
│        tool-input-start → tool-input-available →           │
│        tool-output-available → source-document →           │
│        usage-update → ping (every 10s) → finish            │
│                                                             │
└───────┼─────────────────────────────────────────────────────┘
        │
        ↓  SSE over HTTP
        ↓
┌─────────────────────────────────────────────────────────────┐
│ Frontend (useSSE hook)                                      │
│                                                             │
│  EventSource → Parse SSE → Dispatch to handlers            │
│                                                             │
│  • text-delta → append to message                          │
│  • tool-* → update tool panel                              │
│  • source-document → add citation                          │
│  • ping → update connection health                         │
│  • error → show error UI + retry logic                     │
│  • usage-update → display token count                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Appendix B: Comparison Table

| Aspect | NYQST Current | NYQST Proposed | Dify |
|--------|---------------|----------------|------|
| **Event count** | 14 | 18 (+4) | 25+ |
| **Connection keepalive** | No | Yes (ping) | Yes (ping) |
| **Error handling** | Basic | Structured (error event) | Structured |
| **File attachments** | No | Yes (message-file) | Yes (message_file) |
| **Token tracking** | Run ledger only | Streamed (usage-update) | In message_end |
| **Workflow events** | Step boundaries only | Step boundaries only | Full node trace |
| **Tool execution** | Yes (AI SDK v3) | Yes (AI SDK v3) | Yes (agent_thought) |
| **Reasoning display** | Yes (o1/o3) | Yes (o1/o3) | No (basic thought only) |
| **TTS streaming** | No | No | Yes (tts_message) |
| **Content moderation** | No | No | Yes (message_replace) |
| **Frontend SDK** | Vercel AI SDK v3 | Vercel AI SDK v3 | Custom SSE parser |
| **Reconnection** | Exponential backoff | Exponential backoff + ping health | Basic retry |

**Key differences from Dify:**
- NYQST uses Vercel AI SDK v3 (better maintainability than custom SSE parser)
- NYQST has fewer events because LangGraph orchestration is internal
- NYQST has reasoning events (o1/o3 support) that Dify lacks
- NYQST lacks TTS and content moderation (out of scope for bootstrap)

---

**End of Specification**

**Next Actions:**
1. Review this spec with Mark
2. Update ADR-008 with event catalog
3. Begin Phase 1 implementation (ping events)
4. Test connection health monitoring in staging
