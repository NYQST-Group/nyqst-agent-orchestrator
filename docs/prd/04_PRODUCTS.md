# NYQST: Product Variants

**Product:** NYQST - Deterministic Agentic Infrastructure for Commercial Intelligence  
**Company:** NYQST AI Limited  
**Version:** 1.0  
**Last Updated:** 2026-01-25

---

## Product Strategy

NYQST is a platform that powers vertical product variants. Each variant applies the core platform capabilities to a specific industry domain, with tailored ontologies, workflows, and outputs. The platform provides the infrastructure; the products provide the domain expertise.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NYQST PLATFORM                                    │
│                                                                             │
│  Research · Document Management · Analysis · Modelling · Knowledge · Insight│
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────┐    ┌─────────────────────────────┐        │
│  │        PROPSYGNAL           │    │        REGSYGNAL            │        │
│  │                             │    │                             │        │
│  │   Commercial Real Estate    │    │   Regulatory Intelligence   │        │
│  │                             │    │                             │        │
│  │   • Investment & Acq        │    │   • Regulatory Monitoring   │        │
│  │   • Development & PM        │    │   • Reporting Validation    │        │
│  │   • Asset Management        │    │   • Compliance Modelling    │        │
│  │   • Debt & Credit           │    │                             │        │
│  │   • Property Management     │    │                             │        │
│  └─────────────────────────────┘    └─────────────────────────────┘        │
│                                                                             │
│                         [Future Variants]                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PropSygnal

### Overview

PropSygnal is an AI-powered platform supporting the full real estate investment lifecycle. From acquisition due diligence through asset management to exit, PropSygnal provides integrated tools with a single source of truth and complete evidence trails.

### The Problems We Solve

Real estate operations involve complex, interconnected processes across multiple teams. Current challenges include:

| Pain Point | Impact |
|------------|--------|
| **Manual data extraction** | Hours spent pulling data from documents |
| **Siloed systems** | Same data entered multiple times |
| **No audit trail** | Can't prove where numbers came from |
| **Version confusion** | Which spreadsheet is current? |
| **Inconsistent methods** | Different analysts, different results |
| **Lifecycle disconnects** | Acquisition data doesn't flow to operations |

### Five Product Areas

PropSygnal is organized into five integrated product areas that cover the complete real estate investment lifecycle:

#### 1. Investment & Acquisitions

**Focus:** Deal screening, due diligence, market research, IC memos, legal closing

**Key Capabilities:**
- Deal screening against investment criteria
- Automated due diligence workflows (property, technical, legal, tax, financial)
- Market research and comparables analysis
- Investment Committee memo generation
- Legal closing document review and summary

**Key Outputs:**
- Deal screening summaries
- DD checklists and findings
- IC memos and presentations
- Market research packs

**Investment Return Metrics:**
- Unlevered IRR (returns before financing)
- Levered IRR (returns after financing)
- Multiple on Invested Capital
- Cash on Cash (annual cash yield)
- Entry/Exit Yield (going-in and exit cap rates)

#### 2. Development & Project Management

**Focus:** Cost/programme control, Building Safety Act compliance, project monitoring

**Key Capabilities:**
- Development dashboard with cost, programme, and risk monitoring
- Hard costs, soft costs, and contingency tracking
- Timeline tracking and variance alerts
- Building Safety Act gateway process support
- Planning process support and policy alignment
- Construction documentation management

**Key Outputs:**
- Development dashboards
- Cost reports and variance analysis
- Programme status updates
- BSA compliance packs
- Gateway documentation

#### 3. Asset Management

**Focus:** Value-add initiatives, reporting, capex/opex management

**Key Capabilities:**
- Quarterly reporting with links to source financials
- Value-add initiative tracking (capex analysis, rental growth, refurbishment timing)
- Budget management and variance analysis
- Building Passport integration for golden thread documentation
- Business plan management and tracking

**Key Outputs:**
- Quarterly reports
- Business plans
- Capex/opex analysis
- Performance vs plan comparisons

#### 4. Debt & Credit (Current MVP Focus)

**Focus:** Covenant monitoring, credit papers, lending analysis

**Key Capabilities:**
- Automated covenant calculations (DSCR, LTV, ICR, Debt Yield)
- Rent roll extraction and validation
- Operating statement extraction
- Loan agreement extraction
- Evidence trail generation for all calculations
- Lender pack generation

