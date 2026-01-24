# Requirements Analysis: From-Scratch Codebase Inference

*Date: 2026-01-23*  
*Method: Systematic analysis of code, types, schemas, docs, and research*

---

## Executive Summary

This document infers end-to-end requirements by analyzing:
- **UI System**: React components, TypeScript types, stores, hooks
- **Backend System**: Python models, APIs, services, MCP tools
- **Schemas**: JSON schema definitions for domain primitives
- **Research**: Industry research, workflow analysis, domain knowledge
- **Design Docs**: Architecture documents, UI patterns, research synthesis

**Analysis Approach**: Extract requirements from implementation, infer missing pieces, identify patterns, cross-compare by theme.

---

## 1. UI Requirements (Inferred from Components & Types)

### 1.1 Workbench Architecture

**From**: `src/components/workbench/workbench-shell.tsx`, `src/stores/workspace-store.ts`

**Requirements**:
- **Multi-pane IDE layout** with resizable panels (react-resizable-panels)
- **Pane types**: chat, planner, run-explorer, artifact-browser, document-viewer, table-viewer, graph-viewer, diff-viewer, context-pinboard, evaluations, provenance, governance, admin
- **Command palette** (Cmd/Ctrl+K) for quick actions
- **Collapsible sidebar** for navigation
- **Pane tab bar** for multiple panes per group
- **Error boundaries** around each pane (ComponentErrorFallback)
- **Lazy loading** of pane components (code splitting)
- **Layout persistence** (Zustand persist middleware)
- **Status bar** showing connection status, version

**Inferred Requirements**:
- **Resource URI navigation**: All resources addressable via URIs (`artifact://`, `run://`, `manifest://`, `claim://`, `kb://`)
- **Context pinning**: Pin artifacts/manifests/claims to provide agent context
- **Workspace layouts**: Save/load/switch between layout configurations
- **Recent resources**: Track recently accessed resources (last 20)

### 1.2 Real-Time Updates

**From**: `src/intelli/api/v1/streams.py`, `ui/src/hooks/use-sse.ts`

**Requirements**:
- **Server-Sent Events (SSE)** for real-time updates
- **PostgreSQL LISTEN/NOTIFY** for push notifications (not polling)
- **Run event streaming**: Real-time updates for run steps, tool calls, completions
- **Activity feed**: Global activity stream (runs, pointer changes, artifacts)
- **Heartbeat**: 30-second heartbeat to keep connections alive
- **Reconnection**: Handle connection drops gracefully

**Inferred Requirements**:
- **Event buffering**: Send initial/historical events on connection
- **Sequence-based updates**: `since_sequence` parameter for incremental updates
- **Event filtering**: Filter by event types
- **Connection management**: Multiple concurrent SSE connections

### 1.3 Agent Interaction Components

**From**: `src/components/agent/autonomy-slider.tsx`, `src/components/agent/approval-gate.tsx`

**Requirements**:
- **Autonomy levels**: suggestions, assisted, supervised, autonomous
- **Permission matrix**: Per-action-type permissions (read, analyze, modify, external, compliance)
- **Approval gates**: Human approval required for certain actions
- **Trust indicators**: Visual confidence display
- **Reasoning panel**: Show agent reasoning/thought process
- **Tool visibility**: Show tool calls in real-time

**Inferred Requirements**:
- **Per-task autonomy**: Different autonomy levels per task/workflow
- **Compliance always requires approval**: Even at autonomous level
- **Action type classification**: Categorize actions for permission checking
- **Approval workflow**: Multi-stage approval chains

### 1.4 Canvas Components

**From**: `src/components/canvas/evidence-canvas.tsx`, `src/components/canvas/provenance-graph.tsx`

**Requirements**:
- **Evidence canvas**: Spatial mapping of evidence spans
- **Provenance graph**: Transformation lineage visualization
- **Semantic zoom**: Detail at different scales
- **Spatial clustering**: Force-directed layout for relationships
- **Evidence graph**: Nodes (claim, evidence, document, decision) and edges (supports, contradicts, derived_from)

**Inferred Requirements**:
- **Performance**: 60fps with 1000+ elements (from research synthesis)
- **Interactive**: Click nodes/edges for details
- **Filtering**: Filter by evidence type, relationship type
- **Export**: Export graph as image/data

### 1.5 Document Viewer

**From**: `src/components/panes/document-viewer-pane.tsx`, `src/types/docir.ts`

**Requirements**:
- **PDF rendering**: Display PDF documents
- **DocIR support**: Render structured document representation (pages, blocks, tables, figures)
- **Evidence overlays**: Highlight evidence spans in document
- **Citation sidebar**: Show source citations
- **Page navigation**: Navigate between pages
- **Zoom controls**: Zoom in/out, fit to width/height

**Inferred Requirements**:
- **Multi-format**: Support PDF, Word, images, scanned documents
- **OCR integration**: For scanned documents
- **Annotation support**: User annotations/notes
- **Search**: Search within document
- **Print/export**: Export document or pages

### 1.6 Run Explorer

**From**: `src/components/panes/run-explorer-pane.tsx`

**Requirements**:
- **Run list**: Filterable list of runs (by status, type, project)
- **Run detail**: Timeline view of run events
- **Event types**: tool.call.started, tool.call.completed, artifact.emitted, step_started, step_completed
- **Status badges**: Visual status indicators (pending, running, completed, failed, cancelled, paused)
- **Usage stats**: Token usage, tool calls, duration
- **Error display**: Show errors with code and message
- **Run actions**: Start, pause, resume, cancel, retry

