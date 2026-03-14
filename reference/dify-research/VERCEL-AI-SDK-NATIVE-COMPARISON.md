# Vercel AI SDK Native Features: What We're Missing with Python Backend

**Date:** 2026-02-04
**Author:** Claude Sonnet 4.5
**Purpose:** Understand the gap between NYQST's Python backend + AI SDK adapter vs. native TypeScript AI SDK integration

---

## Executive Summary

NYQST uses the Vercel AI SDK v3 Data Stream Protocol on the frontend but **cannot leverage 80% of AI SDK's native backend features** because our agent runtime is Python (LangGraph) + FastAPI, not TypeScript. The AI SDK's `streamText()`, React Server Components integration, and built-in agent loop only work with native TypeScript backends. We've built a correct adapter (`LangGraphToAISDKAdapter`) that translates LangGraph events to AI SDK SSE format, but this is **manual plumbing** that AI SDK handles automatically in native setups.

**Trade-off:** We gain LangGraph's stateful checkpointing, graph workflows, and human-in-the-loop capabilities (which AI SDK lacks). We lose automatic tool call handling, server-side message persistence patterns, and RSC streaming. The Python backend is the right choice for our domain (complex workflows, MCP tools, audit requirements), but we must accept we're building infrastructure that AI SDK gives away for free to TypeScript shops.

---

## 1. streamText() with Native Backend

### What AI SDK Offers Natively

In a native TypeScript backend (Next.js API route), `streamText()` handles:

```typescript
// app/api/chat/route.ts
import { openai } from '@ai-sdk/openai';
import { streamText, convertToModelMessages } from 'ai';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-4o'),
    messages: await convertToModelMessages(messages),
    tools: {
      getWeatherInformation: {
        description: 'show the weather in a given city to the user',
        inputSchema: z.object({ city: z.string() }),
        execute: async ({ city }: { city: string }) => {
          return `Weather in ${city}: 72°F`;
        },
      },
    },
    stopWhen: stepCountIs(5),
  });

  return result.toUIMessageStreamResponse();
}
```

**What happens automatically:**
1. **Tool execution** — AI SDK invokes `execute()` functions server-side, **in the same process**, without external RPC
2. **Multi-step loop** — `stopWhen` condition controls automatic tool call loops (up to 5 steps in this example)
3. **SSE formatting** — `toUIMessageStreamResponse()` converts to Data Stream Protocol (text chunks, tool calls, finish events) with zero boilerplate
4. **Error handling** — `onError` callback option for custom error messages, default fallback included
5. **Backpressure** — Stream only generates tokens as client consumes them (built-in flow control)

**Configuration options for `toUIMessageStreamResponse()`:**
- `sendReasoning: true` — Stream model reasoning steps (for o1 models)
- `sendSources: true` — Include RAG sources in stream
- `sendFinish: false` — Omit finish event (for multi-part responses)
- `consumeSseStream` — Required for proper abort handling

### What NYQST Does Instead

Our `LangGraphToAISDKAdapter` manually constructs SSE events from LangGraph's `astream_events`:

```python
# intelli/agents/adapters/langgraph_to_aisdk.py
async def stream(self, event_stream: AsyncIterator) -> AsyncIterator[str]:
    async for event in event_stream:
        event_type = event.get("event")

        if event_type == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            yield f'0:"{chunk.content}"\n'

        elif event_type == "on_tool_start":
            yield f'9:{{"toolCallId":"{tool_id}","toolName":"{name}"}}\n'

        elif event_type == "on_tool_end":
            yield f'a:{{"toolCallId":"{tool_id}","result":{result}}}\n'

        elif event_type == "on_chain_end":
            yield f'd:{{"finishReason":"stop"}}\n'
```

**What we handle manually:**
1. **Event mapping** — 10+ LangGraph event types → 6 AI SDK event types (see `NYQST-SSE-EVENT-SPECIFICATION.md`)
2. **Tool execution** — Happens in `MCPToolNode`, which dispatches to `ToolExecutionPipeline` (5 stages: validate → policy → execute → log → return)
3. **Multi-step loop** — LangGraph's conditional edges + recursion limit, not a simple `stopWhen` predicate
4. **SSE formatting** — Hand-written string formatting with JSON escaping
5. **Error handling** — Custom logic in adapter, not a configuration option

### Comparison

