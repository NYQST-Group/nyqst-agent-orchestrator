# Commercial Real Estate User Personas

*Date: 2026-01-23*
*Status: Initial draft - to be enriched with research findings*

---

## Overview

This document defines key user personas for a commercial real estate intelligence platform, spanning acquisition through asset management. Each persona represents real users with specific workflows, pain points, and requirements.

---

## 1. Investment Analyst (Junior/Mid-level)

### Profile
- **Role:** Investment Analyst at a PE real estate fund or institutional investor
- **Experience:** 2-5 years
- **Reports to:** Investment Director/Partner
- **Team size context:** Part of a 3-8 person acquisitions team

### What They Actually Do

**Daily Work:**
- Screen incoming deal flow (IMs, broker packages, off-market opportunities)
- Build and maintain financial models (Argus, Excel)
- Compile market research and comparable transactions
- Prepare investment committee materials
- Coordinate due diligence workstreams
- Chase documents and information from sellers/brokers/advisors

**Weekly/Monthly:**
- Update deal pipeline tracking
- Present deals at team meetings
- Prepare rejection letters/feedback for passed deals
- Support live transactions through closing

### Pain Points

1. **Information Overload**
   - 20-50 IMs per week to review
   - Each IM is 50-200 pages
   - Need to quickly identify: does this fit our mandate?
   - Critical details buried in appendices

2. **Data Extraction Hell**
   - Manually pulling rent rolls from PDFs into Excel
   - Re-keying lease terms from abstracts
   - Reconciling different date formats, currencies, area measurements
   - No standard format across sellers/brokers

3. **Model Building Time**
   - Same model structure rebuilt for each deal
   - Assumption documentation fragmented
   - Version control chaos ("Final_v3_FINAL_JB.xlsx")
   - Audit trail for changes non-existent

4. **Due Diligence Coordination**
   - Tracking 50+ documents across 10+ workstreams
   - Chasing advisors for deliverables
   - Synthesizing findings from multiple expert reports
   - Red flag tracking across sources

5. **Time Pressure**
   - Competitive processes have 2-4 week timelines
   - Working on 3-5 deals simultaneously
   - IC materials needed on tight deadlines
   - Quality vs speed trade-off constant

### What Would Help

- **Instant IM triage:** "Does this meet our criteria?" in 5 minutes not 2 hours
- **Automated data extraction:** Rent roll, lease summary, capex → structured tables
- **Assumption library:** "What did we assume for similar deals?"
- **DD tracker with intelligence:** Auto-populate from document drops
- **Comparable deals database:** Searchable, normalized, trustworthy

### Sensitivities

- Career risk from errors in IC materials
- Skeptical of AI "black boxes" - need to verify everything
- Under pressure from seniors to work faster AND more accurately
- Competitive with peers - quality of analysis is visible

### AI Trust Requirements

