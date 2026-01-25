# Repository Index: Complete Documentation & Code Structure Guide

*Date: 2026-01-23*  
*Purpose: Comprehensive index for models without indexing service access*

---

## Git Update (2026-01-24): Demo Notebook + RAG + Validated Startup

This iteration focused on making the repo **demoable end-to-end** (NotebookLM-like) and reducing integration thrash via a **validated startup sequence**.

**Key additions**
- **Demo login (dev-only)**: `POST /api/v1/auth/dev-bootstrap` (requires `DEBUG=true`) + UI button on the login page.
- **Demo-grade RAG**: pgvector-backed chunk store (`rag_chunks`) + `/api/v1/rag/index` and `/api/v1/rag/ask`.
- **Notebook UX (pointer-based)**: Create notebooks from the Explorer (`+`), upload docs into a notebook, index, and ask with sources.
- **Validated startup**: `docs/STARTUP_SEQUENCE.md` + `scripts/dev/validate.sh` + `scripts/dev/smoke_api.py` to run infra → migrations → backend health → API smoke tests → UI typecheck/build **in order**.

**Important compatibility note**
- Alembic revision IDs were normalized to use date-based IDs (e.g., `20260123_0001`). If you previously ran migrations under the old `0001` ID, you may need to restamp or recreate the dev DB. See `docs/STARTUP_SEQUENCE.md`.

## Context for Second Opinion Agent

### What the User Wanted

The user wanted to understand what **three parallel AI agents** inferred about the requirements for a Commercial Real Estate (CRE) intelligence platform. The agents were given different perspectives:

1. **UI Agent**: "Identify UI requirements and build UI components"
2. **Workflow Agent**: "Come up with CRE workflows and requirements"  
3. **System Agent**: "Build a holistic system architecture"

**The Goal**: Understand what each agent inferred was needed, identify **incompatibilities and conflicts** between their approaches, and extract maximum value from all three perspectives.

**Key Question**: "Do different agents suggest incompatible approaches? Are UI proposals different? Would workflows not be supported by UI or system?"

### What the User Did

**Phase 1: Parallel Development** (Three Independent Branches)
- Created three separate branches, each with a different agent working independently
- Each agent built/documented their approach without seeing the others' work
- All branches were then merged into `merged-branch`

**Phase 2: Analysis Requests** (Iterative Deepening)
1. **Initial Request**: "Update REQUIREMENTS_CONSOLIDATION.md to identify incompatibilities and conflicts"
2. **Expansion**: "Do a from-scratch analysis of the codebase, infer requirements from UI system, general system, research, designs, stubs"
3. **Cross-Comparison**: "Compare what's been described vs what hasn't been reviewed, what analysis hasn't been done"
4. **Deep Mapping**: "Do all the next steps" (persona-to-feature mapping, decision points, trust lifecycle)
5. **Consistency Check**: "Review your approach - are you sure the design is consistent? Did different agents come up with different methods?"
6. **Strategic Questions**: "Is it obvious if there are winning strategies? Rigid vs flexible GUI? What other advanced design questions?"
7. **Index Creation**: "Create a document of what you've documented and where, summarizing content and code structures"
8. **Project Explanation**: "Write an explanation of what I did, use commit histories from original branches"
9. **Commit Review**: "Did you definitely look at all commits? Does what you learned impact your analysis?"
10. **Master Consolidation**: "Which files need editing? Shall we create one master file?"

**Result**: Comprehensive analysis across multiple dimensions, revealing inconsistencies, gaps, and strategic questions.

### What's in the Repository

**Code Structure**:
- `src/intelli/` - Backend Python code (FastAPI, SQLAlchemy models, services, APIs)
- `ui/src/` - Frontend React/TypeScript code (components, stores, hooks, types)
- `schemas/` - JSON schemas for domain primitives (Document, Event, Claim, Extraction)
- `requirements/` - Requirements documents (what to build first, personas, workflows)
- `scenarios/` - Workflow scenarios and persona definitions
- `research/` - Industry research (AI tooling, CRE workflows, architecture patterns)
- `docs/` - Architecture and design documents

**Analysis Documents** (Created During Analysis Phase):
- `REQUIREMENTS_ANALYSIS.md` - From-scratch requirements inference from codebase
- `CROSS_MAPPING_ANALYSIS.md` - Cross-mapping personas, decisions, trust, workflows
- `ARCHITECTURAL_CONSISTENCY_ANALYSIS.md` - Inconsistencies between UI/Backend/Schemas
- `ANALYSIS_GAPS_AND_MISSING.md` - Meta-analysis of what wasn't analyzed
- `ADVANCED_DESIGN_QUESTIONS.md` - Strategic design questions requiring decisions
- `ANALYSIS_UPDATE_FROM_COMMITS.md` - Corrections from detailed commit review
- `REPOSITORY_INDEX.md` - **This file** - Complete index of documentation and code structures
- `PROJECT_EXPLANATION.md` - Explanation of parallel agent development
- `MASTER_ANALYSIS.md` - Consolidated master analysis

**Original Requirements Documents**:
- `REQUIREMENTS_CONSOLIDATION.md` - Initial consolidation (now in .gitignore)
- `requirements/WHAT-TO-BUILD-FIRST.md` - Wedge strategy (Critical Dates)
- `requirements/CRE-USER-PERSONAS.md` - 7 user personas
- `requirements/WORKFLOWS.md` - CRE workflow scenarios

**Architecture Documents**:
- `docs/UI_ARCHITECTURE.md` - UI architecture patterns
- `docs/RESEARCH_SYNTHESIS.md` - Research findings synthesis
- `docs/REFACTORING_OPPORTUNITIES.md` - Code improvement opportunities

### What I (The Analysis Agent) Wrote

**Analysis Documents Created**:

1. **REQUIREMENTS_ANALYSIS.md** (1,157 lines)
   - **Purpose**: Infer requirements from existing code, types, schemas, research
   - **Method**: Systematic analysis of UI components, backend models, schemas, research docs
   - **Key Findings**: 8 major themes, Phase 0 complete, Phase 1 critical gaps
   - **Status**: ✅ Complete, but Phase 0 description needs enhancement (production infrastructure)

2. **CROSS_MAPPING_ANALYSIS.md** (881 lines)
   - **Purpose**: Cross-map personas to features, extract decision points, analyze trust lifecycle
   - **Method**: Deep mapping across personas, workflows, UI, and system
   - **Key Findings**: Focus on decision support (5 minutes), not process automation (100 hours)
   - **Status**: ✅ Complete