| Capability | Native AI SDK | NYQST Adapter | Gap |
|------------|---------------|---------------|-----|
| **Setup complexity** | 5 lines (streamText + toUIMessageStreamResponse) | 200 lines (adapter + event listener + MCPToolNode) | 40x more code |
| **Tool execution** | Inline `execute` functions | Separate MCP tool handlers via pipeline | More flexible but complex |
| **Multi-step control** | `stopWhen(stepCountIs(5))` | LangGraph recursion limit + conditional edges | More powerful but harder to configure |
| **Source streaming** | `sendSources: true` option | Custom `source-document` data event | Parity (both work) |
| **Error messages** | `onError: (e) => "Try again"` | Adapter-level try/catch | Parity |
| **Abort handling** | `consumeSseStream` helper | FastAPI background task cancellation | Both work |

**What we gain:** Tool execution goes through the full MCP pipeline (policy checks, run ledger, retry logic). Native AI SDK tools have no policy layer, no audit trail, no approval gates.

**What we lose:** Simplicity. A native AI SDK backend is 40x less code for basic streaming + tool calls.

---

## 2. Tool Loop Agent: AI SDK vs. LangGraph

### AI SDK's Agent Loop

AI SDK supports **manual agent loops** but not graph workflows:

```typescript
// Manual loop with tool execution
const messages: ModelMessage[] = [{ role: 'user', content: 'Get weather in NYC and SF' }];

let step = 0;
const maxSteps = 10;

while (step < maxSteps) {
  const result = await generateText({
    model: openai('gpt-4o'),
    messages,
    tools: { getWeather: tool({ ... }) },
  });

  messages.push(...result.response.messages);

  if (result.text) break; // Stop when model generates text
  step++;
}
```

**Capabilities:**
- Basic tool calling with automatic `execute()` invocation
- Multi-step reasoning (model can call tools multiple times)
- Message history management (append assistant + tool messages)
- Termination control (break on text, max steps, custom condition)

**Limitations:**
- **No graph workflows** — Cannot define state machines, parallel branches, conditional routing beyond "tools vs. no tools"
- **No checkpointing** — If the loop crashes at step 5, you start over
- **No human-in-the-loop** — No built-in approval gates or pausing
- **No observability** — No structured event log (you build it yourself)

### LangGraph's Agent Loop

Our `ResearchAssistantGraph` is a stateful workflow:

```python
graph = StateGraph(ResearchState)
graph.add_node("agent", agent_node)           # LLM decides next action
graph.add_node("tools", MCPToolNode(...))     # Execute tools via MCP pipeline
graph.add_conditional_edges("agent", tools_condition, {
    "tools": "tools",
    END: END
})
graph.add_edge("tools", "agent")  # Loop back for multi-step
graph = graph.compile(checkpointer=PostgresSaver(engine))
```

**Capabilities:**
- **Graph workflows** — Arbitrary state machines with parallel branches, sub-graphs, conditional routing
- **Checkpointing** — Full state snapshots after every node, stored in PostgreSQL (resume/retry/branch from any point)
- **Human-in-the-loop** — `interrupt()` primitive pauses graph, external system approves, graph resumes
- **Observability** — `astream_events` emits 10+ event types for every node, tool, LLM call
- **Multi-agent** — Multiple graphs can call each other, share state via checkpoints

**Limitations:**
- **Complexity** — 10x more code than AI SDK's manual loop
- **No built-in UI** — AI SDK's `useChat` hook expects simple message arrays, not graph state

### Comparison

| Capability | AI SDK Agent Loop | LangGraph | Winner |
|------------|-------------------|-----------|--------|
| **Basic tool calling** | Yes | Yes | Tie |
| **Multi-step reasoning** | Yes (manual while loop) | Yes (graph edges) | Tie |
| **Conditional routing** | Basic (tools vs. text) | Arbitrary (graph conditionals) | LangGraph |
| **Parallel execution** | No | Yes (parallel branches) | LangGraph |
| **Checkpointing** | No | Yes (PostgreSQL/SQLite) | LangGraph |
| **Resume after crash** | No | Yes | LangGraph |
| **Human approval gates** | No | Yes (`interrupt()`) | LangGraph |
| **Observability** | Basic (you log manually) | Full (astream_events) | LangGraph |
| **Setup complexity** | Low (10 lines) | High (100+ lines) | AI SDK |

**Verdict:** For simple chatbots, AI SDK's loop is sufficient. For NYQST's requirements (audit trail, policy checks, approval gates, workflow complexity), LangGraph is mandatory. AI SDK has no equivalent.

---

## 3. Message Persistence Patterns

### AI SDK's Recommendation

AI SDK does not include a database adapter. The docs recommend:

```typescript
// Save messages in onFinish callback
return result.toUIMessageStreamResponse({
  originalMessages: messages,
  onFinish: ({ messages }) => {
    saveChat({ chatId, messages });
  },
});
```

