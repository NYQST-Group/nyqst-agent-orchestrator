# Analysis Gaps & Missing Analysis

*Date: 2026-01-23*  
*Purpose: Identify what hasn't been analyzed and what additional analysis is needed*

---

## Executive Summary

This document compares:
1. **What has been analyzed** (from REQUIREMENTS_ANALYSIS.md)
2. **What hasn't been reviewed** (files/documents not analyzed)
3. **What analysis is missing** (to extract maximum value from the 3 approaches)

---

## 1. What Has Been Analyzed ✅

### 1.1 Code Analysis (Complete)
- ✅ UI Components (React/TypeScript)
- ✅ Backend Models (Python/SQLAlchemy)
- ✅ API Endpoints (FastAPI)
- ✅ Services & Repositories
- ✅ MCP Tools
- ✅ Storage Backend
- ✅ Authentication & Authorization
- ✅ Database Migrations
- ✅ Configuration (config.py, docker-compose.yml)

### 1.2 Schema Analysis (Complete)
- ✅ Document schema (document.schema.json)
- ✅ Event schema (event.schema.json)
- ✅ Claim schema (claim.schema.json)
- ✅ CRE-specific configs (lease-events.config.json, uk-lease.config.json)

### 1.3 Type System Analysis (Complete)
- ✅ TypeScript types (core.ts, evidence.ts, events.ts, docir.ts, knowledge.ts)
- ✅ Type mismatches identified (Claim, Evidence, Event conflicts)

### 1.4 Research Analysis (Partial)
- ✅ Trust UX patterns (research/ai-tooling/trust-ux-patterns.md)
- ✅ Event-driven patterns (research/architecture/event-driven-patterns.md)
- ✅ AI adoption failures (research/ai-tooling/ai-adoption-failures.md - referenced)
- ⚠️ Document graph patterns (research/architecture/document-graph-patterns.md - not read)
- ⚠️ CRE workflows (research/cre-workflows/ - partially read)
- ⚠️ Cross-domain patterns (research/cross-domain/ - not read)
- ⚠️ RICS standards (research/rics/rics-standards-summary.md - not read)
- ⚠️ INREV guidelines (research/inrev/inrev-guidelines-summary.md - not read)

### 1.5 Documentation Analysis (Partial)
- ✅ UI Architecture (docs/UI_ARCHITECTURE.md)
- ✅ Research Synthesis (docs/RESEARCH_SYNTHESIS.md - referenced)
- ✅ Refactoring Opportunities (docs/REFACTORING_OPPORTUNITIES.md - referenced)
- ⚠️ README (README.md - partially read)

### 1.6 Requirements Analysis (Partial)
- ✅ What to Build First (requirements/WHAT-TO-BUILD-FIRST.md)
- ✅ Universal Abstractions (requirements/UNIVERSAL-ABSTRACTIONS.md - partially read)
- ✅ Safety Requirements (requirements/ai-specific/safety-requirements.md)
- ✅ AI Value Opportunities (requirements/ai-specific/ai-value-opportunities.md - referenced)
- ⚠️ Critical Analysis (requirements/CRITICAL-ANALYSIS.md - partially read)
- ⚠️ Research Consolidation Gates (requirements/research-consolidation-gates.md - not read)

### 1.7 Scenario Analysis (Partial)
- ✅ Lease Event Management (scenarios/asset-management/01-lease-event-management.md)
- ✅ Due Diligence Workflow (scenarios/acquisition/02-due-diligence-workflow.md - partially read)
- ⚠️ Deal Sourcing & Screening (scenarios/acquisition/01-deal-sourcing-screening.md - not read)
- ⚠️ Transaction Closing (scenarios/acquisition/03-transaction-closing-handover.md - not read)
- ⚠️ Debt Financing (scenarios/acquisition/04-debt-financing-workflow.md - not read)
- ⚠️ Investor Reporting (scenarios/asset-management/02-investor-reporting.md - not read)
- ⚠️ Stakeholder Perspectives (scenarios/journeys/stakeholder-perspectives.md - not read)
- ✅ User Personas (scenarios/personas/cre-user-personas.md - just read)

---

## 2. What Hasn't Been Reviewed ❌