- Must be able to see source documents for any extracted data
- Must be faster than doing it manually (or won't adopt)
- Must handle edge cases gracefully (flag uncertainty, don't hallucinate)
- Must integrate with Excel/Argus (not replace core tools)

---

## 2. Investment Director / Principal

### Profile
- **Role:** Senior deal lead at PE fund, REIT, or institutional investor
- **Experience:** 8-15 years
- **Reports to:** Partner/CIO
- **Direct reports:** 2-5 analysts

### What They Actually Do

**Deal Leadership:**
- Decide which deals to pursue from screened pipeline
- Lead negotiations with sellers/brokers
- Structure transactions (JV, debt, tax)
- Present at Investment Committee
- Accountable for deal quality and execution

**Team Management:**
- Assign work to analysts
- Review deliverables (models, memos, DD reports)
- Mentor and develop team
- Manage external advisor relationships

**Strategic:**
- Market positioning and thesis development
- Relationship building with brokers/principals
- Portfolio-level thinking

### Pain Points

1. **Decision Quality Under Time Pressure**
   - Need to quickly absorb analyst work and make calls
   - Can't read every page - need the synthesis
   - Risk of missing critical issues buried in details
   - Accountability if deal goes wrong

2. **Information Asymmetry**
   - Sellers know asset better than buyers
   - Broker spin vs reality
   - What's NOT in the IM is often critical
   - Market comps may be stale or cherry-picked

3. **Team Leverage**
   - Analyst time is finite
   - Quality of analysis varies
   - Training takes years
   - Key person risk when analysts leave

4. **Process Discipline**
   - Consistent evaluation frameworks hard to enforce
   - Lessons from past deals not systematically captured
   - IC prep quality varies by deal team
   - Post-mortem analysis rarely happens

### What Would Help

- **Executive summaries with evidence:** "Here's the headline, here's the support"
- **Risk flags surfaced automatically:** "This lease has unusual break provisions"
- **Deal comparisons:** "How does this compare to similar deals we've done/seen?"
- **Assumption tracking:** "We assumed 5% rental growth - what did comps actually achieve?"
- **Team productivity visibility:** Without micromanaging

### Sensitivities

- Reputational risk from bad deals
- IC members will probe analysis - need defensible work
- Time-poor, interruption-rich work environment
- Skeptical of tools that add friction or learning curve

### AI Trust Requirements

- AI should make team MORE productive, not create new work
- AI outputs need to be IC-ready (professional, accurate, sourced)
- AI should catch things humans miss (that's the value)
- AI should NEVER make confident errors (hallucinations are career-ending)

---

## 3. Asset Manager

### Profile
- **Role:** Asset Manager at institutional investor or fund manager
- **Experience:** 5-12 years
- **Portfolio:** 10-30 assets, $500M-$2B
- **Reports to:** Head of Asset Management/Portfolio Manager

### What They Actually Do

**Operational Oversight:**
- Monitor property manager performance
- Review service charge budgets and reconciliations
- Handle tenant escalations
- Approve major capex decisions
- Manage lease events (breaks, renewals, rent reviews)

**Financial Management:**
- Annual budget preparation and approval
- Monthly/quarterly actual vs budget analysis
- Cash flow forecasting
- Covenant compliance monitoring
- Distribution/redemption calculations

**Reporting:**
- Quarterly investor reports
- Board presentations
- ESG/sustainability reporting
- Regulatory filings

**Value Creation:**
- Asset business plan development
- Lease restructuring negotiations
- Repositioning projects
- Disposition planning and execution

### Pain Points

1. **Data Fragmentation**
   - Property managers use different systems
   - Data arrives in different formats
   - No single source of truth across portfolio
   - Manual aggregation for every report

2. **Lease Administration**
   - Critical dates buried in lease documents
   - Break notices have precise timing requirements
   - Rent review mechanisms vary by lease
   - Service charge provisions are complex

3. **Reporting Burden**
   - Same data reformatted for different audiences
   - Manual copy-paste across documents
   - Commentary writing is time-consuming
   - Error-prone when rushed

4. **Proactive Management**
   - Buried in admin, not enough time for value-add
   - Tenant issues discovered late
   - Market changes not reflected in business plans
   - Opportunities missed due to workload

5. **Institutional Memory**
   - Asset history fragmented across emails, files, systems
   - Lease negotiation context lost when people leave
   - Why were decisions made? No record.

### What Would Help

- **Unified portfolio dashboard:** Real-time view across assets
- **Lease event automation:** Never miss a break notice deadline
- **Report generation:** Draft reports from source data
- **Anomaly detection:** "Service charge up 30% - investigate"
- **Asset knowledge base:** "What was discussed with tenant X in 2023?"

### Sensitivities

- Fiduciary duty to investors
- Lease errors can be very expensive (missed break = 5 more years)
- Covenant breaches have serious consequences
- Investor relations matter - reporting quality reflects on them

### AI Trust Requirements

- AI must not miss critical dates or deadlines
- AI must handle lease complexity correctly (or flag uncertainty)
- AI should generate audit trails
- AI outputs need to be investor-presentable

---

## 4. Fund/Portfolio Manager

### Profile
- **Role:** Portfolio Manager or Fund Manager
- **Experience:** 15-25 years
- **Portfolio:** $1-10B AUM, 50-200 assets
- **Reports to:** Board/Investment Committee

### What They Actually Do

**Portfolio Strategy:**
- Sector allocation and rebalancing
- Fund-level risk management
- Capital deployment pacing
- Disposition timing decisions

**Investor Management:**
- Quarterly investor updates
- Annual meetings
- Ad-hoc investor queries
- Capital raise/marketing

**Governance:**
- Investment Committee participation
- Board reporting
- Regulatory compliance oversight
- External auditor interactions

### Pain Points

1. **Portfolio Visibility**
   - Can't get real-time portfolio view
   - Data freshness varies by asset
   - Aggregation across managers is slow
   - Benchmarking against market is hard

2. **Investor Demands**
   - More data requests, less lead time
   - ESG reporting increasingly detailed
   - Custom reporting for different LPs
   - Attribution analysis expected

3. **Strategic vs Tactical**
   - Drowning in operational details
   - Not enough time for strategic thinking
   - Market insights fragmented
   - Competitive intelligence limited

4. **Decision Documentation**
   - IC decisions and rationale poorly captured
   - Strategy evolution not documented
   - Lessons learned not systematized
   - Succession planning difficult

### What Would Help

- **Real-time portfolio intelligence:** Aggregated, clean, current
- **Investor reporting automation:** Push-button quarterly reports
- **Scenario modeling:** "What if rates rise 100bps across portfolio?"
- **Market intelligence:** Relevant deals, trends, risks surfaced proactively
- **Strategic memory:** "What did we decide in 2022 and why?"

### AI Trust Requirements

- AI must be auditable (investor scrutiny, regulatory requirements)
- AI should enhance strategic thinking, not replace judgment
- AI errors at portfolio level have large consequences
- AI should enable faster, better decisions with full transparency

---

## 5. Property Manager

### Profile
- **Role:** Property Manager (often outsourced)
- **Experience:** 3-10 years
- **Portfolio:** 5-20 buildings
- **Reports to:** Asset Manager or PM firm leadership

### What They Actually Do

**Day-to-Day Operations:**
- Tenant requests and complaints
- Building maintenance coordination
- Contractor management
- Health and safety compliance

**Financial:**
- Rent collection
- Service charge administration
- Invoice processing
- Budget preparation and tracking

**Reporting:**
- Monthly property reports
- Incident reports
- Compliance certificates
- Utility monitoring

### Pain Points

1. **Administrative Burden**
   - Massive paperwork volume
   - Multi-system data entry
   - Reporting to multiple stakeholders
   - Documentation requirements increasing

2. **Tenant Communication**
   - High volume of queries
   - Repeated questions about same issues
   - Expectation of immediate response
   - Language barriers in some markets

3. **Compliance Tracking**
   - Numerous regulatory requirements
   - Certificate expiry tracking
   - Risk assessment documentation
   - Audit preparation

### What Would Help

- **Automated report generation:** From building systems data
- **Tenant query handling:** AI triage/response for common issues
- **Compliance monitoring:** Proactive certificate/deadline tracking
- **Document management:** Organized, searchable, always current

---

## 6. Transactions Lawyer (External Advisor)

### Profile
- **Role:** Real estate partner or senior associate
- **Firm type:** Top 50 law firm, real estate practice
- **Works with:** Fund clients on acquisitions and dispositions

### What They Actually Do

- Title investigation and reporting
- Lease review and summarization
- SPA drafting and negotiation
- Deal coordination and closing
- Due diligence management

### Pain Points

1. **Document Volume**
   - Large data rooms (1000s of documents)
   - Time pressure on DD
   - Junior lawyer capacity constraints
   - Review consistency across team

2. **Lease Analysis**
   - Every lease is different
   - Critical terms buried in schedules
   - Side letters change the deal
   - Summarization is tedious

3. **Client Reporting**
   - Report of title format varies
   - Issue tracking across documents
   - Red flags need prioritization
   - Client wants synthesis, not pages

### What Would Help

- **Automated lease abstraction:** Consistent extraction across documents
- **Issue flagging:** "Unusual provisions detected"
- **Report drafting:** From extracted data to first draft
- **Data room organization:** Smart categorization and indexing

---

## 7. Technical Surveyor (External Advisor)

### Profile
- **Role:** Building surveyor at multi-disciplinary consultancy
- **Experience:** 5-15 years
- **Services:** Building surveys, M&E assessments, defects

### What They Actually Do

- Site inspections
- Technical due diligence reports
- Capex planning
- Defects analysis
- Reinstatement cost assessments

### Pain Points

1. **Report Production**
   - Site notes to report is slow
   - Photo processing and annotation
   - Standardization across surveyors
   - Quality review time

2. **Historical Information**
   - Building history often incomplete
   - Previous reports not available
   - Defects recur without pattern analysis
   - Knowledge leaves with people

### What Would Help

- **Report templates with intelligence:** From site data to first draft
- **Photo analysis:** Auto-categorization and annotation
- **Building databases:** Historical condition data
- **Defect pattern recognition:** "This building type often has..."

---

## Common Themes Across Personas

### Universal Pain Points
1. **Document processing is slow and error-prone**
2. **Data is fragmented across systems**
3. **Reporting is manual and repetitive**
4. **Institutional knowledge is lost**
5. **Time pressure forces quality trade-offs**

### Universal AI Requirements
1. **Explainability:** Show your sources and reasoning
2. **Accuracy over speed:** Errors are costly
3. **Integration:** Work with existing tools, not replace them
4. **Auditability:** Everything must be traceable
5. **Appropriate confidence:** Flag uncertainty, don't guess

### Trust Hierarchy
1. **Never confidently wrong** (career-ending, liability-creating)
2. **Catch what humans miss** (the value proposition)
3. **Faster than manual** (or won't be adopted)
4. **Easy to verify** (trust but verify)
5. **Learns from feedback** (improves over time)

---

*Next: Map these personas to specific workflow scenarios and identify AI intervention points*
