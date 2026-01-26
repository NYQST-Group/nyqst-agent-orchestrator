# NYQST: Architecture

**Product:** NYQST - Deterministic Agentic Infrastructure for Commercial Intelligence  
**Company:** NYQST AI Limited  
**Version:** 1.0  
**Last Updated:** 2026-01-25

---

## Overview

This document provides a high-level overview of the NYQST platform architecture. For detailed technical specifications, see the [Platform Reference Design](../PLATFORM_REFERENCE_DESIGN.md).

The architecture is designed around a core tension: **strong kernel / weak periphery**. The backbone is rigid around containers, sessions, provenance, runs, promotion, policy, and indexing contracts. Domain content (ontologies, models, schemas, skills) is extensible and promotable.

---

## Core Principles

### 1. Single Source of Truth

Immutable artifacts + manifests + run ledger. No module-specific "truth". Every piece of data has one authoritative location.

### 2. Ephemeral Compute, Persistent Outputs

Sessions, VMs, and workbenches are disposable. Outputs are published into the substrate. You can always rebuild the compute environment; you can never lose the outputs.

### 3. Schema-on-Read First, Promote Later

Accept discovered structures initially. Promote stable structures with governance. This allows rapid exploration while maintaining rigor for production use.

### 4. Everything is Inspectable

Agentic work is not "chat logs"; it is structured events + artifacts. Every action, every decision, every output can be examined and audited.

### 5. Pointers Not Mutations

Reversion is moving pointers to older manifests (Git-like), not rewriting history. The past is immutable; only the present view changes.

### 6. Policy-Driven Levels of Care

Required provenance, tool permissions, and gates vary by policy templates. Higher-stakes work requires more verification.

### 7. Index is Substrate

No module owns indexing. Modules select profiles, not strategies. The index is a shared capability, not a module feature.

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                              │
│                                                                             │
│  Workbench UI · Analysis Canvas · Research Interface · Admin Console        │
├─────────────────────────────────────────────────────────────────────────────┤
│                           APPLICATION LAYER                                 │
│                                                                             │
│  Platform Modules: Research · Document · Analysis · Modelling · Knowledge   │
│  Product Variants: PropSygnal · RegSygnal                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                           ORCHESTRATION LAYER                               │
│                                                                             │
│  Agent Runtime · Workflow Engine · Session Management · Skills Framework    │
├─────────────────────────────────────────────────────────────────────────────┤
│                           SERVICES LAYER                                    │
│                                                                             │
│  Index Service · Run Ledger · Schema Registry · Policy Engine               │
├─────────────────────────────────────────────────────────────────────────────┤
│                           SUBSTRATE LAYER                                   │
│                                                                             │
│  Artifact Store · Manifest Store · Pointer Store · Event Store              │
├─────────────────────────────────────────────────────────────────────────────┤
│                           INFRASTRUCTURE LAYER                              │
│                                                                             │
│  PostgreSQL · Object Storage · Vector Store · Message Queue                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Kernel Objects

### Tenancy, Identity, and Access

**Tenant** is the organizational boundary for residency, billing, and policies. Each customer organization is a tenant.

**Principal** is a user, service, or agent identity. All actions are attributed to a principal.

**AccessPolicy** defines RBAC/ABAC rules scoped to project, corpus, knowledge base, tool, or connector. All policy changes are audited.

### Work Context

**Project** is the container for a client engagement or internal initiative. Projects organize work and control access.

**Client** is the organizational entity (customer, counterparty) that projects relate to. Clients can have multiple projects.

**Objective** is the goal of any task, workflow, project, or client relationship. Objectives are critical for context engineering—they provide the commercial reality that enables human-like decision making by agents. Context management draws objectives down to give agents full context without requiring explicit explanation of business goals.

**Workspace** is a saved UI layout with pinned resources. It's a convenience feature, not authoritative storage.

### Task vs Workflow Distinction

