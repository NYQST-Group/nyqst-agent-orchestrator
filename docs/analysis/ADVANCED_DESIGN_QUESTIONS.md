# Advanced Design Questions & Strategic Decisions

*Date: 2026-01-23*  
*Purpose: Extract critical design questions requiring strategic decisions*

---

## Executive Summary

This document identifies **advanced design questions** that require strategic decisions, based on analysis of:
- UI architecture patterns (rigid vs flexible)
- Persona needs (analyst vs director vs manager)
- Trust requirements (verification vs autonomy)
- Adoption strategy (wedge vs platform)
- Technical architecture (consistency vs flexibility)

**Key Finding**: The answers are **NOT obvious**—they require trade-off analysis and strategic choices based on target users, adoption path, and technical constraints.

---

## 1. Rigid GUI vs Flexible GUI: Where Are the Boundaries?

### 1.1 The Question

**Should the UI be:**
- **Rigid**: Fixed layouts, predefined workflows, consistent experience
- **Flexible**: User-configurable panes, dynamic layouts, adaptable workflows
- **Hybrid**: Rigid core + flexible extensions

### 1.2 Current State Analysis

**What We Have:**
- **UI Architecture** proposes: Multi-pane IDE with resizable panels, dynamic pane types, layout persistence
- **Research Synthesis** proposes: **Tiered Dynamism** (3 tiers: hardwired → declarative → fully dynamic)
- **Workbench Shell** implements: Dynamic pane loading, layout persistence, command palette

**What We Don't Have:**
- Clear boundaries between rigid and flexible
- Persona-specific UI requirements
- Adoption path implications

### 1.3 Persona Analysis: Who Needs What?

| Persona | UI Flexibility Need | Rationale | Risk of Too Flexible |
|---------|---------------------|-----------|---------------------|
| **Investment Analyst** | **Medium** | Needs to adapt to different deal types, but consistency helps speed | Overwhelmed by options, slows down |
| **Investment Director** | **Low** | Needs executive view, not customization. Time-pressed, wants predictability | Wastes time configuring, wants "just works" |
| **Asset Manager** | **High** | Manages diverse portfolios, different workflows per asset type | Needs flexibility but within guardrails |
| **Property Manager** | **Low** | Repetitive tasks, wants consistency and speed | Configuration overhead kills adoption |
| **Transactions Lawyer** | **Medium** | Different document types, but needs reliable patterns | Too flexible = inconsistent quality |

**Insight**: **Flexibility needs vary by persona and task frequency.**

### 1.4 The Tiered Dynamism Model (From Research)

```
TIER 1: Hardwired (Rigid)
├── Authentication
├── Payment/Billing
├── Audit Logs
├── Compliance Gates
└── Approval Workflows
→ Zero agent discretion, maximum reliability

TIER 2: Declarative/Schema-Driven (Flexible Structure, Rigid Components)
├── Pane Assembly (agent chooses panes, user arranges)
├── Dashboard Layouts (user configurable)
├── Report Templates (schema-driven)
└── Workflow Steps (configurable sequence)
→ Flexible arrangement, finite component set

TIER 3: Fully Dynamic (Sandboxed)
├── Code Generation (preview only)
├── Prototyping (experimental)
└── Custom Visualizations (user-created)
→ Maximum flexibility, maximum risk mitigation
```

### 1.5 Strategic Decision Framework

**Question 1: What Should Be Rigid?**