**Inferred Requirements**:
- **DAG visualization**: Visual representation of run steps/dependencies
- **Event filtering**: Filter events by type
- **Event search**: Search within event payloads
- **Export**: Export run log/events
- **Checkpoint resumption**: Resume from checkpoint

### 1.7 Artifact Browser

**From**: `src/components/panes/artifact-browser-pane.tsx`

**Requirements**:
- **Artifact list**: List artifacts with filters (type, media type, date range)
- **Artifact preview**: Preview cards showing metadata
- **Search**: Search artifacts by filename, content hash, metadata
- **Upload**: Drag-and-drop or file picker for uploads
- **Download**: Download artifact content
- **Metadata display**: SHA-256, size, media type, created date

**Inferred Requirements**:
- **Bulk operations**: Select multiple artifacts for bulk actions
- **Preview generation**: Thumbnails for images, text previews
- **Reference tracking**: Show which manifests reference artifact
- **Storage location**: Display storage URI/class

### 1.8 Async Patterns

**From**: `src/components/async/suspense-wrapper.tsx`, `src/components/async/error-fallback.tsx`

**Requirements**:
- **React Suspense**: Wrap async components in Suspense
- **Error boundaries**: Catch and display errors gracefully
- **Loading states**: Skeleton loaders, spinners
- **Retry logic**: Retry failed operations
- **Error recovery**: Fallback UI when errors occur

**Inferred Requirements**:
- **Progressive loading**: Load critical content first, lazy load rest
- **Optimistic updates**: Update UI before server confirms
- **Offline support**: Queue actions when offline, sync when online

---

## 2. System Requirements (Inferred from Backend Code)

### 2.1 Substrate Architecture

**From**: `src/intelli/db/models/substrate.py`, `src/intelli/services/substrate/`

**Requirements**:
- **Artifact model**: SHA-256 primary key, content-addressed, immutable
- **Manifest model**: SHA-256 primary key, JSONB tree structure, parent chain
- **Pointer model**: Mutable HEAD references (bundle, corpus, snapshot)
- **Pointer history**: Audit trail for pointer changes
- **Content addressing**: SHA-256 hash for deduplication
- **Storage abstraction**: S3-compatible (MinIO dev, AWS S3 prod)
- **Reference counting**: Track artifact references in manifests

**Inferred Requirements**:
- **Garbage collection**: Delete unreferenced artifacts
- **Storage classes**: Support STANDARD, GLACIER, etc.
- **Pre-signed URLs**: Generate temporary download URLs
- **Manifest diff**: Compare two manifests (added/removed/modified)
- **History traversal**: Walk parent chain for version history

### 2.2 Run & Event Ledger

**From**: `src/intelli/db/models/runs.py`, `src/intelli/services/runs/ledger_service.py`

**Requirements**:
- **Run model**: UUID primary key, status enum, config JSONB, input/output manifests
- **RunEvent model**: Append-only event log with sequence numbers
- **Event types**: step_started, step_completed, tool_call_started, tool_call_completed, artifact_emitted, checkpoint, error
- **Monotonic sequence**: Sequence numbers ensure ordering
- **PostgreSQL NOTIFY**: Publish events for real-time streaming
- **Checkpoint support**: Save resumable state

**Inferred Requirements**:
- **Run lifecycle**: pending → running → completed/failed/cancelled/paused
- **Token tracking**: Track LLM token usage per run
- **Cost tracking**: Calculate cost in cents
- **Parent runs**: Support nested runs (parent_run_id)
- **Session linking**: Link runs to sessions
- **Project scoping**: Link runs to projects

### 2.3 Authentication & Authorization

**From**: `src/intelli/db/models/auth.py`, `src/intelli/api/middleware/auth.py`

**Requirements**:
- **Multi-tenant**: Tenant isolation at data layer
- **User model**: Email, roles (member, admin), password hashing
- **API key model**: Scoped keys (read, write, admin), rate limiting, IP allowlist
- **External auth**: OAuth/SAML support (external_id, external_provider)
- **Soft delete**: API keys soft-deleted for audit
- **Audit logging**: Track all significant actions

**Inferred Requirements**:
- **JWT tokens**: Bearer token authentication
- **API key hashing**: SHA-256 hash of keys
- **Rate limiting**: Per-API-key RPM limits
- **Scope checking**: Enforce read/write/admin scopes
- **Last used tracking**: Track API key usage
- **IP allowlist**: Restrict API key access by IP

### 2.4 API Endpoints

**From**: `src/intelli/api/v1/`

**Implemented APIs**:
- **Artifacts**: POST, GET, GET content, GET URL, LIST, DELETE
- **Manifests**: POST, GET, GET entries, GET history, GET diff, LIST
- **Pointers**: POST, GET, GET resolve, PUT advance, PUT reset, GET history, DELETE, LIST
- **Runs**: POST, GET, POST start/pause/resume/complete/fail/cancel, GET events, GET checkpoint, LIST
- **Streams**: GET run events (SSE), GET activity (SSE)
- **Auth**: POST login, GET me, GET/POST/DELETE API keys

**Inferred Requirements**:
- **Pagination**: Limit/offset for list endpoints
- **Filtering**: Filter by status, type, project, date range
- **Validation**: Pydantic schema validation
- **Error handling**: Structured error responses with codes
- **Correlation IDs**: Request correlation for tracing

### 2.5 MCP Tools

**From**: `src/intelli/mcp/tools/substrate_tools.py`, `src/intelli/mcp/tools/run_tools.py`

**Substrate Tools**:
- list_pointers, resolve_pointer, checkout_manifest, get_manifest_history, diff_manifests
- create_manifest, advance_pointer, create_pointer
- get_artifact_info, get_artifact_url