This is a critical architectural distinction:

**Task** is something in a session. Tasks can be highly complex or simple, visible in DAGs, but the key characteristic is that tasks are **not governed workflows**. Tasks are flexible, exploratory, and user-directed. A task might involve multiple steps, but those steps are not pre-approved or signed off.

**Workflow** is governed and signed off. The method is approved, and you don't expect people to check the results—the workflow itself has been validated. Technically, a workflow is the same as a task (both can use DAGs, both involve agent execution), but workflows have governance, audit, and approval layers.

**Implementation Spectrum:**

| Type | Governance | Use Case | Technical Approach |
|------|------------|----------|-------------------|
| **Simple Linear Task** | None | Commodity todo functionality for agents | Simple sequential execution |
| **DAG Task** | None | Complex multi-step analysis | Graph-based orchestration |
| **Simple Workflow** | Light | Repeatable processes with audit | Camunda simple flows |
| **Complex Workflow** | Full | Regulated processes, lender submissions | Camunda with execution monitoring, gates, approvals |

**System Concepts:** Events and messages are lower-level primitives that support both tasks and workflows.

> **ADR Note (Task vs Workflow Architecture):** ADR needed for: task/workflow technical unification, governance layer design, simple linear vs DAG vs complex workflow implementation, Camunda integration patterns, event and message architecture.

### Artifact Substrate

The artifact substrate provides "filesystem semantics" for all platform data:

**Artifact (immutable)** is any emitted file or object (PDF, JSON, Parquet, Markdown, HTML, PNG). Artifacts are content-addressed and deduplicated. Once created, an artifact never changes.

**Manifest (immutable)** is an immutable tree of references to artifacts (and optionally nested manifests) plus metadata. A manifest is the unit of versioning.

**Pointer (mutable)** is a HEAD reference to a manifest. Pointer moves are the only "mutation" in the system.

Interpretations of these primitives:
- **Bundle** = named pointer (working snapshot; publish/revert is moving pointer)
- **Corpus** = governed pointer (promotion + evaluation + approvals)
- **Snapshot** = point-in-time freeze

### Runs and Run Ledger

**Run** is an execution instance (agentic, deterministic, or hybrid). Every time work is performed, it happens within a run.

**Run Ledger** is an append-only event stream for audit and replay. It captures:
- Plans, tool calls, retrieval operations
- Artifacts and manifests produced
- Pointer moves
- Human approvals and comments

The run ledger is the canonical record of what happened. It enables reproducibility, audit, and debugging.

---

## Agent Architecture

### Agent Definition

An **AgentDefinition** (versioned) specifies:
- Capabilities the agent has
- Allowed tools it can use
- Retrieval profiles it can access
- Policy template it operates under
- Prompt assets it uses

Agents are not autonomous entities making arbitrary decisions. They are constrained workers operating within defined boundaries.

### Sessions and Workspaces

A **Session** binds a user + project/objective + compute realm. Sessions have:
- Mounts to the substrate (read access to artifacts)
- Ephemeral filesystem for working data
- Defined scope of what the agent can access

**Session Management Features:**
- Sessions are filterable by creator, folder, date, and custom tags
- Sessions can be organized into folders for project organization
- "Return to topic" capability—users can resume sessions with full context intact
- Session analysis across the organization for pattern detection

**Session Levels:**
- **Simple sessions** for research tasks (lightweight, fast startup)
- **Complex sessions** for modelling and analysis (full IDE capabilities, more resources)
- Sessions may be backed by VM orchestration (hidden from users) for isolation and persistence

> **ADR Note (Session/VM Architecture):** Sessions may be backed by containerized or VM-based compute for isolation. ADR needed for: VM orchestration strategy (Firecracker, containers, etc.), session persistence mechanisms, cold start optimization, resource allocation per session type.

### Knowledge Management

Knowledge exists at multiple levels:

**System Knowledge:** Platform-provided knowledge (domain models, standard ontologies, best practices).

**Organization Knowledge:** Tenant-specific knowledge shared across all users.

**User Knowledge:** Personal knowledge, preferences, and learned patterns.

**Session Knowledge:** Context specific to a single session.

Knowledge can be:
- Added manually ("Add new knowledge")
- Auto-organized based on content analysis
- Enabled/disabled per session
- Versioned and auditable

> **ADR Note (Knowledge Architecture):** ADR needed for: knowledge storage format, knowledge retrieval during agent execution, knowledge versioning, knowledge sharing and permissions.

### Playbooks (Reusable Workflows)

**Playbooks** are reusable workflow definitions that capture best practices:
- Created from successful session patterns
- Improved based on session analysis and feedback
- Can be shared across the organization
- Version controlled with change history

**Playbook Lifecycle:**
1. **Create** - Define a new playbook from scratch or from a successful session
2. **Improve** - Refine based on session analysis and user feedback
3. **Share** - Make available to team or organization
4. **Execute** - Run as a batch session or individual session

**Batch Sessions:** Execute playbooks across multiple inputs in parallel (e.g., analyze 50 properties using the same workflow).

> **ADR Note (Playbook Architecture):** ADR needed for: playbook definition format, playbook versioning, batch session orchestration, playbook improvement feedback loop.

### Skills Framework

**Skills** are discrete, reusable capabilities:
- A "Lease Extraction" skill knows how to extract structured data from lease documents
- A "Covenant Calculation" skill knows how to compute DSCR, LTV, and other ratios
- Skills are versioned and auditable

Skills exist at multiple levels:
- **Session-level:** Temporary skills for a specific task
- **User-level:** Personal skills and macros
- **Organization-level:** Shared skills across the tenant

Skills can be composed into workflows. A "Debt Monitoring" workflow might use extraction skills, calculation skills, and reporting skills in sequence.

### Orchestration Runtime

The platform uses a graph-based orchestration runtime (LangGraph) for:
- Stateful execution for multi-step and multi-agent workflows
- Streaming execution for UI (progress + partial outputs)
- Durable resumability via checkpointing for long-running runs
- Human-in-the-loop patterns (interrupt → approve/modify → continue)

**Important boundary:** The orchestration runtime does not replace the platform kernel. Checkpoints and stores are operational aids (resumability/memory), not the authoritative audit record. The authoritative record remains: inputs pinned to manifests + run ledger events + emitted artifacts.

#### Checkpointing Architecture

Following LangGraph's durable execution patterns, NYQST implements checkpointing at multiple levels:

**Checkpoint Storage Tiers:**
- **In-Memory (MemorySaver):** For development and testing. Fast but not durable.
- **SQLite (SqliteSaver):** For single-instance deployments. Durable but not distributed.
- **PostgreSQL (PostgresSaver):** For production. Durable, distributed, and queryable.

**Checkpoint Granularity:** Checkpoints are taken at configurable points—after each tool call, after each agent step, or at custom breakpoints. Finer granularity enables better resumability but increases storage costs.

**State Recovery:** When a session resumes, the system loads the most recent checkpoint and continues from that point. Users see their work exactly as they left it.

**Checkpoint Pruning:** Old checkpoints are pruned based on retention policies. Recent checkpoints are kept for quick recovery; older ones are archived or deleted.

> **ADR Note (Checkpointing Architecture):** ADR needed for: checkpoint storage backend selection, checkpoint granularity policies, state serialization format, pruning strategies, cross-session checkpoint sharing.

#### Human-in-the-Loop Patterns

NYQST implements comprehensive human-in-the-loop patterns based on LangGraph research:

**Interrupt Points:** Workflows can be interrupted at any point for human review. Interrupts can be configured to trigger on: high-stakes decisions, low-confidence outputs, policy violations, or explicit user request.