3. **ARCHITECTURAL_CONSISTENCY_ANALYSIS.md** (646 lines)
   - **Purpose**: Identify inconsistencies between UI, Backend, and Schema approaches
   - **Method**: Compare TypeScript types, Python models, JSON schemas
   - **Key Findings**: Two event systems, naming mismatches, type conflicts, missing implementations
   - **Status**: ✅ Complete

4. **ANALYSIS_GAPS_AND_MISSING.md** (585 lines)
   - **Purpose**: Meta-analysis - what hasn't been analyzed?
   - **Method**: Compare what was analyzed vs what exists in repo
   - **Key Findings**: Missing persona-to-feature mapping, decision point analysis, trust lifecycle
   - **Status**: ✅ Complete (led to CROSS_MAPPING_ANALYSIS.md)

5. **ADVANCED_DESIGN_QUESTIONS.md** (692 lines)
   - **Purpose**: Extract strategic design questions requiring decisions
   - **Method**: Analyze trade-offs, persona needs, adoption strategy
   - **Key Findings**: 10 major design questions, 5 clear winning strategies
   - **Status**: ✅ Complete, but Section 6 needs LISTEN/NOTIFY note

6. **ANALYSIS_UPDATE_FROM_COMMITS.md** (376 lines)
   - **Purpose**: Assess impact of detailed commit review on previous analyses
   - **Method**: Review all commits across all branches, identify corrections needed
   - **Key Findings**: LISTEN/NOTIFY already implemented, production infrastructure more mature
   - **Status**: ✅ Complete

7. **REPOSITORY_INDEX.md** (This file, 712 lines)
   - **Purpose**: Complete index for models without indexing service access
   - **Method**: Document all analysis files, repo structure, code structures, relationships
   - **Key Findings**: Comprehensive navigation guide
   - **Status**: ✅ Complete

8. **PROJECT_EXPLANATION.md** (615 lines)
   - **Purpose**: Explain parallel agent development using commit histories
   - **Method**: Review all commits, document deliverables, approaches, challenges
   - **Key Findings**: Detailed history of three-agent parallel development
   - **Status**: ✅ Complete

9. **MASTER_ANALYSIS.md** (~850 lines)
   - **Purpose**: Consolidated master analysis incorporating all findings and corrections
   - **Method**: Synthesize all analysis documents, incorporate corrections
   - **Key Findings**: Complete picture with inconsistencies, gaps, strategic recommendations
   - **Status**: ✅ Complete

### Key Insights for Second Opinion Agent

**What Was Discovered**:
- ✅ System is MORE production-ready than "Phase 0" suggests (Redis, logging, jobs, LISTEN/NOTIFY)
- ⚠️ Significant inconsistencies between three approaches (naming, types, concepts)
- ⚠️ Critical gaps preventing Phase 1 implementation (domain Events missing)
- ⚠️ Strategic design questions requiring decisions (rigid vs flexible GUI, etc.)

**What Each Agent Actually Delivered vs What Was Asked**:

| Agent | Original Ask | What Was Actually Delivered | Advancement Level |
|-------|--------------|----------------------------|-------------------|
| **Branch 1** | "Identify UI requirements and build UI components" | Complete backend infrastructure + UI workbench + production infrastructure + enterprise features | **Significantly Advanced** - Built full platform, not just UI |
| **Branch 2** | "Come up with CRE workflows and requirements" | Workflows + personas + schemas + research + wedge strategy + universal abstractions + cross-domain patterns | **Significantly Advanced** - Discovered universal patterns, created implementation-ready schemas |
| **Branch 3** | "Build a holistic system architecture" | Comprehensive type system + async UI components + agent components + spatial canvas + research synthesis | **Significantly Advanced** - Built component architecture + type system + research foundation |

**Commit History Evidence**:
- **Branch 1**: Started with Phase 0 infrastructure, then added UI workbench, then enterprise features, then production infrastructure
- **Branch 2**: Started with CRE workflows, then discovered universal abstractions, then created schemas, then added research synthesis, then wedge strategy
- **Branch 3**: Started with async components, then added agent components, then spatial canvas, then research synthesis

**Key Finding**: All three agents **went significantly beyond their original asks**, delivering:
- More comprehensive solutions than requested
- Cross-cutting concerns (research, documentation, architecture)
- Production-ready infrastructure (not just prototypes)
- Strategic insights (wedge strategy, universal abstractions, trust patterns)

**What Needs to Be Done**:
1. **Fix Inconsistencies** (Week 1): Event system distinction, artifact field alignment, claim status unification
2. **Implement Phase 1** (Weeks 2-4): Event Management System, Document Extraction, Verification UX
3. **User Testing** (Month 2-3): Get real users, iterate based on feedback

**What You Should Review**:
- Are the inconsistencies correctly identified?
- Are the strategic recommendations sound?
- Are there additional gaps or inconsistencies I missed?
- Are the implementation priorities correct?
- Are there alternative approaches worth considering?
- **Did the agents correctly interpret the asks, or did they go too far beyond scope?**

**How to Use This Index**:
- Start with **Part 1** to understand what analysis documents exist
- Use **Part 2** to navigate the repository structure and see which agent created which files
- Use **Part 3** to find specific code implementations
- Use **Part 4** to understand document relationships
- Use **Part 5** for quick navigation guides

---

## Executive Summary

This document provides a complete index of:
1. **Analysis Documents** - Documents created during analysis sessions
2. **Repository Structure** - What exists and where
3. **Code Structures** - Key implementations and their locations
4. **Document Relationships** - How documents relate to each other

**Use this document to navigate the codebase and understand the full context.**

---

## Part 1: Analysis Documents (Created During Analysis)

### 1.1 Core Analysis Documents

| Document | Location | Purpose | Key Findings |
|----------|----------|---------|--------------|
| **REQUIREMENTS_ANALYSIS.md** | Root | From-scratch requirements inference from codebase | Identifies 8 themes, gaps in implementation, priority requirements |
| **CROSS_MAPPING_ANALYSIS.md** | Root | Cross-mapping personas, decisions, trust, workflows | Maps 7 personas to features, extracts decision points, trust lifecycle |
| **ARCHITECTURAL_CONSISTENCY_ANALYSIS.md** | Root | Identifies inconsistencies between UI/Backend/Schemas | Two event systems, naming mismatches, type conflicts, missing implementations |
| **ANALYSIS_GAPS_AND_MISSING.md** | Root | Meta-analysis of what wasn't analyzed | Identifies missing analysis: persona-to-feature mapping, decision points, trust lifecycle |
| **ADVANCED_DESIGN_QUESTIONS.md** | Root | Extracts strategic design questions | Rigid vs flexible GUI, decision support vs automation, trust lifecycle, 8 major questions |