### 2.1 Research Documents (Not Analyzed)
- ❌ `research/architecture/document-graph-patterns.md` - Document relationship patterns
- ❌ `research/cre-workflows/acquisition-workflows.md` - Full acquisition workflow analysis
- ❌ `research/cre-workflows/asset-management-workflows.md` - Full asset management analysis
- ❌ `research/cross-domain/insurtech-patterns.md` - Insurance domain patterns
- ❌ `research/cross-domain/legaltech-patterns.md` - Legal domain patterns
- ❌ `research/rics/rics-standards-summary.md` - RICS compliance requirements
- ❌ `research/inrev/inrev-guidelines-summary.md` - INREV reporting requirements
- ❌ `research/ai-tooling/ai-cre-landscape.md` - Competitive landscape

### 2.2 Scenario Documents (Not Analyzed)
- ❌ `scenarios/acquisition/01-deal-sourcing-screening.md` - Deal screening workflow
- ❌ `scenarios/acquisition/03-transaction-closing-handover.md` - Closing workflow
- ❌ `scenarios/acquisition/04-debt-financing-workflow.md` - Debt financing workflow
- ❌ `scenarios/asset-management/02-investor-reporting.md` - Reporting workflow
- ❌ `scenarios/journeys/stakeholder-perspectives.md` - Multi-stakeholder views

### 2.3 Requirements Documents (Not Analyzed)
- ❌ `requirements/CRITICAL-ANALYSIS.md` - Full critical analysis (only partially read)
- ❌ `requirements/research-consolidation-gates.md` - Research gates and validation
- ❌ `requirements/RESEARCH-SYNTHESIS.md` - Research synthesis requirements

### 2.4 Configuration & Deployment (Not Analyzed)
- ❌ `.env.example` - Environment variable requirements
- ❌ `alembic.ini` - Migration configuration
- ❌ `tailwind.config.js` - UI styling requirements
- ❌ `vite.config.ts` - Build configuration
- ❌ `tsconfig.json` - TypeScript configuration
- ❌ Test files (`tests/`, `src/test/`) - Testing requirements

### 2.5 Index/Reference Documents (Not Analyzed)
- ❌ `USER-SCENARIOS-INDEX.md` - Scenario index and mapping
- ❌ `schemas/README.md` - Schema documentation

---

## 3. What Analysis Is Missing 🔍

### 3.1 Persona-to-Feature Mapping

**Missing Analysis:**
- Map each persona's pain points to specific features/components
- Identify which personas need which UI components
- Determine persona-specific workflows vs. shared workflows
- Map trust requirements per persona

**Why It Matters:**
- Investment Analyst needs: IM triage, data extraction, model building
- Asset Manager needs: Lease event management, reporting, portfolio dashboard
- Investment Director needs: Executive summaries, risk flags, deal comparisons
- Different personas = different UI priorities

**What to Analyze:**
- Which UI components serve which personas?
- Which workflows are persona-specific vs. universal?
- What trust/verification requirements differ by persona?

### 3.2 Workflow-to-UI Mapping

**Missing Analysis:**
- Map workflow steps to UI components
- Identify workflow gaps (steps without UI support)
- Determine workflow-specific UI patterns
- Map workflow decision points to UI interactions

**Why It Matters:**
- Due diligence workflow has 10+ steps, but only some have UI
- Lease event management workflow needs calendar UI (not implemented)
- Deal screening workflow needs quick triage UI (not implemented)

**What to Analyze:**
- For each workflow scenario, what UI components are needed?
- What workflow steps have no UI support?
- What workflow steps have partial UI support?
- What workflow steps require new UI patterns?

### 3.3 Decision Point Analysis

**Missing Analysis:**
- Identify actual decision points in workflows (not just process steps)
- Map decision support requirements
- Determine what information is needed for each decision
- Identify decision-making personas and their needs

**Why It Matters:**
- Critical Analysis says: "We're describing processes, not decisions"
- Real value is in decision support (5 minutes) not process automation (100 hours)
- Need to understand: What decisions? Who makes them? What info needed?

**What to Analyze:**
- What are the key decision points in each workflow?
- What information is needed for each decision?
- Who makes each decision?
- What UI/features support each decision?
- What's missing for decision support?

### 3.4 Trust Lifecycle Analysis