**State Inspection:** When interrupted, users can inspect the full agent state—what the agent knows, what it's planning, what tools it wants to use. This transparency builds trust.

**Approval Gates:** Certain actions require explicit approval before proceeding. Gates can be configured per workflow, per tool, or per policy level.

**Feedback Integration:** Human feedback is captured and used to improve future runs. Corrections become training data; approvals become confidence signals.

**Edit and Continue:** Users can modify agent state before continuing. Change a value, add context, or redirect the agent's approach—then let it continue from the modified state.

> **ADR Note (Human-in-the-Loop Patterns):** ADR needed for: interrupt trigger configuration, state inspection UI, approval workflow design, feedback capture format, edit-and-continue state management.

---

## Index Service

### What "Index" Means

Index Service is the shared "knowledge plane" that makes everything fast and discoverable:
- Primitive search: keyword/BM25
- Semantic search: dense embeddings
- Hybrid retrieval + reranking
- Faceting/filtering over metadata
- Trace search over runs/events/provenance
- Graph/ontology retrieval (future)

### Contract (Stable Surface)

Modules and agents call the Index Service through a stable contract:

**Ingest:** `ingest(target, profile)` where target is a manifest SHA or pointer ID.

**Search/Retrieve:** `search(query, scope, profile)` returns references (doc IDs + offsets + metadata), not "the truth".

**Explain:** `explain(result)` returns why a result matched (scores/features), for trust.

Backends can change (pgvector → OpenSearch/Qdrant/Vespa) without rewriting product logic, as long as the contract stays stable.

### Profiles (IP Boundary)

Users do not see chunking/reranking knobs. Modules choose **profiles** such as:
- `docs.default`
- `docs.citation_strict`
- `runs.trace_search`
- `projects.cross_project_reuse`

Profiles bind internal strategies (chunking/hybrid/rerankers) and policy constraints (e.g., strict evidence requirements).

### Always-On Indexing

Indexing is automatic:
- Artifact upload → manifest created → pointer advanced → ingest scheduled
- Connector sync → new manifests → ingest scheduled
- No "Index" button; indexing happens as a natural consequence of data changes

---

## Evidence and Trust Architecture

### Evidence Primitives

**EvidenceSpan** is anchored to document IR/PDF offsets. It supports citations and explainability. Every extracted value can point to exactly where in the source document it came from.

**Claim** represents a requirement, control, mapping, risk, interpretation, or fact. Claims are the unit of assertion in the system.

**ClaimSupportLink** connects claims to evidence. A claim might be supported by multiple evidence spans from multiple documents.

**Decision** captures approvals, overrides, and sign-offs. Decisions are attached to claims, promotions, and gates.

### Trust Flow

```
Source Document
      │
      ▼
┌─────────────┐
│  Extraction │ ← AI reads document
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Claim    │ ← "The lease expires on 2027-03-15"
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Evidence   │ ← Page 3, paragraph 2, characters 145-167
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Confidence  │ ← 0.95 (high confidence)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Verification│ ← Human confirms or corrects
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Decision   │ ← "Verified by user on 2026-01-20"
└─────────────┘
```

### Levels of Care

Different work requires different levels of verification. Policy templates define:
- What provenance is required
- What tools are permitted
- What gates must be passed
- What approvals are needed

A quick research task might have minimal gates. A lender submission might require multiple verification steps and sign-offs.

---

## Document Processing

### Canonical Document IR

The platform defines a canonical intermediate representation (DocIR):
- Pages
- Blocks (headings, paragraphs, tables, figures)
- Spans/offsets
- Table model
- Layout geometry (optional)
- Provenance back to source bytes

Downstream modules depend on DocIR, not vendor formats. This allows swapping document processing backends without changing product logic.

### Processing Pipeline

