# AI SDK v3 Streaming Migration

## Problem
The backend adapter (`src/intelli/agents/adapters/__init__.py`) was outputting AI SDK **v2** data stream protocol (`0:"text"`, `2:[data]`, `d:{done}`) but the frontend has AI SDK **v3** (`@ai-sdk/react@3.0.59`, `ai@6.0.57`) which expects SSE-wrapped JSON events.

## v2 vs v3 Wire Format

**v2 (old, broken):**
```
0:"Hello"
0:" world"
2:[{"type":"sources","sources":[...]}]
d:{"finishReason":"stop"}
```

**v3 (current, working):**
```
data: {"type":"start"}

data: {"type":"start-step"}

data: {"type":"source-document","sourceId":"...","mediaType":"text/plain","title":"...","providerMetadata":{"custom":{...}}}

data: {"type":"text-start","id":"text-1"}

data: {"type":"text-delta","id":"text-1","delta":"Hello"}

data: {"type":"text-end","id":"text-1"}

data: {"type":"finish-step"}

data: {"type":"finish"}
```

## Key v3 Requirements

1. **Content-Type**: `text/event-stream` (same as before)
2. **Required header**: `X-Vercel-AI-UI-Message-Stream: v1` — tells SDK which parser to use
3. **SSE format**: Each event is `data: {json}\n\n`
4. **Strict Zod validation**: Every event must match `uiMessageChunkSchema` exactly. No custom types allowed.
5. **No generic "data" type**: Must use specific types: `text-start`, `text-delta`, `text-end`, `source-document`, `source-url`, `start`, `start-step`, `finish-step`, `finish`, etc.
6. **Event lifecycle must be complete**: `start` → `start-step` → `text-start` → `text-delta`(s) → `text-end` → `finish-step` → `finish`

## Sources in v3

There is no generic data channel. RAG sources must be emitted as individual `source-document` events:
```json
{
  "type": "source-document",
  "sourceId": "chunk-uuid",
  "mediaType": "text/plain",
  "title": "filename.txt",
  "providerMetadata": {
    "custom": {
      "content": "chunk text...",
      "score": 0.95,
      "artifact_sha256": "abc123...",
      "chunk_index": 0
    }
  }
}
```

Custom data goes in `providerMetadata.custom` — that's the SDK's escape hatch.

## Frontend Transport

- **Use `DefaultChatTransport`** (parses SSE JSON events via `eventsource-parser`)
- **NOT `TextStreamChatTransport`** (treats entire stream as plain text, no parsing)
- `prepareSendMessagesRequest` converts UIMessage parts format to backend's `{role, content}` format

## Frontend Source Extraction

Sources arrive as `source-document` parts on UIMessage. Extract via:
```typescript
message.parts
  .filter(p => p.type === 'source-document')
  .map(p => ({
    chunk_id: p.sourceId,
    content: p.providerMetadata?.custom?.content,
    score: p.providerMetadata?.custom?.score,
    // etc
  }))
```

## Files Modified (fix/ai-sdk-v3-sse-streaming branch)

- `src/intelli/agents/adapters/__init__.py` — SSE output with v3 event types
- `src/intelli/api/v1/agent.py` — Added `X-Vercel-AI-UI-Message-Stream: v1` header
- `ui/src/hooks/use-agent-chat.ts` — DefaultChatTransport, source extraction from parts
- `ui/src/pages/ResearchPage.tsx` — Consumes sources from hook, UIMessage parts rendering

## Test Coverage (commit `acfe1c4`)

**Adapter: 100% coverage (45 tests)** — `tests/unit/agents/adapters/test_langgraph_to_aisdk_adapter.py`
- SSE wire format validation (every line is `data: {json}\n\n`)
- Event lifecycle contract (start → start-step → text-start → text-delta → text-end → finish-step → finish)
- Source-document events with providerMetadata.custom fields
- State management idempotency (_ensure_start, _ensure_text_start)
- convert_stream (astream mode) and convert_events_stream (astream_events mode)
- Ledger integration for tool start/end events

**Known gap: no contract test between adapter output and AI SDK transport input.**
The adapter tests verify output format. The hook tests verify source extraction from hydrated UIMessages. But nothing proves the AI SDK `DefaultChatTransport` can actually parse our SSE output. This is the exact boundary where v2→v3 broke. See issue #9.