**Missing Analysis:**
- Map trust state machine (UNTRUSTED → VERIFYING → ACCEPTED → AUTHORITATIVE)
- Identify trust transition requirements
- Determine trust metrics and tracking
- Map trust requirements to UI patterns

**Why It Matters:**
- Critical Analysis identifies trust lifecycle as missing
- Trust is not binary - it's a progression
- Need to understand: How does trust build? What enables trust? What breaks trust?

**What to Analyze:**
- What are the trust states for each AI output type?
- What triggers trust state transitions?
- What UI patterns support trust building?
- What metrics track trust progression?
- How do corrections improve trust?

### 3.5 Multi-Party Visibility Analysis

**Missing Analysis:**
- Map data visibility by role (Owner, Buyer, Lender, Tenant)
- Identify role-based view requirements
- Determine what data is visible to whom
- Map multi-party coordination requirements

**Why It Matters:**
- Critical Analysis identifies multi-party visibility as under-analyzed
- Same data has different views for different parties
- Need to understand: Who sees what? What's hidden? What's shared?

**What to Analyze:**
- What data is visible to each role?
- What data is hidden from each role?
- What data is shared between roles?
- What UI patterns support role-based views?
- What coordination features are needed?

### 3.6 CRE-Specific vs. Generic Analysis

**Missing Analysis:**
- Identify what's CRE-specific vs. generic
- Map generic patterns to CRE configurations
- Determine what should be configurable vs. hardcoded
- Identify domain-specific requirements

**Why It Matters:**
- Critical Analysis says: "80% of patterns are not CRE-specific"
- Should build generic platform, configure for CRE
- Need to understand: What's CRE-specific? What's generic? How to configure?

**What to Analyze:**
- What features are CRE-specific (lease structures, valuation)?
- What features are generic (extraction, deadlines, claims)?
- How should generic features be configured for CRE?
- What domain-specific configs are needed?
- What should be in schemas vs. code?

### 3.7 Integration Requirements Analysis

**Missing Analysis:**
- Map external system integrations (Excel, Argus, property management systems)
- Identify integration patterns and requirements
- Determine API requirements for integrations
- Map data sync requirements

**Why It Matters:**
- Personas mention: "Must integrate with Excel/Argus"
- Integration is critical for adoption
- Need to understand: What integrations? How? What data?

**What to Analyze:**
- What external systems need integration?
- What data flows between systems?
- What APIs are needed for integrations?
- What sync patterns are required?
- What's the integration priority?

### 3.8 Performance & Scale Requirements

**Missing Analysis:**
- Identify performance requirements (response times, throughput)
- Determine scale requirements (documents, users, concurrent operations)
- Map performance requirements to architecture decisions
- Identify performance bottlenecks

**Why It Matters:**
- UI components mention: "60fps with 1000+ elements"
- Need to understand: What performance is required? At what scale?

**What to Analyze:**
- What are the performance requirements per feature?
- What are the scale requirements (documents, users)?
- What are the concurrent operation limits?
- What are the response time requirements?
- What architecture supports these requirements?

### 3.9 Testing Requirements Analysis

**Missing Analysis:**
- Map testing requirements from code structure
- Identify test coverage gaps
- Determine testing patterns needed
- Map testing to requirements validation

**Why It Matters:**
- Safety requirements mention: "99.9% detection rate for critical dates"
- Need to understand: How to test? What to test? What's the test strategy?

**What to Analyze:**
- What testing infrastructure exists?
- What test coverage is needed?
- What testing patterns are required?
- How to test AI accuracy?
- How to test trust/verification workflows?

### 3.10 Business Model & Strategy Analysis

**Missing Analysis:**
- Map business model requirements (pricing, quotas, billing)
- Identify go-to-market strategy requirements
- Determine product strategy (wedge strategy, expansion path)
- Map business requirements to technical requirements

**Why It Matters:**
- "What to Build First" mentions wedge strategy
- Need to understand: How does business model affect requirements?

**What to Analyze:**
- What's the pricing model?
- What are the quota/billing requirements?
- What's the go-to-market strategy?
- What's the expansion path?
- How do business requirements affect technical requirements?

---

## 4. Cross-Approach Analysis Gaps 🔄

### 4.1 UI Approach vs. Workflow Approach

**Missing Analysis:**
- Compare UI component requirements to workflow step requirements
- Identify UI components that don't support workflows
- Identify workflow steps without UI support
- Map UI patterns to workflow patterns