**Key Outputs:**
- Covenant compliance reports (PASS/FAIL with evidence)
- Headroom analysis (distance to breach)
- Trend tracking (historical covenant performance)
- Early warning alerts (before breaches occur)
- Audit-ready lender packs

**Core Covenants:**

| Covenant | Formula | Typical Threshold |
|----------|---------|-------------------|
| DSCR | NOI / Debt Service | ≥ 1.20x |
| LTV | Loan Balance / Property Value | ≤ 65% |
| ICR | EBITDA / Interest Expense | ≥ 1.50x |
| Debt Yield | NOI / Loan Balance | ≥ 8% |

#### 5. Property Management

**Focus:** Leasing, marketing, operations, compliance

**Key Capabilities:**
- Leasing and sales management (tenant pipeline, deal tracking)
- Marketing (listing management, lead tracking)
- Tenant management (onboarding, references, turnover)
- Contract and lease administration
- Service charge and operating cost control
- Rent collection and arrears management
- Regulatory compliance and documentation
- Maintenance oversight and contractor coordination
- Health and safety policy integration

**Key Outputs:**
- Rent rolls
- Compliance tracking
- Arrears reports
- Maintenance schedules

### Lifecycle Coverage

PropSygnal maintains data continuity across the entire investment lifecycle:

**Yielding Asset Flow:**
```
Investment & Acquisitions → Asset Management → Property Management
                                    ↑
                          Debt & Credit (throughout)
```

**Development Asset Flow:**
```
Investment & Acquisitions → Development & Project Mgmt → Asset Management → Property Management
                                                                ↑
                                                      Debt & Credit (throughout)
```

### Value Delivered

| Outcome | Measure |
|---------|---------|
| **Time savings** | 80% reduction in compliance workload |
| **Accuracy** | 100% reproducible calculations |
| **Confidence** | Every value traceable to source |
| **Consistency** | Same method, every time |
| **Connectivity** | Data flows through entire lifecycle |

### Who Uses PropSygnal

| Role | Primary Product Areas | Use Case |
|------|----------------------|----------|
| **Investment Analyst** | Investment & Acquisitions | Deal screening, DD, IC memos |
| **Development Manager** | Development & Project Mgmt | Cost control, programme, BSA |
| **Asset Manager** | Asset Management, Debt & Credit | Value-add, reporting, covenants |
| **Property Manager** | Property Management | Leasing, operations, compliance |
| **Financial Controller** | All | Budgets, invoicing, audit support |
| **Credit Analyst** | Debt & Credit, Investment | Lending analysis, credit papers |
| **Fund Operations** | All | Portfolio-level oversight |

### Current Status

**Phase:** MVP — Debt & Credit foundation  
**Focus:** Single asset covenant monitoring with evidence trails  
**Next:** Asset Management reporting and portfolio scale

---

## RegSygnal

### Overview

RegSygnal applies the NYQST platform to financial services regulatory intelligence. It transforms regulatory documents into executable compliance logic, managing the full chain from regulatory text to code, including all ambiguity management and claim verification.

### The Problems We Solve

Financial services firms face an ever-increasing regulatory burden. Current challenges include:

| Pain Point | Impact |
|------------|--------|
| **Regulatory volume** | Thousands of pages of new requirements annually |
| **Interpretation ambiguity** | Same text, different interpretations |
| **Implementation gaps** | Requirements don't map cleanly to systems |
| **Change management** | Regulations evolve; implementations must follow |
| **Audit burden** | Proving compliance requires extensive documentation |
| **Knowledge concentration** | Expertise trapped in individual heads |

### The RegSygnal Difference

Traditional compliance approaches treat regulations as documents to be read and interpreted by humans. RegSygnal treats regulations as specifications to be modelled, tested, and verified.

```
┌─────────────────────────────────────────────────────────────────┐
│                 TRADITIONAL APPROACH                            │
├─────────────────────────────────────────────────────────────────┤
│  Regulation → Human reads → Human interprets → Human implements │
│                                                                 │
│  Problems:                                                      │
│  • Interpretation varies by person                              │
│  • Knowledge leaves when people leave                           │
│  • Audit requires reconstructing reasoning                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 REGSYGNAL APPROACH                              │
├─────────────────────────────────────────────────────────────────┤
│  Regulation → Model requirements → Capture ambiguity →          │
│  → Resolve with evidence → Implement with traceability          │
│                                                                 │
│  Benefits:                                                      │
│  • Interpretation is explicit and versioned                     │
│  • Knowledge persists in the model                              │
│  • Audit trail is built-in                                      │
└─────────────────────────────────────────────────────────────────┘
```

