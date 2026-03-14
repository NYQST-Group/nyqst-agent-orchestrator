# Design Knowledge Map — NYQST DocuIntelli Platform
**Generated**: 2026-02-20
**Source**: 29 development repository documents (devrepo-docs-manifest.json)

---

## 1. Document Graph

### By Type
- **PRD (Product Requirements)**: 11 documents (00_INDEX through 10_APPENDIX)
- **ADR (Architectural Decisions)**: 10 documents (001 through 010)
- **Planning & Reference**: 8 documents (planning docs, reference designs)

### Strategic Dependency Structure

```
00_INDEX
  ├─→ 01_EXECUTIVE_SUMMARY (core thesis)
  │    ├─→ 02_VISION (intelligence commodity, context asset)
  │    ├─→ 03_PLATFORM (6 modules, 13 ADR Notes)
  │    └─→ 07_ROADMAP (delivery timeline)
  ├─→ 03_PLATFORM ← Richest hub (6 module specs, 13 ADR cross-refs)
  │    ├─→ 06_ARCHITECTURE (7 principles, 13 ADR Topics)
  │    ├─→ 08_METRICS (accuracy/trust/efficiency hierarchy)
  │    ├─→ 09_RISKS (17 risks, 12 assumptions)
  │    ├─→ 10_APPENDIX (60+ glossary terms)
  │    └─→ PLATFORM_REFERENCE_DESIGN
  └─→ 04_PRODUCTS (PropSygnal/RegSygnal)
       └─→ 05_USERS (9 personas, trust model)

06_ARCHITECTURE ← Core technical hub
  ├─→ 10 ADRs (001-010)
  ├─→ PLATFORM_REFERENCE_DESIGN (detailed spec)
  ├─→ UI_ARCHITECTURE (component system)
  └─→ SUPERAGENT_PARITY_CLEAN_ROOM_PLAN (5-phase impl)
```

---

## 2. Thematic Clusters

### Strategic Layer
**Documents**: 01_EXECUTIVE_SUMMARY, 02_VISION, 04_PRODUCTS
**Central Thesis**:
- Intelligence is commodity → ontologies are assets
- Tools (fluid) vs Infrastructure (rigid) decoupling
- Historical parallels: Steam→Assembly Line, Microchip→ERP, Agent→**Cognitive ERP**
- Cognitive ERP positions NYQST as enterprise infrastructure (not tools)

### Platform Layer
**Documents**: 03_PLATFORM, 06_ARCHITECTURE, PLATFORM_REFERENCE_DESIGN
**Central Thesis**:
- 6 integrated modules (Research, Document, Analysis, Modelling, Knowledge, Insight)
- Kernel objects: Artifacts, Manifests, Pointers, Sessions, Runs
- Append-only run ledger (authoritative)
- LangGraph as orchestration (operational), not source of truth
- Index Service with pluggable backends (OpenSearch/pgvector)

### Implementation Layer
**Documents**: SUPERAGENT_PARITY_CLEAN_ROOM_PLAN, 10 ADRs, IMPLEMENTATION-PLAN
**Central Thesis**:
- 5-phase path to Superagent parity (event streaming, planning, deliverables, search, HITL)
- Event contract mapping (Superagent semantics → Intelli ledger)
- NDM v1 (JSON AST) for deliverable rendering
- MCP as tool protocol with session-scoped discovery

### Domain Layer
**Documents**: 05_USERS, 07_ROADMAP, 08_METRICS, 09_RISKS
**Central Thesis**:
- 9 personas across PropSygnal (real estate) and RegSygnal (regulatory)
- Trust hierarchy: Never confidently wrong → Catch what humans miss → Faster → Easy to verify → Learns
- Metrics priority: Accuracy (95%+) > Trust (100% calc) > Efficiency > Adoption > Growth
- 17 critical risks + 12 assumptions for validation

---

## 3. Architectural Decision Themes