**Run Tools**:
- create_run, start_run, complete_run, fail_run
- log_step, log_tool_call, checkpoint, get_run_events

**Knowledge Tools** (stub):
- kb_query (placeholder, not implemented)

**Inferred Requirements**:
- **Tool discovery**: Dynamic tool registry
- **Tool versioning**: Track tool versions
- **Tool permissions**: Restrict tools per agent
- **Tool audit**: Log all tool invocations
- **Tool results**: Return artifacts/manifests from tools

### 2.6 Storage Backend

**From**: `src/intelli/storage/`

**Requirements**:
- **Content-addressed**: Key = SHA-256 hash
- **Backend abstraction**: Local storage (dev) or S3 (prod)
- **Pre-signed URLs**: Generate temporary download URLs
- **Hash verification**: Optional hash verification on read
- **Deduplication**: Automatic (same content = same SHA-256)

**Inferred Requirements**:
- **Storage classes**: Support STANDARD, GLACIER, etc.
- **Lifecycle policies**: Move to cheaper storage after time
- **Backup**: Backup strategy for critical artifacts
- **Encryption**: At-rest encryption support

---

## 3. Domain Requirements (Inferred from Schemas & Research)

### 3.1 Document Intelligence Primitive

**From**: `schemas/document.schema.json`, `src/types/docir.ts`

**Schema Requirements**:
- **DocumentSource**: id, content_hash, media_type, ingested_at, artifact_ref
- **DocumentStructure**: document_id, version, pages, blocks, TOC
- **Extraction**: id, document_id, schema_id, field_name, value, confidence, location
- **DocumentRelationship**: amends, supersedes, supplements, references, exhibits
- **ExtractionSchema**: Field definitions with validation rules
- **Gap**: missing_document, missing_field, incomplete_extraction, unresolved_reference

**TypeScript Requirements** (DocIR):
- **DocIRDocument**: sourceArtifactId, pages, toc, extraction metadata
- **DocIRPage**: pageNumber, dimensions, blocks
- **DocIRBlock**: heading, paragraph, list, table, figure, etc.
- **DocIRQualityMetrics**: Overall confidence, extraction quality scores

**Inferred Requirements**:
- **Multi-format ingestion**: PDF, Word, images, scanned documents
- **OCR support**: For scanned documents
- **Structure extraction**: Pages, paragraphs, tables, figures
- **Confidence scoring**: Per-extraction confidence (0-1)
- **Source citation**: Page, block, character offsets
- **Version tracking**: Re-extraction creates new version
- **Gap detection**: Identify missing documents/fields

### 3.2 Event Management Primitive

**From**: `schemas/event.schema.json`, `schemas/cre/lease-events.config.json`

**Schema Requirements**:
- **Event**: id, event_type_id, trigger_date, status, context, deadlines
- **Deadline**: id, deadline_type, deadline_date, status, action_required, calculation
- **Alert**: id, event_id, alert_type, priority, status, recipients, scheduled_at
- **Action**: id, event_id, action_type, performed_by, performed_at, evidence
- **Outcome**: id, event_id, outcome_type, recorded_at, financial_impact
- **EventType**: Configuration with trigger_source, deadline_rules, alert_rules

**Workflow Requirements** (from scenarios):
- **Critical dates**: Break options, rent reviews, lease expiries, renewal options
- **Deadline calculation**: Notice periods, business days, calendar adjustments
- **Tiered alerts**: Red (urgent), Amber (attention), Green (on track)
- **Multi-channel**: Email, dashboard, push notifications
- **Escalation**: Escalate on non-acknowledgment

**Inferred Requirements**:
- **Event detection**: Extract events from documents
- **Deadline rules**: Configurable calculation rules (e.g., "trigger_date - 6 months")
- **Alert rules**: Configurable alert triggers (e.g., "deadline - 30 days")
- **Recipient management**: Role-based and user-based recipients
- **Alert delivery**: Track delivery status, acknowledgments
- **Outcome tracking**: Record what happened when event occurred
- **Financial impact**: Quantify impact of events/outcomes

### 3.3 Claim/Decision Primitive

**From**: `schemas/claim.schema.json`, `src/types/evidence.ts`

**Schema Requirements**:
- **Claim**: id, claim_type_id, statement, severity, status, evidence, quantification
- **Evidence**: id, evidence_type, relationship (supports/refutes/context), strength, location
- **Decision**: id, claim_id, decision_type, rationale, conditions, approval_chain
- **ClaimType**: Configuration with severity_levels, required_evidence, resolution_options

**TypeScript Requirements**:
- **Claim**: type, status, title, content, confidence, tags, claimSchemaId
- **EvidenceSpan**: documentArtifactId, blockId, pageNumber, startOffset, endOffset
- **ClaimSupportLink**: claimId, evidenceSpanId, supportType, confidence
- **Decision**: type, context, subjectType, outcome, rationale, conditions

**Inferred Requirements**:
- **Claim types**: requirement, control, mapping, risk, interpretation, fact, assertion, finding
- **Evidence linking**: Link evidence spans to claims
- **Support relationships**: supports, contradicts, neutral, partial_support
- **Decision workflow**: Draft → Submitted → Under Review → Decided
- **Approval chains**: Multi-stage approval workflows
- **Quantification**: Financial/risk quantification of claims

### 3.4 Knowledge Base (Stub/Phase 2)

**From**: `src/types/knowledge.ts`, `src/intelli/mcp/tools/knowledge_tools.py`

