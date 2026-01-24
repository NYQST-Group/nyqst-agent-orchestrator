# Cross-Mapping Analysis: Personas, Decisions, Trust, and System Alignment

*Date: 2026-01-23*  
*Purpose: Comprehensive cross-mapping to extract maximum value from UI, Workflow, and System approaches*

---

## Executive Summary

This document performs deep cross-mapping analysis across:
1. **Personas → Features/Workflows/UI** - Who needs what?
2. **Decision Points** - Where are the actual decisions? (Not just processes)
3. **Trust Lifecycle** - How does trust build and evolve?
4. **Multi-Party Visibility** - Who sees what?
5. **CRE-Specific vs Generic** - What's domain-specific vs. universal?
6. **Workflow ↔ UI ↔ System** - Alignment across all three approaches

**Key Insight**: The value is in **decision support** (5 minutes) not **process automation** (100 hours). Focus on the moments that matter.

---

## 1. Persona-to-Feature Mapping

### 1.1 Investment Analyst → Features

**Primary Pain Points:**
- 20-50 IMs per week to review (50-200 pages each)
- Manual data extraction from PDFs to Excel
- Model building time and version control chaos
- Due diligence coordination across 10+ workstreams

**Required Features:**

| Feature | Priority | UI Component | Backend Support | Status |
|---------|----------|--------------|-----------------|--------|
| **IM Triage** | Critical | QuickTriagePane (missing) | Document extraction API | ❌ Not built |
| **Automated Data Extraction** | Critical | DocumentViewerPane ✅ | Extraction service (partial) | ⚠️ Partial |
| **Rent Roll Extraction** | Critical | TableViewerPane ✅ | Extraction service | ⚠️ Partial |
| **Model Population** | High | Export to Excel (missing) | Export API (missing) | ❌ Not built |
| **DD Tracker** | High | RunExplorerPane ✅ | Run API ✅ | ✅ Built |
| **Comparable Deals DB** | Medium | SearchPane (missing) | Search API (missing) | ❌ Not built |
| **Assumption Library** | Medium | KnowledgeBasePane (missing) | Knowledge API (partial) | ⚠️ Partial |