### Infrastructure & Storage (ADRs 004, 010)
| Decision | Selection | Rationale |
|----------|-----------|-----------|
| **Data Models** | Domain-first (not CDM-first) | Commercial entities first, CDM integration layer |
| **Index Service** | OpenSearch + pgvector | Hybrid search (BM25+kNN), pgvector fallback dev |
| **Bootstrap Infra** | PostgreSQL + pgvector + Neo4j | Purpose-fit services, free tier (Supabase/Aura) |
| **Storage Evolution** | Single PostgreSQL → PostgreSQL+Neo4j | Dify validated pgvector at scale |

**Key Pattern**: Contract-first, pluggable backends. "Always-on" triggering via pointer advance. Manifest diffs for incremental efficiency.

### Runtime & Orchestration (ADRs 005, 007, 008)
| Decision | Selection | Rationale |
|----------|-----------|-----------|
| **Orchestration** | LangGraph as runtime | Clear boundary: LangGraph (workflow), kernel (trust/audit) |
| **Canonical Store** | Run ledger (append-only) | Replays, audits, replications drive from ledger, not checkpoints |
| **Document Processing** | Tiered pipeline (Fast/Standard/Deep) | Adapter pattern, canonical DocIR artifact format |
| **Tool Protocol** | MCP (Model Context Protocol) | Standard discovery, schema, transport; context-scoped for efficiency |

**Key Pattern**: Separation of concerns. LangGraph checkpoints are operational aids, not system of record. MCP enables multi-agent framework flexibility.

### Integration & Governance (ADRs 003, 006, 009)
| Decision | Selection | Rationale |
|----------|-----------|-----------|
| **Multi-Agent** | Virtual Team Operating System | Standardized coordination layer for subagents |
| **Sessions** | Lightweight DB model (Phase 0) | User + Project + Objective + Compute context; upgrade path to containers |
| **Human-in-Loop** | Policy-driven interrupts (LangGraph) | Four templates (exploratory/standard/regulated/audit-critical) |
| **Governance** | Run ledger + tool execution pipeline | Every action auditable; approvals via interrupts |

**Key Pattern**: Three governance layers (Trust Levels → Approval Workflows → Interrupts). Policy as code.

### Code & Operations (ADRs 001, 002)
| Decision | Selection | Rationale |
|----------|-----------|-----------|
| **Type Safety** | OpenAPI + Code Generation | Single source of truth (Pydantic); frontend types from openapi-typescript |
| **Code Generation** | Pydantic → OpenAPI → TS types | Eliminates manual schema drift |

**Key Pattern**: Contract-first, codegen-driven. Schema Registry (future ADR) versioning profiles/tools.

---

## 4. Technology Stack (Locked)

### Backend Runtime
```
LangGraph 0.2+          (orchestration, checkpointing, streaming)
FastAPI 0.115+          (REST API, WebSocket for SSE)
SQLAlchemy 2.0 async    (ORM, async sessions)
Pydantic v2             (validation, OpenAPI schema)
```

### Data & Search
```
PostgreSQL 16+          (RDBMS, primary storage)
pgvector 0.8+           (semantic search fallback)
Neo4j Aura free         (graph for domain ontologies)
OpenSearch 2.13+        (hybrid search production)
Redis/Upstash           (cache, Celery queues)
```

### Document Processing
```
Docling 2.3+            (primary document parser, supports 100+ formats)
Unstructured 0.15+      (fallback, CSV/JSON/Email)
LlamaParse (optional)   (heavy extraction, paid API)
Rehype ecosystem        (Markdown/HTML processing on frontend)
```

### Tools & Integration
```
MCP Python SDK 0.8+     (Model Context Protocol for tools)
LangChain 0.2+          (parsers, splitters, embeddings)
OpenAI API (primary)    (ChatOpenAI, text-embedding-3-small)
LiteLLM (hot-swap)      (multi-provider, future: Anthropic/Claude)
Langfuse (self-hosted)  (observability, trace storage)
```

### Frontend Runtime
```
React 18.3+             (component framework)
TypeScript 5.6+         (type safety)
Vite 5.2+               (build/dev server)
TailwindCSS v4          (styling)
```