Where `saveChat` is **your own implementation** (PostgreSQL, MongoDB, etc.). AI SDK provides the hook, you provide the database code.

**Example pattern:**
```typescript
// Your database schema (not provided by AI SDK)
interface Chat {
  id: string;
  userId: string;
  messages: UIMessage[];  // Full message array
  createdAt: Date;
  updatedAt: Date;
}

// Your database function (not provided by AI SDK)
async function saveChat({ chatId, messages }: { chatId: string; messages: UIMessage[] }) {
  await db.chats.upsert({
    where: { id: chatId },
    data: { messages, updatedAt: new Date() }
  });
}
```

**What AI SDK provides:**
- `onFinish` callback timing (after stream completes)
- `UIMessage[]` type (normalized message format)
- `convertToModelMessages()` utility (UI format → model format)

**What AI SDK does NOT provide:**
- Database schema for chats/messages
- Migration scripts
- Retrieval functions (`loadChat`)
- Pagination logic
- Cost/latency tracking

### LangGraph's Checkpointing

LangGraph provides **built-in checkpointing** with database schemas:

```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver(engine)
graph = graph.compile(checkpointer=checkpointer)

# Automatic checkpoints after every node
config = {"configurable": {"thread_id": conversation_id}}
async for event in graph.astream_events(state, config=config):
    yield event
```

**What LangGraph provides:**
- Two PostgreSQL tables (`checkpoints`, `checkpoint_writes`) with indexes
- Automatic checkpoint creation after every node execution
- Resume logic (`graph.astream(state, config)` continues from last checkpoint)
- Branching (`update_state()` creates a new branch from checkpoint N)
- Pending writes for optimistic checkpointing

**What LangGraph does NOT provide:**
- Cost tracking (no token counts in checkpoints)
- Latency tracking (no timing data in checkpoints)
- Feedback (no like/dislike mechanism)
- User-facing conversation history (checkpoints are execution state, not chat messages)

### NYQST's Current State

**Message persistence:** None. Messages live in React state only (`useChat` hook on client).

**Run ledger:** Captures execution events (LLM requests/responses, tool calls) but not conversation history. Events are keyed by `run_id`, not `conversation_id`.

**Gap:** No conversation model. Cannot answer "what did user X ask yesterday?" or "how many messages in this conversation?" or "what was the cost of this conversation?"

### Comparison

| Capability | AI SDK Pattern | LangGraph Checkpointing | NYQST (current) |
|------------|----------------|-------------------------|-----------------|
| **Persistence location** | Your database | PostgreSQL/SQLite | None |
| **Schema provided** | No | Yes (2 tables) | N/A |
| **Checkpoint granularity** | Per-conversation (full message array) | Per-node (graph state) | N/A |
| **Resume/retry** | Load from DB, re-invoke | Built-in (config.thread_id) | None |
| **Branching** | Manual (copy message array) | Built-in (`update_state()`) | None |
| **Cost tracking** | You implement | Not included | Run ledger captures token counts |
| **Latency tracking** | You implement | Not included | Run ledger captures timings |
| **Feedback** | You implement | Not included | None |
| **Conversation list** | You implement | Not included | None |

**Verdict:** Neither AI SDK nor LangGraph provides a full conversation model. Both require custom implementation. Dify's 8-table conversation model (messages, feedbacks, annotations, thoughts) is the reference standard. NYQST has none of it.

**Action:** Implement a conversation model (see Dify comparison for requirements). Store chat messages separately from run ledger events. Link via `run_id` → `conversation_id`.

---

## 4. RSC (React Server Components) Integration

### AI SDK's RSC Features

AI SDK provides `streamUI()` for generative UI with React Server Components:

```tsx
// app/actions.tsx
'use server';

import { streamUI } from '@ai-sdk/rsc';
import { openai } from '@ai-sdk/openai';

export async function generateResponse(prompt: string) {
  const result = await streamUI({
    model: openai('gpt-4o'),
    prompt,
    text: async function* ({ content }) {
      yield <div>Loading...</div>;
      return <div>{content}</div>;
    },
    tools: {
      getWeather: {
        description: 'Get weather for a location',
        inputSchema: z.object({ location: z.string() }),
        generate: async function* ({ location }) {
          yield <div>Checking weather...</div>;
          const weather = await fetchWeather(location);
          return <WeatherCard location={location} weather={weather} />;
        }
      }
    }
  });

  return result.value;
}
```

