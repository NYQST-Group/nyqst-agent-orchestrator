# Build Plan V2: Accelerated Client Preview + Foundation

**Date:** 2026-01-27
**Status:** Proposed
**Supersedes:** BUILD_PLAN.md (chain-first approach retained, timeline accelerated)

---

## Executive Summary

This plan introduces a **two-track approach** to deliver a working client preview as fast as possible while building the foundation in parallel. The original chain-first architecture remains correct, but we accelerate time-to-demo by leveraging existing working code.

**Track A (Preview):** 3-week sprint to a demo-ready product with agent chat, document upload, and Q&A.

**Track B (Foundation):** Parallel work on IndexService, Docling upgrade, and session model that will replace preview scaffolding.

The throwaway is minimal and intentional: we build a simple agent and streaming endpoint that will be upgraded (not discarded) when the foundation is ready.

### ADR Alignment

This plan implements decisions from the following Architecture Decision Records:

| ADR | Decision | Plan Implementation |
|-----|----------|---------------------|
| [ADR-004](../adr/004-index-service-architecture.md) | Contract-first IndexService with OpenSearch + pgvector | Track B Week 1-2: IndexService unification |
| [ADR-005](../adr/005-agent-runtime-framework.md) | LangGraph backend + Vercel AI SDK frontend | Track A Week 1: LangGraph agent + useChat hook |
| [ADR-006](../adr/006-session-workspace-architecture.md) | Lightweight database session model | Track B Week 3-4: Session model |
| [ADR-007](../adr/007-document-processing-pipeline.md) | Tiered DocIR with HybridChunker | Track B Week 2-3: Docling + HybridChunker |

---

## 1. Current State Assessment

### What Works Today

| Component | Status | Location |
|-----------|--------|----------|
| **Notebooks UI** | Working | `ui/src/pages/NotebooksPage.tsx`, `NotebookPage.tsx` |
| **File upload** | Working | Upload → artifact → manifest → pointer advance |
| **RAG Q&A** | Working | `POST /api/v1/rag/ask` with citations |
| **Auto-indexing** | Working | Triggers on pointer advance |
| **Run ledger** | Working | All operations logged |
| **Substrate APIs** | Working | Artifacts, manifests, pointers CRUD |
| **SSE streaming** | Working | `GET /api/v1/streams` with PostgreSQL NOTIFY |
| **Chat pane component** | Exists | `packages/ui-library/components/panes/chat-pane.tsx` (mock data) |

### What's Missing for Demo

| Gap | Impact | Fix Complexity |
|-----|--------|----------------|
| ResearchPage is placeholder | No agent interaction UI | Medium (wire existing components) |
| Chat pane uses mock data | No real agent responses | Low (connect to backend) |
| No LangGraph agent | No multi-step reasoning | Medium (simple graph first) |
| No streaming agent responses | Poor UX during generation | Medium (add SSE endpoint) |
| No run timeline in UI | Can't see what agent did | Low (component exists in ui-library) |

---

## 2. Two-Track Approach

```
                    ┌─────────────────────────────────────────────┐
                    │           CLIENT PREVIEW DEMO               │
                    │         (Target: 3 weeks to demo)           │
                    └─────────────────────────────────────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    │                                       │
            ┌───────▼───────┐                       ┌───────▼───────┐
            │   TRACK A     │                       │   TRACK B     │
            │   Preview     │                       │   Foundation  │
            │   (Fast)      │                       │   (Parallel)  │
            └───────┬───────┘                       └───────┬───────┘
                    │                                       │
    Week 1: Agent chat + streaming          Week 1-2: IndexService unification
    Week 2: Run viewer + search             Week 2-3: Docling + HybridChunker
    Week 3: Polish + integration            Week 3-4: Session model
                    │                                       │
                    └───────────────────┬───────────────────┘
                                        │
                    ┌───────────────────▼───────────────────┐
                    │           CONVERGE                     │
                    │   Preview upgraded with foundation     │
                    │   (Minimal throwaway)                  │
                    └───────────────────────────────────────┘
```

---

## 3. Track A: Preview Demo (3 Weeks)

### Goal

A working demo where a client can:
1. Upload documents to a notebook
2. Chat with an agent about those documents
3. See the agent's reasoning and sources
4. View what the agent did (run timeline)

### Week 1: Agent Chat + Streaming (with Vercel AI SDK)

