# CRE Intelligence Platform: User Scenarios and Requirements

*Date: 2026-01-23*
*Branch: user-scenarios*
*Status: Initial research and scenario development complete*

---

## Purpose

This repository contains user scenarios, research, and requirements for a commercial real estate intelligence platform. The work grounds the platform design in real workflows, industry standards, and practical user needs—from acquisition through asset management.

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

### 4. Requirements

Synthesized requirements from scenarios and research.

| Document | Description |
|----------|-------------|
| [AI Value Opportunities](requirements/ai-specific/ai-value-opportunities.md) | Prioritized AI intervention points, trust requirements, safety |
| [Research Consolidation Gates](requirements/research-consolidation-gates.md) | Framework for validating and consolidating research |

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
├── USER-SCENARIOS-INDEX.md          ← This file
├── README.md                        ← Original repo README
│
├── research/                        ← External research inputs
│   ├── rics/                        ← RICS standards research
│   ├── inrev/                       ← INREV guidelines research
│   ├── cre-workflows/               ← Workflow research
│   ├── ai-tooling/                  ← AI landscape research
│   └── market-analysis/             ← Market research (future)
│
├── scenarios/                       ← User scenarios
│   ├── acquisition/                 ← Acquisition phase workflows
│   ├── asset-management/            ← Asset management workflows
│   ├── personas/                    ← User personas
│   └── journeys/                    ← Stakeholder journeys
│
└── requirements/                    ← Synthesized requirements
    ├── functional/                  ← Functional requirements (future)
    ├── non-functional/              ← Non-functional requirements (future)
    ├── ai-specific/                 ← AI-specific requirements
    └── research-consolidation-gates.md  ← Gate framework
```

---

## Next Steps

### Immediate (Gate 1: Validation)
- [ ] Review workflows with industry practitioners
- [ ] Validate pain point priorities
- [ ] Identify missing edge cases

### Short-term (Gate 2: Prioritization)
- [ ] Score AI opportunities on value/feasibility/risk
- [ ] Identify MVP feature set
- [ ] Define success metrics

### Medium-term (Gate 3: Requirements)
- [ ] Write detailed functional requirements
- [ ] Define accuracy requirements per use case
- [ ] Specify integration requirements

---

## Contributing

This is a working document. To contribute:
1. Add research to `/research/` with sources cited
2. Update scenarios with real-world validation
3. Propose requirements with traceability to workflows/pain points

---

*Last updated: 2026-01-23*