### End-to-End Workflow

RegSygnal provides a structured environment with assistive workflows and tools, but unlimited capability. The workflow spans three major areas:

#### Common Plane

Shared capabilities across all RegSygnal work:

| Capability | Description |
|------------|-------------|
| **Project/Analysis Tracking** | Hierarchical view of projects, analyses, and tasks. Agents can publish and modify this view (with history and protection). |
| **AI-Extension Integration** | Theia AI structure connecting AI to extension capabilities—search info from extensions, read playbooks and technical instructions, read/modify content. |
| **Common Indexing & Diffing** | Merkle trees, semantic and smart chunking, embedding (Day 1), indexing (Day 1), RAG and GraphRAG (Day 2). May use Treesitter for code-aware parsing. |
| **Problems/Issues/Commits** | Git-style tracking of issues, commits, and graph visualization. |
| **Unlimited Graph Canvas** | Visualizing and interacting with diagrams, models, relationships. |
| **Plan & Claims Reviews** | UI for reviewing plans and claims with approval workflows. |
| **ISDA CDM Importer/Viewer** | Import and view ISDA Common Domain Model structures. |
| **ISDA DRR Importer/Viewer** | Import and view ISDA Digital Regulatory Reporting structures. |

#### Regulatory Analysis Extension

The core regulatory analysis workflow:

**Corpus Ingestion**
- Scraping tools with inventory to find, scrape, update, and publish inventories of external data
- Regulatory documents, industry body documents, schemas from Trade Repositories
- Packages from ISDA, ICMA, ISLA, FIA, AFME
- Non-financial examples: UK laws on drip pricing, CMA guidance

**Corpus Packaging**
- Adding documents and sources to a regulatory corpus
- Maintaining versions of document packs at points in time (at go-live, on first document update)
- Version control for regulatory snapshots

**Normalize**
- Connecting to normalization services (Docling local, LlamaParse, Unstructured)
- Consuming and storing results
- Publishing provenance, model, and settings for downstream use

**Normalize Analyse**
- Review document content with high-level reasoning over low-level classification proposals
- Contextual review, revision, request for rework

**Extract**
- Combination of ML and LLM agents to create factual inventories
- Document reference inventories, contents inventories
- Tables in PDFs moved to structured DB
- Same for Excel and other formats

**Extract Analyse**
- Validations, IR, cross-references, inconsistencies
- Undefined terms, missing import specificity
- Listing, typing, compiler-style analysis

**Claims Manager**
- Atomic claims made by inferring meaning from extracts and analysis
- Module for showing level of validation to other docs, external sources
- Claim lifecycle management

**Structured Doc Manager**
- Organization and analysis of XML, XSD, etc.
- Where XML is packaging for unstructured (like EU law), it gets re-assigned to appropriate handlers

**Modeller**
- Data models, system models, rule models, domain models, ontologies, ML models
- Anything used as tools and anything produced as outputs
- Design environment for both SaaS provider and consumer (provisioned by tenant/user)

**Domain Model Manager**
- Manages structured models (ISDA CDM, MS CDM) and unstructured
- Once created by Modeller or approved for direct external ingestion

**Domain Model Test**
- Creating and tracking test cases
- Universally applicable (e.g., SFTR test cases)

**Code Test**
- Creating and tracking code test cases
- Integration with implementation

#### Enterprise Analysis

Connecting regulatory requirements to enterprise systems:

**Systems in Scope Inventory**
- Logging deal stores, reference data systems, middleware, etc.
- Rich metadata about each system

**System Code Analysis**
- Relevant code from sources to help analyze upstream
- Code-aware parsing and analysis

**System Documentation Analysis**
- Analysis of system documentation
- Gap identification

**System Modelling and Mapping**
- Mapping to ISDA CDM for field outputs, event models, etc.
- Uses regulatory modelling to provide comparative for assessments

**Canonicalization**
- Draws in system modelling
- Creates canonical representations for cross-system comparison

### Core Capabilities Summary

#### Regulatory Intelligence

**Focus:** Monitoring, understanding, and tracking regulatory requirements

