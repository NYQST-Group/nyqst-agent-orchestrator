# Research Consolidation Gates: Framework

*Date: 2026-01-23*
*Purpose: Ensure systematic consolidation of research into actionable requirements*

---

## Overview

This document defines gates for consolidating research inputs, validating findings, and translating them into platform requirements. Each gate has:
- **Entry criteria:** What must be complete before gate review
- **Gate activities:** What happens during the gate
- **Exit criteria:** What must be confirmed to proceed
- **Outputs:** What artifacts are produced

---

## Gate 0: Research Collection Complete

### Purpose
Confirm that sufficient research has been gathered across all required domains.

### Entry Criteria

| Domain | Required Research | Status |
|--------|-------------------|--------|
| **Industry Standards** | | |
| RICS guidance and standards | Red Book, professional standards, ESG guidance | Pending |
| INREV guidelines | Reporting, governance, data standards | Pending |
| Other bodies (AREF, ULI, CREFC) | Relevant guidance | Optional |
| **Workflow Research** | | |
| Acquisition workflows | Sourcing → DD → execution → close | Pending |
| Asset management workflows | Operations → reporting → value creation | Pending |
| Debt/financing workflows | Origination → monitoring → refinancing | Pending |
| Disposition workflows | Strategy → marketing → execution | Future |
| **Technology Landscape** | | |
| Current AI/ML in CRE | Tools, adoption, successes, failures | Pending |
| PropTech landscape | Relevant adjacent tools | Pending |
| Enterprise requirements | Security, compliance, integration | Pending |
| **Stakeholder Research** | | |
| User interviews (if conducted) | Primary research | If available |
| Published case studies | Secondary research | If available |
| Competitive analysis | What exists today | Pending |

### Gate Activities

1. Review completeness of research collection
2. Identify gaps requiring additional research
3. Assess quality and reliability of sources
4. Flag conflicting information for resolution

### Exit Criteria

- [ ] All required domains have research collected
- [ ] Sources documented with URLs/citations
- [ ] Gap analysis complete
- [ ] Research stored in `/research/` folders

### Outputs

- Research inventory with status
- Gap analysis document
- Prioritized additional research needs

---

## Gate 1: Workflow Validation

### Purpose
Confirm that documented workflows accurately reflect reality and are comprehensive.

### Entry Criteria

- Workflow scenarios drafted
- Stakeholder perspectives documented
- Pain points identified

### Gate Activities

1. **Reality check:**
   - Do workflows match how work actually happens?
   - Are edge cases and exceptions captured?
   - Are workarounds and informal processes noted?

2. **Completeness check:**
   - All stages of lifecycle covered?
   - All key stakeholders represented?
   - All document types identified?

3. **Pain point validation:**
   - Are these the real pain points?
   - Severity accurately assessed?
   - Root causes identified?

### Exit Criteria

- [ ] Workflows validated against industry research
- [ ] Stakeholder perspectives cross-referenced
- [ ] Pain points prioritized by severity/frequency
- [ ] No major gaps identified

### Outputs

- Validated workflow documentation
- Pain point priority matrix
- Stakeholder sign-off checklist

---

## Gate 2: AI Opportunity Assessment

### Purpose
Identify and prioritize AI intervention points based on value, feasibility, and risk.

### Entry Criteria

- Validated workflows
- Pain points prioritized
- Technology landscape understood

### Gate Activities

1. **Value assessment:**
   - Time savings quantified
   - Error reduction potential
   - Decision quality improvement
   - Competitive advantage

2. **Feasibility assessment:**
   - Technical complexity
   - Data availability
   - Integration requirements
   - Current technology capability

3. **Risk assessment:**
   - Professional liability implications
   - Error consequences
   - Adoption barriers
   - Regulatory considerations

4. **Prioritization:**
   - Value / Feasibility / Risk matrix
   - Quick wins identification
   - Foundation capabilities required
   - Long-term vision alignment

### Exit Criteria

- [ ] AI opportunities mapped to workflows
- [ ] Prioritization framework applied
- [ ] Foundation capabilities identified
- [ ] Risk mitigations documented

### Outputs

- AI opportunity matrix
- Prioritized capability roadmap
- Risk and mitigation register
- Foundation architecture requirements

---

## Gate 3: Requirements Definition

### Purpose
Translate validated workflows and AI opportunities into platform requirements.

### Entry Criteria

- AI opportunities prioritized
- Platform reference design available
- Stakeholder perspectives understood

### Gate Activities

1. **Functional requirements:**
   - User stories per persona
   - Acceptance criteria
   - Data requirements
   - Integration requirements

2. **Non-functional requirements:**
   - Performance (latency, throughput)
   - Security (access control, audit)
   - Compliance (data residency, retention)
   - Scalability (users, data volume)

3. **AI-specific requirements:**
   - Accuracy requirements per use case
   - Confidence thresholds
   - Human-in-the-loop requirements
   - Explainability requirements

4. **Integration requirements:**
   - External systems
   - Data sources
   - User workflows

### Exit Criteria

- [ ] Requirements documented per priority area
- [ ] Requirements traceable to workflows/pain points
- [ ] AI requirements include safety/accuracy specs
- [ ] Integration requirements mapped

### Outputs

- Requirements documentation
- Traceability matrix
- AI safety requirements
- Integration specifications

---

## Gate 4: Architecture Alignment

### Purpose
Confirm requirements align with platform architecture and identify gaps.

### Entry Criteria

- Requirements defined
- Platform reference design current
- Technical constraints understood

### Gate Activities

1. **Architecture fit assessment:**
   - Do requirements fit reference architecture?
   - Are new components needed?
   - Are modifications required?

2. **Gap analysis:**
   - Missing capabilities in architecture
   - Missing specifications
   - Missing integration points