### Frontend Libraries
```
@assistant-ui/react     (chat UI components)
shadcn/ui               (component library, Tailwind-based)
Zustand 4.5+            (state management, NOT Recoil)
react-plotly.js 2.13+   (charting, Plotly.js wrapper)
rehype-react 13+        (Markdown to JSX, NOT GML)
rehype-parse 9+         (HTML parser for rehype)
unified 11+             (text processing pipeline)
```

### DevOps & Observability
```
Docker 28+              (containerization)
PostgreSQL Docker image (local dev, pgvector extension)
Neo4j Docker image      (local dev, Cypher support)
LangSmith Studio        (graph inspection, free tier)
Langfuse (self-hosted)  (trace storage, cost tracking)
```

---

## 5. Superagent → NYQST Mapping

### Event Streaming Contract
| Superagent Signal | Superagent Implementation | NYQST Requirement | NYQST Parity | Phase |
|---|---|---|---|---|
| **Chat tokens** | SSE `/api/chat/message/stream` | Real-time token delivery | ✓ AI SDK SSE | Phase 0 |
| **Plan set** | `task_update` event (plan snapshot) | Plan visibility + progress | ✓ Run ledger events | Phase 1 |
| **Node execution** | `node_tools_execution_start` | Task breakdown visibility | ✓ `node_started/completed` | Phase 1 |
| **Current action** | `update_subagent_current_action` | Human-friendly progress string | ✓ `node_action_updated` | Phase 1 |
| **Sources/refs** | `references_found` event (entity list) | Citation binding, provenance | ✓ `references_found` + Entity table | Phase 3 |
| **Deliverable preview** | `node_report_preview_*` (streaming sections) | Streaming report generation | ✓ `deliverable_preview_*` events | Phase 2 |
| **Deliverable publish** | Report artifact + viewer | Saved, downloadable deliverable | ✓ Artifact + manifest linkage | Phase 2 |
| **Browser automation** | `browser_use_*` events + `/api/browser-profile/*` | Remote browser session + HITL | ✓ Interrupt events + browser entity | Phase 4 |
| **Human approval** | `browser_use_await_user_input` | Pause & wait for user input | ✓ LangGraph interrupt + approval | Phase 4 |

### Document Generation Contract
| Feature | Superagent | NYQST Target | Difference | Status |
|---------|-----------|-------------|-----------|--------|
| **Markup Language** | GML (17 custom XML tags) | JSON AST (NDM v1) | Different abstraction level | ✓ DEC-015a |
| **Rendering** | GML → React component (custom) | JSON AST → rehype → React | Lower-level, more flexible | ✓ DEC-015b |
| **Layout Primitives** | `gml-row`, `gml-column`, `gml-card` | Markdown block quotes, dividers | Superagent more structured | Phase 2 |
| **Data Visualization** | `gml-chartcontainer` (Plotly.js) | `react-plotly.js` direct | Same library (Plotly.js) | ✓ DEC-048 |
| **View Types** | Report, Website, Presentation | Report (Phase 2), Website iframe (Phase 2), Slides (Phase 2+) | Superagent wider scope | Phase 2+ |

---

## 6. Implementation Roadmap (Phases)

### Phase 0: Event Contract & Instrumentation (1–2 weeks)
**Objective**: Make agentic workflow visible and replayable.

**Deliverables**:
- Intelli Run Event Contract v1 (types + payload schemas)
- Stable IDs for tool calls and nodes (persisted, not ephemeral)
- New ledger event types: `node_started`, `node_action_updated`, `node_completed`
- RunTimeline UI extended to group by node/tool
- Minimal Plan panel (right sidebar, task list + status + action)

**Acceptance**: For any run, see plan → nodes → tools → artifacts in single UI; events sufficient for replay.

### Phase 1: Planning Layer & Multi-Agent Executor (2–4 weeks)
**Objective**: Replicate Superagent's plan_set/plan/task model clean-room.

