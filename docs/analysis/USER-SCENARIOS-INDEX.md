# CRE Intelligence Platform: User Scenarios and Requirements

*Date: 2026-01-23*
*Branch: claude/cre-intelligence-workflows-8y9MD*
*Status: Research complete, wedge strategy defined, ready to build*

---

## Purpose

This repository contains user scenarios, research, and requirements for a commercial real estate intelligence platform. The work grounds the platform design in real workflows, industry standards, and practical user needs—from acquisition through asset management.

**Critical Update:** After completing detailed scenarios, we identified that 80% of the work is domain-agnostic. The real value is in **five universal primitives** that can be configured for CRE, legal, insurance, or any document-heavy domain. See [Critical Analysis](requirements/CRITICAL-ANALYSIS.md) and [Universal Abstractions](requirements/UNIVERSAL-ABSTRACTIONS.md).

---

## Navigation

### 1. Research Inputs

External research gathered to inform scenarios and requirements.

| Document | Description | Status |
|----------|-------------|--------|
| [RICS Standards Summary](research/rics/rics-standards-summary.md) | RICS Red Book, due diligence, ESG, and AI guidance | Complete |
| [INREV Guidelines Summary](research/inrev/inrev-guidelines-summary.md) | INREV reporting, data standards, NAV, governance | Complete |
| [Acquisition Workflows](research/cre-workflows/acquisition-workflows.md) | Detailed acquisition workflow research | Complete |
| [Asset Management Workflows](research/cre-workflows/asset-management-workflows.md) | Detailed asset management workflow research | Complete |
| [AI in CRE Landscape](research/ai-tooling/ai-cre-landscape.md) | Current AI tools, successes, failures | Complete |
| [AI Adoption Failures](research/ai-tooling/ai-adoption-failures.md) | Why 95% of AI projects fail | Complete |
| [Trust UX Patterns](research/ai-tooling/trust-ux-patterns.md) | Calibrated trust, verification UX patterns | Complete |
| [LegalTech Patterns](research/cross-domain/legaltech-patterns.md) | CLM architectures, trust building in legal | Complete |
| [InsurTech Patterns](research/cross-domain/insurtech-patterns.md) | Claims processing, evidence patterns | Complete |
| [Event-Driven Patterns](research/architecture/event-driven-patterns.md) | Temporal.io, deadline management | Complete |
| [Document Graph Patterns](research/architecture/document-graph-patterns.md) | Relationship models, gap detection | Complete |

---

### 2. User Personas

Understanding of key users and their perspectives.

| Document | Description |
|----------|-------------|
| [CRE User Personas](scenarios/personas/cre-user-personas.md) | 7 detailed personas from analyst to tenant |
| [Stakeholder Perspectives](scenarios/journeys/stakeholder-perspectives.md) | Cross-stakeholder analysis including investors, lenders, advisors |

---

### 3. Workflow Scenarios

Detailed workflow analysis with AI intervention points.

#### Acquisition Phase

| Document | Workflow | Key Insight |
|----------|----------|-------------|
| [Deal Sourcing & Screening](scenarios/acquisition/01-deal-sourcing-screening.md) | IM triage, mandate fit, initial analysis | AI can reduce 45min → 10min per deal |
| [Due Diligence](scenarios/acquisition/02-due-diligence-workflow.md) | Legal, technical, financial DD | Lease abstraction: 3hrs → 30min per lease |
| [Transaction & Handover](scenarios/acquisition/03-transaction-closing-handover.md) | Execution, closing, operational handover | Critical knowledge transfer gap |
| [Debt & Financing](scenarios/acquisition/04-debt-financing-workflow.md) | Loan origination, covenant monitoring | Covenant breach prevention high value |

#### Asset Management Phase

| Document | Workflow | Key Insight |
|----------|----------|-------------|
| [Lease Event Management](scenarios/asset-management/01-lease-event-management.md) | Break options, rent reviews, renewals | Zero tolerance for missed deadlines |
| [Investor Reporting](scenarios/asset-management/02-investor-reporting.md) | Quarterly reports, NAV, ESG | 3-4 weeks → 1-2 weeks possible |

---

### 4. Requirements & Strategy

Synthesized requirements and build strategy.