```
Source Document (PDF, Word, Scanned)
           │
           ▼
┌─────────────────────┐
│  Document Processor │ ← Docling, Unstructured, LlamaParse
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     Canonical IR    │ ← Platform-standard format
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Index Service    │ ← Chunking, embedding, indexing
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Extraction/NLU    │ ← AI extracts structured data
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Claims + Evidence  │ ← Structured output with provenance
└─────────────────────┘
```

---

## Integration Architecture

### Connector Framework

Connectors integrate external systems:
- Provider (Slack, HubSpot, Monday, Jira, Confluence, SharePoint, etc.)
- Authentication (OIDC/OAuth), secret references
- Scopes, rate-limit policy
- Webhook subscriptions

Connectors are producers (and sometimes action tools) in the same platform contracts:
- Inbound sync produces artifacts and manifests
- Outbound actions are exposed as tools (via MCP)
- All actions are logged to the run ledger

### MCP (Model Context Protocol)

The platform uses MCP for tool integration:
- Tools are exposed as MCP servers
- Agents call tools through the MCP protocol
- Tool calls are logged with inputs, outputs, and timing
- Tools can be gated by policy

### MCP Marketplace

The platform includes an MCP marketplace for discovering and managing integrations:

**Installed MCPs:** MCPs currently enabled for the tenant/user.

**Available MCPs:** MCPs available for installation, organized by category:
- Essentials (core platform capabilities)
- AI & Machine Learning
- Cloud & Infrastructure
- Communication (Slack, Teams, etc.)
- Customer & Sales (CRM integrations)
- Databases
- Design & Creative
- Development Tools
- Finance
- Monitoring & Analytics
- Productivity

**Add Your Own:** Organizations can add custom MCP servers not in the marketplace.

**MCP Metadata:**
- Official vs community badges
- Transport type (HTTP, SSE, STDIO)
- Enabled/Not installed status
- Description and capabilities

> **ADR Note (MCP Marketplace):** ADR needed for: MCP discovery and registration, MCP versioning, MCP security and sandboxing, custom MCP onboarding process, MCP billing/metering.

### External System Mapping

External systems map to canonical objects:
- Account/Client
- Engagement/Project
- Task/Ticket
- Message/Thread
- Document/Attachment
- Approval

This allows consistent handling regardless of which external system is the source.

### CRM and Project Management Integration

The platform provides basic client and project management capabilities but prefers integration with major tools:

**Basic Feature Set:** Entry and maintenance of clients and projects directly in NYQST. Sufficient for organizations without existing CRM/PM tools.

**Preferred Integration:** Plug into major tools like Monday, HubSpot, Salesforce, or similar. This provides:
- Sessions linked to customers linked to projects
- Context automatically enriched from CRM data
- Bidirectional sync of relevant information

**Repeatable Import Flow:** For organizations with non-integrated tools, a repeatable flow that imports information from existing systems into NYQST's client/project structure.

**Session-Client-Project Linkage:**
```
Client (from CRM)
    │
    └── Project (from PM tool)
            │
            └── Session (in NYQST)
                    │
                    └── Tasks, Workflows, Artifacts
```

This linkage enables:
- Context injection from client/project data into agent sessions
- Organizational insight aggregated by client and project
- Billing and reporting aligned with client structure

> **ADR Note (CRM/PM Integration):** ADR needed for: connector architecture for Monday/HubSpot/Salesforce, bidirectional sync patterns, repeatable import flow design, session-client-project data model.

---

## Model Provider Architecture

### Multi-Provider Support

The platform supports multiple model providers without coupling to any single vendor:

**ProviderConnection (tenant-scoped):** How to talk to a provider.
- Provider: OpenAI, Anthropic, Azure OpenAI, Bedrock, Vertex, etc.
- Endpoint/base URL, region
- Credential references (secret manager)
- Budgets/quotas, allowlists/denylists, data-handling constraints

**ModelRegistry (tenant/project-scoped):** What models are allowed.
- Chat models (for generation + tool calling)
- Embedding models (for Index Service)
- Optional rerankers

