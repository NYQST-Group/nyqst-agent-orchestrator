# NYQST: Platform Modules

**Product:** NYQST - Deterministic Agentic Infrastructure for Commercial Intelligence  
**Company:** NYQST AI Limited  
**Version:** 1.0  
**Last Updated:** 2026-01-25

---

## Platform Overview

The NYQST platform comprises six integrated modules that together form the "Cognitive ERP"—the structural layer that makes agentic workforces productive rather than chaotic. Each module addresses a specific aspect of organizational intelligence while maintaining deep integration with the others.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NYQST PLATFORM                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  RESEARCH   │  │  DOCUMENT   │  │  ANALYSIS   │  │  MODELLING  │        │
│  │             │  │ MANAGEMENT  │  │             │  │             │        │
│  │ Fast search │  │ File store  │  │ Infinite    │  │ Provable    │        │
│  │ Deep dive   │  │ Versioning  │  │ canvas      │  │ methods     │        │
│  │ Scraping    │  │ Ingestion   │  │ Visual      │  │ Claims      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                                             │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐          │
│  │  KNOWLEDGE & DOMAIN        │  │  ORGANISATIONAL INSIGHT     │          │
│  │                            │  │                             │          │
│  │  Ontologies                │  │  Practical intelligence     │          │
│  │  Domain models             │  │  Operations visibility      │          │
│  │  Context injection         │  │  Decision support           │          │
│  └─────────────────────────────┘  └─────────────────────────────┘          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                        CORE INFRASTRUCTURE                                  │
│  Agentic System · Skills Framework · Session Management · Assisted Workflows│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Module 1: Research

### Purpose

The Research module provides NotebookLM-like capabilities with fast search, deep research, and repeatable scraping workflows. It enables systematic investigation with full provenance, allowing users to explore information landscapes while maintaining complete audit trails.

### Core Capabilities

**Fast Search** enables rapid discovery across the organization's knowledge base. Unlike generic search, NYQST search understands domain context—a search for "DSCR breach" in PropSygnal knows to look at covenant calculations, not just text matches.

**Deep Research** supports extended investigation workflows where users can dive deep into a topic, following threads across documents and sources while the system maintains the research trail. Every finding links back to its source.

**Repeatable Scraping Workflows** (Day 2) allow organizations to set up systematic data collection from external sources. A real estate firm might configure weekly market data pulls; a regulatory team might monitor specific regulatory bodies for updates.

### Key Features

| Feature | Description |
|---------|-------------|
| Semantic search | Find information by meaning, not just keywords |
| Source linking | Every result traces to its origin |
| Research sessions | Save and resume investigation threads |
| Collaborative research | Share findings with team members |
| Export capabilities | Generate research summaries and reports |

### Integration Points

Research integrates with Document Management for source access, Knowledge & Domain for context-aware search, and Analysis for visual exploration of findings.

---

## Module 2: Document Management

### Purpose

Document Management handles file storage, versioning, bundle/corpus organization, and ingestion from tough sources. Every document maintains complete lineage from upload through all transformations and extractions.

### Core Capabilities

**File Storage** provides secure, versioned storage for all document types. Documents are immutable once stored—edits create new versions, preserving the complete history.

**Bundle/Corpus Organization** allows documents to be grouped logically. A property acquisition might have a "Due Diligence Bundle" containing all related documents. A regulatory project might have a "EMIR Corpus" containing all relevant regulatory texts.

**Ingestion from Tough Sources** handles the reality of enterprise documents: scanned PDFs, legacy formats, inconsistent structures, and poor quality originals. The system extracts what it can and flags what requires human attention.

### Document Lifecycle

```
Upload → Validate → Store → Index → Extract → Link → Version
   │         │        │       │        │       │       │
   └─────────┴────────┴───────┴────────┴───────┴───────┘
                    Full Provenance Trail
```

### Key Features

| Feature | Description |
|---------|-------------|
| Content-addressed storage | Documents identified by content hash, ensuring integrity |
| Version control | Complete history of all document versions |
| Format handling | PDF, Word, Excel, scanned documents, images |
| OCR processing | Extract text from scanned and image-based documents |
| Metadata extraction | Automatic capture of document properties |
| Access control | Fine-grained permissions at document and bundle level |

### Integration Points

Document Management feeds all other modules. Research searches documents, Analysis visualizes them, Modelling extracts structured data from them, and Knowledge & Domain builds ontologies from them.

