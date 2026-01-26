# NYQST: Users & Personas

**Product:** NYQST - Deterministic Agentic Infrastructure for Commercial Intelligence  
**Company:** NYQST AI Limited  
**Version:** 1.0  
**Last Updated:** 2026-01-25

---

## Overview

This document defines the key user personas for the NYQST platform and its product variants. Understanding who we serve, what they need, and how they work is essential to building products that deliver real value.

The personas are organized by product variant, with common themes and requirements identified across all users.

---

## Target Organizations

### Primary Target: Mid-Cap Enterprises with Fiduciary Responsibilities

NYQST is built for organizations that:

- Have fiduciary responsibilities requiring auditability and governance
- Prioritize margin and agility over massive engineering headcount
- Need operational certainty from their technology investments
- Want to own their truth rather than renting it from a model

**Typical Profile:**
- $500M - $10B in assets under management
- 20-200 employees in knowledge work roles
- Regulated or quasi-regulated industry
- Significant document-intensive workflows

### Why Mid-Cap?

Large enterprises have the resources to build custom solutions. Small firms can use generic tools. Mid-cap organizations face the worst of both worlds: enterprise-grade requirements without enterprise-grade budgets. NYQST provides the discipline of high-end data engineering, productized for this underserved market.

---

## PropSygnal Personas

### 1. Investment Analyst (Junior/Mid-level)

**Profile:**
- Role: Investment Analyst at a PE real estate fund or institutional investor
- Experience: 2-5 years
- Reports to: Investment Director/Partner
- Team context: Part of a 3-8 person acquisitions team

**What They Actually Do:**

Daily work involves screening incoming deal flow (IMs, broker packages, off-market opportunities), building and maintaining financial models in Argus and Excel, compiling market research and comparable transactions, preparing investment committee materials, coordinating due diligence workstreams, and chasing documents and information from sellers, brokers, and advisors.

Weekly and monthly activities include updating deal pipeline tracking, presenting deals at team meetings, preparing rejection letters and feedback for passed deals, and supporting live transactions through closing.

**Pain Points:**

Information overload is constant: 20-50 IMs per week to review, each 50-200 pages, with critical details buried in appendices. Data extraction is manual hell: pulling rent rolls from PDFs into Excel, re-keying lease terms, reconciling different formats. Model building is repetitive: same structure rebuilt for each deal, assumption documentation fragmented, version control chaos. Due diligence coordination means tracking 50+ documents across 10+ workstreams. Time pressure is relentless: competitive processes have 2-4 week timelines while working on 3-5 deals simultaneously.

**What Would Help:**
- Instant IM triage: "Does this meet our criteria?" in 5 minutes not 2 hours
- Automated data extraction: Rent roll, lease summary, capex to structured tables
- Assumption library: "What did we assume for similar deals?"
- DD tracker with intelligence: Auto-populate from document drops
- Comparable deals database: Searchable, normalized, trustworthy

