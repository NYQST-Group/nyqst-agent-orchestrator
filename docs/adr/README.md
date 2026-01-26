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

## Pending ADRs (from PRD Notes)

The following ADRs have been flagged in the PRD documents and need to be written:

### Core Architecture

| Topic | PRD Source | Key Questions |
|-------|------------|---------------|
| Session/VM Architecture | 06_ARCHITECTURE.md | VM orchestration, session persistence, cold start, resource allocation |
| Knowledge Architecture | 06_ARCHITECTURE.md | Storage format, retrieval, versioning, sharing permissions |
| Playbook Architecture | 06_ARCHITECTURE.md | Definition format, versioning, batch orchestration, improvement loop |
| Task vs Workflow Architecture | 06_ARCHITECTURE.md | Task/workflow unification, governance layer, Camunda integration |
| Checkpointing Architecture | 06_ARCHITECTURE.md | Storage backend, granularity policies, serialization, pruning |
| Human-in-the-Loop Patterns | 06_ARCHITECTURE.md | Interrupt triggers, state inspection, approval workflow, feedback |
| Long-Running Agent Patterns | 03_PLATFORM.md | Initializer vs progress agent, artifact format, checkpoint granularity |
| Tool Design Standards | 03_PLATFORM.md | Skill interface specification, namespacing, response format |

### Integration

| Topic | PRD Source | Key Questions |
|-------|------------|---------------|
| CRM/PM Integration | 06_ARCHITECTURE.md | Monday/HubSpot/Salesforce connectors, bidirectional sync |
| MCP Marketplace | 06_ARCHITECTURE.md | Discovery, versioning, security, custom onboarding, billing |
| MCP Architecture | 06_ARCHITECTURE.md | Full adoption vs selective, tool design, workflow in MCP |
| Agent Framework Choice | 06_ARCHITECTURE.md | LangGraph vs Vercel AI SDK vs custom |

### UI/UX

| Topic | PRD Source | Key Questions |
|-------|------------|---------------|
| Research UI | 06_ARCHITECTURE.md | Panel layout, source ingestion, Deep vs Fast research |
| Workbench UI | 06_ARCHITECTURE.md | IDE framework, terminal integration, file system |
| Analysis Canvas | 06_ARCHITECTURE.md | Canvas framework, data model, collaboration, export |
| Cross-Session Analysis | 06_ARCHITECTURE.md | Permissions, pattern detection, coaching reports, privacy |
| Generative UI Architecture | 06_ARCHITECTURE.md | Component library, AG-UI protocol, state sync, guardrails |

### Platform Services

| Topic | PRD Source | Key Questions |
|-------|------------|---------------|
| Document Processing Pipeline | 03_PLATFORM.md | Tier selection, parser technology, evaluation metrics |
| Classification Service | 03_PLATFORM.md | Service boundary, MCP interface, taxonomy management |
| Domain Model Library | 03_PLATFORM.md | Context7-style server, search, LLM summarization |
| CDM Integration | 03_PLATFORM.md | Microsoft CDM, table structures, extensions |
| Indexing/Diffing Service | 03_PLATFORM.md | Service boundary, API vs MCP, swap-in/swap-out |
| Context Management Service | 03_PLATFORM.md | Connector architecture, email parsing, client/project matching |

### Product Features

| Topic | PRD Source | Key Questions |
|-------|------------|---------------|
| Dynamic Views | 03_PLATFORM.md | View generation, visualization framework, task integration |
| Agent-Generated Apps | 03_PLATFORM.md | Guardrailed component library, app configuration, constraints |
| Background Copilot | 03_PLATFORM.md | Trigger conditions, organizational model building, opportunity detection |
| MCP Workflow Capability | 03_PLATFORM.md | MCP workflow extension, external packaging, billing |

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