| Document | Description |
|----------|-------------|
| [Research Synthesis](requirements/RESEARCH-SYNTHESIS.md) | **START HERE** — Consolidated findings from all research |
| [What to Build First](requirements/WHAT-TO-BUILD-FIRST.md) | Wedge strategy: "Never Miss a Critical Date" |
| [Universal Abstractions](requirements/UNIVERSAL-ABSTRACTIONS.md) | The five universal primitives |
| [Critical Analysis](requirements/CRITICAL-ANALYSIS.md) | Where we missed the point |
| [AI Value Opportunities](requirements/ai-specific/ai-value-opportunities.md) | Prioritized AI intervention points |
| [Research Consolidation Gates](requirements/research-consolidation-gates.md) | Framework for research validation |

### 5. Schemas (Ready for Implementation)

Domain-agnostic primitive schemas and CRE-specific configurations.

| Schema | Description |
|--------|-------------|
| [Document Schema](schemas/document.schema.json) | Document Intelligence primitive |
| [Event Schema](schemas/event.schema.json) | Event Management primitive |
| [Claim Schema](schemas/claim.schema.json) | Claim/Decision primitive |
| [UK Lease Config](schemas/cre/uk-lease.config.json) | CRE extraction schema |
| [Lease Events Config](schemas/cre/lease-events.config.json) | CRE event type configurations |

---

## Critical Meta-Analysis

After completing detailed scenarios, we identified fundamental gaps. See full analysis in:
- [Critical Analysis](requirements/CRITICAL-ANALYSIS.md) — Where we missed the point
- [Universal Abstractions](requirements/UNIVERSAL-ABSTRACTIONS.md) — Primitives that replace scenarios

### Key Realizations

| What We Thought | What's Actually True |
|-----------------|----------------------|
| CRE needs custom features | CRE needs configured generic primitives |
| Extraction is the hard part | Relationships, gaps, and interpretation are the value |
| Build for accuracy | Build for adoption (95% AI projects fail on adoption) |
| Scenarios define requirements | Primitives define requirements; scenarios are config |

### The Five Universal Primitives

Every CRE workflow (and legal, insurance, compliance) is a composition of:

1. **Document Intelligence** — Extract facts, relate documents, detect gaps
2. **Entity Resolution** — Cross-document identity (tenants, properties, parties)
3. **Event Management** — Deadlines, alerts, actions, outcomes
4. **Claim/Decision** — Interpretation + evidence → recorded judgment
5. **Generation/Review** — Draft → review → approve → publish

**Implication:** A 20-page workflow scenario becomes 20 lines of configuration.

---

## Key Findings Summary

### Where AI Adds Most Value (Tier 1: Risk Reduction)

1. **Lease critical date monitoring** — Zero tolerance for missed breaks/reviews
2. **Covenant compliance monitoring** — Prevent default triggers
3. **DD red flag detection** — Catch what humans miss
4. **Insurance/certificate expiry tracking** — Compliance protection

### Where AI Saves Most Time (Tier 3: Efficiency)

1. **Document data extraction** — 50-90% time savings
2. **Report generation** — First drafts automated
3. **Search across documents** — Instant vs hours
4. **Data normalization** — Eliminate re-keying

### Critical AI Trust Requirements

1. **Never confidently wrong** — Confidence scoring, human-in-the-loop
2. **Source citation always** — Every extraction linked to document/page
3. **Audit trail complete** — All actions logged
4. **Fail safely** — Flag uncertainty, don't guess

### Key Industry Standards to Support

- **RICS Red Book** — Valuation standards, ESG requirements, AI guidance
- **INREV Guidelines** — Reporting, NAV, data standards (SDDS)
- **GRESB** — ESG benchmarking
- **SFDR/EU Taxonomy** — Regulatory ESG disclosure

---

## Stakeholder Summary

| Stakeholder | Primary Need | AI Opportunity |
|-------------|--------------|----------------|
| **Investment Analyst** | Faster data extraction, fewer errors | High — routine work automation |
| **Investment Director** | Better synthesis, risk visibility | High — decision support |
| **Asset Manager** | No missed deadlines, unified data | Very High — monitoring/alerting |
| **Fund Manager** | Real-time portfolio view | Medium — aggregation |
| **Lender** | Covenant monitoring, consistent reporting | High — automation |
| **Legal Advisor** | Faster lease review | High — extraction assistance |
| **Property Manager** | Compliance tracking, reporting | Medium — efficiency |