### 1.2 Analysis Document Summaries

#### REQUIREMENTS_ANALYSIS.md
**Purpose**: Infer requirements from existing code, types, schemas, and research.

**Key Sections**:
- UI Requirements (from components & types)
- Backend Requirements (from models & APIs)
- Schema Requirements (from JSON schemas)
- Research Requirements (from research docs)
- Cross-Theme Analysis (8 themes)
- Requirements by Priority (Phase 0/1/2/3)

**Key Findings**:
- 8 major themes identified
- Significant gaps: Event Management, Extraction, Claims, Evidence
- Phase 0 complete (Substrate, Run Ledger)
- Phase 1 critical: Critical Dates (Wedge Strategy)

**Code References**:
- `src/types/core.ts` - Core domain types
- `src/intelli/db/models/substrate.py` - Database models
- `schemas/*.schema.json` - Domain primitives

#### CROSS_MAPPING_ANALYSIS.md
**Purpose**: Cross-map personas, decision points, trust lifecycle, and workflows.

**Key Sections**:
1. Persona-to-Feature Mapping (7 personas)
2. Decision Point Analysis (extracts critical decisions)
3. Trust Lifecycle Analysis (UNTRUSTED → ACCEPTED → AUTHORITATIVE)
4. Multi-Party Visibility Analysis (role-based views)
5. CRE-Specific vs Generic Analysis (80% generic)
6. Workflow ↔ UI ↔ System Mapping (alignment analysis)
7. Integration Requirements (external systems)
8. Cross-Approach Synthesis (alignment matrix)
9. Recommendations (prioritized actions)

**Key Findings**:
- Focus on decision support (5 minutes), not process automation (100 hours)
- Critical gaps: Event Management, Covenant Monitoring, Report Generation
- Well-aligned: Run Tracking, Artifact Management, Document Viewing

**Code References**:
- `scenarios/personas/cre-user-personas.md` - Persona definitions
- `scenarios/acquisition/*.md` - Workflow scenarios
- `src/types/evidence.ts` - Claim/Evidence types

#### ARCHITECTURAL_CONSISTENCY_ANALYSIS.md
**Purpose**: Identify inconsistencies between UI, Backend, and Schema approaches.

**Key Sections**:
1. Event System Confusion (RunLedgerEvent vs Domain Event)
2. Naming Convention Inconsistencies (camelCase vs snake_case)
3. Claim Type Inconsistencies (status values differ)
4. Evidence vs EvidenceSpan Confusion (different concepts)
5. Decision Type Inconsistencies (structure differences)
6. Missing Implementations (schemas without backend)
7. Conceptual Architecture Differences (Substrate, Document models)
8. API Response Mismatches (TypeScript vs Python)
9. Run Event Type Mismatches (naming conventions)

**Key Findings**:
- Two different "Event" systems (not explained)
- Artifact model mismatches (field names differ)
- Claim status values incompatible
- EvidenceSpan vs Evidence confusion
- Missing domain Event implementation (critical)

**Code References**:
- `src/types/events.ts` - RunLedgerEvent types
- `src/intelli/db/models/runs.py` - RunEventType enum
- `schemas/event.schema.json` - Domain Event schema
- `src/types/evidence.ts` - Claim/Evidence types
- `schemas/claim.schema.json` - Claim schema

#### ANALYSIS_GAPS_AND_MISSING.md
**Purpose**: Meta-analysis identifying what wasn't analyzed.

**Key Sections**:
- What Was Analyzed vs What Wasn't
- Critical Missing Analysis (persona-to-feature, decision points, trust lifecycle)
- Cross-Approach Gaps (UI vs Workflow vs System)
- Files Not Yet Analyzed (specific files listed)
- Recommended Next Steps

**Key Findings**:
- Missing: Persona-to-feature mapping, decision point extraction, trust lifecycle analysis
- Missing: Multi-party visibility, CRE-specific vs generic analysis
- Missing: Integration requirements, performance & scale analysis

**Code References**:
- Lists specific files to analyze
- References scenarios and research not yet cross-mapped

#### ADVANCED_DESIGN_QUESTIONS.md
**Purpose**: Extract strategic design questions requiring decisions.

**Key Sections**:
1. Rigid GUI vs Flexible GUI (boundaries)
2. Decision Support vs Process Automation (mix)
3. Trust Lifecycle (rigid vs flexible)
4. Generic Primitives vs CRE-Specific (mix)
5. UI Architecture (IDE vs Forms)
6. Real-Time vs On-Demand (update strategy)
7. Autonomy Slider (control level)
8. Data Model (immutable vs mutable)
9. Integration Strategy (deep vs shallow)
10. Winning Strategies (clear winners)

**Key Findings**:
- Hybrid GUI: Rigid core + flexible layout + rigid components
- Adaptive Trust: Rigid for critical, flexible for routine
- Task-Based UI: IDE for complex, forms for simple
- 5 clear winning strategies identified

**Code References**:
- `docs/UI_ARCHITECTURE.md` - UI architecture patterns
- `docs/RESEARCH_SYNTHESIS.md` - Research on UI patterns
- `requirements/CRITICAL-ANALYSIS.md` - Strategic insights

---

## Part 2: Repository Structure

### 2.1 File-to-Agent Mapping

**Branch 1: Agent-First Document Intelligence** (`agent-first-doc-intelligence-XoERL`)
- **Commits**: `0ef57fa`, `9278d91`, `0e6e3e4`, `678e48c`
- **Files Created/Modified**:
  - `src/intelli/` - **All backend Python code** (models, APIs, services, MCP tools, storage)
  - `ui/src/` - **React UI workbench** (workbench shell, viewers, explorer, timeline)
  - `docs/UI_ARCHITECTURE.md` - UI architecture patterns
  - `docs/REFACTORING_OPPORTUNITIES.md` - Code improvement opportunities
  - `src/intelli/core/pubsub.py` - PostgreSQL LISTEN/NOTIFY PubSub class (exists but not used by streams.py)
  - `src/intelli/core/cache.py` - Redis caching
  - `src/intelli/core/logging.py` - Structured logging
  - `src/intelli/core/jobs.py` - ARQ background jobs
  - `src/intelli/api/v1/auth.py` - Authentication endpoints
  - `src/intelli/api/v1/streams.py` - SSE streaming (implements own LISTEN connection, does not use pubsub.py)
  - All database models (`src/intelli/db/models/`)
  - All API endpoints (`src/intelli/api/v1/`)
  - All MCP tools (`src/intelli/mcp/`)