**AI Trust Requirements:**
- Must be able to see source documents for any extracted data
- Must be faster than doing it manually (or won't adopt)
- Must handle edge cases gracefully (flag uncertainty, don't hallucinate)
- Must integrate with Excel/Argus (not replace core tools)

---

### 2. Investment Director / Principal

**Profile:**
- Role: Senior deal lead at PE fund, REIT, or institutional investor
- Experience: 8-15 years
- Reports to: Partner/CIO
- Direct reports: 2-5 analysts

**What They Actually Do:**

Deal leadership involves deciding which deals to pursue from screened pipeline, leading negotiations with sellers and brokers, structuring transactions (JV, debt, tax), presenting at Investment Committee, and being accountable for deal quality and execution.

Team management includes assigning work to analysts, reviewing deliverables (models, memos, DD reports), mentoring and developing the team, and managing external advisor relationships.

Strategic work encompasses market positioning and thesis development, relationship building with brokers and principals, and portfolio-level thinking.

**Pain Points:**

Decision quality under time pressure is the core challenge: need to quickly absorb analyst work and make calls, can't read every page but need the synthesis, risk of missing critical issues buried in details, accountability if deal goes wrong. Information asymmetry is constant: sellers know assets better than buyers, broker spin versus reality, what's NOT in the IM is often critical. Team leverage is limited: analyst time is finite, quality of analysis varies, training takes years, key person risk when analysts leave. Process discipline is hard to maintain: consistent evaluation frameworks hard to enforce, lessons from past deals not systematically captured.

**What Would Help:**
- Executive summaries with evidence: "Here's the headline, here's the support"
- Risk flags surfaced automatically: "This lease has unusual break provisions"
- Deal comparisons: "How does this compare to similar deals we've done/seen?"
- Assumption tracking: "We assumed 5% rental growth - what did comps actually achieve?"
- Team productivity visibility without micromanaging

**AI Trust Requirements:**
- AI should make team MORE productive, not create new work
- AI outputs need to be IC-ready (professional, accurate, sourced)
- AI should catch things humans miss (that's the value)
- AI should NEVER make confident errors (hallucinations are career-ending)

---

### 3. Asset Manager

**Profile:**
- Role: Asset Manager at institutional investor or fund manager
- Experience: 5-12 years
- Portfolio: 10-30 assets, $500M-$2B
- Reports to: Head of Asset Management/Portfolio Manager

**What They Actually Do:**

Operational oversight includes monitoring property manager performance, reviewing service charge budgets and reconciliations, handling tenant escalations, approving major capex decisions, and managing lease events (breaks, renewals, rent reviews).

Financial management encompasses annual budget preparation and approval, monthly/quarterly actual vs budget analysis, cash flow forecasting, covenant compliance monitoring, and distribution/redemption calculations.

Reporting covers quarterly investor reports, board presentations, ESG/sustainability reporting, and regulatory filings.

Value creation involves asset business plan development, lease restructuring negotiations, repositioning projects, and disposition planning and execution.

**Pain Points:**

Data fragmentation is pervasive: property managers use different systems, data arrives in different formats, no single source of truth across portfolio, manual aggregation for every report. Lease administration is complex: critical dates buried in lease documents, break notices have precise timing requirements, rent review mechanisms vary by lease, service charge provisions are complex. Reporting burden is heavy: same data reformatted for different audiences, manual copy-paste across documents, commentary writing is time-consuming, error-prone when rushed. Proactive management suffers: buried in admin with not enough time for value-add, tenant issues discovered late, market changes not reflected in business plans.

**What Would Help:**
- Unified portfolio dashboard: Real-time view across assets
- Lease event automation: Never miss a break notice deadline
- Report generation: Draft reports from source data
- Anomaly detection: "Service charge up 30% - investigate"
- Asset knowledge base: "What was discussed with tenant X in 2023?"

**AI Trust Requirements:**
- AI must not miss critical dates or deadlines
- AI must handle lease complexity correctly (or flag uncertainty)
- AI should generate audit trails
- AI outputs need to be investor-presentable

---

### 4. Fund/Portfolio Manager

**Profile:**
- Role: Portfolio Manager or Fund Manager
- Experience: 15-25 years
- Portfolio: $1-10B AUM, 50-200 assets
- Reports to: Board/Investment Committee

**What They Actually Do:**

Portfolio strategy involves sector allocation and rebalancing, fund-level risk management, capital deployment pacing, and disposition timing decisions.

Investor management includes quarterly investor updates, annual meetings, ad-hoc investor queries, and capital raise/marketing.

Governance encompasses Investment Committee participation, board reporting, regulatory compliance oversight, and external auditor interactions.

**Pain Points:**

Portfolio visibility is limited: can't get real-time portfolio view, data freshness varies by asset, aggregation across managers is slow, benchmarking against market is hard. Investor demands are increasing: more data requests with less lead time, ESG reporting increasingly detailed, custom reporting for different LPs, attribution analysis expected. Strategic vs tactical balance is off: drowning in operational details, not enough time for strategic thinking, market insights fragmented, competitive intelligence limited. Decision documentation is poor: IC decisions and rationale poorly captured, strategy evolution not documented, lessons learned not systematized.

**What Would Help:**
- Real-time portfolio intelligence: Aggregated, clean, current
- Investor reporting automation: Push-button quarterly reports
- Scenario modeling: "What if rates rise 100bps across portfolio?"
- Market intelligence: Relevant deals, trends, risks surfaced proactively
- Strategic memory: "What did we decide in 2022 and why?"

**AI Trust Requirements:**
- AI must be auditable (investor scrutiny, regulatory requirements)
- AI should enhance strategic thinking, not replace judgment
- AI errors at portfolio level have large consequences
- AI should enable faster, better decisions with full transparency

---

### 5. Property Manager

**Profile:**
- Role: Property Manager (often outsourced)
- Experience: 3-10 years
- Portfolio: 5-20 buildings
- Reports to: Asset Manager or PM firm leadership

**What They Actually Do:**

Day-to-day operations include tenant requests and complaints, building maintenance coordination, contractor management, and health and safety compliance.

Financial work covers rent collection, service charge administration, invoice processing, and budget preparation and tracking.

Reporting encompasses monthly property reports, incident reports, compliance certificates, and utility monitoring.

**Pain Points:**

Administrative burden is massive: huge paperwork volume, multi-system data entry, reporting to multiple stakeholders, documentation requirements increasing. Tenant communication is high-volume: many queries, repeated questions about same issues, expectation of immediate response. Compliance tracking is complex: numerous regulatory requirements, certificate expiry tracking, risk assessment documentation, audit preparation.

**What Would Help:**
- Automated report generation from building systems data
- Tenant query handling: AI triage/response for common issues
- Compliance monitoring: Proactive certificate/deadline tracking
- Document management: Organized, searchable, always current

---

### 6. Financial Controller

**Profile:**
- Role: Financial Controller or Finance Director
- Experience: 10-20 years
- Scope: Fund or portfolio-level financial oversight
- Reports to: CFO or Fund Manager

**What They Actually Do:**

Financial oversight includes fund accounting, NAV calculations, fee computations, and audit coordination. Covenant monitoring ensures compliance with lender requirements. Investor reporting produces financial statements and performance metrics. Treasury management handles cash flow and distributions.

**Pain Points:**

Data reconciliation across systems is time-consuming. Covenant calculations require manual verification. Audit preparation is labor-intensive. Reporting deadlines create pressure.

**What Would Help:**
- Automated covenant calculations with full evidence trails
- Reconciliation tools that identify discrepancies
- Audit-ready documentation generated automatically
- Real-time financial dashboards

---

## RegSygnal Personas

### 1. Compliance Officer

**Profile:**
- Role: Head of Compliance or Senior Compliance Manager
- Experience: 10-20 years
- Scope: Firm-wide regulatory compliance
- Reports to: CEO, Board, or General Counsel

**What They Actually Do:**

Regulatory monitoring involves tracking new and changing regulations, assessing impact on the firm, and communicating requirements to business units. Policy management includes developing and maintaining compliance policies, ensuring policies reflect current regulations, and training staff on requirements. Oversight encompasses monitoring compliance across the firm, investigating potential breaches, and reporting to regulators and board.

**Pain Points:**

Regulatory volume is overwhelming: thousands of pages of new requirements annually, multiple regulators with overlapping requirements, constant change requiring continuous monitoring. Interpretation ambiguity is common: same regulatory text interpreted differently, guidance evolves over time, industry practice varies. Implementation gaps exist: requirements don't map cleanly to systems, business units implement inconsistently, proving compliance requires extensive documentation. Knowledge concentration is risky: expertise trapped in individual heads, succession planning difficult, key person risk is high.

**What Would Help:**
- Regulatory change monitoring with impact assessment
- Requirement tracking from regulation to implementation
- Gap analysis showing unmet requirements
- Compliance evidence generation for audits
- Knowledge capture that persists beyond individuals

**AI Trust Requirements:**
- AI must not miss regulatory requirements
- AI interpretations must be traceable to source text
- AI should surface ambiguity, not resolve it silently
- AI outputs must be defensible to regulators

---

### 2. Regulatory Analyst

**Profile:**
- Role: Regulatory Analyst or Policy Specialist
- Experience: 3-8 years
- Focus: Specific regulatory domain (e.g., EMIR, MiFID II)
- Reports to: Compliance Officer or Head of Regulatory Affairs

**What They Actually Do:**

Regulatory analysis involves reading and interpreting regulatory text, identifying requirements applicable to the firm, and tracking regulatory developments. Implementation support includes translating requirements into business specifications, working with technology to implement controls, and testing compliance solutions. Documentation encompasses maintaining regulatory interpretation records, documenting compliance rationale, and preparing regulatory submissions.

**Pain Points:**

Document volume is high: regulations run to hundreds of pages, supporting guidance adds more, cross-references require tracking multiple documents. Interpretation complexity is significant: regulatory language is often ambiguous, multiple valid interpretations exist, industry practice evolves. Implementation translation is difficult: regulatory concepts don't map directly to systems, business processes vary, edge cases are common. Change management is constant: regulations are amended frequently, implementation timelines are tight, impact assessment is time-consuming.

**What Would Help:**
- Regulatory text parsing with requirement extraction
- Interpretation tracking with evidence
- Implementation mapping from requirements to controls
- Change impact analysis when regulations are amended
- Cross-regulation mapping showing overlaps and conflicts

---

### 3. Technology Lead (Regulatory Systems)

**Profile:**
- Role: Technology Lead or Architect for regulatory systems
- Experience: 8-15 years
- Focus: Building and maintaining compliance systems
- Reports to: CTO or Head of Regulatory Technology

**What They Actually Do:**

System development involves building regulatory reporting systems, implementing compliance controls, and integrating with business systems. Maintenance includes updating systems for regulatory changes, fixing defects and issues, and performance optimization. Coordination encompasses working with compliance on requirements, managing vendor relationships, and supporting audits and examinations.

**Pain Points:**

Requirement clarity is often lacking: compliance requirements are ambiguous, business rules change frequently, edge cases are discovered late. Testing complexity is high: regulatory scenarios are numerous, test data is hard to obtain, regression testing is time-consuming. Change velocity is challenging: regulatory changes require system updates, timelines are often compressed, multiple changes overlap.

**What Would Help:**
- Clear requirement specifications from regulatory text
- Test case generation from requirements
- Impact analysis for regulatory changes
- Traceability from regulation to code
- Automated compliance verification

---

## Common Themes Across All Personas

### Universal Pain Points

1. **Document processing is slow and error-prone** - Every persona deals with documents that need to be read, understood, and acted upon. Manual processing is the bottleneck.

2. **Data is fragmented across systems** - No single source of truth. Same information entered multiple times. Reconciliation is constant.

3. **Reporting is manual and repetitive** - Same data reformatted for different audiences. Copy-paste across documents. Error-prone when rushed.

4. **Institutional knowledge is lost** - Expertise trapped in individual heads. Context leaves when people leave. Decisions not documented.

5. **Time pressure forces quality trade-offs** - Not enough time to do things properly. Corners cut under deadline pressure. Errors discovered too late.

### Universal AI Requirements

1. **Explainability** - Show your sources and reasoning. "The AI said so" is not acceptable.

2. **Accuracy over speed** - Errors are costly. Better to be slower and right than fast and wrong.

3. **Integration** - Work with existing tools, not replace them. Excel, Argus, existing systems must remain.

4. **Auditability** - Everything must be traceable. Regulators, auditors, and investors will ask questions.

5. **Appropriate confidence** - Flag uncertainty, don't guess. "I'm not sure" is better than a confident error.

### Trust Hierarchy

The hierarchy of trust requirements, from most critical to least:

1. **Never confidently wrong** - Hallucinations are career-ending and liability-creating. This is non-negotiable.

2. **Catch what humans miss** - This is the value proposition. If AI doesn't find things humans would miss, why use it?

3. **Faster than manual** - If it's not faster, it won't be adopted. Time savings must be real and significant.

4. **Easy to verify** - Trust but verify. Users need to be able to check AI outputs quickly.

5. **Learns from feedback** - Improves over time. Corrections should make the system better.

---

## User Journey: From Skeptic to Advocate

### Stage 1: Skeptical Trial

User tries the system on a task they've already done manually. They compare results. They look for errors. They test edge cases.

**NYQST Response:** Full transparency. Show every source. Highlight uncertainty. Make verification easy.

### Stage 2: Cautious Adoption

User starts using the system for real work, but verifies everything. They build confidence through repeated accuracy.

**NYQST Response:** Consistent accuracy. No surprises. Gradual trust building through reliability.

### Stage 3: Confident Usage

User trusts the system for routine tasks. They still verify high-stakes outputs but rely on the system for day-to-day work.

**NYQST Response:** Proactive value. Surface insights they wouldn't have found. Catch things they would have missed.

### Stage 4: Advocacy

User recommends the system to colleagues. They can't imagine working without it. They push for expanded usage.

**NYQST Response:** Continuous improvement. New capabilities. Deeper integration. Expanding value.

---

## Persona-to-Module Mapping

| Persona | Primary Modules | Key Workflows |
|---------|-----------------|---------------|
| Investment Analyst | Research, Document Management, Analysis | Deal screening, DD coordination, model building |
| Investment Director | Analysis, Organisational Insight | Deal review, team oversight, IC preparation |
| Asset Manager | Document Management, Modelling, Insight | Covenant monitoring, reporting, lease management |
| Fund/Portfolio Manager | Organisational Insight, Analysis | Portfolio oversight, investor reporting |
| Property Manager | Document Management, Insight | Operations, compliance, tenant management |
| Financial Controller | Modelling, Insight | Covenant calculations, audit support |
| Compliance Officer | Knowledge & Domain, Insight | Regulatory tracking, gap analysis |
| Regulatory Analyst | Research, Modelling | Interpretation, implementation mapping |
| Technology Lead | Modelling, Knowledge & Domain | Requirement specs, traceability |

---

**Related Documents:**
- [Executive Summary](01_EXECUTIVE_SUMMARY.md) - Quick overview
- [Platform Modules](03_PLATFORM.md) - Core capabilities
- [Products](04_PRODUCTS.md) - PropSygnal & RegSygnal
- [Roadmap](07_ROADMAP.md) - Delivery plan