**Deliverables**:
- PlanSet/Plan/PlanTask models (ADR-003 Virtual Team)
- Planner node emitting plan set before execution
- Parallel subagent nodes (LangGraph subgraphs)
- Plan viewer panel: tasks, sources pending, current action, status

**Acceptance**: Complex request → multi-task plan; tasks progress independently; UI legible.

### Phase 2: Deliverables v1 (Report Preview + Publish) (2–4 weeks)
**Objective**: Ship Superagent-grade deliverable (report first).

**Deliverables**:
- NDM v1 schema (JSON AST, stored as artifact)
- Streaming `deliverable_preview_*` events (delta chunks)
- DeliverableViewer component (sections, TOC, download)
- Final deliverable persist + manifest linkage

**Acceptance**: User asks for "a report" → high-quality, structured, readable with citations and viewer.

### Phase 3: Web Research Toolchain (3–6 weeks)
**Objective**: Add web search/crawl + entity store + citations beyond docs.

**Deliverables**:
- MCP search tools (Brave/Tavily hot-swap via DEC-046)
- Entity table for URLs, extracted text, source metadata
- Citation binding rules (citations reference entity IDs)
- Source drawer with entity previews

**Acceptance**: Run cites external sources with stable provenance; sources discoverable.

### Phase 4: Human-in-Loop & Browser-Use (3–6 weeks)
**Objective**: Introduce safe interrupts + optional browser automation.

**Deliverables**:
- LangGraph interrupt patterns (pause → resume)
- Approval requested/granted/denied flow end-to-end
- Browser session service + streaming view
- Resume input endpoint

**Acceptance**: Agent pauses, asks for approval/input, resumes safely; run remains auditable.

### Phase 5: Production Hardening (Ongoing)
**Objective**: "Production-level" reliability + governance.

**Workstreams**:
- Multi-tenant controls (RBAC, quotas, feature flags)
- Background execution + retries (queue/workflow engine)
- Observability (tracing, costs, evals)
- Security review, sandboxing, connector secrets

---

## 7. Decision Register Snapshot

### Strategic Decisions (DEC-001-010)
- DEC-001: Cognitive ERP positioning
- DEC-002: Event-streamed planning required
- DEC-003: Domain-first models (ADR-001)
- DEC-004: Index Service contract (ADR-004)
- DEC-005: LangGraph orchestration (ADR-005)
- DEC-006: MCP tools (ADR-008)
- DEC-007: NDJSON event schema v1
- DEC-008: NDM v1 (JSON AST) deliverables
- DEC-009: Entity table for citations
- DEC-010: Run ledger canonical

### Implementation Decisions (DEC-011-041)
- DEC-011-020: Platform modules, users, metrics
- DEC-021-030: Infrastructure, dependency fixes
- DEC-031-041: Delivery strategy, cost model, auth

### Recent Decisions (DEC-042-052)
- **DEC-042**: LiteLLM multi-provider hot-swap (OpenAI-only v1)
- **DEC-043**: GML in separate ReportPanel, rehype-to-JSX
- **DEC-044**: Website iframe-only v1
- **DEC-045**: Langfuse self-hosted + $2/run state budget
- **DEC-046**: MCP search (hot-swap Brave/Tavily, supersedes DEC-032)
- **DEC-047**: Clarification UI deferred to v1.5
- **DEC-048**: Plotly.js (NOT Recharts)
- **DEC-049**: LangSmith Studio + graph-as-code (no visual editor)
- **DEC-050**: LangChain `with_structured_output()` for all JSON nodes
- **DEC-051**: Per-node async sessions from shared `async_sessionmaker`
- **DEC-052**: Migration 0005 split into 0005a/b/c
- **DEC-015a/b**: Backend JSON AST + Frontend rehype-to-JSX (split from DEC-015)

---

## 8. Cross-Document Consistency