**Deliverables:**
- Research agent graph (LangGraph) that wraps existing RAG service
- Streaming endpoint for agent responses (`POST /api/v1/agent/chat`) compatible with Vercel AI SDK
- ResearchPage wired to real backend using `useChat` hook
- Chat pane with professional streaming UX (typing indicators, message history, error handling)

**Tasks:**

| ID | Task | Estimate | Dependencies |
|----|------|----------|--------------|
| A1.1 | Create `research_assistant` LangGraph graph | 1d | None |
| A1.2 | Add streaming chat endpoint (AI SDK compatible format) | 1d | A1.1 |
| A1.3 | Install Vercel AI SDK (`ai`, `@ai-sdk/react`) | 0.5d | None |
| A1.4 | Replace mock streaming with `useChat` hook | 0.5d | A1.2, A1.3 |
| A1.5 | Replace ResearchPage placeholder with working UI | 1d | A1.4 |
| A1.6 | Add document context selector (mount pointers) | 1d | A1.5 |

**Why Vercel AI SDK:**
- Production-ready streaming with built-in loading states and error handling
- `useChat` hook manages message history, input state, and streaming automatically
- Compatible with LangGraph streaming output
- Used by major AI products (ChatGPT-like UX out of the box)

**Agent Graph (Simple Version):**

```python
# src/intelli/agents/graphs/research_assistant.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from operator import add

class ResearchState(TypedDict):
    messages: Annotated[list, add]
    context_pointer_id: str | None
    sources: list[dict]

def retrieve_node(state: ResearchState) -> dict:
    """Search the mounted document context."""
    # Calls existing RagService.retrieve()
    ...

def generate_node(state: ResearchState) -> dict:
    """Generate response with citations."""
    # Calls existing RagService.answer() pattern
    ...

graph = StateGraph(ResearchState)
graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)
graph.set_entry_point("retrieve")

research_assistant = graph.compile()
```

**Streaming Endpoint (Vercel AI SDK Compatible):**

Per [ADR-005](../adr/005-agent-runtime-framework.md), LangGraph's streaming output is bridged to the Vercel AI SDK UI protocol via a stream adapter:

```
LangGraph StreamEvents
       │
       ▼
  LangGraphToAISDKAdapter
       │
       ├──► SSE (AI SDK UI protocol) → Frontend useChat
       │
       └──► Run Ledger Events → Platform audit
```

```python
# src/intelli/api/v1/agent.py

from intelli.agents.adapters import LangGraphToAISDKAdapter

@router.post("/chat")
async def agent_chat(
    request: AgentChatRequest,
    session: AsyncSession = Depends(get_session),
    run_service: RunService = Depends(get_run_service),
):
    """Stream agent responses in Vercel AI SDK format."""
    adapter = LangGraphToAISDKAdapter(run_service)
    
    async def generate():
        async for event in research_assistant.astream(
            {"messages": request.messages, "context_pointer_id": request.pointer_id}
        ):
            # Adapter converts LangGraph events to AI SDK format
            # AND emits run ledger events for audit
            for ai_sdk_chunk in adapter.convert(event):
                yield ai_sdk_chunk
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

**Frontend Integration (useChat hook):**

```typescript
// ui/src/hooks/useAgentChat.ts

import { useChat } from '@ai-sdk/react';

