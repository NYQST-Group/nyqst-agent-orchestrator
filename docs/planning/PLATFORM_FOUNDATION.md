# NYQST Platform Foundation Plan

**Product:** NYQST - Deterministic Agentic Infrastructure for Commercial Intelligence  
**Company:** NYQST AI Limited  
**Version:** 1.0  
**Last Updated:** 2026-01-26

---

## Purpose

This document defines the **Platform Foundation**—the core infrastructure that must exist before any product features can be built. Unlike product features where prioritization frameworks (RICE, MoSCoW) determine order, the Platform Foundation sequence is driven by **technical dependencies**. These components are all required; the only question is what order to build them.

This is not a backlog to be prioritized. It is a dependency graph to be executed.

---

## Guiding Principle

**Platform first, then products.**

The Platform Foundation is the "Cognitive ERP" substrate. Without it, product features are impossible to build reliably. With it, product features become straightforward compositions of platform capabilities.

---

## Architecture Layers (Build Order)

The platform is built bottom-up. Lower layers must be stable before higher layers can be built.

```
BUILD ORDER (bottom to top):

6. USER INTERFACE LAYER          ← Last: consumes all below
   Workbench UI · Analysis Canvas · Research Interface
   
5. APPLICATION LAYER             ← After orchestration works
   Platform Modules · Product Variants
   
4. ORCHESTRATION LAYER           ← After services exist
   Agent Runtime · Workflow Engine · Session Management · Skills
   
3. SERVICES LAYER                ← After substrate exists
   Index Service · Run Ledger · Schema Registry · Policy Engine
   
2. SUBSTRATE LAYER               ← After infrastructure exists
   Artifact Store · Manifest Store · Pointer Store · Event Store
   
1. INFRASTRUCTURE LAYER          ← First: everything depends on this
   PostgreSQL · Object Storage · Vector Store · Message Queue
```

---

## Foundation Sequence

### Phase F1: Infrastructure Layer

**Dependencies:** None (starting point)

| Component | Description | Unblocks |
|-----------|-------------|----------|
| **PostgreSQL** | Primary relational store for metadata, auth, run ledger | All substrate components |
| **Object Storage** | S3-compatible blob storage for artifacts | Artifact Store |
| **Vector Store** | pgvector or dedicated vector DB for embeddings | Index Service |
| **Message Queue** | Redis/NATS for async events and pub/sub | Event Store, real-time updates |

**Completion Criteria:**
- All infrastructure services running and accessible
- Connection pooling and health checks configured
- Basic monitoring in place

**Status:** Complete (Docker Compose stack operational)

---

### Phase F2: Substrate Layer

**Dependencies:** F1 (Infrastructure)

| Component | Description | Unblocks |
|-----------|-------------|----------|
| **Artifact Store** | Immutable, content-addressed blob storage | Document ingestion, all data storage |
| **Manifest Store** | Immutable trees of artifact references | Versioning, bundles, corpora |
| **Pointer Store** | Mutable HEAD references to manifests | Current state, navigation |
| **Event Store** | Append-only event stream | Run ledger, audit, replay |

**Dependency Graph:**
```
Artifact Store ─────┐
                    ├──► Manifest Store ──► Pointer Store
Event Store ────────┘
```

**Completion Criteria:**
- Artifacts can be stored and retrieved by content hash
- Manifests can reference artifacts and other manifests
- Pointers can be created, moved, and queried
- Events can be appended and queried

**Status:** Complete (API endpoints operational)

---

### Phase F3: Services Layer

**Dependencies:** F2 (Substrate)

| Component | Description | Unblocks |
|-----------|-------------|----------|
| **Run Ledger** | Append-only audit trail for all operations | Agent runtime, audit, replay |
| **Index Service** | Search and retrieval (keyword, semantic, hybrid) | Research, document discovery |
| **Schema Registry** | Type definitions and validation | Structured data, claims |
| **Policy Engine** | RBAC/ABAC rules and enforcement | Access control, governance |

**Dependency Graph:**
```
Run Ledger ──────────────────────────────────────────┐
                                                     │
Index Service ───────────────────────────────────────┼──► Orchestration Layer
                                                     │
Schema Registry ─────────────────────────────────────┤
                                                     │
Policy Engine ───────────────────────────────────────┘
```

**Build Order within F3:**
1. **Run Ledger** (no dependencies within F3, needed for audit)
2. **Index Service** (needed for search/retrieval)
3. **Schema Registry** (needed for structured data)
4. **Policy Engine** (needed for access control)

**Completion Criteria:**
- All operations logged to run ledger
- Documents indexed and searchable
- Schemas can be registered and validated
- Policies can be defined and enforced

**Status:** In Progress
- Run Ledger: Complete
- Index Service: In Progress (OpenSearch integration)
- Schema Registry: Planned
- Policy Engine: Planned

---

### Phase F4: Orchestration Layer

**Dependencies:** F3 (Services)

| Component | Description | Unblocks |
|-----------|-------------|----------|
| **Agent Runtime** | LangGraph-based execution engine | All agent-driven work |
| **Session Management** | User sessions with state persistence | Workbench, "return to topic" |
| **Skills Framework** | Reusable capabilities for agents | Domain-specific extraction |
| **Workflow Engine** | Camunda integration for governed workflows | Regulated processes |

**Dependency Graph:**
```
Agent Runtime ──────────┐
                        │
Session Management ─────┼──► Application Layer
                        │
Skills Framework ───────┤
                        │
Workflow Engine ────────┘
```