**Key Capabilities:**
- Regulatory document ingestion and parsing
- Requirement extraction and classification
- Change detection and impact analysis
- Regulatory timeline tracking
- Cross-regulation mapping (identifying overlaps and conflicts)

#### Reporting Validation

**Focus:** Ensuring regulatory reports are accurate and complete

**Key Capabilities:**
- Report schema validation
- Data quality checks
- Reconciliation against source systems
- Exception identification and tracking
- Submission audit trails

#### Compliance Modelling

**Focus:** Transforming regulatory text into executable logic

**Key Capabilities:**
- Requirement decomposition (breaking regulations into testable assertions)
- Ambiguity capture and resolution tracking
- Logic modelling (expressing requirements as verifiable rules)
- Implementation mapping (linking requirements to controls)
- Gap analysis (identifying unmet requirements)

### Target Regulations

RegSygnal is designed to handle complex regulatory frameworks including:

| Regulation | Domain | Complexity |
|------------|--------|------------|
| EMIR | Derivatives reporting | High |
| MiFID II | Markets and trading | High |
| SFTR | Securities financing | Medium |
| Basel III | Capital requirements | High |
| BCBS 239 | Risk data aggregation | Medium |

### Who Uses RegSygnal

| Role | Primary Use Case |
|------|------------------|
| **Compliance Officer** | Requirement tracking, gap analysis |
| **Regulatory Analyst** | Interpretation, modelling |
| **Technology Lead** | Implementation mapping |
| **Internal Audit** | Control verification |
| **Risk Manager** | Regulatory risk assessment |

### Current Status

**Phase:** Planning  
**Focus:** Architecture and initial regulatory domain models  
**Next:** Pilot with selected regulatory framework

> **ADR Note (RegSygnal Architecture):** The extension-based architecture (Common Plane + Regulatory Analysis Extension + Enterprise Analysis) may benefit from splitting into separate extensions. ADR needed for: extension boundaries, shared vs. separate capabilities, Theia AI integration patterns, ISDA CDM/DRR integration approach.

---

## Implementation Packages

Both PropSygnal and RegSygnal are available in two implementation packages that reflect different organizational priorities:

### Accelerate Package

**For:** High-velocity expansion organizations  
**Focus:** Throughput and Deal Flow  
**Philosophy:** "Capture opportunity"

**Characteristics:**
- Adaptive, fluid ontology that evolves with the business
- Emphasis on speed of insight over exhaustive verification
- Streamlined approval workflows
- Optimized for volume processing

**Ideal For:**
- Growing investment platforms
- Active acquirers
- Organizations prioritizing market opportunity

### Preserve Package

**For:** Institutional asset management organizations  
**Focus:** Auditability and Risk Control  
**Philosophy:** "Defend the asset"

**Characteristics:**
- Rigid, standard-compliant ontology
- Emphasis on verification and evidence
- Comprehensive approval workflows
- Optimized for audit readiness

**Ideal For:**
- Institutional investors
- Regulated entities
- Organizations prioritizing governance

---

## Product Roadmap Summary

### PropSygnal

| Phase | Focus | Timeline |
|-------|-------|----------|
| **Phase 1 (Current)** | Debt & Credit MVP | Q1 2026 |
| **Phase 2** | Asset Management & Portfolio Scale | Q2 2026 |
| **Phase 3** | Investment & Acquisitions | Q3 2026 |
| **Phase 4** | Development & Project Management | Q4 2026 |
| **Phase 5** | Property Management | 2027 |
| **Phase 6** | Ecosystem & Integrations | 2027 |

### RegSygnal

| Phase | Focus | Timeline |
|-------|-------|----------|
| **Phase 1** | Architecture & Domain Models | Q2 2026 |
| **Phase 2** | Pilot Regulatory Framework | Q3 2026 |
| **Phase 3** | Reporting Validation | Q4 2026 |
| **Phase 4** | Full Compliance Modelling | 2027 |

---

**Related Documents:**
- [Executive Summary](01_EXECUTIVE_SUMMARY.md) - Quick overview
- [Vision & Thesis](02_VISION.md) - Strategic context
- [Platform Modules](03_PLATFORM.md) - Core capabilities
- [Users & Personas](05_USERS.md) - Who we serve
- [Roadmap](07_ROADMAP.md) - Detailed delivery plan