**TypeScript Requirements**:
- **KnowledgeBase**: id, name, description, indexingConfig, retrievalProfiles
- **RetrievalProfile**: name, strategy, parameters
- **EvidenceSpanRef**: Document location references for evidence

**Stub Requirements**:
- **kb_query**: Semantic search (NOT IMPLEMENTED, placeholder)

**Inferred Requirements**:
- **Vector indexing**: pgvector for semantic search
- **Retrieval profiles**: Different retrieval strategies per use case
- **Evidence indexing**: Index evidence spans for retrieval
- **Query interface**: Semantic search over knowledge base

---

## 4. Cross-Theme Analysis

### 4.1 Theme: Real-Time Observability

**UI Components**: RunExplorerPane, SSE hooks, event streaming
**Backend**: SSE endpoints, PostgreSQL NOTIFY, ledger service
**Types**: RunLedgerEvent union type with all event types
**Research**: Real-time observability patterns

**Inferred Requirements**:
- **Real-time run updates**: Stream run events as they occur
- **Activity feed**: Global activity stream
- **Event buffering**: Send historical events on connection
- **Connection management**: Handle multiple concurrent streams
- **Heartbeat**: Keep connections alive
- **Reconnection**: Automatic reconnection on drop

**Gaps**:
- No WebSocket support (only SSE)
- No event filtering UI
- No event replay capability

### 4.2 Theme: Trust & Verification

**UI Components**: AutonomySlider, ApprovalGate, TrustIndicator, EvidenceCanvas
**Backend**: Approval workflows (stub), audit logging
**Schemas**: Confidence scoring, source citation, verification tracking
**Research**: Trust UX patterns, safety requirements

**Inferred Requirements**:
- **Confidence scoring**: Per-extraction confidence (0-1)
- **Source citation**: Document, page, block, character offsets
- **Click-to-verify**: Click extraction → see source document
- **Verification tracking**: Track who verified what and when
- **Autonomy levels**: Progressive trust building
- **Approval gates**: Mandatory approvals for critical actions
- **Audit trail**: Complete audit log of all actions

**Gaps**:
- No explicit trust state machine (UNTRUSTED → ACCEPTED → AUTHORITATIVE)
- No trust calibration UI
- No trust metrics dashboard

### 4.3 Theme: Content Addressing & Immutability

**Backend**: Artifact SHA-256 PK, Manifest SHA-256 PK, content-addressed storage
**Types**: ContentHash type, ResourceURI with artifact:// scheme
**Research**: Git-like versioning patterns

**Inferred Requirements**:
- **SHA-256 hashing**: All content content-addressed
- **Deduplication**: Same content = same SHA-256
- **Immutable artifacts**: Cannot modify artifacts
- **Immutable manifests**: Cannot modify manifests (create new)
- **Mutable pointers**: HEAD references can be moved
- **History chains**: Parent manifests for version history
- **Diff support**: Compare manifests to see changes

**Gaps**:
- No garbage collection for unreferenced artifacts
- No storage lifecycle policies
- No manifest compression for large trees

### 4.4 Theme: Multi-Tenant Isolation

**Backend**: Tenant model, tenant_id FK on all scoped entities
**Types**: TenantScopedEntity, ProjectScopedEntity
**Auth**: Multi-tenant auth middleware

**Inferred Requirements**:
- **Tenant isolation**: Zero cross-tenant data exposure
- **Project scoping**: Projects within tenants
- **RBAC**: Role-based access control (member, admin)
- **API key scoping**: Per-tenant API keys
- **Audit logging**: Track tenant_id on all actions
- **Data residency**: Tenant-level data residency settings

**Gaps**:
- No tenant quotas/billing
- No tenant-level settings UI
- No tenant admin console

### 4.5 Theme: Agent Execution & Tooling

**Backend**: Run model, RunEvent ledger, MCP tools
**UI**: RunExplorerPane, ToolVisibility component
**Types**: RunLedgerEvent with tool call events

**Inferred Requirements**:
- **Run lifecycle**: Create → Start → Running → Complete/Fail/Cancel/Pause
- **Event logging**: Append-only event log for reproducibility
- **Tool calls**: Log tool invocations with args/results
- **Checkpoints**: Save resumable state
- **MCP integration**: Expose tools via Model Context Protocol
- **Tool discovery**: Dynamic tool registry
- **Tool permissions**: Restrict tools per agent
- **Token tracking**: Track LLM token usage
- **Cost tracking**: Calculate cost per run

**Gaps**:
- No agent definition model (only stub)
- No workflow definition model
- No tool versioning
- No tool result caching

### 4.6 Theme: Document Processing Pipeline

**Schemas**: DocumentSource, DocumentStructure, Extraction
**Types**: DocIRDocument, DocIRPage, DocIRBlock
**Research**: Docling parsing, extraction workflows

**Inferred Requirements**:
- **Ingestion**: Upload PDF/Word/images
- **Parsing**: Extract structure (pages, blocks, tables)
- **Extraction**: Extract fields with confidence scores
- **Source citation**: Link extractions to document locations
- **Verification**: Human verification workflow
- **Version tracking**: Track extraction versions
- **Gap detection**: Identify missing documents/fields

**Gaps**:
- No document parsing service (only stub)
- No extraction service (only stub)
- No DocIR storage model
- No extraction schema management

### 4.7 Theme: Event & Deadline Management

**Schemas**: Event, Deadline, Alert, Action, Outcome
**Research**: Lease event management scenarios, deadline calculation
**Workflows**: Critical dates workflow