---

## Module 3: Analysis

### Purpose

The Analysis module delivers an infinite canvas for visual analysis, enabling users to explore relationships and patterns across their knowledge base with a professional-grade application. It transforms abstract data relationships into visual, manipulable representations.

### Core Capabilities

**Infinite Canvas** provides an unbounded workspace where users can arrange, connect, and annotate information. Unlike traditional dashboards with fixed layouts, the canvas adapts to the user's thinking process.

**Visual Analysis Application** offers professional-grade tools for exploring data relationships. Users can see how documents connect, how entities relate, and how information flows through their organization.

**Pattern Recognition** surfaces relationships that might not be obvious in tabular data. When a user is analyzing a portfolio, they can see clusters of similar properties, outliers that need attention, and trends over time.

### Key Features

| Feature | Description |
|---------|-------------|
| Drag-and-drop canvas | Arrange information spatially |
| Relationship visualization | See connections between entities |
| Timeline views | Understand temporal relationships |
| Filtering and highlighting | Focus on what matters |
| Annotation and notes | Capture insights as you work |
| Export and sharing | Generate reports from canvas state |

### Use Cases

**PropSygnal:** Visualize a property portfolio showing covenant status, upcoming dates, and risk indicators. Drag in a new acquisition to see how it fits.

**RegSygnal:** Map regulatory requirements to internal controls, seeing coverage gaps and overlaps. Trace a specific requirement through to its implementation.

### Integration Points

Analysis draws from Document Management for source materials, Knowledge & Domain for entity relationships, and Modelling for calculated values. Insights captured in Analysis can feed back into Organisational Insight.

---

## Module 4: Modelling

### Purpose

Modelling is where NYQST differentiates from vaporware competitors. We prove our methods, track data provenance, and manage ambiguity and claims explicitly. When we produce an IC pack or regulatory interpretation, we can show exactly why it's correct.

### Core Capabilities

**Provable Methods** means every calculation, every extraction, every conclusion can be traced back to its inputs and the logic that produced it. This is not "the AI said so"—this is "here is the formula, here are the inputs, here is the result."

**Data Provenance** tracks where every piece of data came from. A DSCR calculation shows not just the result but the NOI figure (from which operating statement, which line), the debt service figure (from which loan agreement, which schedule), and the formula used.

**Ambiguity Management** acknowledges that real-world documents are messy. When a lease term is unclear, the system doesn't guess—it captures the ambiguity, records the possible interpretations, and tracks how the ambiguity was resolved.

**Claim Management** treats extracted information as claims that require verification. A claim might be "The lease expires on 2027-03-15" with confidence 0.95, source "Lease Agreement p.3", and status "Verified by user on 2026-01-20."

### The Modelling Difference