```tsx
// app/page.tsx
'use client';

import { useState } from 'react';
import { generateResponse } from './actions';

export default function Page() {
  const [component, setComponent] = useState<React.ReactNode>();

  return (
    <div>
      <form onSubmit={async e => {
        e.preventDefault();
        setComponent(await generateResponse('Get weather in NYC'));
      }}>
        <button>Ask</button>
      </form>
      <div>{component}</div>
    </div>
  );
}
```

**How it works:**
1. Client calls server action (`generateResponse`)
2. Server streams **React components** (not text) via RSC transport
3. Client receives serialized components, renders them
4. LLM can return custom UI (weather cards, charts, forms) instead of text

**Additional features:**
- `createAI()` provider for managing server/client state
- `useActions()` hook (client-side) to call server actions
- `useUIState()` hook to access streamed UI
- `useStreamableValue()` for streaming primitive values (not just components)

**State flow:**
```
Server: AIState (full message history, invisible to client)
   ↓ onGetUIState transform
Client: UIState (renderable components, visible to user)
   ↓ useActions call
Server: AIState updated
   ↓ onSetAIState hook
Database: Persist AIState
```

### Why NYQST Cannot Use RSC

**Blocker:** RSC requires **Next.js server actions**, which are TypeScript-only. Our backend is FastAPI (Python).