**Example Gaps:**
- UI has EvidenceCanvas, but no workflow uses evidence canvas
- Workflow needs event calendar, but UI doesn't have calendar component
- UI has ChatPane, but no workflow defines chat interactions

**What to Analyze:**
- Which UI components support which workflows?
- Which workflows have no UI support?
- Which UI components have no workflow use case?
- What UI patterns are missing for workflows?

### 4.2 Workflow Approach vs. System Approach

**Missing Analysis:**
- Compare workflow requirements to system capabilities
- Identify workflow steps that system can't support
- Identify system capabilities not used by workflows
- Map workflow patterns to system patterns

**Example Gaps:**
- Workflow needs event detection, but system has no event service
- System has MCP tools, but workflows don't define agent interactions
- Workflow needs deadline calculation, but system has no deadline engine

**What to Analyze:**
- Which workflows can the system support?
- Which workflows require new system capabilities?
- Which system capabilities are unused by workflows?
- What system patterns are missing for workflows?

### 4.3 System Approach vs. UI Approach

**Missing Analysis:**
- Compare system capabilities to UI component requirements
- Identify system capabilities without UI
- Identify UI components without backend support
- Map system APIs to UI components

**Example Gaps:**
- System has Run API, UI has RunExplorerPane ✅
- System has no Event API, UI has no EventCalendar ❌
- System has no Claim API, UI has EvidenceCanvas ❌

**What to Analyze:**
- Which system capabilities have UI support?
- Which system capabilities need UI?
- Which UI components need backend support?
- What APIs are missing for UI components?

### 4.4 All Three Approaches: Decision Support

**Missing Analysis:**
- Map decision points across all three approaches
- Identify decision support requirements
- Determine what information/UI/system support is needed for decisions
- Map decision patterns to features

**Why It Matters:**
- Critical Analysis emphasizes: "Focus on decision support, not process automation"
- Need to understand: What decisions? What support needed?

**What to Analyze:**
- What are the key decision points?
- What information is needed for each decision?
- What UI supports each decision?
- What system capabilities support each decision?
- What's missing for decision support?

---

## 5. Specific Files to Analyze 📄

### 5.1 High Priority (Critical for Requirements)

1. **`scenarios/acquisition/01-deal-sourcing-screening.md`**
   - Deal screening workflow
   - IM triage requirements
   - Quick decision support needs

2. **`scenarios/asset-management/02-investor-reporting.md`**
   - Reporting workflow
   - Data aggregation requirements
   - Multi-stakeholder view needs

3. **`requirements/CRITICAL-ANALYSIS.md`** (full read)
   - Decision point analysis
   - Trust lifecycle requirements
   - Multi-party visibility requirements
   - CRE-specific vs. generic analysis

4. **`scenarios/journeys/stakeholder-perspectives.md`**
   - Multi-stakeholder workflows
   - Role-based requirements
   - Coordination needs

5. **`research/architecture/document-graph-patterns.md`**
   - Document relationship patterns
   - Graph requirements
   - Relationship types

### 5.2 Medium Priority (Important for Completeness)

6. **`scenarios/acquisition/03-transaction-closing-handover.md`**
   - Closing workflow
   - Handover requirements

7. **`scenarios/acquisition/04-debt-financing-workflow.md`**
   - Debt financing workflow
   - Lender requirements

8. **`research/cre-workflows/acquisition-workflows.md`**
   - Full acquisition analysis

9. **`research/cre-workflows/asset-management-workflows.md`**
   - Full asset management analysis

10. **`research/rics/rics-standards-summary.md`**
    - RICS compliance requirements
    - Reporting standards

### 5.3 Lower Priority (Supporting Context)

11. **`research/inrev/inrev-guidelines-summary.md`**
    - INREV reporting requirements

12. **`research/cross-domain/insurtech-patterns.md`**
    - Cross-domain patterns

13. **`research/cross-domain/legaltech-patterns.md`**
    - Cross-domain patterns

14. **`requirements/research-consolidation-gates.md`**
    - Research validation gates

15. **`USER-SCENARIOS-INDEX.md`**
    - Scenario mapping

---

## 6. Analysis Patterns to Apply 🔬