### Known Corrections (v3 Synchronized)
1. **Chart Library**: Plotly.js (react-plotly.js), NOT Recharts
2. **Recoil vs Zustand**: Frontend uses Zustand (not Superagent's Recoil)
3. **BL-022 Dependency**: Must precede BL-001, not follow
4. **BL-003 Independence**: Standalone tools, no BL-001 dependency
5. **Migration 0005 Split**: 0005a (DB schema) + 0005b (LangGraph) + 0005c (indices)
6. **DEC-015 Split**: DEC-015a (backend JSON AST) + DEC-015b (frontend rehype-to-JSX)
7. **LangGraph Studio → LangSmith Studio**: Oct 2025 product rename
8. **DEC-032 Superseded**: DEC-046 (MCP search) replaces DEC-032 (tool selection)

### Verified Consistency
- ✓ 52+ decisions tracked in DECISION-REGISTER.md v2
- ✓ 7 Open Questions resolved with explicit decisions
- ✓ IMPLEMENTATION-PLAN v3 synchronized with PRD + ADRs
- ✓ LIBRARY-REFERENCE v2 updated with unified/rehype-parse/rehype-react
- ✓ All cross-references bidirectional (docs → docs)

---

## 9. Critical Knowledge Paths

### For New Team Members
1. **Day 1**: Read PLATFORM-FRAMING.md (bridge doc)
2. **Day 2**: Read 01_EXECUTIVE_SUMMARY + 02_VISION
3. **Day 3**: Read 03_PLATFORM (skim ADR Notes)
4. **Week 1**: Read IMPLEMENTATION-PLAN v3 (your phase + 2 phases ahead)
5. **Week 2**: Deep dive relevant ADRs (backend → ADR-004/005/008; frontend → ADR-002)

### For Product Decisions
→ 01_EXECUTIVE_SUMMARY → 04_PRODUCTS → 05_USERS → 07_ROADMAP → 08_METRICS → 09_RISKS

### For Architecture Reviews
→ PLATFORM-FRAMING → 06_ARCHITECTURE → (10 ADRs) → PLATFORM_REFERENCE_DESIGN

### For Implementation
→ IMPLEMENTATION-PLAN v3 (master reference) + phase-specific docs

---

## 10. Open Threads & Clarifications

### Needed Soon
- [ ] NDM v1 exact JSON schema (sketched in SUPERAGENT_PARITY_PLAN §3.4, needs formalization)
- [ ] Entity reference algorithm (sketched, needs edge cases: citations, tool outputs, deliverables)
- [ ] MCP tool discovery filtering (context-scoped, needs algorithm for "is tool X relevant to session Y?")
- [ ] Policy evaluation order (ADR-009 lists 4 templates, needs conflict resolution)

### Deferred to v1.5+
- [ ] LiteLLM hot-swap implementation (DEC-042, designed but not coded)
- [ ] Feature flag system UI (DEC-047, backend only in v1)
- [ ] Clarification UI for agent reasoning (DEC-047, deferred)

### External Dependencies (TBD)
- [ ] Search provider selection (Brave API vs Tavily, cost comparison needed)
- [ ] Langfuse self-hosted deployment (sizing, backup strategy)
- [ ] Neo4j Aura free tier limits → upgrade/fallback plan

---

## Manifest Summary

This knowledge map synthesizes insights from:
- **29 development documents** (11 PRD + 10 ADR + 8 planning/reference)
- **150+ supporting files** (analysis, research, prototypes)
- **2000+ pages** of specification and design

**Key Insight**: The platform is **specification-complete** for Phase 0–2 (event contract → planning → deliverables). Phases 3–5 (search → HITL → hardening) require external integrations (search APIs, observability platforms) but no architectural changes.

**Recommendation**: Phase 0 (2 weeks) is **de-risking**. If streaming + plan visibility works, rest of roadmap is high-confidence execution.

---

*Last Updated*: 2026-02-20
*Manifest Source*: `/Users/markforster/AirTable-SuperAgent/docs/design-reconstruction/00-inventory/devrepo-docs-manifest.json`
*Supporting Inventory*: 8 other manifest files in `00-inventory/` directory