---

## Lifecycle Coverage

```
ACQUISITION                          ASSET MANAGEMENT
───────────────────────────────────────────────────────────────→

┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  Deal   │   │   Due   │   │  Trans  │   │  Ops &  │   │ Report  │
│Sourcing │ → │Diligence│ → │ Close   │ → │Leasing  │ → │   &     │
│         │   │         │   │Handover │   │         │   │  Exit   │
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
     │             │             │             │             │
     ▼             ▼             ▼             ▼             ▼
  [Scenario]   [Scenario]   [Scenario]   [Scenario]   [Scenario]
     01            02            03           01/02        Future

  ┌─────────────────────────────────────────────────────────────┐
  │                   DEBT / FINANCING                          │
  │         Origination → Monitoring → Refinance                │
  │                     [Scenario 04]                           │
  └─────────────────────────────────────────────────────────────┘
```

---

## Gate Framework

Research and requirements progress through consolidation gates:

| Gate | Purpose | Status |
|------|---------|--------|
| Gate 0 | Research collection complete | ✅ Complete |
| Gate 1 | Workflow validation | Ready for review |
| Gate 2 | AI opportunity assessment | Ready for review |
| Gate 3 | Requirements definition | In progress |
| Gate 4 | Architecture alignment | Pending |

---

## Repository Structure

```
/
├── USER-SCENARIOS-INDEX.md          ← This file (start here)
├── README.md                        ← Original repo README
│
├── research/                        ← External research inputs
│   ├── rics/                        ← RICS standards research
│   ├── inrev/                       ← INREV guidelines research
│   ├── cre-workflows/               ← Workflow research
│   ├── ai-tooling/                  ← AI landscape, adoption failures, trust UX
│   ├── cross-domain/                ← LegalTech, InsurTech patterns
│   └── architecture/                ← Event-driven, document graph patterns
│
├── scenarios/                       ← User scenarios
│   ├── acquisition/                 ← Acquisition phase workflows
│   ├── asset-management/            ← Asset management workflows
│   ├── personas/                    ← User personas
│   └── journeys/                    ← Stakeholder journeys
│
├── schemas/                         ← JSON schemas for primitives
│   ├── document.schema.json         ← Document Intelligence primitive
│   ├── event.schema.json            ← Event Management primitive
│   ├── claim.schema.json            ← Claim/Decision primitive
│   └── cre/                         ← CRE-specific configurations
│       ├── uk-lease.config.json     ← UK commercial lease extraction
│       └── lease-events.config.json ← Lease event types
│
└── requirements/                    ← Strategy and requirements
    ├── RESEARCH-SYNTHESIS.md        ← Consolidated research findings
    ├── WHAT-TO-BUILD-FIRST.md       ← Wedge strategy
    ├── UNIVERSAL-ABSTRACTIONS.md    ← Five universal primitives
    ├── CRITICAL-ANALYSIS.md         ← Gap analysis
    └── ai-specific/                 ← AI-specific requirements
```

---

## Next Steps: The 30-Day Build Plan

**Stop designing. Start building.**

### Week 1: Extraction POC
- [ ] Build PDF/Word/scanned document ingestion
- [ ] Train/configure date extraction on 50 sample leases
- [ ] Measure accuracy: target 85%
- [ ] Build basic verification UI

### Week 2: Event Engine
- [ ] Implement event schema (simplified for dates only)
- [ ] Build deadline calculation
- [ ] Build email alert system
- [ ] Build dashboard view

### Week 3: Integration
- [ ] Connect extraction → event engine
- [ ] End-to-end: upload → extract → alert
- [ ] Add verification UX (click to source)
- [ ] Bug fixes, UX polish

### Week 4: User Testing
- [ ] Get 3-5 real users with real leases
- [ ] Watch them use it
- [ ] Learn what's broken, what's missing

**At end of 30 days:** Either we have something users want, or we learn why not.

---

## Contributing

This is a working document. To contribute:
1. Add research to `/research/` with sources cited
2. Update scenarios with real-world validation
3. Propose requirements with traceability to workflows/pain points

---

*Last updated: 2026-01-23*