export function useAgentChat(pointerId: string) {
  const { messages, input, handleInputChange, handleSubmit, isLoading, error } = useChat({
    api: '/api/v1/agent/chat',
    body: { pointer_id: pointerId },
  });

  return {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    error,
  };
}
```

**Exit Criteria Week 1:**
- User can open Research page, select a notebook, and chat with agent
- Agent responses stream in real-time
- Sources are displayed with each response

### Week 2: Run Viewer + Search

**Deliverables:**
- Run timeline component showing agent steps
- Search results panel with source highlighting
- Tool call visibility (what the agent did)

**Tasks:**

| ID | Task | Estimate | Dependencies |
|----|------|----------|--------------|
| A2.1 | Wire run-explorer-pane.tsx to `/api/v1/runs` | 1d | Week 1 |
| A2.2 | Add run events fetch and display | 1d | A2.1 |
| A2.3 | Create search results component | 1d | None |
| A2.4 | Add source highlighting in document viewer | 1d | A2.3 |
| A2.5 | Connect tool calls to run ledger display | 1d | A2.2 |

**Exit Criteria Week 2:**
- User can see timeline of agent actions
- Search results show with relevance scores
- Clicking a source opens document at relevant section

### Week 3: Polish + Integration (Material 3 Design Principles)

**Deliverables:**
- Professional visual polish following Material 3 design principles
- Consistent use of component library (no ad-hoc styling)
- Error handling and loading states
- Mobile-responsive layout
- Demo script and walkthrough
- Bug fixes from internal testing

**Tasks:**

| ID | Task | Estimate | Dependencies |
|----|------|----------|--------------|
| A3.1 | UI audit: ensure all pages use component library | 0.5d | Week 2 |
| A3.2 | Apply Material 3 spacing and typography hierarchy | 0.5d | A3.1 |
| A3.3 | Add error boundaries and fallbacks | 0.5d | A3.1 |
| A3.4 | Loading skeletons for all async operations | 0.5d | A3.3 |
| A3.5 | Mobile layout adjustments | 0.5d | None |
| A3.6 | Visual QA checklist (see below) | 0.5d | A3.1-A3.5 |
| A3.7 | Internal demo and bug bash | 1d | A3.6 |
| A3.8 | Fix critical bugs from testing | 0.5d | A3.7 |
| A3.9 | Demo script and client walkthrough prep | 0.5d | A3.8 |

**Material 3 Design Principles Applied:**

The existing shadcn/ui component library (Radix + Tailwind) will be enhanced with Material 3 design principles from RESEARCH_SYNTHESIS.md:

1. **Emotional Design for Engagement**
   - Smooth transitions and micro-animations (tailwindcss-animate)
   - Satisfying feedback on interactions (button press states, loading indicators)
   - Consistent visual rhythm across all pages

2. **Automatic Compliance with Spacing, Hierarchy, Contrast**
   - Use design tokens from `globals.css` consistently
   - Typography scale: text-xs → text-sm → text-base → text-lg → text-xl
   - Spacing scale: p-2 → p-4 → p-6 → p-8 (consistent padding/margins)
   - Color contrast: all text meets WCAG AA standards

3. **Cross-Platform Consistency**
   - All UI from `packages/ui-library/components/ui/*`
   - Domain-specific variants (artifact, manifest, run, evidence, claim, corpus, bundle)
   - No inline styles or ad-hoc Tailwind classes for core UI elements

**Visual QA Checklist:**

```markdown
## Pre-Demo Visual QA

### Component Consistency
- [ ] All buttons use Button component with correct variants
- [ ] All inputs use Input component (no raw <input>)
- [ ] All badges use Badge component with domain variants
- [ ] All tooltips use Tooltip component
- [ ] All dialogs use Dialog component

### Spacing & Layout
- [ ] Consistent padding in all panes (p-4 standard)
- [ ] Proper spacing between sections (space-y-4 or space-y-6)
- [ ] No overlapping elements
- [ ] Proper alignment (items-center, justify-between used correctly)

### Typography
- [ ] Headings use correct scale (text-lg for pane titles, text-xl for page titles)
- [ ] Body text is text-sm or text-base
- [ ] Muted text uses text-muted-foreground
- [ ] No orphaned text (proper line heights)

### States & Feedback
- [ ] Loading states show skeletons (not spinners everywhere)
- [ ] Error states show clear messages with retry options
- [ ] Empty states have helpful guidance
- [ ] Hover states on all interactive elements
- [ ] Focus rings on keyboard navigation

### Dark Mode
- [ ] All colors use CSS variables (not hardcoded)
- [ ] Contrast maintained in dark mode
- [ ] No white flashes on page load

### Mobile (if applicable)
- [ ] Touch targets minimum 44x44px
- [ ] No horizontal scroll
- [ ] Readable text without zooming
```

**Exit Criteria Week 3:**
- Demo runs smoothly for 30-minute client presentation
- No critical bugs in happy path
- Error states handled gracefully
- Visual QA checklist 100% complete
- CEO/client impression: "This looks professional and polished"

---

## 4. Track B: Foundation (Parallel, 4 Weeks)

Track B builds the architectural foundation from BUILD_PLAN.md. This work happens in parallel with Track A and will upgrade (not replace) the preview code.

### Week 1-2: IndexService Unification (E-IDX-01)

**Goal:** Unify `RagService` and `opensearch_chunks.py` behind the `IndexService` contract.

**Tasks:**

| ID | Task | Estimate | Dependencies |
|----|------|----------|--------------|
| B1.1 | Define `IndexService` interface (from INDEX_CONTRACT.md) | 0.5d | None |
| B1.2 | Create `IndexProfile` model and registry | 1d | B1.1 |
| B1.3 | Implement OpenSearch backend adapter | 1d | B1.2 |
| B1.4 | Implement pgvector backend adapter | 1d | B1.2 |
| B1.5 | Migrate `RagService` to use `IndexService` | 1d | B1.3, B1.4 |
| B1.6 | Update auto-indexing to use new service | 0.5d | B1.5 |

**Convergence with Track A:** Once IndexService is ready, the preview agent's retrieval calls switch from `RagService` to `IndexService`. No UI changes needed.

### Week 2-3: Docling + HybridChunker (E-DOC-01, E-DOC-03)

**Goal:** Upgrade document processing with tiered Docling and structure-aware chunking.

**Tasks:**

| ID | Task | Estimate | Dependencies |
|----|------|----------|--------------|
| B2.1 | Configure Docling `PdfPipelineOptions` for tiers | 1d | None |
| B2.2 | Integrate `HybridChunker` (replace 2000-char split) | 1d | B2.1 |
| B2.3 | Add chunk metadata (headings, page, origin) | 0.5d | B2.2 |
| B2.4 | Update index records with structural metadata | 0.5d | B2.3, B1.5 |
| B2.5 | Test with complex PDFs (tables, multi-column) | 1d | B2.4 |

**Convergence with Track A:** Better chunking improves search quality automatically. No UI changes needed.

### Week 3-4: Session Model (E-SES-01)

**Goal:** Add session persistence for "return to topic" and agent context scoping.

**Tasks:**

| ID | Task | Estimate | Dependencies |
|----|------|----------|--------------|
| B3.1 | Create `Session` database model | 0.5d | None |
| B3.2 | Add session CRUD API endpoints | 1d | B3.1 |
| B3.3 | Link runs to sessions | 0.5d | B3.2 |
| B3.4 | Add session context injection for agents | 1d | B3.3 |
| B3.5 | Frontend session store and restore | 1d | B3.4 |

**Convergence with Track A:** Preview agent gains session persistence. User can close browser and return to see previous conversation.

---

## 5. Throwaway Analysis

| Preview Component | Foundation Replacement | Throwaway? |
|-------------------|----------------------|------------|
| Simple `research_assistant` graph | Full research agent with Tavily/Perplexity | **Upgrade** (patterns transfer) |
| Direct `RagService` calls | `IndexService` calls | **Upgrade** (swap service) |
| Naive chunking | `HybridChunker` | **Upgrade** (transparent) |
| No session persistence | Session model | **Upgrade** (add feature) |
| Streaming endpoint | Same endpoint, richer events | **Upgrade** (extend) |

**Total throwaway: ~0%** — All preview code is upgraded, not discarded.

---

## 6. Testing Strategy

### 6.1 Test Pyramid

```
                    ┌─────────────┐
                    │    E2E      │  ← Playwright: critical user flows
                    │   (few)     │     ~10 tests
                    ├─────────────┤
                    │ Integration │  ← API tests with test DB
                    │  (medium)   │     ~50 tests
                    ├─────────────┤
                    │    Unit     │  ← pytest + vitest
                    │   (many)    │     ~200+ tests
                    └─────────────┘
```

### 6.2 Backend Testing (pytest)

**Structure:**
```
tests/
├── unit/
│   ├── services/
│   │   ├── test_rag_service.py
│   │   ├── test_index_service.py
│   │   ├── test_run_service.py
│   │   └── test_ledger_service.py
│   ├── repositories/
│   │   └── test_*.py
│   └── agents/
│       └── test_research_assistant.py
├── integration/
│   ├── api/
│   │   ├── test_artifacts_api.py
│   │   ├── test_rag_api.py
│   │   ├── test_agent_api.py
│   │   └── test_streams_api.py
│   └── services/
│       └── test_indexing_pipeline.py
└── conftest.py  # Fixtures: test DB, test client, mock services
```

**Key Fixtures:**

```python
# tests/conftest.py

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from intelli.db.base import Base

@pytest.fixture
async def test_db():
    """Create a fresh test database for each test."""
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test_intelli")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def session(test_db):
    """Provide a database session for tests."""
    async with AsyncSession(test_db) as session:
        yield session

@pytest.fixture
def test_client(session):
    """FastAPI test client with injected session."""
    from fastapi.testclient import TestClient
    from intelli.main import app
    from intelli.api.dependencies import get_session
    
    app.dependency_overrides[get_session] = lambda: session
    return TestClient(app)
```

**Example Unit Test:**

```python
# tests/unit/services/test_rag_service.py

import pytest
from intelli.services.knowledge.rag_service import RagService, _chunk_text

class TestChunking:
    def test_chunk_text_splits_at_boundaries(self):
        text = "word " * 500  # 2500 chars
        chunks = _chunk_text(text, max_chars=1000, overlap=100)
        assert len(chunks) == 3
        assert all(len(c) <= 1000 for c in chunks)
    
    def test_chunk_text_empty_input(self):
        assert _chunk_text("") == []
        assert _chunk_text("   ") == []

class TestRagService:
    @pytest.mark.asyncio
    async def test_index_manifest_creates_chunks(self, session, sample_manifest):
        rag = RagService(session)
        stats = await rag.index_manifest(sample_manifest.sha256)
        assert stats.chunks_created > 0
        assert stats.artifacts_indexed == 1
```

**Example Integration Test:**

```python
# tests/integration/api/test_rag_api.py

import pytest

class TestRagAskEndpoint:
    @pytest.mark.asyncio
    async def test_ask_returns_answer_with_sources(self, test_client, indexed_notebook):
        response = test_client.post("/api/v1/rag/ask", json={
            "pointer_id": str(indexed_notebook.id),
            "question": "What is the main topic?",
            "top_k": 5,
        })
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert len(data["sources"]) <= 5
    
    @pytest.mark.asyncio
    async def test_ask_empty_notebook_returns_error(self, test_client, empty_notebook):
        response = test_client.post("/api/v1/rag/ask", json={
            "pointer_id": str(empty_notebook.id),
            "question": "What is this?",
        })
        assert response.status_code == 400
```

### 6.3 Frontend Testing (vitest + React Testing Library)

**Structure:**
```
ui/src/
├── __tests__/
│   ├── components/
│   │   ├── ChatPane.test.tsx
│   │   ├── RunTimeline.test.tsx
│   │   └── SearchResults.test.tsx
│   ├── pages/
│   │   ├── ResearchPage.test.tsx
│   │   └── NotebookPage.test.tsx
│   └── hooks/
│       └── useAgentChat.test.tsx
└── test-utils.tsx  # Custom render with providers
```

**Example Component Test:**

```typescript
// ui/src/__tests__/components/ChatPane.test.tsx

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatPane } from '@/components/panes/chat-pane';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

const wrapper = ({ children }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
);

describe('ChatPane', () => {
  it('renders message input', () => {
    render(<ChatPane paneId="test" />, { wrapper });
    expect(screen.getByPlaceholderText(/type a message/i)).toBeInTheDocument();
  });

  it('sends message on enter', async () => {
    render(<ChatPane paneId="test" />, { wrapper });
    const input = screen.getByPlaceholderText(/type a message/i);
    
    fireEvent.change(input, { target: { value: 'Hello agent' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    
    await waitFor(() => {
      expect(screen.getByText('Hello agent')).toBeInTheDocument();
    });
  });

  it('shows loading state while streaming', async () => {
    render(<ChatPane paneId="test" />, { wrapper });
    const input = screen.getByPlaceholderText(/type a message/i);
    
    fireEvent.change(input, { target: { value: 'Test' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    
    expect(screen.getByText(/thinking/i)).toBeInTheDocument();
  });
});
```

### 6.4 E2E Testing (Playwright)

**Structure:**
```
e2e/
├── tests/
│   ├── research-flow.spec.ts
│   ├── document-upload.spec.ts
│   └── agent-chat.spec.ts
├── fixtures/
│   └── sample-documents/
└── playwright.config.ts
```

**Example E2E Test:**

```typescript
// e2e/tests/research-flow.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Research Flow', () => {
  test('user can upload document and chat with agent', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'testpass');
    await page.click('button[type="submit"]');
    
    // Navigate to notebooks
    await page.goto('/docs');
    await expect(page.locator('h1')).toContainText('Doc Intelligence');
    
    // Create notebook
    await page.click('text=New notebook');
    await page.fill('input[type="text"]', 'Test Notebook');
    await page.keyboard.press('Enter');
    
    // Upload document
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('e2e/fixtures/sample-documents/test.pdf');
    await expect(page.locator('text=Sources')).toBeVisible();
    
    // Ask question
    await page.fill('input[placeholder*="Ask"]', 'What is this document about?');
    await page.click('button:has-text("Ask")');
    
    // Verify answer appears
    await expect(page.locator('text=Answer')).toBeVisible({ timeout: 30000 });
    await expect(page.locator('.source-card')).toHaveCount({ minimum: 1 });
  });
});
```

### 6.5 CI Pipeline

```yaml
# .github/workflows/ci.yml

name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_intelli
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      - name: Run linting
        run: poetry run ruff check src/
      - name: Run type checking
        run: poetry run mypy src/
      - name: Run tests
        run: poetry run pytest tests/ -v --cov=src/intelli --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v4

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - name: Install dependencies
        run: npm ci
      - name: Run linting
        run: npm run lint
      - name: Run type checking
        run: npm run typecheck
      - name: Run tests
        run: npm run test -- --coverage

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright
        run: npx playwright install --with-deps
      - name: Start services
        run: docker compose up -d
      - name: Run E2E tests
        run: npx playwright test
      - name: Upload test results
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
```

### 6.6 Test Coverage Targets

| Area | Target | Rationale |
|------|--------|-----------|
| Backend services | 80% | Core business logic |
| API endpoints | 90% | Contract stability |
| Frontend components | 70% | UI behavior |
| E2E critical paths | 100% | User-facing flows |

---

## 7. Risk Register (Updated)

| Risk | Impact | Track | Mitigation |
|------|--------|-------|------------|
| LangGraph streaming complexity | Delays Week 1 | A | Start with simple sync endpoint, add streaming incrementally |
| Chat pane integration issues | Delays Week 1 | A | Mock backend first, integrate incrementally |
| IndexService migration breaks RAG | Blocks Track A | B | Feature flag: `USE_NEW_INDEX_SERVICE=false` default |
| Docling upgrade changes output | Breaks existing indexes | B | Version index profiles, rebuild on upgrade |
| Session model scope creep | Delays convergence | B | MVP: just pointer mounts + LangGraph thread_id |
| Testing infrastructure setup | Delays all testing | Both | Set up CI in Week 1, add tests incrementally |

---

## 8. Success Metrics

### Preview Demo (Week 3)

| Metric | Target |
|--------|--------|
| Demo completion rate | 100% (no crashes) |
| Agent response time (p50) | < 5 seconds |
| Document upload success | 100% for PDF/DOCX |
| Client feedback | "I can see how this would help" |

### Foundation (Week 4+)

| Metric | Target |
|--------|--------|
| IndexService migration | Zero regression in search quality |
| Chunking improvement | 20% better retrieval relevance |
| Session persistence | Return-to-topic works across browser sessions |

---

## 9. Timeline Summary

```
Week 1  │ Track A: Agent chat + streaming
        │ Track B: IndexService interface + adapters
        │ Testing: CI pipeline setup, initial unit tests
        │
Week 2  │ Track A: Run viewer + search results
        │ Track B: Docling tiers + HybridChunker
        │ Testing: Integration tests for APIs
        │
Week 3  │ Track A: Polish + demo prep
        │ Track B: Session model
        │ Testing: E2E tests for critical paths
        │
        │ ──────── CLIENT PREVIEW DEMO ────────
        │
Week 4+ │ Convergence: Upgrade preview with foundation
        │ Continue Chain 3-5 from BUILD_PLAN.md
```

---

## 10. Appendix: File Changes Summary

### New Files (Track A)

```
src/intelli/agents/graphs/research_assistant.py   # Simple LangGraph agent
src/intelli/agents/adapters/__init__.py           # LangGraphToAISDKAdapter (per ADR-005)
src/intelli/api/v1/agent.py                       # Streaming chat endpoint (AI SDK compatible)
src/intelli/schemas/agent.py                      # Request/response models
ui/src/hooks/useAgentChat.ts                      # Vercel AI SDK useChat wrapper
ui/src/pages/ResearchPage.tsx                     # Replace placeholder
```

### Modified Files (Track A)

```
ui/package.json                                   # Add ai, @ai-sdk/react dependencies
ui/src/App.tsx                                    # Route updates
packages/ui-library/components/panes/chat-pane.tsx # Wire to useChat hook
```

### New Dependencies (Track A)

```json
// ui/package.json additions
{
  "dependencies": {
    "ai": "^3.0.0",
    "@ai-sdk/react": "^0.0.50"
  }
}
```

### New Files (Track B)

```
src/intelli/services/indexing/index_service.py    # Unified interface
src/intelli/services/indexing/profiles.py         # Profile registry
src/intelli/db/models/sessions.py                 # Session model
src/intelli/api/v1/sessions.py                    # Session endpoints
```

### New Files (Testing)

```
tests/conftest.py
tests/unit/services/test_*.py
tests/integration/api/test_*.py
e2e/tests/*.spec.ts
.github/workflows/ci.yml
```