**Branch 2: CRE Intelligence Workflows** (`cre-intelligence-workflows-8y9MD`)
- **Commits**: `b7a9f50`, `84cc99d`, `432474a`, `5fa5f47`, `efb841c`, `a14e1f5`
- **Files Created/Modified**:
  - `scenarios/` - **All workflow scenarios and personas**
    - `scenarios/personas/cre-user-personas.md` - 7 user personas
    - `scenarios/acquisition/*.md` - 4 acquisition workflows
    - `scenarios/asset-management/*.md` - 2 asset management workflows
    - `scenarios/journeys/stakeholder-perspectives.md` - Stakeholder analysis
  - `schemas/` - **All JSON schemas**
    - `schemas/document.schema.json` - Document Intelligence primitive
    - `schemas/event.schema.json` - Event Management primitive
    - `schemas/claim.schema.json` - Claim/Decision primitive
    - `schemas/cre/lease-events.config.json` - CRE event types
    - `schemas/cre/uk-lease.config.json` - UK lease extraction schema
  - `requirements/` - **All requirements documents**
    - `requirements/WHAT-TO-BUILD-FIRST.md` - Wedge strategy
    - `requirements/CRITICAL-ANALYSIS.md` - Gap analysis, universal abstractions
    - `requirements/UNIVERSAL-ABSTRACTIONS.md` - Five universal primitives
    - `requirements/RESEARCH-SYNTHESIS.md` - Consolidated research
    - `requirements/ai-specific/` - AI-specific requirements
  - `research/` - **All research documents**
    - `research/ai-tooling/` - AI tooling patterns, trust UX, adoption failures
    - `research/architecture/` - Event-driven, document graph patterns
    - `research/cre-workflows/` - CRE workflow research
    - `research/cross-domain/` - Insurtech, legaltech patterns
    - `research/rics/` - RICS standards
    - `research/inrev/` - INREV guidelines
  - `USER-SCENARIOS-INDEX.md` - Navigation guide

**Branch 3: Async UI Components** (`async-ui-components-setup-MGSvt`)
- **Commits**: `106fd37`, `73b51e4`
- **Files Created/Modified**:
  - `src/types/` - **All TypeScript type definitions**
    - `src/types/core.ts` - Backbone objects (Artifact, Manifest, Pointer, Run)
    - `src/types/evidence.ts` - Evidence system (Claim, EvidenceSpan, Decision)
    - `src/types/events.ts` - Run Ledger events
    - `src/types/docir.ts` - Document Intermediate Representation
    - `src/types/knowledge.ts` - Knowledge base types
    - `src/types/connectors.ts` - Connector types
  - `src/components/` - **All React UI components**
    - `src/components/async/` - Async primitives (Suspense, ErrorBoundary, loading)
    - `src/components/agent/` - Agent interaction (AutonomySlider, ApprovalGate, TrustIndicator)
    - `src/components/canvas/` - Spatial canvas (EvidenceCanvas, ProvenanceGraph)
    - `src/components/panes/` - Workbench panes (ArtifactBrowser, RunExplorer, DocumentViewer)
    - `src/components/ui/` - shadcn/ui components
  - `src/stores/` - Zustand state management
  - `src/hooks/` - React hooks (use-sse, use-query, etc.)
  - `src/api/` - API client (matching backend schemas)
  - `docs/RESEARCH_SYNTHESIS.md` - UI research synthesis

**Overlap/Shared Files**:
- `README.md` - Project overview (likely from Branch 1)
- `docs/` - Some docs from Branch 1, some from Branch 3
- `requirements/` - All from Branch 2
- `schemas/` - All from Branch 2
- `scenarios/` - All from Branch 2
- `research/` - All from Branch 2

### 2.2 Root-Level Documents

| File | Purpose | Status | Agent Source |
|------|---------|--------|--------------|
| **README.md** | Project overview, architecture, quick start | ✅ Complete | Branch 1 |
| **USER-SCENARIOS-INDEX.md** | Navigation guide to scenarios, research, requirements | ✅ Complete | Branch 2 |
| **REQUIREMENTS_CONSOLIDATION.md** | (In .gitignore) Previous consolidation attempt | ⚠️ Ignored | Analysis phase |

### 2.3 Directory Structure

```
/
├── src/                          # Source code (TypeScript + Python)
│   ├── components/              # React UI components
│   ├── types/                   # TypeScript type definitions
│   ├── stores/                  # Zustand state management
│   ├── hooks/                   # React hooks
│   └── intelli/                 # Python backend
│       ├── api/                 # FastAPI endpoints
│       ├── db/                  # Database models
│       ├── services/            # Business logic
│       ├── repositories/        # Data access layer
│       ├── schemas/             # Pydantic schemas
│       ├── mcp/                 # MCP server & tools
│       └── storage/             # Storage backends
│
├── schemas/                      # JSON schemas (domain primitives)
│   ├── document.schema.json     # Document Intelligence primitive
│   ├── event.schema.json        # Event Management primitive
│   ├── claim.schema.json        # Claim/Decision primitive
│   └── cre/                     # CRE-specific configurations
│
├── requirements/                 # Requirements & strategy documents
│   ├── CRITICAL-ANALYSIS.md     # Gap analysis, universal abstractions
│   ├── WHAT-TO-BUILD-FIRST.md   # Wedge strategy
│   ├── UNIVERSAL-ABSTRACTIONS.md # Five universal primitives
│   ├── RESEARCH-SYNTHESIS.md    # Consolidated research findings
│   └── ai-specific/             # AI-specific requirements
│
├── scenarios/                    # User scenarios & workflows
│   ├── acquisition/             # Acquisition phase workflows
│   ├── asset-management/        # Asset management workflows
│   ├── personas/               # User personas
│   └── journeys/                # Stakeholder journeys
│
├── research/                     # External research inputs
│   ├── rics/                    # RICS standards research
│   ├── inrev/                   # INREV guidelines research
│   ├── cre-workflows/           # CRE workflow research
│   ├── ai-tooling/              # AI landscape, adoption, trust UX
│   ├── cross-domain/            # LegalTech, InsurTech patterns
│   └── architecture/            # Event-driven, document graph patterns
│
├── docs/                         # Architecture & design documents
│   ├── UI_ARCHITECTURE.md       # UI architecture patterns
│   ├── RESEARCH_SYNTHESIS.md    # Research synthesis
│   └── REFACTORING_OPPORTUNITIES.md # Code refactoring opportunities
│
├── migrations/                   # Database migrations (Alembic)
│   └── versions/                # Migration scripts
│
└── tests/                        # Test files
```