**Inferred Requirements**:
- **Event detection**: Extract events from documents
- **Deadline calculation**: Calculate deadlines from notice periods
- **Alert generation**: Generate alerts based on rules
- **Alert delivery**: Multi-channel delivery (email, dashboard, push)
- **Action tracking**: Track actions taken on events
- **Outcome recording**: Record what happened when event occurred
- **Event calendar**: Unified calendar view
- **Escalation**: Escalate on non-acknowledgment

**Gaps**:
- No Event/Deadline/Alert models in database
- No event detection service
- No alert delivery service
- No deadline calculation engine

### 4.8 Theme: Evidence & Claims

**Schemas**: Claim, Evidence, Decision, ClaimType
**Types**: Claim, EvidenceSpan, ClaimSupportLink, Decision
**UI**: EvidenceCanvas, ProvenancePane

**Inferred Requirements**:
- **Claim creation**: Create claims from extractions/analysis
- **Evidence linking**: Link evidence spans to claims
- **Support relationships**: supports, contradicts, neutral
- **Decision workflow**: Draft → Review → Decided
- **Approval chains**: Multi-stage approvals
- **Evidence graph**: Visualize claim-evidence relationships
- **Provenance tracking**: Track claim derivation

**Gaps**:
- No Claim/Evidence/Decision models in database
- No claim service
- No evidence linking service
- No decision workflow engine

---

## 5. Requirements by Priority

### 5.1 Phase 0 (Complete) ✅

- Substrate (Artifact, Manifest, Pointer)
- Run ledger (Run, RunEvent)
- Basic APIs (artifacts, manifests, pointers, runs)
- MCP tools (substrate, run)
- Auth (multi-tenant, API keys)
- SSE streaming (run events, activity)

### 5.2 Phase 1 (Critical Dates - Wedge Strategy)

**Must Have**:
- Document ingestion (PDF/Word/scanned)
- Date extraction with confidence
- Event model (Event, Deadline, Alert)
- Event calendar UI
- Alert delivery (email + dashboard)
- Verification UI (click-to-verify)

**Nice to Have**:
- DocIR storage
- Extraction versioning
- Advanced alert rules

**Defer**:
- Full lease extraction
- Entity resolution
- Claim/decision workflows
- Knowledge base

### 5.3 Phase 2 (Expansion)

**Must Have**:
- Full document extraction
- Extraction schemas
- Document relationships
- Entity resolution
- Knowledge base indexing
- Claim/evidence/decision models
- Approval workflows

**Nice to Have**:
- Advanced analytics
- Report generation
- External integrations

### 5.4 Phase 3 (Platform)

**Must Have**:
- Connector framework
- External integrations (Slack, Monday, HubSpot)
- Admin console
- Quotas and billing
- Advanced governance

---

## 6. Cross-Comparison: Implementation vs Requirements

### 6.1 Implemented vs Schema-Defined

| Domain Primitive | Schema Exists? | TypeScript Type Exists? | Database Model Exists? | API Exists? | Status |
|-----------------|----------------|------------------------|----------------------|-------------|--------|
| **Artifact** | ❌ | ✅ (different) | ✅ | ✅ | **Implemented** |
| **Manifest** | ❌ | ✅ (different) | ✅ | ✅ | **Implemented** |
| **Pointer** | ❌ | ✅ (different) | ✅ | ✅ | **Implemented** |
| **Run** | ❌ | ✅ | ✅ | ✅ | **Implemented** |
| **RunEvent** | ❌ | ✅ | ✅ | ✅ | **Implemented** |
| **DocumentSource** | ✅ | ❌ | ❌ | ❌ | **Not Implemented** |
| **DocumentStructure** | ✅ | ✅ (DocIR, different) | ❌ | ❌ | **Partial** |
| **Extraction** | ✅ | ❌ | ❌ | ❌ | **Not Implemented** |
| **Event** (domain) | ✅ | ❌ | ❌ | ❌ | **Not Implemented** |
| **Deadline** | ✅ | ❌ | ❌ | ❌ | **Not Implemented** |
| **Alert** | ✅ | ❌ | ❌ | ❌ | **Not Implemented** |
| **Claim** | ✅ | ✅ (incompatible) | ❌ | ❌ | **Type Mismatch** |
| **Evidence** | ✅ | ✅ (different concept) | ❌ | ❌ | **Concept Mismatch** |
| **Decision** | ✅ | ✅ (incompatible) | ❌ | ❌ | **Type Mismatch** |

### 6.2 UI Components vs Backend Support

| UI Component | Backend Support | Status |
|--------------|----------------|--------|
| **RunExplorerPane** | ✅ Run API, RunEvent API | **Supported** |
| **ArtifactBrowserPane** | ✅ Artifact API | **Supported** |
| **DocumentViewerPane** | ❌ No Document API | **Not Supported** |
| **EvidenceCanvas** | ❌ No Claim/Evidence API | **Not Supported** |
| **ProvenancePane** | ❌ No Claim/Evidence API | **Not Supported** |
| **GovernancePane** | ❌ No Approval API | **Not Supported** |
| **ChatPane** | ❌ No Thread API | **Not Supported** |
| **AutonomySlider** | ❌ No autonomy enforcement | **UI Only** |

### 6.3 Workflow Requirements vs Implementation

| Workflow Need | Implementation | Status |
|---------------|----------------|--------|
| **Upload leases** | ✅ Artifact upload | **Supported** |
| **Extract dates** | ❌ No extraction service | **Not Implemented** |
| **Event calendar** | ❌ No Event API | **Not Implemented** |
| **Deadline alerts** | ❌ No Alert API | **Not Implemented** |
| **Verification UI** | ❌ No Extraction API | **Not Implemented** |
| **Outcome tracking** | ❌ No Outcome API | **Not Implemented** |