**ModelProfile (versioned):** The binding used by a module/agent.
- Chat model: provider + model ID + decoding params
- Embedding model: provider + model ID + dimensions
- Policy flags (e.g., "no tool calls", "citations required")

### Enforcement

Agents never choose providers ad-hoc. They run under an AgentDefinition, which selects a ModelProfile. Policies can override or block profiles at higher levels of care. Every run logs model/provider selection + config hashes to the run ledger for audit.

---

## Deployment Architecture

### SaaS Deployment

The default deployment is multi-tenant SaaS:
- Shared infrastructure with tenant isolation
- Data residency controls per tenant
- Automatic scaling and updates

### Single-Tenant / Private Cloud

For organizations requiring additional isolation:
- Dedicated infrastructure
- Customer-managed keys
- VPC deployment options
- On-premises options (future)

---

## Security Architecture

### Data Protection

- All data encrypted at rest and in transit
- Content-addressed storage ensures integrity
- Immutable audit logs prevent tampering
- Fine-grained access controls at every level

### Authentication and Authorization

- OIDC/OAuth for user authentication
- Service accounts for system-to-system
- RBAC/ABAC for authorization
- All access decisions logged

### Compliance

- Full audit trail for all operations
- Data residency controls
- Retention policies configurable per tenant
- Export capabilities for regulatory requirements

---

## Performance Characteristics

### Scalability

- Horizontal scaling for compute workloads
- Distributed storage for artifacts
- Caching at multiple layers
- Async processing for long-running operations

### Reliability

- Durable workflows with checkpointing
- Automatic retry with backoff
- Graceful degradation under load
- Disaster recovery capabilities

---

## User Interface Architecture

### Research Interface (NotebookLM-like)

The Research module uses a three-panel layout:

**Sources Panel (Left):**
- Add sources (upload files, websites, drive, copied text)
- Search for new sources with "Fast research" toggle
- Saved sources appear here
- Deep Research option for in-depth reports

**Chat Panel (Center):**
- Conversational interface for research queries
- Context-aware responses grounded in sources
- Citation links to source materials

**Studio Panel (Right):**
- Output generation options:
  - Audio Overview (podcast-style summary)
  - Video Overview
  - Mind Map
  - Reports
  - Flashcards
  - Quiz
  - Infographic
  - Slide deck
  - Data table
- Notes and annotations

> **ADR Note (Research UI):** ADR needed for: panel layout framework, source ingestion pipeline, Deep Research vs Fast Research implementation, Studio output generation.

### Workbench Interface (IDE-like)

The Workbench provides an IDE-like experience for complex work:

**Setup Flow:**
- Guided setup: "Let's set up my machine together"
- Steps: Git pull, Configure secrets, Install dependencies, Setup lint, Setup tests, Local app testing, Additional notes
- Terminal visibility for transparency
- "Finish setup" / "Finish later" options

**Main Interface:**
- Agent panel with conversation and task execution
- Terminal panel showing command execution
- File browser and editor
- README and documentation viewer

**Task Tracking:**
- Expandable todo list with status indicators
- Progress tracking (e.g., "2/6 tasks complete")
- File operations with line ranges visible

> **ADR Note (Workbench UI):** ADR needed for: IDE framework choice (Theia, VS Code web, custom), terminal integration, file system abstraction, guided setup flow implementation.

### Analysis Canvas

The Analysis module provides an infinite canvas for visual exploration:

**Canvas Features:**
- Unlimited graph canvas for diagrams, models, relationships
- Drag-and-drop arrangement
- Zoom and pan navigation
- Relationship visualization
- Annotation and notes

**Integration:**
- Pull in documents from Document Management
- Visualize claims and evidence from Modelling
- Export to various formats

> **ADR Note (Analysis Canvas):** ADR needed for: canvas framework (tldraw, excalidraw, custom), data model for canvas objects, collaboration features, export formats.