---

## Part 3: Key Code Structures

### 3.1 TypeScript Type Definitions

**Location**: `src/types/`

| File | Purpose | Key Types |
|------|---------|-----------|
| **core.ts** | Core domain types | `Artifact`, `Manifest`, `Pointer`, `Run`, `Project`, `Tenant` |
| **events.ts** | Run ledger event types | `RunLedgerEvent`, `BaseEvent`, event type unions |
| **evidence.ts** | Evidence, claims, decisions | `Claim`, `EvidenceSpan`, `Decision`, `ClaimSupportLink` |
| **docir.ts** | Document IR types | `DocIRDocument`, `DocIRPage`, `DocIRBlock`, `DocIRTable` |
| **knowledge.ts** | Knowledge base types | `KnowledgeBase`, `RetrievalProfile`, `EvidenceSpanRef` |
| **connectors.ts** | Connector types | `Connector`, `ConnectorConfig`, `WebhookEvent` |

**Key Structures**:
- **Artifact**: `contentHash`, `logicalType`, `mimeType`, `sizeBytes`, `storageKey`
- **Run**: `type`, `status`, `inputManifestIds`, `outputManifestId`, `checkpoints`
- **Claim**: `type`, `status`, `title`, `content`, `confidence`, `tags`
- **EvidenceSpan**: `documentArtifactId`, `blockId`, `pageNumber`, `startOffset`, `endOffset`

### 3.2 Python Database Models

**Location**: `src/intelli/db/models/`

| File | Purpose | Key Models |
|------|---------|------------|
| **substrate.py** | Substrate models | `Artifact`, `Manifest`, `Pointer`, `PointerHistory` |
| **runs.py** | Run & event models | `Run`, `RunEvent`, `RunStatus`, `RunEventType` |
| **auth.py** | Auth & multi-tenancy | `Tenant`, `User`, `APIKey`, `AuditLog` |

**Key Structures**:
- **Artifact**: `sha256` (PK), `media_type`, `size_bytes`, `storage_uri`, `reference_count`
- **Manifest**: `sha256` (PK), `tree` (JSONB), `parent_sha256`, `entry_count`
- **Pointer**: `id` (PK), `namespace`, `name`, `manifest_sha256`, `pointer_type`
- **Run**: `id` (PK), `run_type`, `status`, `input_manifest_sha256`, `output_manifest_sha256`
- **RunEvent**: `id` (PK), `run_id`, `event_type`, `payload` (JSONB), `sequence_num`

### 3.3 Python Services

**Location**: `src/intelli/services/`