3. **Constraint identification:**
   - Technical constraints
   - Resource constraints
   - Timeline constraints

### Exit Criteria

- [ ] Requirements mapped to architecture
- [ ] Gaps identified and documented
- [ ] Architecture updates proposed
- [ ] Constraints documented

### Outputs

- Architecture mapping
- Gap analysis
- Proposed architecture updates
- Constraint register

---

## Research Domain Consolidation Templates

### Industry Standards Consolidation

**For each standard/guidance document:**

```markdown
## [Standard Name]

### Source
- Organization:
- Document:
- Version/Date:
- URL:

### Scope
- What does it cover?
- Who is it mandatory for?
- Who typically follows it voluntarily?

### Key Requirements
1. [Requirement 1]
2. [Requirement 2]
...

### Documentation/Evidence Requirements
- What records must be kept?
- For how long?
- In what format?

### Implications for Platform
- Features required:
- Data to capture:
- Processes to support:

### Gaps in Current Draft
- What we haven't addressed:
```

---

### Workflow Consolidation

**For each workflow:**

```markdown
## [Workflow Name]

### Overview
- Stage in lifecycle:
- Primary persona:
- Secondary personas:
- Typical duration:

### Steps
| Step | Activities | Documents | Systems | Pain Points |
|------|------------|-----------|---------|-------------|
| 1    |            |           |         |             |
...

### Information Flow
- Inputs:
- Outputs:
- Handoffs:

### Pain Points (Prioritized)
| Pain Point | Severity | Frequency | Root Cause | AI Addressable? |
|------------|----------|-----------|------------|-----------------|
...

### AI Opportunities
| Opportunity | Value | Feasibility | Risk | Priority |
|-------------|-------|-------------|------|----------|
...

### Requirements Derived
- Functional:
- Non-functional:
- AI-specific:
```

---

### Technology Landscape Consolidation

**For each tool/vendor:**

```markdown
## [Tool/Vendor Name]

### Overview
- Category:
- Primary function:
- Target users:
- Deployment model:

### Capabilities
- What it does well:
- Limitations:

### Market Position
- Market share:
- Key competitors:
- Differentiation:

### Integration
- APIs available:
- Data formats:
- Common integrations:

### Lessons Learned
- Success patterns:
- Failure patterns:
- Adoption challenges:

### Implications for Platform
- Compete with:
- Integrate with:
- Learn from:
```

---

## Consolidation Meeting Framework

### Research Review Meeting (Gate 0)

**Agenda:**
1. Research inventory review (15 min)
2. Quality assessment (15 min)
3. Gap identification (15 min)
4. Additional research needs (15 min)

**Participants:**
- Research lead
- Domain experts
- Product lead

---

### Workflow Validation Meeting (Gate 1)

**Agenda:**
1. Workflow walkthrough (30 min per workflow)
2. Reality check discussion (15 min per workflow)
3. Pain point validation (15 min per workflow)
4. Gap identification (15 min)

**Participants:**
- Industry expert / practitioner
- Workflow researcher
- Product lead

---

### AI Opportunity Assessment Meeting (Gate 2)

**Agenda:**
1. Opportunity inventory review (20 min)
2. Value assessment (30 min)
3. Feasibility assessment (30 min)
4. Risk assessment (20 min)
5. Prioritization (20 min)

**Participants:**
- Product lead
- Technical lead
- AI/ML lead
- Industry expert

---

### Requirements Review Meeting (Gate 3)

**Agenda:**
1. Requirements walkthrough (per priority area)
2. Acceptance criteria review
3. Gap identification
4. Prioritization confirmation

**Participants:**
- Product lead
- Technical lead
- UX lead
- Stakeholder representative

---

## Research Quality Criteria

### Primary Sources (Higher weight)
- Industry body publications (RICS, INREV)
- Regulatory documents
- Academic research
- Practitioner interviews

### Secondary Sources (Medium weight)
- Industry press
- Vendor white papers
- Conference presentations
- Consultant reports

### Tertiary Sources (Lower weight)
- Blog posts
- Social media
- Marketing materials

### Quality Indicators
- Recency (prefer <2 years old)
- Authority (recognized experts/bodies)
- Objectivity (limited commercial bias)
- Specificity (CRE-focused, not generic)

---

## Artifact Storage Structure

```
/research/
├── rics/
│   ├── rics-standards-summary.md
│   └── sources/
├── inrev/
│   ├── inrev-guidelines-summary.md
│   └── sources/
├── cre-workflows/
│   ├── acquisition-workflows.md
│   ├── asset-management-workflows.md
│   └── sources/
├── ai-tooling/
│   ├── ai-cre-landscape.md
│   └── sources/
└── consolidation/
    ├── research-inventory.md
    ├── gap-analysis.md
    └── quality-assessment.md

/scenarios/
├── acquisition/
│   ├── 01-deal-sourcing-screening.md
│   ├── 02-due-diligence-workflow.md
│   ├── 03-transaction-closing-handover.md
│   └── 04-debt-financing-workflow.md
├── asset-management/
│   ├── 01-lease-event-management.md
│   └── 02-investor-reporting.md
├── personas/
│   └── cre-user-personas.md
└── journeys/
    └── stakeholder-perspectives.md

/requirements/
├── functional/
│   ├── [priority-area]-requirements.md
│   └── ...
├── non-functional/
│   ├── security-requirements.md
│   ├── performance-requirements.md
│   └── ...
├── ai-specific/
│   ├── accuracy-requirements.md
│   ├── safety-requirements.md
│   └── ...
└── research-consolidation-gates.md
```

---

*This gate framework ensures systematic progression from research to requirements while maintaining traceability and quality.*