### Cross-Session Analysis

Advanced mode enables analysis across sessions:

**Suggested Analysis Prompts:**
- "Coach these sessions" - Get high-impact feedback and concrete next steps
- "User coaching report" - Find recurring patterns across sessions
- "Org-wide coaching report" - Create an org report and propose outreach automation

**Capabilities:**
- Inspect other sessions (with permission)
- Manage playbooks
- Propose starting batch sessions
- Pattern detection across organizational usage

> **ADR Note (Cross-Session Analysis):** ADR needed for: session data access permissions, pattern detection algorithms, coaching report generation, privacy and consent model.

### Generative UI Architecture

Based on CopilotKit's AG-UI Protocol research, NYQST implements generative UI patterns for agent-driven interfaces:

**Two Surfaces:**
- **Chat Surface:** Conversational interface where agents communicate with users. Supports rich content (markdown, code, tables, charts) and inline actions.
- **Application Surface:** The main application UI that agents can observe and modify. Agents can read application state, suggest changes, and (with approval) make changes directly.

**Agent-Generated Components:**
- Agents can generate UI components from a guardrailed component library
- Components are configured, not coded—agents select and parameterize pre-built components
- This enables "vibe coding" for business users: describe what you want, agent builds it

**Streaming UI Updates:**
- UI updates stream in real-time as agents work
- Partial results are shown immediately (not waiting for completion)
- Users can interrupt and redirect at any point

**State Synchronization:**
- Application state is synchronized between agent and UI
- Agents can read current state to understand context
- State changes are bidirectional—user actions update agent context, agent actions update UI

**Guardrails:**
- Agents operate within defined component libraries
- No arbitrary code generation—only configuration of approved components
- All generated UI is auditable and reversible

> **ADR Note (Generative UI Architecture):** ADR needed for: component library design, AG-UI protocol implementation, state synchronization mechanism, guardrail enforcement, streaming update protocol.

---

## ADR Summary

The following architectural decisions are flagged for detailed ADR documentation:

| ADR Topic | Scope | Key Questions |
|-----------|-------|---------------|
| **Session/VM Architecture** | Core | VM orchestration, session persistence, cold start, resource allocation |
| **Knowledge Architecture** | Core | Storage format, retrieval, versioning, sharing permissions |
| **Playbook Architecture** | Core | Definition format, versioning, batch orchestration, improvement loop |
| **Task vs Workflow Architecture** | Core | Task/workflow unification, governance layer, Camunda integration, events/messages |
| **CRM/PM Integration** | Integration | Monday/HubSpot/Salesforce connectors, bidirectional sync, session-client-project model |
| **MCP Marketplace** | Integration | Discovery, versioning, security, custom onboarding, billing |
| **Research UI** | UI | Panel layout, source ingestion, Deep vs Fast research, Studio outputs |
| **Workbench UI** | UI | IDE framework, terminal integration, file system, guided setup |
| **Analysis Canvas** | UI | Canvas framework, data model, collaboration, export |
| **Cross-Session Analysis** | Feature | Permissions, pattern detection, coaching reports, privacy |
| **Checkpointing Architecture** | Core | Storage backend, granularity policies, serialization, pruning |
| **Human-in-the-Loop Patterns** | Core | Interrupt triggers, state inspection, approval workflow, feedback |
| **Generative UI Architecture** | UI | Component library, AG-UI protocol, state sync, guardrails |
| **Agent Framework Choice** | Core | LangGraph vs Vercel AI SDK vs custom, state management, streaming |
| **MCP Architecture** | Integration | Full adoption vs selective, tool design, workflow in MCP |

---

**Related Documents:**
- [Platform Reference Design](../PLATFORM_REFERENCE_DESIGN.md) - Detailed technical specification
- [Platform Modules](03_PLATFORM.md) - Module capabilities
- [Roadmap](07_ROADMAP.md) - Delivery plan
