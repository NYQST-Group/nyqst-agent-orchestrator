# NYQST PRD Document Suite

**Product:** NYQST - Deterministic Agentic Infrastructure for Commercial Intelligence  
**Company:** NYQST AI Limited  
**Version:** 1.0  
**Last Updated:** 2026-01-25  
**Status:** Living Document

---

## Document Architecture

This PRD suite provides comprehensive product documentation for the NYQST platform and its product variants (PropSygnal, RegSygnal). Documents are organized by purpose and audience, designed to be read independently or as a complete set.

### Document Map

```
docs/
├── prd/                         <- Product Requirements (what & why)
│   ├── 00_INDEX.md              <- You are here (navigation guide)
│   ├── 01_EXECUTIVE_SUMMARY.md  <- Start here (2-page overview for all audiences)
│   ├── 02_VISION.md             <- Strategic thesis, market position, why NYQST exists
│   ├── 03_PLATFORM.md           <- NYQST Platform modules and core capabilities
│   ├── 04_PRODUCTS.md           <- Product variants: PropSygnal & RegSygnal
│   ├── 05_USERS.md              <- User personas across products
│   ├── 06_ARCHITECTURE.md       <- Technical architecture and design principles
│   ├── 07_ROADMAP.md            <- Phased delivery plan, current priorities
│   ├── 08_METRICS.md            <- Success metrics, KPIs, acceptance criteria
│   ├── 09_RISKS.md              <- Risks, dependencies, assumptions, mitigations
│   └── 10_APPENDIX.md           <- Glossary, references, supporting materials
│
├── planning/                    <- Execution Planning (when & how)
│   └── PLATFORM_FOUNDATION.md   <- Core infrastructure build sequence
│
├── adr/                         <- Architecture Decision Records (why this way)
│   ├── README.md                <- ADR index and pending decisions
│   └── 000-TEMPLATE.md          <- Template for new ADRs
│
└── research/                    <- Research & Analysis
    └── AGENTIC_SYSTEMS_RESEARCH.md <- Agentic systems ecosystem research
```

### Reading Guide by Audience

| Audience | Start With | Then Read | Reference As Needed |
|----------|------------|-----------|---------------------|
| **Executives / Investors** | 01_EXECUTIVE_SUMMARY | 02_VISION, 07_ROADMAP | 08_METRICS |
| **Product Team** | 01_EXECUTIVE_SUMMARY | 03_PLATFORM, 04_PRODUCTS, 05_USERS | 07_ROADMAP |
| **Engineering Team** | 01_EXECUTIVE_SUMMARY | 06_ARCHITECTURE, 03_PLATFORM | 07_ROADMAP |
| **Design Team** | 01_EXECUTIVE_SUMMARY | 05_USERS, 03_PLATFORM | 06_ARCHITECTURE |
| **Sales / GTM** | 01_EXECUTIVE_SUMMARY | 02_VISION, 04_PRODUCTS | 05_USERS |
| **New Team Members** | 01_EXECUTIVE_SUMMARY | All documents in order | 10_APPENDIX |

### Document Purposes

| Document | Purpose | Update Frequency |
|----------|---------|------------------|
| **00_INDEX** | Navigation and document architecture | When structure changes |
| **01_EXECUTIVE_SUMMARY** | Quick orientation for any stakeholder | Quarterly or major pivots |
| **02_VISION** | Strategic thesis and long-term direction | Annually or major pivots |
| **03_PLATFORM** | Platform modules and capabilities | Each release cycle |
| **04_PRODUCTS** | PropSygnal and RegSygnal specifics | Each release cycle |
| **05_USERS** | Who we serve and their needs | When personas evolve |
| **06_ARCHITECTURE** | How the system works | When architecture evolves |
| **07_ROADMAP** | When we're building what | Monthly |
| **08_METRICS** | How we measure success | Each release cycle |
| **09_RISKS** | What could go wrong and mitigations | Monthly |
| **10_APPENDIX** | Supporting materials and glossary | As needed |

---

## Product Hierarchy