**What happens if we try:**
- `'use server'` directive → ignored (not a Next.js file)
- `streamUI()` function → not available (AI SDK's `@ai-sdk/rsc` is TypeScript-only)
- Server actions → N/A (FastAPI has no equivalent)
- RSC transport → not supported (requires Next.js runtime)

**Alternative:** We could run Next.js for the frontend AND backend, but then:
1. Lose LangGraph (no Python)
2. Lose MCP tool pipeline (rewrite 2000+ lines in TypeScript)
3. Lose run ledger integration (PostgreSQL checkpointing ≠ AI SDK's saveChat pattern)
4. Lose existing FastAPI routes (60+ endpoints)

**Not viable.**

### What We Lose

| RSC Feature | NYQST Impact | Workaround |
|-------------|--------------|------------|
| **Generative UI** (model returns components, not text) | Cannot do it | Return structured JSON, client renders based on type |
| **Loading states** (yield intermediate components) | Cannot do it | Return SSE events for state transitions, client renders loading UI |
| **Server state** (`createAI` provider) | Cannot do it | Manage state in FastAPI session or database |
| **useActions hook** (type-safe server action calls) | Cannot do it | Use `fetch()` to call FastAPI endpoints |
| **Server-side component streaming** | Cannot do it | Stream JSON, client assembles React components |

**Impact assessment:** RSC is compelling for consumer apps (ChatGPT-style interfaces with rich UI), but NYQST is an API-first platform for B2B. Our clients are:
- Claude Desktop (consumes MCP JSON-RPC, not RSC)
- VS Code extension (consumes MCP over stdio, not RSC)
- Custom agents (consume REST API + SSE, not RSC)
- Internal staff portal (Next.js client, but backend is still FastAPI)

**Only the staff portal could benefit from RSC**, and that's 10% of the product surface area. Not worth re-platforming the entire backend to TypeScript.

---

## 5. Migration Complexity Estimate

### Scenario: Rewrite to Native AI SDK Backend

**What we'd migrate:**
- FastAPI → Next.js API routes (60+ endpoints)
- LangGraph → AI SDK agent loop (manual while loops)
- Python MCP tools → TypeScript equivalents (6 servers, 72+ tools)
- SQLAlchemy ORM → Prisma or Drizzle
- Pydantic schemas → Zod schemas
- AsyncIO → Promise-based async
- Run ledger → Custom implementation (AI SDK has no equivalent)
- LangGraphToAISDKAdapter → Delete (native `toUIMessageStreamResponse()`)

**Code volume:**
- **Current Python backend:** ~8,000 lines (agents, MCP, services, API routes)
- **Estimated TypeScript rewrite:** ~6,000 lines (AI SDK simplifies streaming, but we lose LangGraph's abstractions)
- **Net reduction:** 2,000 lines (~25% smaller)

**Effort estimate:**
- Core rewrite: 4-6 weeks (full-time engineer)
- Testing: 2 weeks (regression tests, integration tests)
- Migration of production data: 1 week
- **Total:** 7-9 weeks

**Risk:**
- **High:** Lose LangGraph's checkpointing (cannot resume conversations after crash)
- **High:** Lose `interrupt()` for human-in-the-loop (no equivalent in AI SDK)
- **High:** Lose graph workflows (cannot model complex multi-step processes)
- **Medium:** Lose run ledger integration (would need to rebuild event emission)
- **Low:** Lose Python MCP tools (can rewrite, but 72 tools is significant)

### What We'd Gain

| Feature | Value | Priority |
|---------|-------|----------|
| **Simpler streaming** | Delete 200 lines of adapter code | Low (current adapter works) |
| **Native tool execution** | Delete MCPToolNode bridge logic | Low (bridge enables policy checks) |
| **RSC support** | Generative UI for staff portal | Medium (nice-to-have for 10% of product) |
| **Ecosystem** | Access to Vercel AI SDK plugins, examples, community support | Medium |
| **Type safety** | End-to-end TypeScript (client → server) | Medium (Pydantic + Zod already provides this) |

### What We'd Lose

| Feature | Impact | Mitigation |
|---------|--------|-----------|
| **LangGraph checkpointing** | Cannot resume after crash | Rebuild using AI SDK's saveChat + custom state machine |
| **Human-in-the-loop** | No approval gates | Rebuild using polling or webhooks |
| **Graph workflows** | Cannot model complex state machines | Rebuild using manual state transitions |
| **Run ledger** | No structured event log | Rebuild custom logging |
| **MCP pipeline** | No policy checks, no audit trail | Rebuild middleware layer |
| **Python MCP tools** | 72 tools to rewrite | Rewrite in TypeScript (6-8 weeks) |

### Recommendation

**Do not migrate.** The cost (7-9 weeks + high risk of losing critical capabilities) far exceeds the benefit (simplify streaming adapter, enable RSC for 10% of product). The Python backend with LangGraph is the right choice for NYQST's requirements:
- Complex workflows (graph-based, not linear)
- Audit requirements (run ledger, policy checks)
- Human-in-the-loop (approval gates)
- MCP-native tooling (72 tools already implemented in Python)

**Alternative:** If RSC becomes critical, consider a **hybrid architecture**:
- FastAPI for core backend (agents, MCP tools, run ledger)
- Next.js API routes for staff portal only (use `streamUI` for generative UI)
- Next.js routes proxy to FastAPI for tool execution

This preserves LangGraph while enabling RSC for the small surface area that needs it.

---

## 6. Summary Table: Native AI SDK vs. NYQST

| Capability | Native AI SDK (TypeScript) | NYQST (Python + LangGraph) | Verdict |
|------------|---------------------------|----------------------------|---------|
| **Basic streaming** | `streamText()` + `toUIMessageStreamResponse()` (5 lines) | `LangGraphToAISDKAdapter` (200 lines) | AI SDK wins on simplicity |
| **Tool execution** | Inline `execute` functions | MCP pipeline (validate → policy → execute → log) | NYQST wins on auditability |
| **Multi-step agents** | Manual while loop (10 lines) | LangGraph graph (100 lines) | AI SDK wins on simplicity |
| **Graph workflows** | Not supported | Full support (parallel, conditional, sub-graphs) | NYQST wins on power |
| **Checkpointing** | Not supported | PostgreSQL-backed, automatic | NYQST wins |
| **Human-in-the-loop** | Not supported | `interrupt()` built-in | NYQST wins |
| **Message persistence** | You implement (onFinish hook) | You implement (no built-in) | Tie (both require custom code) |
| **RSC (generative UI)** | Full support (`streamUI`) | Not supported (Python backend) | AI SDK wins |
| **Cost tracking** | You implement | Run ledger captures token counts | NYQST wins |
| **Error handling** | `onError` callback | Custom adapter logic | Tie |
| **Ecosystem** | Large (Vercel, community plugins) | Small (LangGraph community) | AI SDK wins |
| **Complexity** | Low (framework handles most) | High (custom plumbing) | AI SDK wins |
| **Fit for NYQST** | Poor (no graph workflows, no checkpointing, no audit) | Excellent | NYQST wins |

**Overall verdict:** We are using the right stack. The manual plumbing (adapter, bridge, event listener) is the price we pay for capabilities that AI SDK fundamentally cannot provide (graph workflows, checkpointing, human-in-the-loop). If we were building a simple chatbot, AI SDK native would be better. We are building an agentic platform with audit requirements, so LangGraph is mandatory.

**Action items:**
1. **Accept the adapter tax** — We maintain 200 lines of streaming adapter code. This is fine.
2. **Do not migrate to TypeScript backend** — The cost exceeds the benefit by 10x.
3. **Implement conversation model** — Neither AI SDK nor LangGraph provides this. Build it ourselves (see Dify comparison).
4. **Consider hybrid architecture** — If RSC becomes critical, run Next.js API routes alongside FastAPI, not instead of.

---

*End of comparison document*
