# Build Plan Status (as of 2026-02-04)

## Active Plan: BUILD_PLAN_V2.md (Accelerated Client Preview + Foundation)

Two-track approach: Track A (preview demo, 3 weeks) + Track B (foundation, 4 weeks parallel).

---

### Track A: Preview Demo

#### Week 1: Agent Chat + Streaming — COMPLETE ✅

**Code: DONE ✅** | **Tests: DONE ✅**

- [x] LangGraph research assistant graph (`src/intelli/agents/graphs/research_assistant.py`)
- [x] Streaming chat endpoint (`src/intelli/api/v1/agent.py`)
- [x] LangGraphToAISDKAdapter (`src/intelli/agents/adapters/__init__.py`)
- [x] ResearchPage UI with chat interface
- [x] useAgentChat hook → **Upgraded to @assistant-ui/react** (commit `02ad587`)
- [x] AI SDK v3 SSE fix (migrated from v2 data stream to v3 SSE)
- [x] Sources sidebar with provenance display
- [x] RAG pipeline verified end-to-end (upload → index → ask with citations)

**Test Suite Status:**

| Suite | Count | Status |
|-------|-------|--------|
| Backend tests (pytest) | 619 passed | ✅ |
| Frontend tests (vitest) | 221 passed | ✅ |
| Agent tests | 114 passed | ✅ |
| SSE contract tests | Passed | ✅ |

**Closed Issues:** #6, #7, #8, #9 (test gaps addressed)

#### Week 2: Run Viewer + Search — PARTIAL 🔶

- [x] Run timeline component exists
- [x] Run events API working
- [ ] Run timeline wired to real data in UI
- [ ] Search results panel with highlighting
- [ ] Real-time updates via SSE in run viewer

#### Week 3: Polish + Integration — PARTIAL 🔶

- [x] Dark mode support (commit `3280119`)
- [x] @assistant-ui migration for production-grade chat UX (commit `02ad587`)
- [x] Smoke test infrastructure (`scripts/smoke-test.sh`)
- [ ] Visual QA checklist (30+ items)
- [ ] Mobile responsiveness audit
- [ ] Demo script and walkthrough prep

---

### Track B: Foundation

#### Week 1-2: IndexService Unification — NOT STARTED

- [ ] Define IndexService interface
- [ ] Create IndexProfile model and registry
- [ ] OpenSearch backend adapter
- [ ] pgvector backend adapter
- [ ] Migrate RagService to use IndexService

#### Week 2-3: Docling + HybridChunker — NOT STARTED

- [ ] Configure Docling PdfPipelineOptions for tiers
- [ ] Integrate HybridChunker
- [ ] Add chunk metadata (headings, page, origin)

#### Week 3-4: Session Model — COMPLETE ✅

- [x] Session database model (commit `307304d`)
- [x] Session CRUD API endpoints
- [x] Link runs to sessions
- [x] Conversations subsystem with messages
- [x] Session lifecycle management (active → idle transitions)
- [x] Frontend conversation store

---

### Additional Work Done (beyond original plan)

| Item | Commit | Impact |
|------|--------|--------|
| Auth enforcement on all endpoints | `c34f491` | Security hardening |
| Conversations + tags subsystem | `307304d` | Full chat persistence |
| ~500 new tests | `91638d2`, `dc0cabf`, `a079699` | Quality assurance |
| Agent system prompt rewrite | `a079699` | Better tool-calling behavior |
| Live API evaluation harness | `2d49517` | Testing infrastructure |
| @assistant-ui/react migration | `02ad587` | -637 lines, production UX |
| Smoke test script | `02ad587` | Dev environment verification |

---

## What Works Right Now

1. **Doc Intelligence**: Upload artifacts → create manifests → advance pointers → auto-index → search with citations
2. **Research Assistant**: Streaming agent chat over documents with source display (now using @assistant-ui)
3. **Run Ledger**: Audit trail for all operations
4. **Sessions/Conversations**: Full persistence with message history
5. **Auth**: JWT + API key authentication on all endpoints
6. **Dark Mode**: System preference detection + manual toggle

## What's Next (Priority Order)

1. **Merge PR #12** — `fix/ai-sdk-v3-sse-streaming` (28 commits, ready for review)
2. **Track A Week 2**: Wire run viewer to real data, search results UI
3. **Track A Week 3**: Visual QA checklist, mobile audit
4. **Track B Week 1**: IndexService unification

---

## Branch Status

| Branch | Commits Ahead | Status |
|--------|---------------|--------|
| `fix/ai-sdk-v3-sse-streaming` | 28 | PR #12 open |
| `main` | — | Stable |

## Test Coverage Summary

- **Backend**: 619 tests passing (~80% coverage on services)
- **Frontend**: 221 tests passing (24 test files)
- **E2E**: Smoke tests passing (10 checks)

## Implementation Plan

The @assistant-ui/react migration followed the plan at `docs/planning/CHAT_UI_MIGRATION_PLAN.md` (phases 1-9 complete).