### 6.1 Decision Point Extraction

**For each workflow scenario:**
1. Identify decision points (not just process steps)
2. Map decision maker (persona)
3. Identify information needed
4. Map to UI/system support
5. Identify gaps

### 6.2 Trust Requirement Mapping

**For each AI output type:**
1. Map trust state machine
2. Identify verification requirements
3. Map to UI patterns
4. Identify trust metrics
5. Map correction loops

### 6.3 Multi-Party Visibility Mapping

**For each data type:**
1. Map visibility by role
2. Identify hidden data
3. Identify shared data
4. Map to UI patterns
5. Identify coordination needs

### 6.4 CRE-Specific vs. Generic Mapping

**For each feature:**
1. Identify if CRE-specific or generic
2. Map to configuration requirements
3. Identify domain-specific needs
4. Map to schema vs. code
5. Identify abstraction opportunities

### 6.5 Integration Requirement Mapping

**For each external system:**
1. Identify integration type (API, file, sync)
2. Map data flows
3. Identify API requirements
4. Map sync patterns
5. Identify priority

---

## 7. Recommended Next Steps 🎯

### 7.1 Immediate (Complete Missing Analysis)

1. **Read and analyze Critical Analysis document** (full)
   - Extract decision point requirements
   - Extract trust lifecycle requirements
   - Extract multi-party visibility requirements
   - Extract CRE-specific vs. generic analysis

2. **Read and analyze remaining scenario documents**
   - Deal sourcing & screening
   - Transaction closing
   - Debt financing
   - Investor reporting
   - Stakeholder perspectives

3. **Read and analyze persona document** (already read, need to map)
   - Map personas to features
   - Map personas to workflows
   - Map personas to UI components
   - Map personas to trust requirements

### 7.2 Short-term (Cross-Approach Analysis)

4. **Map workflows to UI components**
   - Which workflows have UI support?
   - Which workflows need UI?
   - Which UI components support workflows?

5. **Map workflows to system capabilities**
   - Which workflows can system support?
   - Which workflows need new capabilities?
   - Which system capabilities are unused?

6. **Map UI components to system APIs**
   - Which UI components have backend support?
   - Which UI components need APIs?
   - Which APIs need UI?

### 7.3 Medium-term (Deep Analysis)

7. **Decision point analysis**
   - Extract all decision points
   - Map decision support requirements
   - Identify gaps

8. **Trust lifecycle analysis**
   - Map trust state machines
   - Map trust requirements
   - Identify trust patterns

9. **Multi-party visibility analysis**
   - Map role-based views
   - Identify visibility requirements
   - Map coordination needs

10. **CRE-specific vs. generic analysis**
    - Categorize all features
    - Map configuration requirements
    - Identify abstraction opportunities

---

## 8. Expected Value from Missing Analysis 💎

### 8.1 Decision Support Focus

**Value:**
- Shift from process automation to decision support
- Focus on high-value 5-minute decisions vs. 100-hour processes
- Build features that actually matter

**Example:**
- Instead of: "Automate entire DD workflow"
- Focus on: "Support the 3 key decisions in DD"

### 8.2 Trust Requirements Clarity

**Value:**
- Understand how trust actually builds
- Design UI patterns that support trust progression
- Build verification workflows that are faster than manual

**Example:**
- Instead of: "Show confidence scores"
- Focus on: "Make verification faster than manual work"

### 8.3 Multi-Party Coordination

**Value:**
- Understand role-based requirements
- Build features that support multi-party workflows
- Design data visibility correctly

**Example:**
- Instead of: "Show all data to everyone"
- Focus on: "Show right data to right people at right time"

### 8.4 Generic Platform Design

**Value:**
- Build generic platform, configure for CRE
- Enable other domains (legal, insurance, compliance)
- Reduce CRE-specific code

**Example:**
- Instead of: "Build lease-specific features"
- Focus on: "Build generic event management, configure for leases"

### 8.5 Integration Requirements

**Value:**
- Understand what integrations are critical
- Build APIs that support integrations
- Enable adoption through integration

**Example:**
- Instead of: "Build standalone platform"
- Focus on: "Integrate with Excel/Argus/property management systems"

---

*This gap analysis should guide the next phase of requirements analysis to extract maximum value from all three approaches (UI, workflows, holistic system).*
