# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for the NYQST platform.

## What is an ADR?

An Architecture Decision Record (ADR) captures an important architectural decision made along with its context and consequences. ADRs are immutable once accepted—if a decision changes, a new ADR supersedes the old one.

## ADR Status

- **Proposed:** Under discussion, not yet accepted
- **Accepted:** Decision has been made and is in effect
- **Deprecated:** No longer relevant (but kept for history)
- **Superseded:** Replaced by a newer ADR (link to replacement)

## ADR Index

| ADR | Title | Status | PRD Reference |
|-----|-------|--------|---------------|
| [000](./000-TEMPLATE.md) | Template | N/A | N/A |
| [001](./001-data-model-strategy.md) | Data Model Strategy - Domain-First with CDM Mapping | Accepted | 03_PLATFORM.md, 06_ARCHITECTURE.md |
| [002](./002-code-generation-strategy.md) | Code Generation and Contract Strategy | Proposed | 06_ARCHITECTURE.md |
| [003](./003-virtual-team-architecture.md) | Virtual Team Architecture for AI Agent Coordination | Proposed | 03_PLATFORM.md, 06_ARCHITECTURE.md |
| [004](./004-index-service-architecture.md) | Index Service Architecture | Proposed | 03_PLATFORM.md, 06_ARCHITECTURE.md |
| [005](./005-agent-runtime-framework.md) | Agent Runtime and Framework Choice | Proposed | 06_ARCHITECTURE.md, 03_PLATFORM.md |
| [006](./006-session-workspace-architecture.md) | Session and Workspace Architecture | Proposed | 06_ARCHITECTURE.md |
| [007](./007-document-processing-pipeline.md) | Document Processing Pipeline | Proposed | 03_PLATFORM.md, 06_ARCHITECTURE.md |
| [008](./008-mcp-tool-architecture.md) | MCP Tool Architecture | Proposed | 06_ARCHITECTURE.md, 03_PLATFORM.md |
| [009](./009-human-in-the-loop-governance.md) | Human-in-the-Loop and Governance Patterns | Proposed | 06_ARCHITECTURE.md, 03_PLATFORM.md |
| [010](./010-bootstrap-infrastructure.md) | Bootstrap Infrastructure — PostgreSQL + pgvector + Neo4j | Proposed | 03_PLATFORM.md |

## Pending ADRs (from PRD Notes)

The following ADRs have been flagged in the PRD documents and need to be written:

### Core Architecture

| Topic | PRD Source | Key Questions | Status |
|-------|------------|---------------|--------|
| Session/VM Architecture | 06_ARCHITECTURE.md | VM orchestration, session persistence, cold start, resource allocation | **→ [ADR-006](./006-session-workspace-architecture.md)** |
| Knowledge Architecture | 06_ARCHITECTURE.md | Storage format, retrieval, versioning, sharing permissions | Pending |
| Playbook Architecture | 06_ARCHITECTURE.md | Definition format, versioning, batch orchestration, improvement loop | Pending |
| Task vs Workflow Architecture | 06_ARCHITECTURE.md | Task/workflow unification, governance layer, Camunda integration | Pending |
| Checkpointing Architecture | 06_ARCHITECTURE.md | Storage backend, granularity policies, serialization, pruning | Partially covered in **[ADR-005](./005-agent-runtime-framework.md)** |
| Human-in-the-Loop Patterns | 06_ARCHITECTURE.md | Interrupt triggers, state inspection, approval workflow, feedback | **→ [ADR-009](./009-human-in-the-loop-governance.md)** |
| Long-Running Agent Patterns | 03_PLATFORM.md | Initializer vs progress agent, artifact format, checkpoint granularity | Partially covered in **[ADR-005](./005-agent-runtime-framework.md)** |
| Tool Design Standards | 03_PLATFORM.md | Skill interface specification, namespacing, response format | **→ [ADR-008](./008-mcp-tool-architecture.md)** |

### Integration

| Topic | PRD Source | Key Questions | Status |
|-------|------------|---------------|--------|
| CRM/PM Integration | 06_ARCHITECTURE.md | Monday/HubSpot/Salesforce connectors, bidirectional sync | Pending |
| MCP Marketplace | 06_ARCHITECTURE.md | Discovery, versioning, security, custom onboarding, billing | Pending |
| MCP Architecture | 06_ARCHITECTURE.md | Full adoption vs selective, tool design, workflow in MCP | **→ [ADR-008](./008-mcp-tool-architecture.md)** |
| Agent Framework Choice | 06_ARCHITECTURE.md | LangGraph vs Vercel AI SDK vs custom | **→ [ADR-005](./005-agent-runtime-framework.md)** |

### UI/UX

| Topic | PRD Source | Key Questions | Status |
|-------|------------|---------------|--------|
| Research UI | 06_ARCHITECTURE.md | Panel layout, source ingestion, Deep vs Fast research | Pending |
| Workbench UI | 06_ARCHITECTURE.md | IDE framework, terminal integration, file system | Pending |
| Analysis Canvas | 06_ARCHITECTURE.md | Canvas framework, data model, collaboration, export | Pending |
| Cross-Session Analysis | 06_ARCHITECTURE.md | Permissions, pattern detection, coaching reports, privacy | Pending |
| Generative UI Architecture | 06_ARCHITECTURE.md | Component library, AG-UI protocol, state sync, guardrails | Pending |

### Platform Services

| Topic | PRD Source | Key Questions | Status |
|-------|------------|---------------|--------|
| Document Processing Pipeline | 03_PLATFORM.md | Tier selection, parser technology, evaluation metrics | **→ [ADR-007](./007-document-processing-pipeline.md)** |
| Classification Service | 03_PLATFORM.md | Service boundary, MCP interface, taxonomy management | Pending |
| Domain Model Library | 03_PLATFORM.md | Context7-style server, search, LLM summarization | Pending |
| CDM Integration | 03_PLATFORM.md | Microsoft CDM, table structures, extensions | Covered in **[ADR-001](./001-data-model-strategy.md)** |
| Indexing/Diffing Service | 03_PLATFORM.md | Service boundary, API vs MCP, swap-in/swap-out | **→ [ADR-004](./004-index-service-architecture.md)** |
| Context Management Service | 03_PLATFORM.md | Connector architecture, email parsing, client/project matching | Pending |

### Product Features

| Topic | PRD Source | Key Questions | Status |
|-------|------------|---------------|--------|
| Dynamic Views | 03_PLATFORM.md | View generation, visualization framework, task integration | Pending |
| Agent-Generated Apps | 03_PLATFORM.md | Guardrailed component library, app configuration, constraints | Pending |
| Background Copilot | 03_PLATFORM.md | Trigger conditions, organizational model building, opportunity detection | Pending |
| MCP Workflow Capability | 03_PLATFORM.md | MCP workflow extension, external packaging, billing | Pending |

## How to Write an ADR

1. Copy `000-TEMPLATE.md` to a new file with the next number (e.g., `001-session-architecture.md`)
2. Fill in all sections
3. Submit for review via PR
4. Once accepted, update this README index

## Naming Convention

ADRs are numbered sequentially: `NNN-short-title.md`

Examples:
- `001-session-vm-architecture.md`
- `002-agent-framework-choice.md`
- `003-document-processing-pipeline.md`