| Directory | Purpose | Key Services |
|-----------|---------|--------------|
| **substrate/** | Substrate operations | `ArtifactService`, `ManifestService`, `PointerService` |
| **runs/** | Run management | `RunService`, `LedgerService` |
| **audit_service.py** | Audit logging | `AuditService` |

**Key Methods**:
- **ArtifactService**: `create_artifact()`, `get_artifact()`, `get_content()`, `delete_artifact()`
- **ManifestService**: `create_manifest()`, `get_manifest()`, `get_entries()`, `diff_manifests()`
- **PointerService**: `create_pointer()`, `advance_pointer()`, `reset_pointer()`
- **RunService**: `create_run()`, `start_run()`, `complete_run()`, `fail_run()`
- **LedgerService**: `log_event()`, `get_events()`, `stream_events()`

### 3.4 Python API Endpoints

**Location**: `src/intelli/api/v1/`

| File | Purpose | Key Endpoints |
|------|---------|---------------|
| **artifacts.py** | Artifact API | `POST /artifacts`, `GET /artifacts/{sha256}`, `GET /artifacts/{sha256}/url` |
| **manifests.py** | Manifest API | `POST /manifests`, `GET /manifests/{sha256}`, `GET /manifests/{sha256}/diff/{new}` |
| **pointers.py** | Pointer API | `GET /pointers/{ns}/{name}`, `PUT /pointers/{id}/advance` |
| **runs.py** | Run API | `POST /runs`, `GET /runs/{id}`, `GET /runs/{id}/events` |
| **streams.py** | SSE streaming | `GET /runs/{id}/stream` (SSE) |
| **auth.py** | Authentication | `POST /auth/login`, `POST /auth/api-keys` |

### 3.5 React Components

**Location**: `src/components/`

| Directory | Purpose | Key Components |
|-----------|---------|---------------|
| **workbench/** | Workbench shell | `WorkbenchShell`, `WorkbenchSidebar`, `CommandPalette` |
| **panes/** | Content panes | `RunExplorerPane`, `ArtifactBrowserPane`, `DocumentViewerPane`, `ChatPane` |
| **agent/** | Agent UI | `AutonomySlider`, `ApprovalGate`, `TrustIndicator`, `ReasoningPanel` |
| **canvas/** | Canvas views | `EvidenceCanvas`, `ProvenanceGraph`, `SemanticZoom` |
| **async/** | Async handling | `ErrorFallback`, `LoadingStates`, `SuspenseWrapper` |

**Key Structures**:
- **WorkbenchShell**: Multi-pane layout, resizable panels, pane management
- **RunExplorerPane**: Run timeline, event list, step details
- **ArtifactBrowserPane**: Artifact list, filters, preview cards
- **DocumentViewerPane**: PDF viewer, evidence highlights, citations

### 3.6 JSON Schemas

**Location**: `schemas/`

| File | Purpose | Key Definitions |
|------|---------|-----------------|
| **document.schema.json** | Document Intelligence | `DocumentSource`, `DocumentStructure`, `Extraction`, `DocumentRelationship` |
| **event.schema.json** | Event Management | `Event`, `Deadline`, `Alert`, `Action`, `Outcome`, `EventType` |
| **claim.schema.json** | Claim/Decision | `Claim`, `Evidence`, `Decision`, `ClaimType`, `ClaimSet` |

**Key Structures**:
- **DocumentSource**: `id`, `content_hash`, `media_type`, `ingested_at`, `artifact_ref`
- **Event**: `id`, `event_type_id`, `trigger_date`, `status`, `deadlines`, `context`
- **Claim**: `id`, `claim_type_id`, `statement`, `status`, `evidence`, `quantification`

---

## Part 4: Document Relationships

### 4.1 Analysis Document Flow

```
REQUIREMENTS_ANALYSIS.md
    ↓ (identifies gaps)
ANALYSIS_GAPS_AND_MISSING.md
    ↓ (recommends next steps)
CROSS_MAPPING_ANALYSIS.md
    ↓ (identifies inconsistencies)
ARCHITECTURAL_CONSISTENCY_ANALYSIS.md
    ↓ (extracts design questions)
ADVANCED_DESIGN_QUESTIONS.md
```

### 4.2 Requirements Document Flow

```
requirements/CRITICAL-ANALYSIS.md
    ↓ (identifies universal abstractions)
requirements/UNIVERSAL-ABSTRACTIONS.md
    ↓ (defines wedge strategy)
requirements/WHAT-TO-BUILD-FIRST.md
    ↓ (synthesizes research)
requirements/RESEARCH-SYNTHESIS.md
```

### 4.3 Code-to-Document Mapping

| Code Structure | Documented In | Analysis Document |
|----------------|---------------|-------------------|
| **TypeScript Types** | `src/types/*.ts` | REQUIREMENTS_ANALYSIS.md (Section 1.1) |
| **Python Models** | `src/intelli/db/models/*.py` | REQUIREMENTS_ANALYSIS.md (Section 2.1) |
| **JSON Schemas** | `schemas/*.schema.json` | REQUIREMENTS_ANALYSIS.md (Section 3.1) |
| **UI Components** | `src/components/**/*.tsx` | REQUIREMENTS_ANALYSIS.md (Section 1.1) |
| **API Endpoints** | `src/intelli/api/v1/*.py` | REQUIREMENTS_ANALYSIS.md (Section 2.2) |
| **Inconsistencies** | All code | ARCHITECTURAL_CONSISTENCY_ANALYSIS.md |

### 4.4 Scenario-to-Requirement Mapping

| Scenario | Requirements Document | Analysis Document |
|----------|----------------------|-------------------|
| **Personas** | `scenarios/personas/cre-user-personas.md` | CROSS_MAPPING_ANALYSIS.md (Section 1) |
| **Acquisition Workflows** | `scenarios/acquisition/*.md` | CROSS_MAPPING_ANALYSIS.md (Section 6) |
| **Asset Management** | `scenarios/asset-management/*.md` | CROSS_MAPPING_ANALYSIS.md (Section 6) |
| **Research** | `research/**/*.md` | REQUIREMENTS_ANALYSIS.md (Section 4) |

---

## Part 5: Key Findings Summary

### 5.1 Critical Inconsistencies (ARCHITECTURAL_CONSISTENCY_ANALYSIS.md)

1. **Two Event Systems**: `RunLedgerEvent` (execution) vs Domain `Event` (business) - not explained
2. **Artifact Model Mismatch**: `contentHash` vs `sha256`, `storageKey` vs `storage_uri`
3. **Claim Status Incompatibility**: TypeScript `'proposed'` vs Schema `'submitted'`
4. **EvidenceSpan vs Evidence**: Location-based vs concept-based (not clearly related)
5. **Missing Domain Events**: Schema exists, no backend/UI implementation

### 5.2 Critical Gaps (REQUIREMENTS_ANALYSIS.md)

1. **Event Management System**: Schema exists, no implementation
2. **Extraction Service**: Schema exists, only stubs
3. **Claim/Evidence Models**: Types exist, no database models
4. **Document Models**: DocIR types exist, no storage
5. **Alert System**: Schema exists, no implementation

### 5.3 Strategic Decisions (ADVANCED_DESIGN_QUESTIONS.md)

1. **GUI Flexibility**: Hybrid - rigid core + flexible layout + rigid components
2. **Decision Support**: Automate preparation, support decisions
3. **Trust Lifecycle**: Adaptive - rigid for critical, flexible for routine
4. **Generic vs CRE**: Generic core + CRE configuration
5. **UI Architecture**: Task-based - IDE for complex, forms for simple

### 5.4 Winning Strategies (ADVANCED_DESIGN_QUESTIONS.md)

1. ✅ **Wedge Strategy**: Start narrow ("Critical Dates"), expand after trust
2. ✅ **Generic Primitives**: Build platform, configure for CRE
3. ✅ **Trust Through Verification**: Start skeptical, earn trust gradually
4. ✅ **Decision Support**: Automate prep, support decisions
5. ✅ **Immutable Core**: Source immutable, interpretations mutable

---

## Part 6: Quick Reference: Where to Find What

### 6.1 Understanding Requirements

- **Start Here**: `requirements/WHAT-TO-BUILD-FIRST.md` (Wedge Strategy)
- **Universal Patterns**: `requirements/UNIVERSAL-ABSTRACTIONS.md` (Five Primitives)
- **Gap Analysis**: `requirements/CRITICAL-ANALYSIS.md` (What We Missed)
- **Full Requirements**: `REQUIREMENTS_ANALYSIS.md` (From-Scratch Analysis)

### 6.2 Understanding Architecture

- **UI Architecture**: `docs/UI_ARCHITECTURE.md` (Multi-pane IDE)
- **Backend Architecture**: `README.md` (Substrate, Run Ledger)
- **Inconsistencies**: `ARCHITECTURAL_CONSISTENCY_ANALYSIS.md` (UI/Backend/Schema)
- **Design Questions**: `ADVANCED_DESIGN_QUESTIONS.md` (Strategic Decisions)

### 6.3 Understanding Users

- **Personas**: `scenarios/personas/cre-user-personas.md` (7 Personas)
- **Persona Mapping**: `CROSS_MAPPING_ANALYSIS.md` (Section 1)
- **Stakeholders**: `scenarios/journeys/stakeholder-perspectives.md`

### 6.4 Understanding Workflows

- **Acquisition**: `scenarios/acquisition/*.md` (4 Workflows)
- **Asset Management**: `scenarios/asset-management/*.md` (2 Workflows)
- **Workflow Mapping**: `CROSS_MAPPING_ANALYSIS.md` (Section 6)

### 6.5 Understanding Code

- **TypeScript Types**: `src/types/*.ts` (Core domain types)
- **Python Models**: `src/intelli/db/models/*.py` (Database models)
- **Python Services**: `src/intelli/services/**/*.py` (Business logic)
- **Python APIs**: `src/intelli/api/v1/*.py` (REST endpoints)
- **React Components**: `src/components/**/*.tsx` (UI components)
- **JSON Schemas**: `schemas/*.schema.json` (Domain primitives)

### 6.6 Understanding Research

- **Research Index**: `USER-SCENARIOS-INDEX.md` (Section 1)
- **Research Synthesis**: `requirements/RESEARCH-SYNTHESIS.md`
- **AI Patterns**: `research/ai-tooling/*.md`
- **CRE Workflows**: `research/cre-workflows/*.md`
- **Cross-Domain**: `research/cross-domain/*.md`

---

## Part 7: Code Structure Quick Reference

### 7.1 TypeScript Type Hierarchy

```
src/types/
├── core.ts              # Base types: Artifact, Manifest, Pointer, Run
├── events.ts            # RunLedgerEvent types (execution tracking)
├── evidence.ts          # Claim, EvidenceSpan, Decision
├── docir.ts             # DocIRDocument, DocIRPage, DocIRBlock
├── knowledge.ts         # KnowledgeBase, RetrievalProfile
└── connectors.ts        # Connector, ConnectorConfig
```

### 7.2 Python Model Hierarchy

```
src/intelli/db/models/
├── substrate.py         # Artifact, Manifest, Pointer, PointerHistory
├── runs.py              # Run, RunEvent, RunStatus, RunEventType
└── auth.py              # Tenant, User, APIKey, AuditLog
```

### 7.3 Python Service Hierarchy

```
src/intelli/services/
├── substrate/
│   ├── artifact_service.py    # Artifact CRUD, content retrieval
│   ├── manifest_service.py    # Manifest CRUD, diff, history
│   └── pointer_service.py      # Pointer CRUD, advance, reset
├── runs/
│   ├── run_service.py         # Run lifecycle management
│   └── ledger_service.py      # RunEvent logging, streaming
└── audit_service.py           # Audit logging
```

### 7.4 Python API Hierarchy

```
src/intelli/api/v1/
├── artifacts.py         # POST /artifacts, GET /artifacts/{sha256}
├── manifests.py         # POST /manifests, GET /manifests/{sha256}
├── pointers.py          # GET /pointers/{ns}/{name}, PUT /pointers/{id}/advance
├── runs.py              # POST /runs, GET /runs/{id}, GET /runs/{id}/events
├── streams.py           # GET /runs/{id}/stream (SSE)
└── auth.py              # POST /auth/login, POST /auth/api-keys
```

### 7.5 React Component Hierarchy

```
src/components/
├── workbench/
│   ├── workbench-shell.tsx      # Main layout container
│   ├── workbench-sidebar.tsx    # Navigation sidebar
│   └── command-palette.tsx      # Cmd+K command palette
├── panes/
│   ├── run-explorer-pane.tsx    # Run timeline & events
│   ├── artifact-browser-pane.tsx # Artifact list & filters
│   ├── document-viewer-pane.tsx  # PDF/document viewer
│   └── chat-pane.tsx            # Chat/thread interface
├── agent/
│   ├── autonomy-slider.tsx      # AI autonomy control
│   ├── approval-gate.tsx        # Approval workflow UI
│   └── trust-indicator.tsx      # Trust/confidence display
└── canvas/
    ├── evidence-canvas.tsx      # Evidence visualization
    └── provenance-graph.tsx     # Provenance DAG
```

---

## Part 8: Document Status & Completeness

### 8.1 Analysis Documents

| Document | Status | Completeness | Last Updated |
|----------|--------|--------------|--------------|
| REQUIREMENTS_ANALYSIS.md | ✅ Complete | 100% | 2026-01-23 |
| CROSS_MAPPING_ANALYSIS.md | ✅ Complete | 100% | 2026-01-23 |
| ARCHITECTURAL_CONSISTENCY_ANALYSIS.md | ✅ Complete | 100% | 2026-01-23 |
| ANALYSIS_GAPS_AND_MISSING.md | ✅ Complete | 100% | 2026-01-23 |
| ADVANCED_DESIGN_QUESTIONS.md | ✅ Complete | 100% | 2026-01-23 |

### 8.2 Requirements Documents

| Document | Status | Completeness | Last Updated |
|----------|--------|--------------|--------------|
| requirements/CRITICAL-ANALYSIS.md | ✅ Complete | 100% | 2026-01-23 |
| requirements/WHAT-TO-BUILD-FIRST.md | ✅ Complete | 100% | 2026-01-23 |
| requirements/UNIVERSAL-ABSTRACTIONS.md | ✅ Complete | 100% | 2026-01-23 |
| requirements/RESEARCH-SYNTHESIS.md | ✅ Complete | 100% | 2026-01-23 |

### 8.3 Code Implementation Status

| Component | Status | Completeness | Notes |
|-----------|--------|--------------|-------|
| **Substrate** | ✅ Complete | 100% | Artifact, Manifest, Pointer implemented |
| **Run Ledger** | ✅ Complete | 100% | Run, RunEvent implemented |
| **APIs** | ✅ Complete | 100% | All Phase 0 APIs implemented |
| **UI Shell** | ✅ Complete | 100% | Workbench shell, panes implemented |
| **Domain Events** | ❌ Missing | 0% | Schema exists, no implementation |
| **Extraction** | ⚠️ Partial | 20% | Stubs only, no service |
| **Claims/Evidence** | ❌ Missing | 0% | Types exist, no models/APIs |
| **DocIR Storage** | ❌ Missing | 0% | Types exist, no storage |

---

## Part 9: Navigation Guide for Models

### 9.1 If You Want to Understand Requirements

1. **Start**: `requirements/WHAT-TO-BUILD-FIRST.md` (Wedge Strategy)
2. **Then**: `requirements/UNIVERSAL-ABSTRACTIONS.md` (Five Primitives)
3. **Then**: `REQUIREMENTS_ANALYSIS.md` (Full Requirements)
4. **Finally**: `CROSS_MAPPING_ANALYSIS.md` (Persona Mapping)

### 9.2 If You Want to Understand Architecture

1. **Start**: `README.md` (Overview)
2. **Then**: `docs/UI_ARCHITECTURE.md` (UI Patterns)
3. **Then**: `ARCHITECTURAL_CONSISTENCY_ANALYSIS.md` (Inconsistencies)
4. **Finally**: `ADVANCED_DESIGN_QUESTIONS.md` (Design Decisions)

### 9.3 If You Want to Understand Code

1. **Start**: `README.md` (Project Structure)
2. **Then**: `src/types/core.ts` (Core Types)
3. **Then**: `src/intelli/db/models/substrate.py` (Database Models)
4. **Finally**: `src/intelli/services/substrate/artifact_service.py` (Service Logic)

### 9.4 If You Want to Understand Users

1. **Start**: `scenarios/personas/cre-user-personas.md` (7 Personas)
2. **Then**: `CROSS_MAPPING_ANALYSIS.md` (Section 1: Persona-to-Feature)
3. **Then**: `scenarios/acquisition/*.md` (Workflow Scenarios)
4. **Finally**: `ADVANCED_DESIGN_QUESTIONS.md` (Section 1: GUI Flexibility)

### 9.5 If You Want to Understand Inconsistencies

1. **Start**: `ARCHITECTURAL_CONSISTENCY_ANALYSIS.md` (Full Analysis)
2. **Then**: Compare `src/types/core.ts` vs `src/intelli/db/models/substrate.py`
3. **Then**: Compare `src/types/events.ts` vs `schemas/event.schema.json`
4. **Finally**: Compare `src/types/evidence.ts` vs `schemas/claim.schema.json`

---

## Part 10: Key Code Locations

### 10.1 Core Domain Types

- **TypeScript**: `src/types/core.ts` (lines 152-305: Artifact, Manifest, Pointer, Run)
- **Python**: `src/intelli/db/models/substrate.py` (Artifact, Manifest, Pointer models)
- **Python**: `src/intelli/db/models/runs.py` (Run, RunEvent models)

### 10.2 Event Types

- **RunLedgerEvent**: `src/types/events.ts` (TypeScript types)
- **RunEventType**: `src/intelli/db/models/runs.py` (Python enum)
- **Domain Event**: `schemas/event.schema.json` (JSON schema - NOT IMPLEMENTED)

### 10.3 Claim/Evidence Types

- **TypeScript**: `src/types/evidence.ts` (Claim, EvidenceSpan, Decision)
- **JSON Schema**: `schemas/claim.schema.json` (Claim, Evidence, Decision - INCOMPATIBLE)

### 10.4 Document Types

- **DocIR**: `src/types/docir.ts` (DocIRDocument, DocIRPage, DocIRBlock)
- **Document Schema**: `schemas/document.schema.json` (DocumentSource, DocumentStructure)

### 10.5 Service Implementations

- **ArtifactService**: `src/intelli/services/substrate/artifact_service.py`
- **ManifestService**: `src/intelli/services/substrate/manifest_service.py`
- **PointerService**: `src/intelli/services/substrate/pointer_service.py`
- **RunService**: `src/intelli/services/runs/run_service.py`
- **LedgerService**: `src/intelli/services/runs/ledger_service.py`

### 10.6 API Implementations

- **Artifacts API**: `src/intelli/api/v1/artifacts.py`
- **Manifests API**: `src/intelli/api/v1/manifests.py`
- **Pointers API**: `src/intelli/api/v1/pointers.py`
- **Runs API**: `src/intelli/api/v1/runs.py`
- **Streams API**: `src/intelli/api/v1/streams.py` (SSE)

### 10.7 UI Components

- **Workbench Shell**: `src/components/workbench/workbench-shell.tsx`
- **Run Explorer**: `src/components/panes/run-explorer-pane.tsx`
- **Artifact Browser**: `src/components/panes/artifact-browser-pane.tsx`
- **Document Viewer**: `src/components/panes/document-viewer-pane.tsx`

---

## Part 11: Critical Files to Read

### 11.1 Must-Read Documents (In Order)

1. `requirements/WHAT-TO-BUILD-FIRST.md` - Wedge Strategy
2. `requirements/UNIVERSAL-ABSTRACTIONS.md` - Five Primitives
3. `REQUIREMENTS_ANALYSIS.md` - Full Requirements
4. `ARCHITECTURAL_CONSISTENCY_ANALYSIS.md` - Inconsistencies
5. `ADVANCED_DESIGN_QUESTIONS.md` - Design Decisions

### 11.2 Must-Read Code Files (In Order)

1. `src/types/core.ts` - Core TypeScript types
2. `src/intelli/db/models/substrate.py` - Database models
3. `src/intelli/services/substrate/artifact_service.py` - Service pattern
4. `src/intelli/api/v1/artifacts.py` - API pattern
5. `src/components/workbench/workbench-shell.tsx` - UI architecture

### 11.3 Must-Read Schemas

1. `schemas/document.schema.json` - Document Intelligence primitive
2. `schemas/event.schema.json` - Event Management primitive
3. `schemas/claim.schema.json` - Claim/Decision primitive

---

## Part 12: Summary

### 12.1 What This Index Provides

- ✅ **Complete document inventory** (all analysis documents)
- ✅ **Repository structure** (what exists and where)
- ✅ **Code structure mapping** (key implementations)
- ✅ **Document relationships** (how documents relate)
- ✅ **Quick reference** (where to find what)
- ✅ **Navigation guide** (for models without indexing)

### 12.2 Key Takeaways

1. **5 Analysis Documents** created during analysis sessions
2. **4 Requirements Documents** defining strategy and primitives
3. **2 Event Systems** (RunLedgerEvent vs Domain Event) - inconsistent
4. **Critical Gaps**: Domain Events, Extraction, Claims/Evidence not implemented
5. **Winning Strategy**: Wedge approach (Critical Dates first)

### 12.3 Next Steps for Models

1. **Read**: `requirements/WHAT-TO-BUILD-FIRST.md` (understand strategy)
2. **Read**: `ARCHITECTURAL_CONSISTENCY_ANALYSIS.md` (understand inconsistencies)
3. **Read**: `REQUIREMENTS_ANALYSIS.md` (understand requirements)
4. **Read**: `src/types/core.ts` (understand types)
5. **Read**: `src/intelli/db/models/substrate.py` (understand models)

---

*This index provides comprehensive navigation for models without indexing service access. Use it to understand the full context of the codebase and documentation.*