```
NYQST AI Limited
    |
    +-- NYQST Platform (Infrastructure Layer)
    |       |
    |       +-- Research Module
    |       +-- Document Management Module
    |       +-- Analysis Module
    |       +-- Modelling Module
    |       +-- Knowledge & Domain Module
    |       +-- Organisational Insight Module
    |
    +-- Product Variants
            |
            +-- PropSygnal (Real Estate)
            |       +-- Investment & Acquisitions
            |       +-- Development & Project Management
            |       +-- Asset Management
            |       +-- Debt & Credit
            |       +-- Property Management
            |
            +-- RegSygnal (Regulatory)
                    +-- Regulatory Intelligence
                    +-- Reporting Validation
                    +-- Compliance Modelling
```

---

## ADR Notes Approach

This PRD suite includes **ADR Notes** embedded within relevant documents. These notes flag architectural decisions that require deeper exploration and will be developed into full Architecture Decision Records (ADRs) during implementation.

**ADR Notes are found in:**
- `03_PLATFORM.md` - Core infrastructure decisions (Session/VM, Workflow Engine, Indexing, Classification, Domain Model Library, CDM Integration, Background Copilot)
- `04_PRODUCTS.md` - Product-specific decisions (RegSygnal Architecture)
- `06_ARCHITECTURE.md` - UI and integration decisions (Research UI, Workbench UI, Analysis Canvas, Cross-Session Analysis, MCP Marketplace, Knowledge Architecture, Playbook Architecture)

**ADR Notes format:**
> **ADR Note (Topic):** Brief description of decision needed and key questions to address.

ADRs will be created in `docs/adr/` when architectural decisions are made during implementation. See [ADR README](../adr/README.md) for the full list of pending ADRs.

---

## Planning Documents

Planning documents bridge the PRD (what to build) with execution (how to build it).

| Document | Purpose | Audience |
|----------|---------|----------|
| [Platform Foundation](../planning/PLATFORM_FOUNDATION.md) | Dependency-sequenced core infrastructure build order | Engineering, Product |
| Epic Backlog (future) | Prioritized product features for PropSygnal/RegSygnal | Product, Engineering |

**Key Distinction:**
- **Platform Foundation** - Order driven by technical dependencies (all required, just sequenced)
- **Epic Backlog** - Order driven by business value (prioritization frameworks apply)

---

## Relationship to Other Documentation

This PRD suite is the authoritative source for **what we're building and why**. It relates to other documentation as follows:

### Canonical References

| Document | Location | Purpose | Relationship to PRD |
|----------|----------|---------|---------------------|
| **Platform Reference Design** | `docs/PLATFORM_REFERENCE_DESIGN.md` | Detailed technical architecture | PRD 06_ARCHITECTURE summarizes; Reference Design provides depth |
| **Index Contract** | `docs/INDEX_CONTRACT.md` | Indexing system contract | Technical specification referenced by PRD |
| **Research Synthesis** | `docs/RESEARCH_SYNTHESIS.md` | UI/UX research findings | Informs PRD decisions |
| **ADRs** | `docs/adr/` (future) | Architecture Decision Records | Detailed decisions flagged by ADR Notes in PRD |

### External Documentation (Confluence)

| Space | Purpose |
|-------|---------|
| **Platform** | NYQST platform thesis, method, components |
| **PropSygnal** | Product-specific documentation, MVP scope, roadmap |
| **Technical** | Architecture, MCP layer, infrastructure |

### Supporting Materials in Repository

| Location | Contents |
|----------|----------|
| `scenarios/personas/` | Detailed user persona documentation |
| `scenarios/acquisition/` | Acquisition workflow scenarios |
| `scenarios/asset-management/` | Asset management workflow scenarios |
| `schemas/` | JSON schemas for domain primitives |
| `docs/analysis/` | Historical analysis and decision records |
| `requirements/` | Strategy documents and requirements |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-25 | Initial | Initial PRD suite creation |

---

## Quick Links

- [Executive Summary](01_EXECUTIVE_SUMMARY.md) - Start here
- [Vision & Thesis](02_VISION.md) - Why NYQST exists
- [Platform Modules](03_PLATFORM.md) - What we're building
- [Products](04_PRODUCTS.md) - PropSygnal & RegSygnal
- [Users & Personas](05_USERS.md) - Who we serve
- [Architecture](06_ARCHITECTURE.md) - How it works
- [Roadmap](07_ROADMAP.md) - When we're building it
- [Metrics](08_METRICS.md) - How we measure success
- [Risks](09_RISKS.md) - What could go wrong
- [Appendix](10_APPENDIX.md) - Glossary and references