**Candidates for Rigid:**
- ✅ **Core Navigation** (always know where you are)
- ✅ **Trust Indicators** (confidence, source citations always visible)
- ✅ **Approval Gates** (can't bypass governance)
- ✅ **Data Entry Forms** (consistency prevents errors)
- ✅ **Critical Actions** (delete, publish, approve - need confirmation)

**Rationale**: **Trust and safety require consistency.**

**Question 2: What Should Be Flexible?**

**Candidates for Flexible:**
- ✅ **Pane Layouts** (users arrange what they need)
- ✅ **Dashboard Widgets** (choose what to see)
- ✅ **View Filters** (personal preferences)
- ✅ **Workflow Steps** (skip optional steps)
- ✅ **Report Sections** (include/exclude sections)

**Rationale**: **Efficiency requires personalization.**

**Question 3: Where Is the Boundary?**

**Proposed Boundary:**
- **Rigid**: Anything affecting **trust, safety, or data integrity**
- **Flexible**: Anything affecting **efficiency or personal preference**
- **Hybrid**: **Structure is flexible, components are rigid**

**Example:**
- ✅ **Flexible**: User arranges panes (RunExplorer left, DocumentViewer right)
- ✅ **Rigid**: RunExplorer always shows confidence scores
- ✅ **Flexible**: User chooses which event types to filter
- ✅ **Rigid**: Event extraction always shows source document

### 1.6 Adoption Implications

**Wedge Strategy (Phase 1):**
- **Start Rigid**: Fixed layout for "Critical Dates" feature
- **Rationale**: Users learning new tool need consistency
- **Risk**: Too rigid = feels limiting
- **Mitigation**: Add flexibility after trust is earned

**Platform Strategy (Phase 2+):**
- **Add Flexibility**: User-configurable dashboards, layouts
- **Rationale**: Power users want customization
- **Risk**: Too flexible = overwhelming, inconsistent
- **Mitigation**: Provide templates, sensible defaults

### 1.7 Recommendation

**Hybrid Approach with Clear Boundaries:**

1. **Core Workbench**: Rigid structure (sidebar, main area, status bar)
2. **Pane Layout**: Flexible arrangement (user arranges panes)
3. **Pane Content**: Rigid components (RunExplorer always shows same data structure)
4. **Configuration**: Flexible preferences (filters, views, defaults)
5. **Critical Actions**: Rigid workflows (approval gates, confirmations)

**Boundary Rule**: **"If it affects trust or safety, it's rigid. If it affects efficiency, it's flexible."**

---

## 2. Decision Support vs Process Automation: What's the Mix?

### 2.1 The Question

**Should the platform focus on:**
- **Decision Support**: Help humans make better decisions (5 minutes)
- **Process Automation**: Automate entire workflows (100 hours)
- **Hybrid**: Automate prep, support decisions

### 2.2 Current Analysis

**CRITICAL-ANALYSIS Finding:**
> "We're describing processes, not decisions. The value is in the 5 minutes of decision, not the 100 hours of preparation."

**CROSS_MAPPING Finding:**
> "Focus on decision support, not process automation."

**WHAT-TO-BUILD-FIRST Finding:**
> "Wedge strategy: Win one job (critical dates), then expand."

### 2.3 Decision Point Analysis

**Critical Decision Points (5 minutes each):**
1. **Deal Pursuit**: Does this meet our mandate? (Investment Director)
2. **Break Notice**: Should we exercise the break? (Asset Manager)
3. **IC Approval**: Do we approve this deal? (Investment Committee)
4. **Rent Review**: What's our negotiation strategy? (Asset Manager)
5. **Covenant Test**: Are we compliant? (Fund Manager)

**Preparation Work (100 hours each):**
1. **Due Diligence**: Extract data, analyze documents, synthesize findings
2. **Lease Abstraction**: Extract all terms, normalize, verify
3. **Model Building**: Build financial models, populate assumptions
4. **Report Generation**: Compile data, format, distribute
5. **Portfolio Monitoring**: Track events, calculate deadlines, generate alerts

### 2.4 Strategic Decision

**Recommendation: Hybrid with Clear Separation**

**Automate (Process):**
- ✅ **Data Extraction** (documents → structured data)
- ✅ **Event Detection** (documents → events → deadlines)
- ✅ **Alert Generation** (deadlines → alerts → notifications)
- ✅ **Report Compilation** (data → formatted reports)
- ✅ **Monitoring** (continuous tracking, anomaly detection)

**Support (Decisions):**
- ✅ **Risk Flagging** (show risks, don't decide)
- ✅ **Comparable Analysis** (show comparables, don't price)
- ✅ **Scenario Modeling** (show outcomes, don't choose)
- ✅ **Evidence Synthesis** (show evidence, don't interpret)
- ✅ **Recommendation** (suggest, don't execute)

**Boundary Rule**: **"Automate preparation, support decisions. Never automate decisions that have consequences."**

### 2.5 Persona-Specific Mix

| Persona | Automation Need | Decision Support Need |
|---------|------------------|----------------------|
| **Investment Analyst** | **High** (extraction, data entry) | **Medium** (flag issues, don't decide) |
| **Investment Director** | **Low** (has analysts) | **High** (needs synthesis for decisions) |
| **Asset Manager** | **High** (monitoring, alerts) | **High** (break decisions, rent reviews) |
| **Property Manager** | **High** (reports, compliance) | **Low** (routine tasks) |
| **Transactions Lawyer** | **High** (abstraction, extraction) | **Medium** (flag issues, don't interpret) |

**Insight**: **Different personas need different automation/decision support mixes.**

---

## 3. Trust Lifecycle: How Rigid Should Trust Be?

### 3.1 The Question

**Should trust be:**
- **Rigid**: Fixed trust states, strict transitions, no shortcuts
- **Flexible**: User-controlled trust, can skip verification, gradual building
- **Adaptive**: System learns trust patterns, adjusts requirements

### 3.2 Current State

**CRITICAL-ANALYSIS Proposed Lifecycle:**
```
NEW AI OUTPUT
     │
     ▼
[UNTRUSTED] ──verify──→ [ACCEPTED] ──promote──→ [AUTHORITATIVE]
     │                        │                        │
     │                        ▼                        ▼
     └──reject──→ [CORRECTED] ────────────────→ [TRAINING DATA]
```

**Research Synthesis Finding:**
> "Trust Calibration: Begin supervised, gain autonomy through demonstrated reliability"

**WHAT-TO-BUILD-FIRST Trust Journey:**
- Week 1: Skeptic (verify everything)
- Week 2-4: Verifier (spot-check)
- Month 2-3: Truster (rely on alerts)
- Month 4+: Advocate (can't work without it)

### 3.3 Strategic Decision

**Recommendation: Adaptive Trust with Rigid Boundaries**

**Rigid (Never Skip):**
- ✅ **Critical Actions** (break notices, approvals) → Always require verification
- ✅ **High-Stakes Outputs** (IC materials, investor reports) → Always require review
- ✅ **First-Time Use** (new extraction type) → Always verify initially

**Flexible (User Controls):**
- ✅ **Low-Stakes Outputs** (internal notes, drafts) → User can skip verification
- ✅ **Repeated Patterns** (same extraction, proven accurate) → Auto-trust after N successes
- ✅ **Personal Preferences** (user sets own trust thresholds)

**Adaptive (System Learns):**
- ✅ **Accuracy Tracking** (system tracks verification results)
- ✅ **Confidence Calibration** (system learns which extractions are reliable)
- ✅ **User Patterns** (system learns user's verification habits)

**Boundary Rule**: **"Critical = rigid trust. Routine = flexible trust. System learns from both."**

---

## 4. Generic Primitives vs CRE-Specific Features: What's the Mix?

### 4.1 The Question

**Should the platform be:**
- **Generic**: Universal primitives, configure for CRE
- **CRE-Specific**: Built-in CRE knowledge, workflows, templates
- **Hybrid**: Generic core + CRE configuration layer

### 4.2 Current Analysis

**CRITICAL-ANALYSIS Finding:**
> "80% of patterns are not CRE-specific. Build generic primitives, configure for CRE."

**CROSS_MAPPING Finding:**
> "CRE-Specific: Lease structures, valuation, RICS standards. Generic: Extraction, events, claims, decisions."

**WHAT-TO-BUILD-FIRST Finding:**
> "Build for the wedge, design for the platform. Schemas are right, implement incrementally."

### 4.3 Strategic Decision

**Recommendation: Generic Core + CRE Configuration**

**Generic (Platform Provides):**
- ✅ **Document Extraction Engine** (works for any document type)
- ✅ **Event Management System** (works for any deadline)
- ✅ **Claim/Evidence/Decision Framework** (works for any domain)
- ✅ **Deadline Calculation Engine** (works for any rule)
- ✅ **Alert System** (works for any event)

**CRE Configuration (Domain Layer):**
- ✅ **Lease Extraction Schemas** (CRE-specific fields)
- ✅ **CRE Event Types** (break options, rent reviews)
- ✅ **CRE Claim Types** (covenant breaches, lease risks)
- ✅ **CRE Calculations** (rent review formulas, covenant tests)
- ✅ **CRE Templates** (lease abstracts, IC materials)

**Boundary Rule**: **"Platform = generic. Domain = configuration. Never hardcode domain logic in platform."**

### 4.4 Adoption Implications

**Wedge Strategy (Phase 1):**
- **Start CRE-Specific**: "Critical Dates" is CRE-focused
- **Rationale**: Users need to see immediate value
- **Risk**: Too generic = feels incomplete
- **Mitigation**: Generic under the hood, CRE-specific on top

**Platform Strategy (Phase 2+):**
- **Expand to Generic**: Add legal, insurance, compliance configurations
- **Rationale**: Platform value increases with more domains
- **Risk**: Too generic = loses CRE focus
- **Mitigation**: Maintain CRE as primary domain, add others incrementally

---

## 5. UI Architecture: Multi-Pane IDE vs Traditional Forms?

### 5.1 The Question

**Should the UI be:**
- **IDE-Like**: Multi-pane workbench, resource URIs, dynamic layouts
- **Traditional**: Forms, wizards, fixed workflows
- **Hybrid**: IDE for power users, simplified for casual users

### 5.2 Current State

**UI_ARCHITECTURE Proposes:**
- Multi-pane IDE with resizable panels
- Resource URI navigation
- Dynamic pane loading
- Real-time SSE updates

**Persona Analysis:**
- **Investment Analyst**: Needs IDE (multiple documents, comparisons)
- **Investment Director**: Needs simplified (executive summary, not details)
- **Property Manager**: Needs forms (routine tasks, not exploration)

### 5.3 Strategic Decision

**Recommendation: Adaptive UI Based on Task**

**IDE Mode (Power Users, Complex Tasks):**
- ✅ **Due Diligence** (multiple documents, comparisons)
- ✅ **Lease Analysis** (document + extraction + claims)
- ✅ **Portfolio Analysis** (multiple assets, dashboards)
- ✅ **Research Sessions** (exploration, discovery)

**Simplified Mode (Casual Users, Routine Tasks):**
- ✅ **Event Calendar** (simple list/calendar view)
- ✅ **Alert Dashboard** (cards, notifications)
- ✅ **Quick Actions** (approve, reject, comment)
- ✅ **Report Viewing** (read-only, formatted)

**Hybrid Mode (Progressive Disclosure):**
- ✅ **Start Simple**: Show summary, hide details
- ✅ **Expand on Demand**: Click to see full IDE
- ✅ **Remember Preference**: User chooses default mode

**Boundary Rule**: **"Complex tasks = IDE. Simple tasks = forms. User chooses."**

---

## 6. Real-Time vs On-Demand: What Updates When?

### 6.1 The Question

**Should updates be:**
- **Real-Time**: SSE streams, live updates, immediate feedback
- **On-Demand**: Polling, refresh buttons, user-initiated
- **Hybrid**: Real-time for critical, on-demand for background

### 6.2 Current State

**UI_ARCHITECTURE Proposes:**
- SSE for run events, artifact updates
- Real-time for critical actions
- Polling fallback

**Persona Needs:**
- **Investment Analyst**: Real-time for active runs, on-demand for browsing
- **Asset Manager**: Real-time for alerts, on-demand for reports
- **Investment Director**: On-demand (not watching, just reviewing)

### 6.3 Strategic Decision

**Recommendation: Context-Aware Update Strategy**

**Real-Time (Always):**
- ✅ **Active Run Events** (user is watching)
- ✅ **Critical Alerts** (deadlines, approvals)
- ✅ **Collaborative Edits** (multiple users)
- ✅ **Status Changes** (run completion, approval)

**On-Demand (User Initiated):**
- ✅ **Historical Data** (past runs, archived events)
- ✅ **Reports** (generated on request)
- ✅ **Search Results** (query-based)
- ✅ **Background Processing** (not user-facing)

**Hybrid (Smart):**
- ✅ **Real-Time When Active**: If user is viewing, stream updates
- ✅ **On-Demand When Inactive**: If user is away, refresh on return
- ✅ **Batch Updates**: Group updates, reduce noise

**Boundary Rule**: **"User is watching = real-time. User is browsing = on-demand. System optimizes."**

---

## 7. Autonomy Slider: How Much Control Should Users Have?

### 7.1 The Question

**Should AI autonomy be:**
- **Fixed**: System determines autonomy level
- **User-Controlled**: Slider for each task type
- **Adaptive**: System learns from user behavior

### 7.2 Current State

**Research Synthesis Finding:**
> "Autonomy Slider: Let users control AI independence level (tab completion → suggestions → full agent mode)"

**Persona Analysis:**
- **Investment Analyst**: Wants control (verify everything)
- **Investment Director**: Wants delegation (let AI do prep)
- **Asset Manager**: Wants automation (routine tasks)

### 7.3 Strategic Decision

**Recommendation: Per-Task Autonomy with Adaptive Learning**

**Fixed Autonomy (Never Change):**
- ✅ **Critical Actions** (approvals, publishes) → Always require confirmation
- ✅ **High-Stakes Outputs** (IC materials) → Always require review
- ✅ **First-Time Tasks** → Always supervised

**User-Controlled Autonomy:**
- ✅ **Per Task Type** (extraction = high, generation = low)
- ✅ **Per User Preference** (skeptic = low, truster = high)
- ✅ **Per Context** (deal = low, research = high)

**Adaptive Autonomy:**
- ✅ **Learn from Accuracy** (if extractions are 95%+ accurate, suggest higher autonomy)
- ✅ **Learn from User Behavior** (if user always approves, suggest auto-approve)
- ✅ **Learn from Corrections** (if user corrects often, reduce autonomy)

**Boundary Rule**: **"Critical = fixed. Routine = user-controlled. System suggests based on performance."**

---

## 8. Data Model: Immutable vs Mutable?

### 8.1 The Question

**Should data be:**
- **Immutable**: Git-like versioning, append-only, audit trail
- **Mutable**: Traditional CRUD, updates in place
- **Hybrid**: Immutable core (artifacts, events), mutable views (pointers, claims)

### 8.2 Current State

**Substrate Architecture:**
- **Artifacts**: Immutable (content-addressed)
- **Manifests**: Immutable (content-addressed)
- **Pointers**: Mutable (HEAD references)
- **Runs**: Immutable (append-only events)

**Schemas:**
- **Events**: Immutable (append-only)
- **Claims**: Mutable (status changes)
- **Decisions**: Immutable (recorded, can't change)

### 8.3 Strategic Decision

**Recommendation: Immutable Core + Mutable Views**

**Immutable (Never Change):**
- ✅ **Artifacts** (documents, files)
- ✅ **Manifests** (snapshots)
- ✅ **Run Events** (audit trail)
- ✅ **Decisions** (recorded judgments)
- ✅ **Extractions** (what was extracted, when)

**Mutable (Can Update):**
- ✅ **Pointers** (current HEAD)
- ✅ **Claims** (status, owner, notes)
- ✅ **Events** (status, outcomes)
- ✅ **User Preferences** (layout, filters)

**Hybrid (Versioned):**
- ✅ **Claims** (status changes create new versions)
- ✅ **Events** (outcome updates append to history)
- ✅ **Reports** (draft → approved → published)

**Boundary Rule**: **"Source data = immutable. Interpretations = mutable. Changes = versioned."**

---

## 9. Integration Strategy: Deep vs Shallow?

### 9.1 The Question

**Should integrations be:**
- **Deep**: Full sync, bidirectional, embedded workflows
- **Shallow**: Export/import, one-way, standalone
- **Hybrid**: Deep for critical, shallow for optional

### 9.2 Current State

**CROSS_MAPPING Integration Requirements:**
- Excel, Argus, Property Management, Accounting, Email, Data Rooms, Banking, Valuation Systems

**Persona Needs:**
- **Investment Analyst**: Deep Excel integration (export rent rolls)
- **Asset Manager**: Shallow integrations (export reports)
- **Property Manager**: Deep integrations (sync with property management system)

### 9.3 Strategic Decision

**Recommendation: Shallow First, Deep Later**

**Shallow (Phase 1):**
- ✅ **Export to Excel** (one-way, user-initiated)
- ✅ **Email Alerts** (one-way notifications)
- ✅ **PDF Reports** (export, not sync)
- ✅ **API Access** (external systems pull data)

**Deep (Phase 2+):**
- ✅ **Excel Sync** (bidirectional, live updates)
- ✅ **Property Management Sync** (automatic, scheduled)
- ✅ **Accounting Integration** (transaction sync)
- ✅ **Data Room Integration** (automatic uploads)

**Boundary Rule**: **"Start shallow (export). Add depth (sync) after trust is earned. Never force integration."**

---

## 10. Winning Strategies: What Are the Clear Winners?

### 10.1 Decisions That Are Clear Winners

**1. Wedge Strategy (Start Narrow, Expand)**
- ✅ **Winner**: Start with "Critical Dates" (high pain, clear value)
- ✅ **Rationale**: Adoption requires focus, not breadth
- ✅ **Risk**: Too narrow = limited value
- ✅ **Mitigation**: Expand after trust is earned

**2. Generic Primitives + Domain Configuration**
- ✅ **Winner**: Build generic platform, configure for CRE
- ✅ **Rationale**: 80% is generic, 20% is CRE-specific
- ✅ **Risk**: Too generic = feels incomplete
- ✅ **Mitigation**: Start CRE-specific, reveal generic later

**3. Trust Through Verification**
- ✅ **Winner**: Start with verification, earn trust gradually
- ✅ **Rationale**: Skeptical users need to verify initially
- ✅ **Risk**: Too much verification = slow adoption
- ✅ **Mitigation**: Reduce verification as accuracy improves

**4. Decision Support Over Process Automation**
- ✅ **Winner**: Automate preparation, support decisions
- ✅ **Rationale**: Value is in decisions, not processes
- ✅ **Risk**: Too much automation = users feel replaced
- ✅ **Mitigation**: Always show human is in control

**5. Immutable Core + Mutable Views**
- ✅ **Winner**: Source data immutable, interpretations mutable
- ✅ **Rationale**: Trust requires auditability
- ✅ **Risk**: Too immutable = can't correct errors
- ✅ **Mitigation**: Corrections create new versions, don't delete

### 10.2 Decisions That Need More Analysis

**1. Rigid vs Flexible GUI**
- ⚠️ **Unclear**: Depends on persona and task
- **Need**: User testing to determine boundaries
- **Recommendation**: Start rigid, add flexibility based on feedback

**2. IDE vs Forms UI**
- ⚠️ **Unclear**: Depends on task complexity
- **Need**: Task analysis to determine which tasks need IDE
- **Recommendation**: Hybrid - IDE for complex, forms for simple

**3. Real-Time vs On-Demand**
- ⚠️ **Unclear**: Depends on user context
- **Need**: Usage analytics to determine what needs real-time
- **Recommendation**: Context-aware - real-time when active, on-demand when browsing

**4. Autonomy Level**
- ⚠️ **Unclear**: Depends on user trust and task risk
- **Need**: Trust metrics to determine optimal autonomy
- **Recommendation**: Per-task autonomy with adaptive learning

**5. Integration Depth**
- ⚠️ **Unclear**: Depends on user needs and system capabilities
- **Need**: User interviews to determine integration priorities
- **Recommendation**: Start shallow, add depth based on demand

---

## 11. Summary: Key Design Questions Requiring Decisions

### 11.1 Must Decide Now (Blocking Implementation)

1. **GUI Flexibility Boundaries**
   - What is rigid? (trust, safety, governance)
   - What is flexible? (layout, preferences, views)
   - **Decision Needed**: Clear boundary rules

2. **Trust Lifecycle**
   - What requires verification? (critical actions)
   - What can auto-trust? (routine, proven accurate)
   - **Decision Needed**: Trust state machine

3. **UI Architecture**
   - IDE for all? (too complex)
   - Forms for all? (too limiting)
   - **Decision Needed**: Task-based UI mode selection

### 11.2 Can Decide Later (Non-Blocking)

1. **Autonomy Slider**
   - Can start with fixed autonomy, add slider later
   - **Decision Needed**: Phase 2

2. **Integration Depth**
   - Can start with shallow, add depth later
   - **Decision Needed**: Phase 2+

3. **Real-Time Strategy**
   - Can start with on-demand, add real-time later
   - **Decision Needed**: Based on usage patterns

### 11.3 Recommendations

**Immediate Decisions:**
1. **Hybrid GUI**: Rigid core + flexible layout + rigid components
2. **Adaptive Trust**: Rigid for critical, flexible for routine, adaptive learning
3. **Task-Based UI**: IDE for complex, forms for simple, user chooses

**Deferred Decisions:**
1. **Autonomy Slider**: Start fixed, add control based on user feedback
2. **Integration Depth**: Start shallow, add depth based on demand
3. **Real-Time Strategy**: Start on-demand, add real-time based on usage

**Winning Strategies:**
1. ✅ **Wedge Strategy**: Start narrow, expand
2. ✅ **Generic Primitives**: Build platform, configure domain
3. ✅ **Trust Through Verification**: Start skeptical, earn trust
4. ✅ **Decision Support**: Automate prep, support decisions
5. ✅ **Immutable Core**: Source immutable, views mutable

---

## 12. Next Steps: How to Make These Decisions

### 12.1 User Research Needed

1. **GUI Flexibility**: Test rigid vs flexible with target personas
2. **UI Architecture**: Test IDE vs forms with different task types
3. **Trust Lifecycle**: Test verification requirements with skeptical users
4. **Autonomy Level**: Test different autonomy levels, measure trust building

### 12.2 Prototype Testing

1. **Build MVP**: Critical Dates feature with rigid GUI
2. **Test with Users**: Measure adoption, identify pain points
3. **Iterate**: Add flexibility where users request it
4. **Measure**: Track trust building, accuracy, adoption

### 12.3 Decision Framework

**For Each Design Question:**
1. **Identify Trade-offs**: What are the pros/cons?
2. **Test with Users**: What do personas prefer?
3. **Measure Impact**: How does it affect adoption?
4. **Iterate**: Adjust based on feedback

**Decision Rule**: **"Start conservative (rigid, simple, verified). Add flexibility based on user demand and trust metrics."**

---

*These design questions require strategic decisions, but the answers are not obvious. They require user research, prototyping, and iterative refinement based on real usage patterns.*