---

## 7. Requirements by Topic

### 7.1 Authentication & Authorization

**From**: `src/intelli/db/models/auth.py`, `src/intelli/api/middleware/auth.py`

**Requirements**:
- Multi-tenant isolation
- User authentication (email/password + OAuth/SAML)
- API key authentication
- Role-based access control (member, admin)
- API key scopes (read, write, admin)
- Rate limiting per API key
- IP allowlist for API keys
- Audit logging

**Gaps**:
- No SSO UI
- No API key management UI
- No user management UI
- No permission management UI

### 7.2 Storage & Versioning

**From**: `src/intelli/storage/`, `src/intelli/db/models/substrate.py`

**Requirements**:
- Content-addressed storage (SHA-256)
- S3-compatible backend (MinIO dev, AWS S3 prod)
- Pre-signed URLs
- Reference counting
- Manifest history chains
- Manifest diff

**Gaps**:
- No garbage collection
- No storage lifecycle policies
- No backup strategy
- No encryption at rest

### 7.3 Real-Time Updates

**From**: `src/intelli/api/v1/streams.py`, `ui/src/hooks/use-sse.ts`

**Requirements**:
- SSE streaming
- PostgreSQL LISTEN/NOTIFY
- Run event streaming
- Activity feed streaming
- Heartbeat
- Event buffering

**Gaps**:
- No WebSocket support
- No event replay
- No event filtering UI
- No connection pooling

### 7.4 Agent Execution

**From**: `src/intelli/db/models/runs.py`, `src/intelli/services/runs/`

**Requirements**:
- Run lifecycle management
- Event logging (append-only)
- Checkpoint support
- Token/cost tracking
- Tool call logging
- Run resumption

**Gaps**:
- No agent definition model
- No workflow definition model
- No tool versioning
- No tool result caching

### 7.5 Document Processing

**From**: `schemas/document.schema.json`, `src/types/docir.ts`

**Requirements**:
- Multi-format ingestion
- Structure extraction (DocIR)
- Field extraction with confidence
- Source citation
- Version tracking
- Gap detection

**Gaps**:
- No document parsing service
- No extraction service
- No DocIR storage
- No extraction schema management

### 7.6 Event Management

**From**: `schemas/event.schema.json`, `scenarios/asset-management/01-lease-event-management.md`

**Requirements**:
- Event detection from documents
- Deadline calculation
- Alert generation and delivery
- Action tracking
- Outcome recording
- Event calendar

**Gaps**:
- No Event/Deadline/Alert models
- No event detection service
- No alert delivery service
- No deadline calculation engine

### 7.7 Claims & Decisions

**From**: `schemas/claim.schema.json`, `src/types/evidence.ts`

**Requirements**:
- Claim creation and management
- Evidence linking
- Decision workflow
- Approval chains
- Evidence graph visualization

**Gaps**:
- No Claim/Evidence/Decision models
- No claim service
- No evidence linking service
- No decision workflow engine

---

## 8. Inferred Architecture Patterns

### 8.1 Content-Addressed Storage Pattern

**Evidence**: Artifact SHA-256 PK, Manifest SHA-256 PK, content-addressed storage

**Pattern**:
- All content content-addressed by SHA-256
- Immutable once created
- Deduplication automatic
- References via hash, not mutable IDs

**Requirements**:
- SHA-256 hashing for all content
- Immutability enforcement
- Reference counting
- Garbage collection for unreferenced content

### 8.2 Event Sourcing Pattern

**Evidence**: RunEvent append-only ledger, sequence numbers, event types

**Pattern**:
- Append-only event log
- Events are source of truth
- Replay events to reconstruct state
- Checkpoints for resumption

**Requirements**:
- Monotonic sequence numbers
- Event type system
- Event replay capability
- Checkpoint support

### 8.3 Repository Pattern

**Evidence**: `src/intelli/repositories/` directory structure

**Pattern**:
- Data access abstraction
- Repository per aggregate
- Service layer uses repositories

**Requirements**:
- Repository per model
- Abstract base repository
- Query builders
- Transaction management

### 8.4 Service Layer Pattern

**Evidence**: `src/intelli/services/` directory structure

**Pattern**:
- Business logic in services
- Services use repositories
- API endpoints use services

**Requirements**:
- Service per domain area
- Service interfaces
- Dependency injection
- Error handling

### 8.5 MCP Tool Pattern

**Evidence**: MCP tools for substrate, runs, knowledge

**Pattern**:
- Expose capabilities as tools
- Agents invoke tools
- Tools return structured results
- Tool calls logged

**Requirements**:
- Tool discovery
- Tool versioning
- Tool permissions
- Tool audit logging

---

## 9. Missing Requirements (Gaps)

### 9.1 Domain Models Not Implemented

1. **DocumentSource**: Link documents to artifacts
2. **Extraction**: Store extractions with confidence and location
3. **Event** (domain): Store domain events (lease breaks, deadlines)
4. **Deadline**: Store calculated deadlines
5. **Alert**: Store alerts and delivery status
6. **Action**: Track actions on events
7. **Outcome**: Record event outcomes
8. **Claim**: Store claims and status
9. **Evidence**: Store evidence spans and links
10. **Decision**: Store decisions and approvals

### 9.2 Services Not Implemented

1. **DocumentService**: Parse documents, extract structure
2. **ExtractionService**: Extract fields with confidence
3. **EventService**: Detect events, calculate deadlines
4. **AlertService**: Generate and deliver alerts
5. **ClaimService**: Create and manage claims
6. **EvidenceService**: Link evidence to claims
7. **DecisionService**: Record decisions and approvals