**Build Order within F4:**
1. **Agent Runtime** (core execution, needed by everything)
2. **Session Management** (user context, needed for workbench)
3. **Skills Framework** (reusable capabilities, needed for domain work)
4. **Workflow Engine** (governed processes, can be parallel with skills)

**Completion Criteria:**
- Agents can execute multi-step tasks with checkpointing
- Sessions persist across browser refreshes
- Skills can be defined, versioned, and invoked
- Workflows can be defined and executed with human-in-the-loop

**Status:** In Progress
- Agent Runtime: In Progress (LangGraph integration)
- Session Management: Planned
- Skills Framework: Planned
- Workflow Engine: Planned

---

### Phase F5: Application Layer

**Dependencies:** F4 (Orchestration)

| Component | Description | Unblocks |
|-----------|-------------|----------|
| **Research Module** | Fast search, deep research, source linking | Research workflows |
| **Document Module** | Bundle/corpus management, version control | Document organization |
| **Analysis Module** | Infinite canvas, relationship visualization | Visual analysis |
| **Modelling Module** | Calculations, evidence chains, claims | Structured outputs |
| **Knowledge Module** | Ontologies, domain models, context injection | Domain expertise |
| **Insight Module** | Dashboards, alerts, reports | Organizational intelligence |

**Build Order within F5:**
1. **Document Module** (foundational for all other modules)
2. **Research Module** (needed for discovery)
3. **Analysis Module** (needed for exploration)
4. **Modelling Module** (needed for structured outputs)
5. **Knowledge Module** (needed for domain expertise)
6. **Insight Module** (aggregates from other modules)

**Completion Criteria:**
- Each module operational with basic capabilities
- Modules can compose (e.g., research feeds analysis)
- Data flows between modules via substrate

**Status:** Planned

---

### Phase F6: User Interface Layer

**Dependencies:** F5 (Application)

| Component | Description | Unblocks |
|-----------|-------------|----------|
| **Workbench UI** | IDE-like interface for complex work | Power user workflows |
| **Research Interface** | NotebookLM-like three-panel layout | Research workflows |
| **Analysis Canvas** | Infinite canvas for visual exploration | Visual analysis |
| **Admin Console** | Configuration and monitoring | Operations |

**Build Order within F6:**
1. **Workbench UI** (primary interface, needed for all work)
2. **Research Interface** (high-value, frequently used)
3. **Analysis Canvas** (visual exploration)
4. **Admin Console** (operations, can be parallel)

**Completion Criteria:**
- Users can perform end-to-end workflows
- UI is responsive and provides real-time feedback
- All platform capabilities accessible via UI

**Status:** In Progress
- Workbench UI: In Progress (React shell operational)
- Research Interface: Planned
- Analysis Canvas: Planned
- Admin Console: Planned

---

## Critical Path

The critical path through the foundation is:

```
Infrastructure → Substrate → Run Ledger → Index Service → Agent Runtime → Document Module → Workbench UI
```

This is the minimum path to a working system where users can:
1. Upload documents
2. Have agents process them
3. See results in the UI

Everything else can be built in parallel once this path is complete.

---

## Current Status Summary

| Phase | Status | Blocking Issues |
|-------|--------|-----------------|
| F1: Infrastructure | Complete | None |
| F2: Substrate | Complete | None |
| F3: Services | In Progress | Index Service integration |
| F4: Orchestration | In Progress | Agent Runtime integration |
| F5: Application | Planned | Waiting on F4 |
| F6: UI | In Progress | Workbench shell exists, needs modules |

---

## Jira Epic Mapping

When creating Jira epics, use this mapping:

| Foundation Phase | Jira Epic Prefix | Example |
|------------------|------------------|---------|
| F1: Infrastructure | `NYQST-INFRA-` | `NYQST-INFRA-001: PostgreSQL Setup` |
| F2: Substrate | `NYQST-SUB-` | `NYQST-SUB-001: Artifact Store` |
| F3: Services | `NYQST-SVC-` | `NYQST-SVC-001: Run Ledger` |
| F4: Orchestration | `NYQST-ORCH-` | `NYQST-ORCH-001: Agent Runtime` |
| F5: Application | `NYQST-APP-` | `NYQST-APP-001: Document Module` |
| F6: UI | `NYQST-UI-` | `NYQST-UI-001: Workbench Shell` |

---

## What This Document Does NOT Cover

This document covers **platform foundation only**. The following are covered elsewhere:

- **Product Features** (PropSygnal, RegSygnal) → See `EPIC_BACKLOG.md` (to be created)
- **Architectural Decisions** → See `/docs/adr/` (ADR documents)
- **Detailed Technical Specs** → See `/docs/PLATFORM_REFERENCE_DESIGN.md`
- **Success Metrics** → See `/docs/prd/08_METRICS.md`
- **Risk Analysis** → See `/docs/prd/09_RISKS.md`

---

## Related Documents

- [Architecture](../prd/06_ARCHITECTURE.md) - Technical architecture details
- [Roadmap](../prd/07_ROADMAP.md) - Full product roadmap including product features
- [Platform Modules](../prd/03_PLATFORM.md) - Module capabilities
- [Platform Reference Design](../PLATFORM_REFERENCE_DESIGN.md) - Detailed technical specification
- [Virtual Team Operating System](./VIRTUAL_TEAM_OPERATING_SYSTEM.md) - AI agent coordination infrastructure