```
┌─────────────────────────────────────────────────────────────────┐
│                    VAPORWARE APPROACH                           │
├─────────────────────────────────────────────────────────────────┤
│  Input: Documents                                               │
│  Output: "The DSCR is 1.25"                                     │
│  Evidence: None                                                 │
│  Reproducibility: None                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    NYQST APPROACH                               │
├─────────────────────────────────────────────────────────────────┤
│  Input: Documents                                               │
│  Output: DSCR = 1.2500                                          │
│  Evidence:                                                      │
│    ├── NOI: £850,000                                            │
│    │     └── Source: Operating Statement Q3 2025, Line 47       │
│    ├── Debt Service: £680,000                                   │
│    │     └── Source: Loan Agreement Schedule 2, Row 12          │
│    └── Formula: NOI / Debt Service (Engine v2.3.1)              │
│  Reproducibility: Deterministic                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Features

| Feature | Description |
|---------|-------------|
| Calculation engines | Versioned, deterministic computation |
| Evidence chains | Every output traces to inputs |
| Confidence scoring | Quantified certainty for extractions |
| Claim lifecycle | Track claims from extraction through verification |
| Ambiguity capture | Record and resolve uncertainties explicitly |
| Audit export | Generate complete audit packages |

### Integration Points

Modelling consumes documents from Document Management, uses ontologies from Knowledge & Domain, and produces structured data that feeds Analysis and Organisational Insight.

---

## Module 5: Knowledge & Domain Management

### Purpose

Knowledge & Domain Management maintains the ontologies and domain models that give structure to organizational intelligence. This is the "Graph" that makes context injection possible—the rigid structure that transforms raw AI capability into directed organizational value.

### Core Capabilities

**Ontology Management** defines the concepts, relationships, and rules that structure a domain. For commercial real estate, this includes entities like Property, Lease, Tenant, Covenant, and the relationships between them.

**Domain Models** capture industry-specific knowledge. A CRE domain model knows that a DSCR covenant typically requires NOI to exceed debt service by some ratio. A regulatory domain model knows that EMIR requires certain fields in trade reports.

**Context Injection** is the key capability that makes agents productive. When an agent needs to analyze a property, it doesn't start from scratch—it receives the full context of what a property is, what matters about it, and how it relates to other entities.

### The Ontology as Asset

The ontology is not configuration—it is a core asset. It represents the accumulated knowledge of how the organization's domain works. This is what allows:

- Instant onboarding of new agents (they inherit the ontology)
- Consistency across all operations (everyone uses the same definitions)
- Persistence beyond individuals (the knowledge stays when people leave)

### Key Features

| Feature | Description |
|---------|-------------|
| Entity definitions | Define the concepts in your domain |
| Relationship mapping | Capture how entities connect |
| Validation rules | Enforce domain constraints |
| Inheritance | Build specialized models from general ones |
| Version control | Track ontology evolution over time |
| Import/export | Share ontologies across deployments |

### Integration Points

Knowledge & Domain provides the structural foundation for all other modules. Research uses it for context-aware search, Document Management uses it for classification, Analysis uses it for relationship visualization, and Modelling uses it for calculation context.

---

## Module 6: Organisational Insight

### Purpose

Organisational Insight surfaces practical intelligence from the system, enabling organizations to understand their own knowledge and operations. It transforms the accumulated data and analysis into actionable understanding.

### Core Capabilities

**Practical Intelligence** means insights that drive action, not just dashboards that look impressive. When the system surfaces that "3 properties have covenants within 10% of breach," that's actionable. When it shows "Document processing volume increased 40% this quarter," that's context.

**Operations Visibility** provides a clear view of how the organization is using the system. Which workflows are running? What's the extraction accuracy? Where are the bottlenecks?

**Decision Support** helps users make better decisions by surfacing relevant context. When evaluating a new acquisition, the system can show similar past deals, how they performed, and what factors mattered.

### Key Features

| Feature | Description |
|---------|-------------|
| Portfolio dashboards | Aggregate views across assets |
| Alert management | Proactive notification of important events |
| Trend analysis | Understand patterns over time |
| Comparison tools | Benchmark against history or peers |
| Report generation | Produce standard and custom reports |
| Workflow monitoring | Track operational health |

### Integration Points

Organisational Insight consumes data from all other modules to produce its views. It draws on Document Management for volume metrics, Modelling for calculated values, Analysis for relationship insights, and Knowledge & Domain for contextual understanding.

---

## Core Infrastructure

Underlying all modules is the core infrastructure that makes NYQST work:

### Agentic System

The agentic system manages AI agents that perform work within the platform. Agents are not autonomous—they operate within defined boundaries, with defined capabilities, and with full logging of their actions.

**Agent-Maintained Skills:** A key differentiator is that agents maintain skills over time, looking across sessions and states for insights. This starts simple but becomes more habitual in workflows, allowing the system to learn and improve from organizational usage patterns.

#### Workflow vs Agent Distinction

Following Anthropic's architectural distinction, NYQST differentiates between two types of agentic systems:

**Workflows** are systems where LLMs and tools are orchestrated through **predefined code paths**. They are deterministic, auditable, and predictable. In NYQST, these are governed workflows backed by Camunda—the method is signed off, and you don't expect people to check the results.

**Agents** are systems where LLMs **dynamically direct their own processes** and tool usage. They are flexible, exploratory, and user-directed. In NYQST, these are tasks within sessions—they can be complex but are not pre-approved.

This distinction is critical: we use workflows for regulated processes requiring audit trails, and agents for exploratory work where flexibility matters.

#### Long-Running Agent Patterns

For complex tasks spanning multiple sessions, NYQST implements patterns from Anthropic's research on long-running agents:

**Initializer Agent:** Sets up the environment on first run—loads context, configures tools, establishes working state.

**Incremental Progress Agent:** Makes progress in every session while leaving clear artifacts for the next session. Each session produces checkpointable state.

**Session Bridging:** State persists across context windows through checkpointing. Users can return to a topic with their setup intact.

> **ADR Note (Long-Running Agent Patterns):** ADR needed for: initializer vs progress agent separation, artifact format for session handoff, checkpoint granularity, context window management strategies.

### Skills Framework

Skills are discrete capabilities that agents can use. A "Lease Extraction" skill knows how to extract structured data from lease documents. A "Covenant Calculation" skill knows how to compute DSCR, LTV, and other ratios. Skills are versioned and auditable.

Skills exist at multiple levels:
- **Session-level:** Temporary skills for a specific task
- **User-level:** Personal skills and macros
- **Organization-level:** Shared skills across the tenant

#### Tool Design Principles

Following Anthropic's research on effective tools for agents, NYQST skills adhere to these principles:

**Namespacing:** Skills define clear boundaries in functionality. A "Lease.Extract" skill is distinct from "Covenant.Calculate"—agents know exactly what each skill does.

**Meaningful Context Return:** Skills return meaningful context back to agents, not just raw data. A lease extraction returns not just dates but confidence scores, source locations, and ambiguity flags.

**Token Efficiency:** Skill responses are optimized for token efficiency. Large documents are summarized; only relevant sections are returned in full.

**Good Descriptions:** Every skill has a well-engineered description that helps agents understand when and how to use it. Descriptions include: purpose, inputs, outputs, and usage examples.

> **ADR Note (Tool Design Standards):** ADR needed for: skill interface specification, namespacing conventions, response format standards, description templates, versioning strategy.

### Session Management

Sessions track user interactions with the system. Every action is logged, every decision is recorded, and the full context of a work session can be reconstructed.

**Return to Topic:** Users can return to a topic with their setup intact in a contained space. Sessions preserve state, context, and working environment so users can pick up exactly where they left off.

**Guided for Business Users:** The interface is guided and tailored for business users—not a raw IDE experience. Simple sessions for research tasks, more complex environments for modelling and analysis, but always appropriate to the user's skill level and task.

> **ADR Note (Session/VM Architecture):** The session management layer may be backed by VM orchestration (hidden from users). This enables contained workspaces, environment persistence, and clean isolation. ADR needed for: VM orchestration strategy, session persistence mechanisms, user/org/session-level customization, IDE exposure decisions (hidden vs. exposed based on task type).

### Assisted Workflows

Assisted workflows guide users through complex processes. A "Property Onboarding" workflow might include document upload, extraction verification, covenant setup, and alert configuration—with the system handling routine steps and prompting for human input where needed.

**Camunda-Based Governance:** Workflows use a well-governed workflow engine (Camunda Community Edition) for audit, compliance, and organizational control.

> **ADR Note (Workflow Engine):** ADR needed for: Camunda integration patterns, workflow definition format, human-in-the-loop checkpoints, workflow versioning and migration.

### Indexing, Diffing, and Staleness Detection

A core capability that powers search, change detection, and workflow triggering:

**Indexing:** Automatic indexing using Merkle trees, semantic chunking, and embeddings. Supports keyword search (Day 1), semantic search (Day 1), and RAG/GraphRAG (Day 2). May use tools like Treesitter for code-aware parsing.

**Diffing:** When documents are updated, the system detects changes and marks dependent analysis as stale. Workflows are flagged for re-running.

**Staleness Propagation:** If a planning application identified that project management was needed and we created a relational structure, but we now see risk management in the picture, the system identifies the new structure needed and either sources or extends from existing domain models.

> **ADR Note (Indexing/Diffing Service):** This is core to our design but should be architected as a swappable service accessible via both API and MCP. ADR needed for: service boundary definition, API vs MCP access patterns, swap-in/swap-out design, backend flexibility (pgvector → OpenSearch/Qdrant/Vespa).

### Document Processing Pipeline

The document processing pipeline handles ingestion, parsing, and extraction from diverse document types. Based on industry research (Docling, LlamaParse, Unstructured.io), NYQST implements a multi-tier approach:

**Tier 1 - Fast Parse:** Quick extraction for simple documents using traditional parsing. No AI required—fast and cheap.

**Tier 2 - LLM Parse:** Text understanding for complex documents. Uses LLM to interpret structure and meaning.

**Tier 3 - Vision Parse:** Multimodal understanding for scanned documents, images, and complex layouts. Screenshots pages and uses VLM for extraction.

**Tier 4 - Agent Parse:** Full agent-based processing for the most complex documents. Agent orchestrates multiple tools and makes judgment calls.

**Key Capabilities:**
- OCR for scanned documents (with language support)
- Table extraction with structure preservation
- Layout understanding (multi-column, nested structures)
- Math and code extraction
- Semantic chunking for RAG

**Evaluation Framework:** Following Unstructured's SCORE framework, document processing is evaluated on:
- Structural accuracy (layout, tables, hierarchy)
- Content fidelity (text accuracy, no hallucinations)
- Semantic preservation (meaning, relationships)

> **ADR Note (Document Processing Pipeline):** ADR needed for: tier selection logic, parser technology choices (Docling vs LlamaParse vs custom), evaluation metrics, quality thresholds, fallback strategies.

### Document Classification Service

ML models compare document content to existing taxonomies and domain models to quickly suggest what concepts are present (legal, ISDA CDM, commercial property, etc.), then deploy the right skills.

**Taxonomy Matching:** Fast classification against known taxonomies to route documents to appropriate processing pipelines.

**Skill Deployment:** Based on classification, the system automatically selects and deploys relevant skills for extraction and analysis.

> **ADR Note (Classification Service):** This may be architected as a separate MCP service that can be sold externally or used internally. ADR needed for: service boundary, MCP interface design, taxonomy management, skill routing logic.

### Domain Model Library

A Context7-style server offering structured domain models for specialist work:

**Search and Discovery:** Search "commercial real estate" and get library IDs of INREV, RICS models, Red Book guidance, etc. Search "derivatives" and get ISDA CDM, DRR, etc.

**Technical Details and Summaries:** LLM-generated summaries of technical standards, or full technical details for implementation.

**Extensible Corpus:** Organizations can add their own domain models via the Knowledge Management layer.

**Dedicated Specialist Work:** Unlike general-purpose copilots (where you might find the info, you might not), this is for dedicated specialist work where we know the shape of the domain. Information is vast but tailored.

> **ADR Note (Domain Model Library):** Could use a private Context7 instance initially, then build custom. ADR needed for: Context7 integration vs custom build, domain model ingestion pipeline, search and retrieval interface, tenant-specific extensions.

### Microsoft CDM Integration

When structures relate to concepts in Microsoft Common Data Model, we use MS CDM to build relational stores:

**CDM Helper:** An MCP service that provides information on MS CDM structures, proposes relevant table structures and extensions.

**Relational Store Setup:** A simple relational store that can instantly set up proposed structures, then agents use researcher/extractor/structuring tools to populate.

**Extension Workflow:** Either extend CDM using the MCP helper, or use the catalogue to find existing structures.

> **ADR Note (CDM Integration):** ADR needed for: MS CDM version strategy, extension governance, relational store technology choice, MCP interface design.

### Background Copilot

A constantly-running background agent system:

**Request Analysis:** Looks at requests and links them to tasks in an organizational domain model it builds innately.

**Opportunity Detection:** Looks for opportunities, patterns, and insights across the organization's work.

**Institutional Knowledge Building:** With tenant consent, builds institutional knowledge that can be applied later. This allows landing the product with a lightweight copilot experience while building deep organizational understanding.

> **ADR Note (Background Copilot):** ADR needed for: consent and privacy model, background processing architecture, opportunity surfacing UX, institutional knowledge storage and access.

### Dynamic Views

Agents can create views dynamically based on corpus analysis, enabling adaptive visualization and application generation:

**Agent-Generated Visualizations:** When analyzing a corpus, agents create views that best capture the relevant information. This is not a fixed dashboard—it's a dynamic representation tailored to the specific content and analysis goals.

**Two Forms of Dynamic Views:**

1. **Corpus Visualization (Day 1):** Visual representation of relevant documents, concepts/domains/skills, and the workflow for analysis. Shows the landscape of information being analyzed. Clickable elements can be added to tasks—users see the proposed analysis path and can commit steps to their task list.

2. **Agent-Generated Business Apps (Day 2):** Agents generate functional business applications for specific use cases. Similar to Monday's "vibe" approach or Google AI Studio where an agent builds a product, but much more guardrailed. The agent configures views based on a guardrailed environment rather than arbitrary code generation.

   Examples:
   - Generate a covenant monitoring dashboard for a specific portfolio
   - Create a regulatory compliance tracker for a specific corpus
   - Build a lease critical date monitoring application
   
   The generated apps are constrained to the platform's component library and data model—agents configure and compose, they don't write arbitrary code.

**Use Cases:**
- Analyze a regulatory corpus and see a visual map of documents, key concepts, and suggested analysis workflow
- Review a property portfolio and see clustered properties, relevant domain models, and recommended extraction workflows
- Explore a new document bundle and see suggested skills, related domain knowledge, and proposed processing steps
- Generate a monitoring application for ongoing covenant compliance

> **ADR Note (Dynamic Views):** ADR needed for: view generation algorithms, visualization framework, task integration, view persistence and sharing.

> **ADR Note (Agent-Generated Apps):** Day 2 concept. ADR needed for: guardrailed component library, app configuration schema, agent constraints, app persistence and sharing, app versioning.

### Context Management Service

Beyond the context management built for agents (compaction, injections), this is organizational context management:

**Email Ingestion:** Ingest emails to create context appended to clients and projects. If allocation is unclear, a queue is created for users to assign information to the correct client/project.

**Connector Pattern:** Offered via a connector (Gmail, Outlook), a skill, an agent, and a workflow. This pattern is common and sellable:
- **Connector** - Integration with external system (Gmail, Slack, etc.)
- **Skill** - Capability to process the data
- **Agent** - Orchestration of the processing
- **Workflow** - Governed execution with audit trail
- **Tool** (optional) - User-facing interface

**Organizational Context Building:** Automatically builds context around clients and projects from ingested communications, creating a rich understanding of relationships and history.

> **ADR Note (Context Management Service):** ADR needed for: connector architecture, email parsing and classification, client/project matching algorithms, user queue UX, privacy and consent model.

> **ADR Note (MCP Workflow Capability):** Day 3 concept: Build workflow capability into MCP itself, allowing the connector+skill+agent+workflow pattern to be packaged and sold externally via MCP. ADR needed for: MCP workflow extension design, external packaging, billing/metering.

---

## Design Principles

All modules adhere to core design principles:

| Principle | Implementation |
|-----------|----------------|
| **Evidence by default** | Every output traces to source—fundamental architecture, not compliance feature |
| **AI for translation, engines for truth** | AI handles extraction and interpretation; deterministic engines handle calculations |
| **Schema-first development** | Data model defined before features—becomes contract between components |
| **Human oversight at checkpoints** | AI accelerates; humans retain judgment |
| **One source of truth** | Data flows through lifecycle with full audit trail |

---

## ADR Summary

The following architectural decisions are flagged for detailed ADR documentation:

| ADR Topic | Scope | Key Questions |
|-----------|-------|---------------|
| **Session/VM Architecture** | Core | VM orchestration, session persistence, IDE exposure decisions |
| **Workflow Engine** | Core | Camunda integration, workflow definition, human-in-the-loop |
| **Indexing/Diffing Service** | Core | Service boundary, API vs MCP, backend flexibility |
| **Classification Service** | MCP Service | Service boundary, taxonomy management, skill routing |
| **Domain Model Library** | MCP Service | Context7 vs custom, ingestion pipeline, tenant extensions |
| **CDM Integration** | MCP Service | MS CDM versioning, extension governance, relational store |
| **Background Copilot** | Core | Consent model, background processing, knowledge storage |
| **Dynamic Views** | Core | View generation, visualization framework, task integration |
| **Agent-Generated Apps** | Day 2 | Guardrailed component library, app configuration, agent constraints |
| **Context Management Service** | Core | Connector architecture, email parsing, client/project matching |
| **MCP Workflow Capability** | Day 3 | MCP workflow extension, external packaging, billing |
| **Long-Running Agent Patterns** | Core | Initializer vs progress agent, artifact format, checkpoint granularity |
| **Tool Design Standards** | Core | Skill interface specification, namespacing, response format |
| **Document Processing Pipeline** | Core | Tier selection, parser technology, evaluation metrics |

---

**Related Documents:**
- [Executive Summary](01_EXECUTIVE_SUMMARY.md) - Quick overview
- [Vision & Thesis](02_VISION.md) - Strategic context
- [Products](04_PRODUCTS.md) - PropSygnal & RegSygnal
- [Architecture](06_ARCHITECTURE.md) - Technical implementation