### 9.3 APIs Not Implemented

1. **Documents API**: Upload, parse, get structure
2. **Extractions API**: List, verify, correct extractions
3. **Events API**: List events, get calendar
4. **Deadlines API**: List deadlines, get calculations
5. **Alerts API**: List alerts, acknowledge, snooze
6. **Claims API**: Create, list, update claims
7. **Evidence API**: Link evidence, get evidence graph
8. **Decisions API**: Record decisions, get approval status

### 9.4 UI Components Not Fully Supported

1. **DocumentViewerPane**: No Document API
2. **EvidenceCanvas**: No Claim/Evidence API
3. **ProvenancePane**: No Claim/Evidence API
4. **GovernancePane**: No Approval API
5. **ChatPane**: No Thread API

---

## 10. Recommendations

### 10.1 Immediate Actions (Phase 1)

1. **Implement domain models**: DocumentSource, Extraction, Event, Deadline, Alert
2. **Implement domain services**: DocumentService, ExtractionService, EventService, AlertService
3. **Implement domain APIs**: Documents, Extractions, Events, Deadlines, Alerts
4. **Align TypeScript types**: Generate from JSON schemas or manually align
5. **Simplify UI for Phase 1**: Dashboard instead of full workbench

### 10.2 Type System Alignment

1. **Choose JSON schemas as source of truth** for domain primitives
2. **Generate TypeScript types** from JSON schemas
3. **Resolve Claim/Evidence conflicts**: Clarify if EvidenceSpan ≠ Evidence
4. **Resolve Event conflicts**: Clarify RunLedgerEvent ≠ domain Event
5. **Align DocIR with DocumentStructure**: Map or create adapter

### 10.3 Architecture Decisions

1. **Event engine**: Choose Temporal.io vs custom vs message queue
2. **Graph database**: Add Neo4j/Apache AGE now or defer?
3. **Multi-tenant launch**: Build multi-tenant, launch single-tenant?
4. **Storage lifecycle**: Implement garbage collection and lifecycle policies
5. **Tool versioning**: Implement tool versioning system

---

## 11. Additional Requirements from Research & Patterns

### 11.1 Trust & Verification Patterns

**From**: `research/ai-tooling/trust-ux-patterns.md`

**Requirements**:
- **Calibrated trust**: Balance between trust and skepticism
- **Confidence display**: Visual confidence indicators (high/moderate/low, numerical scores)
- **Progressive trust building**: Start with low-risk tasks, gradually increase
- **Three pillars**: Awareness (when/how AI used), Agency (user control), Assurance (evidence of reliability)
- **Click-to-verify pattern**: Progressive disclosure (summary → sources → full source → original)
- **Source citation**: Inline highlights for PDFs, numbered references for search, lightweight links for quick verification
- **Error transparency**: Being transparent about errors builds trust
- **Confidence-based flagging**: Auto-flag low confidence results

**Inferred Requirements**:
- **Trust state machine**: UNTRUSTED → VERIFYING → ACCEPTED → AUTHORITATIVE
- **Trust metrics**: Track user verification patterns, correction rates
- **Trust calibration UI**: Show trust level per extraction/claim
- **Verification speed**: Verification must be faster than manual work

### 11.2 Event-Driven Architecture Patterns

**From**: `research/architecture/event-driven-patterns.md`

**Requirements**:
- **Temporal.io integration**: Durable workflows for deadline management
- **Deadline calculation**: Business day handling, timezone management, holiday calendars
- **Event-driven alerts**: Trigger-based (not scheduled polling)
- **Multi-channel notifications**: Email, SMS, push, webhook, Slack/Teams
- **Escalation chains**: Time-based escalation, acknowledgment tracking
- **Alert lifecycle**: Generated → Routed → Delivered → Acknowledged → Resolved
- **Snooze functionality**: Up to one week, repeatable
- **Alert fatigue mitigation**: MTTA, MTTR, false positive rate tracking

**Inferred Requirements**:
- **Deadline engine**: Calculate deadlines from notice periods, business days
- **Alert delivery service**: Multi-channel delivery with retry logic
- **Acknowledgment tracking**: Track who acknowledged when
- **Escalation engine**: Automatic escalation on non-acknowledgment
- **Alert quality metrics**: Track alert effectiveness

### 11.3 Security & Error Handling Patterns

**From**: `src/intelli/core/security.py`, `src/intelli/api/middleware/error_handler.py`

**Requirements**:
- **Password hashing**: Argon2 (primary), bcrypt (fallback)
- **API key hashing**: SHA-256 hash of keys
- **JWT tokens**: 24-hour expiry, tenant_id and role in payload
- **Rate limiting**: In-memory (dev), Redis-based (prod)
- **Error handling**: Structured error responses with correlation IDs
- **Audit logging**: Track all significant actions with tenant_id, user_id, IP, user_agent

**Inferred Requirements**:
- **Correlation IDs**: Request correlation for distributed tracing
- **Error codes**: Structured error codes (INTERNAL_ERROR, NOT_FOUND, etc.)
- **Error details**: Additional context in error responses
- **Security headers**: CORS, CSP, security headers
- **IP allowlist**: Restrict API key access by IP

### 11.4 Pub/Sub Patterns

**From**: `src/intelli/core/pubsub.py`

**Requirements**:
- **PostgreSQL LISTEN/NOTIFY**: Native pub/sub without external broker
- **Channel support**: run_events, activity, pointer_changes
- **Queue-based subscription**: Async queues for message delivery
- **Heartbeat**: 30-second heartbeat to keep connections alive
- **Payload limits**: 8000 bytes (PostgreSQL limit), truncate or reference for larger