**Trust Requirements:**
- Must see source documents for any extracted data
- Must be faster than manual (or won't adopt)
- Must handle edge cases gracefully (flag uncertainty)
- Must integrate with Excel/Argus

**Workflow Mapping:**
- **Deal Sourcing & Screening** → IM triage, mandate fit scoring
- **Due Diligence** → Document extraction, DD tracker, issue flagging
- **Underwriting** → Model population, assumption tracking

### 1.2 Investment Director → Features

**Primary Pain Points:**
- Decision quality under time pressure
- Information asymmetry (sellers know more)
- Team leverage (analyst time is finite)
- Process discipline (lessons not captured)

**Required Features:**

| Feature | Priority | UI Component | Backend Support | Status |
|---------|----------|--------------|-----------------|--------|
| **Executive Summaries** | Critical | SummaryPane (missing) | Summarization API (missing) | ❌ Not built |
| **Risk Flags** | Critical | RiskDashboardPane (missing) | Risk detection service (missing) | ❌ Not built |
| **Deal Comparisons** | High | ComparisonPane (missing) | Comparison API (missing) | ❌ Not built |
| **Assumption Tracking** | High | AssumptionTrackerPane (missing) | Tracking API (missing) | ❌ Not built |
| **Team Productivity** | Medium | TeamDashboardPane (missing) | Analytics API (missing) | ❌ Not built |
| **IC Materials** | Critical | ReportGeneratorPane (missing) | Generation API (missing) | ❌ Not built |

**Trust Requirements:**
- AI outputs need to be IC-ready (professional, accurate, sourced)
- AI should catch things humans miss (that's the value)
- AI should NEVER make confident errors (hallucinations are career-ending)

**Decision Points:**
- **Deal Pursuit Decision** (5 minutes) → Needs: Executive summary, risk flags, mandate fit
- **IC Approval Decision** (30 minutes) → Needs: IC materials, deal comparison, assumption validation
- **Negotiation Decision** (ongoing) → Needs: Risk assessment, comparable deals, team input

### 1.3 Asset Manager → Features

**Primary Pain Points:**
- Data fragmentation across systems
- Lease administration (critical dates buried)
- Reporting burden (manual copy-paste)
- Proactive management (buried in admin)

**Required Features:**

| Feature | Priority | UI Component | Backend Support | Status |
|---------|----------|--------------|-----------------|--------|
| **Portfolio Dashboard** | Critical | PortfolioDashboardPane (missing) | Portfolio API (missing) | ❌ Not built |
| **Lease Event Calendar** | Critical | EventCalendarPane (missing) | Event API (missing) | ❌ Not built |
| **Break Notice Automation** | Critical | AlertSystemPane (missing) | Alert service (missing) | ❌ Not built |
| **Report Generation** | High | ReportGeneratorPane (missing) | Generation API (missing) | ❌ Not built |
| **Anomaly Detection** | High | AlertSystemPane (missing) | Detection service (missing) | ❌ Not built |
| **Asset Knowledge Base** | Medium | KnowledgeBasePane (missing) | Knowledge API (partial) | ⚠️ Partial |
| **Service Charge Tracking** | High | ServiceChargePane (missing) | Tracking API (missing) | ❌ Not built |

**Trust Requirements:**
- AI must not miss critical dates or deadlines (zero tolerance)
- AI must handle lease complexity correctly (or flag uncertainty)
- AI should generate audit trails
- AI outputs need to be investor-presentable

**Decision Points:**
- **Break Notice Decision** (1 minute) → Needs: Break clause details, notice requirements, deadline calculation
- **Rent Review Decision** (30 minutes) → Needs: Market comparables, lease terms, negotiation strategy
- **Capex Approval Decision** (1 hour) → Needs: Business case, ROI analysis, budget impact

### 1.4 Fund/Portfolio Manager → Features

**Primary Pain Points:**
- Portfolio visibility (can't get real-time view)
- Investor demands (more data requests, less lead time)
- Strategic vs tactical (drowning in operational details)
- Decision documentation (IC decisions poorly captured)

**Required Features:**

| Feature | Priority | UI Component | Backend Support | Status |
|---------|----------|--------------|-----------------|--------|
| **Portfolio Intelligence** | Critical | PortfolioDashboardPane (missing) | Portfolio API (missing) | ❌ Not built |
| **Investor Reporting** | Critical | ReportGeneratorPane (missing) | Generation API (missing) | ❌ Not built |
| **Scenario Modeling** | High | ScenarioPane (missing) | Modeling API (missing) | ❌ Not built |
| **Market Intelligence** | Medium | MarketIntelligencePane (missing) | Intelligence API (missing) | ❌ Not built |
| **Strategic Memory** | Medium | KnowledgeBasePane (missing) | Knowledge API (partial) | ⚠️ Partial |

**Trust Requirements:**
- AI must be auditable (investor scrutiny, regulatory requirements)
- AI should enhance strategic thinking, not replace judgment
- AI errors at portfolio level have large consequences

**Decision Points:**
- **Portfolio Allocation Decision** (1 hour) → Needs: Portfolio performance, market outlook, risk analysis
- **Disposition Timing Decision** (30 minutes) → Needs: Asset performance, market conditions, fund lifecycle
- **Capital Deployment Decision** (ongoing) → Needs: Pipeline status, capital availability, market opportunities

### 1.5 Property Manager → Features

**Primary Pain Points:**
- Administrative burden (massive paperwork)
- Tenant communication (high volume, repeated questions)
- Compliance tracking (numerous regulatory requirements)

**Required Features:**

| Feature | Priority | UI Component | Backend Support | Status |
|---------|----------|--------------|-----------------|--------|
| **Automated Reports** | High | ReportGeneratorPane (missing) | Generation API (missing) | ❌ Not built |
| **Tenant Query Handling** | Medium | ChatPane ✅ | Chat API (partial) | ⚠️ Partial |
| **Compliance Monitoring** | High | CompliancePane (missing) | Compliance API (missing) | ❌ Not built |
| **Document Management** | Medium | DocumentViewerPane ✅ | Document API ✅ | ✅ Built |

**Trust Requirements:**
- Tenant-facing must be accurate and appropriate
- Compliance gaps must not be missed

### 1.6 Transactions Lawyer → Features

**Primary Pain Points:**
- Document volume (1000s of documents in data rooms)
- Lease analysis (every lease is different, critical terms buried)
- Client reporting (synthesis needed, not pages)

**Required Features:**

| Feature | Priority | UI Component | Backend Support | Status |
|---------|----------|--------------|-----------------|--------|
| **Automated Lease Abstraction** | Critical | DocumentViewerPane ✅ | Extraction service (partial) | ⚠️ Partial |
| **Issue Flagging** | Critical | RiskDashboardPane (missing) | Risk detection service (missing) | ❌ Not built |
| **Report Drafting** | High | ReportGeneratorPane (missing) | Generation API (missing) | ❌ Not built |
| **Data Room Organization** | Medium | ArtifactBrowserPane ✅ | Artifact API ✅ | ✅ Built |

**Trust Requirements:**
- AI assists, never replaces legal judgment
- Clear boundary between extraction and interpretation
- Professional liability must remain clear

### 1.7 Technical Surveyor → Features

**Primary Pain Points:**
- Report production (site notes to report is slow)
- Historical information (building history incomplete)
- Defect pattern recognition (defects recur without pattern analysis)

**Required Features:**

| Feature | Priority | UI Component | Backend Support | Status |
|---------|----------|--------------|-----------------|--------|
| **Report Templates** | High | ReportGeneratorPane (missing) | Generation API (missing) | ❌ Not built |
| **Photo Analysis** | Medium | ImageAnalysisPane (missing) | Image API (missing) | ❌ Not built |
| **Building Databases** | Medium | KnowledgeBasePane (missing) | Knowledge API (partial) | ⚠️ Partial |
| **Defect Pattern Recognition** | Low | PatternRecognitionPane (missing) | ML service (missing) | ❌ Not built |

---

## 2. Decision Point Analysis

### 2.1 Critical Insight from Analysis

**From Critical Analysis:**
> "We're describing processes, not decisions. The value is in the 5 minutes of decision, not the 100 hours of preparation."

**Key Decision Points Identified:**

| Workflow | Decision Point | Time | Decision Maker | Information Needed | Current Support |
|----------|---------------|------|----------------|-------------------|----------------|
| **Deal Sourcing** | Does this meet our mandate? | 5 min | Investment Director | Mandate fit score, key metrics | ❌ Not built |
| **Deal Sourcing** | Should we pursue this? | 30 min | Investment Director | Executive summary, risk flags, comparables | ❌ Not built |
| **Due Diligence** | Is there a showstopper? | 1 hour | Investment Director | DD findings synthesis, risk assessment | ⚠️ Partial |
| **Due Diligence** | What's the right price? | 30 min | Investment Director | Model, comparables, market analysis | ⚠️ Partial |
| **IC Approval** | Approve this deal? | 30 min | Investment Committee | IC materials, risk analysis, returns | ❌ Not built |
| **Lease Events** | Exercise break option? | 1 min | Asset Manager | Break clause details, notice requirements | ❌ Not built |
| **Lease Events** | Accept rent review? | 30 min | Asset Manager | Market comparables, lease terms, negotiation | ❌ Not built |
| **Covenant** | Risk of breach? | 5 min | Asset Manager | Current position, forecast, headroom | ❌ Not built |
| **Portfolio** | Hold or sell? | 1 hour | Portfolio Manager | Performance, market conditions, fund lifecycle | ❌ Not built |

### 2.2 Decision Support Requirements

**For Each Decision Point:**

1. **Information Aggregation**
   - Pull data from multiple sources
   - Normalize and validate
   - Present in decision-ready format

2. **Risk Assessment**
   - Flag risks automatically
   - Quantify risk impact
   - Provide mitigation options

3. **Comparable Analysis**
   - Find similar past decisions
   - Show outcomes
   - Highlight differences

4. **Scenario Modeling**
   - Model different outcomes
   - Show sensitivity
   - Quantify uncertainty

5. **Audit Trail**
   - Record decision rationale
   - Track decision outcomes
   - Learn from decisions

**Missing System Capabilities:**
- ❌ Decision support framework
- ❌ Risk quantification engine
- ❌ Comparable analysis service
- ❌ Scenario modeling engine
- ❌ Decision tracking system

---

## 3. Trust Lifecycle Analysis

### 3.1 Trust State Machine

**From Critical Analysis:**
```
NEW AI OUTPUT
     │
     ▼
[UNTRUSTED] ──verify──→ [ACCEPTED] ──promote──→ [AUTHORITATIVE]
     │                        │                        │
     │                        ▼                        ▼
     └──reject──→ [CORRECTED] ────────────────→ [TRAINING DATA]
```

### 3.2 Trust States by Output Type

| Output Type | Initial State | Verification Required | Promotion Criteria | Authoritative Use |
|-------------|---------------|---------------------|-------------------|-------------------|
| **Extracted Data** | UNTRUSTED | Source citation review | Human verification | Used in models/reports |
| **Risk Flags** | UNTRUSTED | Evidence review | Human confirmation | Included in IC materials |
| **Comparable Analysis** | UNTRUSTED | Comparability check | Human validation | Used in underwriting |
| **Generated Reports** | UNTRUSTED | Full review | Human approval | Published to investors |
| **Calculations** | UNTRUSTED | Formula verification | Human sign-off | Used in decisions |
| **Recommendations** | UNTRUSTED | Rationale review | Human judgment | Implemented |

### 3.3 Trust Transition Requirements

**UNTRUSTED → ACCEPTED (Verification):**
- Show source citations
- Highlight confidence scores
- Flag uncertainties
- Enable quick verification (< manual time)
- Track verification time

**ACCEPTED → AUTHORITATIVE (Promotion):**
- Multiple verifications
- No corrections needed
- Used successfully in decisions
- Time-based (e.g., 30 days without issues)

**UNTRUSTED → CORRECTED (Rejection):**
- Capture corrections
- Update extraction logic
- Retrain models
- Track error patterns

**CORRECTED → TRAINING DATA:**
- Add to training set
- Improve future accuracy
- Close feedback loop

### 3.4 Trust Metrics

**Per Output:**
- Verification time
- Verification rate (verified / total)
- Correction rate
- Time to authoritative
- Usage frequency

**Per User:**
- Trust progression over time
- Verification patterns
- Correction patterns
- Adoption rate

**System-Wide:**
- Overall verification rate
- Overall correction rate
- Trust progression trends
- Error patterns

### 3.5 Trust UI Patterns

**Current UI Support:**
- ✅ Confidence scores (mentioned in types)
- ✅ Source citations (EvidenceSpan type)
- ⚠️ Verification workflow (partial)
- ❌ Trust state display (missing)
- ❌ Trust metrics dashboard (missing)
- ❌ Correction interface (missing)

**Required UI Patterns:**
- Trust state badges (UNTRUSTED, ACCEPTED, AUTHORITATIVE)
- Verification interface (quick, efficient)
- Correction interface (capture feedback)
- Trust metrics dashboard
- Trust progression visualization

---

## 4. Multi-Party Visibility Analysis

### 4.1 Role-Based Data Visibility

**From Critical Analysis:**
> "Different parties see different things. The same data has different views."

| Data Type | Owner Sees | Buyer Sees | Lender Sees | Tenant Sees |
|----------|-----------|------------|-------------|-------------|
| **Rent** | Actual | What seller disclosed | Covenant calc input | Their obligation |
| **Valuation** | Internal estimate | Broker opinion | LTV denominator | Not visible |
| **Tenant Credit** | Assessment | Disclosed if material | Security assessment | Not visible |
| **Break Option** | Risk to manage | Opportunity or risk | Cashflow risk | Their right |
| **Covenant Status** | Actual | Not disclosed | Full details | Not visible |
| **Lease Terms** | All details | Disclosed terms | Key terms only | Their lease |
| **DD Findings** | Not visible | Full findings | Material issues | Not visible |
| **Transaction Terms** | Full terms | Full terms | Loan terms | Not visible |

### 4.2 Multi-Party Workflow Requirements

**Acquisition Workflow:**
- **Buyer** sees: Full DD findings, deal terms, negotiation history
- **Seller** sees: Buyer requests, offer terms, closing status
- **Lender** sees: Property details, DD summary, loan terms
- **Legal** sees: All documents, issues, resolutions

**Asset Management Workflow:**
- **Asset Manager** sees: Full portfolio data, all leases, all events
- **Property Manager** sees: Property-level data, tenant details, work orders
- **Investor** sees: Performance data, reports, high-level metrics
- **Lender** sees: Covenant data, financials, compliance status
- **Tenant** sees: Their lease, their obligations, their events

### 4.3 Visibility Requirements by Role

**Investment Analyst:**
- See: All deal data, all DD findings, all models
- Hidden: Other deals (sometimes), investor details

**Investment Director:**
- See: All deals, team work, strategic data
- Hidden: Personal information, sensitive negotiations

**Asset Manager:**
- See: Portfolio data, all leases, all events
- Hidden: Other portfolios, investor details (sometimes)

**Fund Manager:**
- See: Portfolio-level data, investor data, strategic data
- Hidden: Deal-level details (sometimes), sensitive negotiations

**Lender:**
- See: Property data, financials, covenants, compliance
- Hidden: Internal strategy, other lenders, sensitive negotiations

**Tenant:**
- See: Their lease, their obligations, their events
- Hidden: Other tenants, landlord strategy, financials

### 4.4 Multi-Party Coordination Requirements

**Shared Views:**
- Deal status (buyer/seller/lender)
- Transaction timeline (all parties)
- Closing checklist (buyer/seller/lender)
- Lease events (landlord/tenant)

**Coordination Features:**
- Comment threads (per document/issue)
- Approval workflows (multi-party)
- Notification system (role-based)
- Activity feeds (filtered by role)

**Missing System Capabilities:**
- ❌ Role-based access control (partial)
- ❌ Multi-party views
- ❌ Coordination features
- ❌ Notification system (partial)

---

## 5. CRE-Specific vs. Generic Analysis

### 5.1 Critical Insight

**From Critical Analysis:**
> "80% of the underlying patterns are not CRE-specific. Build generic primitives that CRE (and legal, insurance, compliance) can configure."

### 5.2 Categorization Matrix

| Feature | CRE-Specific? | Generic Pattern | Configuration Needed |
|---------|--------------|-----------------|---------------------|
| **Lease Abstraction** | ✅ CRE-specific | Document Extraction | Lease schema config |
| **Rent Roll** | ✅ CRE-specific | Tabular Data Extraction | Rent roll schema |
| **Break Options** | ✅ CRE-specific | Event Management | Break event config |
| **Rent Reviews** | ✅ CRE-specific | Event Management | Rent review config |
| **Covenant Monitoring** | ✅ CRE-specific | Event Management | Covenant config |
| **Valuation** | ✅ CRE-specific | Calculation Engine | Valuation formulas |
| **Document Extraction** | ❌ Generic | Extraction Engine | Schema config |
| **Event Management** | ❌ Generic | Event System | Event type config |
| **Deadline Calculation** | ❌ Generic | Deadline Engine | Rule config |
| **Claim/Decision** | ❌ Generic | Claim System | Claim type config |
| **Evidence Linking** | ❌ Generic | Evidence System | Evidence types |
| **Multi-Party Views** | ❌ Generic | Access Control | Role config |
| **Report Generation** | ❌ Generic | Generation Engine | Template config |
| **Knowledge Base** | ❌ Generic | Knowledge System | Domain config |

### 5.3 Generic Primitives (From Universal Abstractions)

**1. Document Intelligence**
- Extract facts from documents
- Relate documents (amendments, references)
- Detect gaps (missing documents, incomplete data)
- **CRE Config**: Lease schemas, rent roll schemas, DD document types

**2. Entity Resolution**
- Cross-document identity (tenants, properties, parties)
- Entity linking and disambiguation
- **CRE Config**: Tenant matching rules, property matching rules

**3. Event Management**
- Deadlines, alerts, actions, outcomes
- Event types and rules
- **CRE Config**: Lease events, covenant events, reporting deadlines

**4. Claim/Decision**
- Interpretation + evidence → recorded judgment
- Claim types and evidence requirements
- **CRE Config**: DD claims, risk claims, compliance claims

**5. Generation/Review**
- Draft → review → approve → publish
- Generation sources and review workflows
- **CRE Config**: IC materials, investor reports, lease abstracts

### 5.4 Configuration Requirements

**Schema-Based Configuration:**
- Document extraction schemas (JSON)
- Event type definitions (JSON)
- Claim type definitions (JSON)
- Calculation formulas (JSON)
- Report templates (JSON)

**Code-Based (CRE-Specific):**
- Valuation methodologies
- Market-specific rules
- Regulatory compliance logic

**Recommendation:**
- Build generic platform
- Configure for CRE via schemas
- Minimize CRE-specific code
- Enable other domains (legal, insurance, compliance)

---

## 6. Workflow ↔ UI ↔ System Mapping

### 6.1 Deal Sourcing & Screening Workflow

**Workflow Steps:**
1. Deal arrives (email, data room, broker)
2. IM extraction (property details, financials, tenancy)
3. Mandate screening (geography, size, sector, yield)
4. Initial assessment (pass/review/director review)
5. Director triage (weekly review, decisions)

**UI Components Needed:**
- ❌ DealIntakePane (missing)
- ❌ IMTriagePane (missing)
- ❌ MandateScoringPane (missing)
- ❌ DealPipelinePane (missing)
- ✅ DocumentViewerPane (exists)

**System Capabilities Needed:**
- ❌ Deal intake service (missing)
- ⚠️ Document extraction (partial)
- ❌ Mandate scoring engine (missing)
- ❌ Deal pipeline API (missing)
- ✅ Document API (exists)

**Gaps:**
- No deal intake workflow
- No mandate scoring
- No deal pipeline management
- No quick triage UI

### 6.2 Due Diligence Workflow

**Workflow Steps:**
1. Document collection (data room, requests)
2. Document organization (categorization, indexing)
3. Extraction (leases, financials, reports)
4. Issue identification (red flags, risks)
5. Issue tracking (resolution, mitigation)
6. DD report synthesis (findings, recommendations)

**UI Components Needed:**
- ✅ ArtifactBrowserPane (exists)
- ✅ DocumentViewerPane (exists)
- ✅ RunExplorerPane (exists)
- ❌ IssueTrackerPane (missing)
- ❌ DDRiskDashboardPane (missing)
- ❌ DDReportPane (missing)

**System Capabilities Needed:**
- ✅ Artifact API (exists)
- ✅ Document API (exists)
- ✅ Run API (exists)
- ⚠️ Extraction service (partial)
- ❌ Issue tracking API (missing)
- ❌ Risk detection service (missing)
- ❌ Report generation API (missing)

**Gaps:**
- No issue tracking system
- No risk detection service
- No DD report generation
- No DD-specific UI components

### 6.3 Lease Event Management Workflow

**Workflow Steps:**
1. Event detection (extract from leases)
2. Event calendar (all events across portfolio)
3. Alert generation (break notices, rent reviews)
4. Event handling (notices, negotiations, renewals)
5. Outcome recording (decisions, new terms)

**UI Components Needed:**
- ❌ EventCalendarPane (missing)
- ❌ EventAlertPane (missing)
- ❌ BreakNoticePane (missing)
- ❌ RentReviewPane (missing)
- ❌ LeaseRenewalPane (missing)

**System Capabilities Needed:**
- ❌ Event API (missing)
- ❌ Event detection service (missing)
- ❌ Deadline calculation engine (missing)
- ❌ Alert service (missing)
- ❌ Event tracking API (missing)

**Gaps:**
- **CRITICAL**: No event management system
- No event calendar UI
- No alert system
- No deadline calculation

### 6.4 Investor Reporting Workflow

**Workflow Steps:**
1. Data collection (property data, financials, ESG)
2. Data validation (accuracy, completeness)
3. Report generation (tables, charts, narrative)
4. Review and approval (internal review, sign-off)
5. Distribution (investor portal, email)

**UI Components Needed:**
- ❌ ReportGeneratorPane (missing)
- ❌ ReportReviewPane (missing)
- ❌ ReportDistributionPane (missing)
- ❌ DataValidationPane (missing)

**System Capabilities Needed:**
- ❌ Report generation API (missing)
- ❌ Data aggregation service (missing)
- ❌ Report template engine (missing)
- ❌ Review workflow API (missing)
- ❌ Distribution API (missing)

**Gaps:**
- No report generation system
- No data aggregation
- No review workflow
- No distribution system

### 6.5 Covenant Monitoring Workflow

**Workflow Steps:**
1. Covenant extraction (from loan documents)
2. Covenant tracking (current position, forecast)
3. Alert generation (approaching breach)
4. Compliance reporting (lender reports)
5. Breach management (waivers, cures)

**UI Components Needed:**
- ❌ CovenantDashboardPane (missing)
- ❌ CovenantAlertPane (missing)
- ❌ ComplianceReportPane (missing)

**System Capabilities Needed:**
- ❌ Covenant API (missing)
- ❌ Covenant extraction service (missing)
- ❌ Covenant calculation engine (missing)
- ❌ Alert service (missing)
- ❌ Compliance reporting API (missing)

**Gaps:**
- **CRITICAL**: No covenant monitoring system
- No covenant dashboard
- No alert system
- No compliance reporting

---

## 7. Integration Requirements

### 7.1 External System Integrations

**From Personas:**
- "Must integrate with Excel/Argus" (Investment Analyst)
- "Property managers use different systems" (Asset Manager)
- "Data arrives in different formats" (Asset Manager)

**Required Integrations:**

| System | Integration Type | Priority | Data Flow | Status |
|--------|-----------------|----------|-----------|--------|
| **Excel** | Export/Import | Critical | Models, reports, data | ❌ Not built |
| **Argus** | Export/Import | High | Financial models | ❌ Not built |
| **Property Management** | API/SFTP | High | Rent rolls, financials | ❌ Not built |
| **Accounting Systems** | API | High | Financials, budgets | ❌ Not built |
| **Email** | Integration | Medium | Deal intake, alerts | ❌ Not built |
| **Data Rooms** | Integration | Medium | Document import | ⚠️ Partial |
| **Banking** | API | Low | Cash positions | ❌ Not built |
| **Valuation Systems** | Export | Low | Valuation data | ❌ Not built |

### 7.2 Integration Patterns

**Export Pattern:**
- Generate Excel/CSV files
- Format for external systems
- Scheduled or on-demand

**Import Pattern:**
- Accept file uploads
- Parse and validate
- Store in system

**API Pattern:**
- REST APIs for external systems
- Authentication/authorization
- Rate limiting

**Sync Pattern:**
- Periodic sync (daily, weekly)
- Real-time sync (webhooks)
- Conflict resolution

### 7.3 Integration Priorities

**Phase 0 (Critical):**
- Excel export (models, reports)
- Excel import (data entry)

**Phase 1 (High Priority):**
- Property management system integration
- Accounting system integration
- Argus export/import

**Phase 2 (Medium Priority):**
- Email integration
- Data room integration
- Banking integration

---

## 8. Cross-Approach Synthesis

### 8.1 Alignment Matrix

| Requirement | UI Approach | Workflow Approach | System Approach | Alignment |
|-------------|-------------|-------------------|-----------------|-----------|
| **Document Extraction** | ✅ DocumentViewerPane | ✅ DD workflow | ⚠️ Partial extraction | ⚠️ Partial |
| **Event Management** | ❌ Missing | ✅ Lease events | ❌ Missing | ❌ Misaligned |
| **Covenant Monitoring** | ❌ Missing | ✅ Debt workflow | ❌ Missing | ❌ Misaligned |
| **Report Generation** | ❌ Missing | ✅ Reporting workflow | ❌ Missing | ❌ Misaligned |
| **Risk Detection** | ❌ Missing | ✅ DD workflow | ❌ Missing | ❌ Misaligned |
| **Portfolio Dashboard** | ❌ Missing | ✅ Asset mgmt | ❌ Missing | ❌ Misaligned |
| **Run Tracking** | ✅ RunExplorerPane | ✅ All workflows | ✅ Run API | ✅ Aligned |
| **Artifact Management** | ✅ ArtifactBrowserPane | ✅ All workflows | ✅ Artifact API | ✅ Aligned |

### 8.2 Critical Gaps

**1. Event Management System** (CRITICAL)
- **Workflow**: Lease events, covenant events, reporting deadlines
- **UI**: Event calendar, alerts, event handling
- **System**: Event API, deadline calculation, alert service
- **Status**: ❌ Not built (all three approaches)

**2. Covenant Monitoring** (CRITICAL)
- **Workflow**: Debt financing, ongoing monitoring
- **UI**: Covenant dashboard, alerts, compliance reports
- **System**: Covenant API, calculation engine, alert service
- **Status**: ❌ Not built (all three approaches)

**3. Report Generation** (HIGH)
- **Workflow**: Investor reporting, IC materials
- **UI**: Report generator, review interface, distribution
- **System**: Generation API, template engine, review workflow
- **Status**: ❌ Not built (all three approaches)

**4. Risk Detection** (HIGH)
- **Workflow**: Due diligence, deal screening
- **UI**: Risk dashboard, issue tracker
- **System**: Risk detection service, issue tracking API
- **Status**: ❌ Not built (all three approaches)

**5. Decision Support** (HIGH)
- **Workflow**: All decision points
- **UI**: Executive summaries, comparisons, scenario modeling
- **System**: Decision support framework, comparable analysis
- **Status**: ❌ Not built (all three approaches)

### 8.3 Well-Aligned Features

**1. Run Tracking**
- ✅ UI: RunExplorerPane
- ✅ Workflow: All workflows use runs
- ✅ System: Run API, RunEvent logging
- **Status**: ✅ Fully aligned

**2. Artifact Management**
- ✅ UI: ArtifactBrowserPane
- ✅ Workflow: All workflows use artifacts
- ✅ System: Artifact API, storage backend
- **Status**: ✅ Fully aligned

**3. Document Viewing**
- ✅ UI: DocumentViewerPane
- ✅ Workflow: All workflows view documents
- ✅ System: Document API, DocIR types
- **Status**: ✅ Fully aligned

---

## 9. Recommendations

### 9.1 Immediate Priorities (Phase 0)

**1. Event Management System** (CRITICAL)
- Build event API
- Build deadline calculation engine
- Build alert service
- Build event calendar UI
- **Rationale**: Zero tolerance for missed deadlines

**2. Covenant Monitoring** (CRITICAL)
- Build covenant API
- Build covenant extraction service
- Build covenant calculation engine
- Build covenant dashboard UI
- **Rationale**: Prevent covenant breaches

**3. Decision Support Framework** (HIGH)
- Build decision tracking system
- Build comparable analysis service
- Build executive summary generation
- Build risk detection service
- **Rationale**: Focus on decisions, not processes

### 9.2 Short-Term Priorities (Phase 1)

**4. Report Generation**
- Build report generation API
- Build template engine
- Build review workflow
- Build report generator UI

**5. Integration Layer**
- Build Excel export/import
- Build property management integration
- Build accounting system integration

**6. Trust Lifecycle**
- Build trust state tracking
- Build verification interface
- Build correction interface
- Build trust metrics dashboard

### 9.3 Medium-Term Priorities (Phase 2)

**7. Multi-Party Visibility**
- Build role-based access control
- Build multi-party views
- Build coordination features

**8. Portfolio Dashboard**
- Build portfolio API
- Build aggregation service
- Build portfolio dashboard UI

**9. Knowledge Base**
- Build knowledge API
- Build search service
- Build knowledge base UI

---

## 10. Conclusion

### 10.1 Key Findings

1. **Decision Support is Critical**: Focus on 5-minute decisions, not 100-hour processes
2. **Event Management is Missing**: Critical for lease events, covenants, deadlines
3. **Trust Lifecycle is Under-Specified**: Need trust state machine and metrics
4. **Multi-Party Visibility is Under-Analyzed**: Need role-based views and coordination
5. **Generic Platform Design**: 80% is generic, configure for CRE

### 10.2 Alignment Status

- **Well-Aligned**: Run tracking, artifact management, document viewing
- **Partially Aligned**: Document extraction, knowledge base
- **Misaligned**: Event management, covenant monitoring, report generation, risk detection

### 10.3 Next Steps

1. **Build Event Management System** (highest priority)
2. **Build Covenant Monitoring** (highest priority)
3. **Build Decision Support Framework** (high priority)
4. **Complete Trust Lifecycle** (high priority)
5. **Build Multi-Party Visibility** (medium priority)

---

*This analysis synthesizes requirements from UI, Workflow, and System approaches to identify gaps, alignments, and priorities.*