**Inferred Requirements**:
- **Connection pooling**: Reuse connections for multiple subscribers
- **Channel management**: Dynamic channel registration
- **Message persistence**: For critical events (not just NOTIFY)
- **Retry logic**: Retry failed deliveries

### 11.5 Database Migration Patterns

**From**: `migrations/versions/20260123_0001_initial_substrate.py`, `migrations/versions/20260123_0002_auth_tables.py`

**Requirements**:
- **PostgreSQL extensions**: uuid-ossp, pgcrypto, vector (pgvector)
- **Content-addressed constraints**: SHA-256 format validation
- **Soft delete**: deleted_at column for pointers
- **Multi-tenant**: tenant_id FK on all scoped entities
- **Indexes**: GIN indexes for JSONB, partial indexes for soft-deleted rows
- **Foreign keys**: Referential integrity for manifests, runs, pointers

**Inferred Requirements**:
- **Migration versioning**: Sequential revision IDs
- **Rollback support**: downgrade() functions for all migrations
- **Data migrations**: Separate from schema migrations
- **Index optimization**: Partial indexes for filtered queries

### 11.6 Universal Abstractions

**From**: `requirements/UNIVERSAL-ABSTRACTIONS.md`

**Requirements**:
- **Extraction schemas**: Generic extraction engine with domain-specific schemas
- **Entity resolution**: Identify → Resolve → Enrich pattern
- **Event management**: Detect → Calendar → Alert → Action → Outcome pattern
- **Claim/Decision**: Claim → Evidence → Decision workflow
- **Generation/Review**: Generate → Review → Approve → Publish pattern

**Inferred Requirements**:
- **Schema registry**: Store and version extraction schemas
- **Entity store**: Canonical entity storage with aliases
- **Resolution rules**: Configurable matching rules per entity type
- **Event type configuration**: Configurable event types with deadline/alert rules

---

## 12. Cross-Comparison Summary

### 12.1 Implementation Completeness Matrix

| Component | Schema | TypeScript | Database | API | Service | UI | Status |
|-----------|--------|------------|----------|-----|---------|----|----|
| **Artifact** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | **Complete** |
| **Manifest** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | **Complete** |
| **Pointer** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | **Complete** |
| **Run** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | **Complete** |
| **RunEvent** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | **Complete** |
| **Document** | ✅ | ⚠️ (DocIR) | ❌ | ❌ | ❌ | ⚠️ | **Not Started** |
| **Extraction** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | **Not Started** |
| **Event** (domain) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | **Not Started** |
| **Deadline** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | **Not Started** |
| **Alert** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | **Not Started** |
| **Claim** | ✅ | ⚠️ (incompatible) | ❌ | ❌ | ❌ | ⚠️ | **Type Mismatch** |
| **Evidence** | ✅ | ⚠️ (different) | ❌ | ❌ | ❌ | ⚠️ | **Concept Mismatch** |
| **Decision** | ✅ | ⚠️ (incompatible) | ❌ | ❌ | ❌ | ❌ | **Type Mismatch** |

**Legend**:
- ✅ = Implemented
- ⚠️ = Partial/Incompatible
- ❌ = Not Implemented

### 12.2 Critical Path Dependencies

**Phase 1 (Critical Dates) Dependencies**:
1. **Document ingestion** → Requires: Artifact API ✅, Document parsing service ❌
2. **Date extraction** → Requires: Document parsing ✅, Extraction service ❌, Extraction schemas ❌
3. **Event detection** → Requires: Extraction service ❌, Event service ❌, Event models ❌
4. **Deadline calculation** → Requires: Event models ❌, Deadline engine ❌
5. **Alert delivery** → Requires: Alert models ❌, Alert service ❌, Notification infrastructure ❌
6. **Verification UI** → Requires: Extraction API ❌, Document viewer ✅

**Blockers for Phase 1**:
- No document parsing service
- No extraction service
- No event/deadline/alert models
- No alert delivery infrastructure

---

## 13. Recommendations by Priority

### 13.1 Immediate (Phase 1 Blockers)

1. **Document parsing service**: Parse PDF/Word/images → DocIR
2. **Extraction service**: Extract fields with confidence → Extraction model
3. **Event models**: Event, Deadline, Alert database models
4. **Event service**: Detect events, calculate deadlines
5. **Alert service**: Generate and deliver alerts
6. **Extraction API**: CRUD for extractions
7. **Event API**: CRUD for events/deadlines/alerts

### 13.2 Short-term (Phase 1 Enhancements)

1. **Type system alignment**: Generate TypeScript from JSON schemas
2. **Verification UI**: Click-to-verify workflow
3. **Alert delivery**: Email + dashboard notifications
4. **Event calendar**: Unified calendar view
5. **Trust metrics**: Track verification patterns

### 13.3 Medium-term (Phase 2)

1. **Claim/Evidence/Decision models**: Full claim workflow
2. **Knowledge base**: Vector indexing, semantic search
3. **Entity resolution**: Cross-document entity linking
4. **Approval workflows**: Multi-stage approvals
5. **Advanced analytics**: Reporting, dashboards

### 13.4 Long-term (Phase 3)

1. **Connector framework**: External integrations
2. **Admin console**: Tenant management, billing
3. **Advanced governance**: Policy engine, compliance
4. **Multi-tenant launch**: Production multi-tenancy

---

*This analysis should be updated as implementation progresses and new requirements are discovered.*
