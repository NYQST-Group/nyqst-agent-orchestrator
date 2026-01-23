# Critical Analysis: Where We're Missing the Point

*Date: 2026-01-23*
*Purpose: Identify gaps, over-specification, and universal abstractions*

---

## Part 1: Where We're Missing the Point

### 1.1 We're Describing Processes, Not Decisions

**The problem:**
The scenarios describe *what happens* in great detail, but not *where decisions actually get made* that determine outcomes.

**Example:**
We have 3 pages on DD workflow, but the actual decision points are:
1. Does this meet our mandate? (5 minutes, one person)
2. Is there a showstopper? (1 hour synthesis of 100 hours work)
3. What's the right price? (30 minutes, based on weeks of analysis)

**The fix:**
Focus on **decision support**, not process automation. The value is in the 5 minutes of decision, not the 100 hours of preparation.

---

### 1.2 We're CRE-Specific When We Should Be Generic

**The problem:**
We've written detailed CRE scenarios, but 80% of the underlying patterns are not CRE-specific:

| CRE-Specific | Actually Generic |
|--------------|------------------|
| Lease structure knowledge | Document extraction |
| Property valuation models | Deadline management |
| RICS/INREV standards | Multi-party coordination |
| Tenant credit analysis | Evidence → Claim → Decision |
| Market comparables | Mandate → Score → Route |

**The fix:**
Build generic primitives that CRE (and legal, insurance, compliance, etc.) can configure, not CRE-specific features.

---

### 1.3 We're Ignoring the 95% Failure Rate

**The research says:**
> "Only 5% of CRE firms have achieved their AI program goals—a 95% failure rate"

**We haven't asked:**
- Why do AI projects fail?
- What's different about the 5%?
- What organizational/change management factors matter?

**The likely answers:**
1. **Data quality:** AI needs clean data; CRE data is messy
2. **Integration:** Tools that don't fit workflows get abandoned
3. **Trust:** Users don't trust AI outputs
4. **Change management:** Training and adoption are afterthoughts
5. **Over-promising:** AI positioned as replacement, not assistant

**The fix:**
Build for adoption, not just capability. The product is only as good as the percentage of work that flows through it.

---

### 1.4 We're Under-Specifying Trust

**The problem:**
We say "source citations" and "audit trails" but haven't defined what trust actually requires in practice.

**What trust really means:**
1. **Verification time < manual time** — If checking AI takes as long as doing it yourself, no one will use AI
2. **Error visibility** — Users must see errors quickly, not after damage is done
3. **Correction loops** — Fixing AI must improve future AI
4. **Graceful degradation** — When AI fails, work continues

**The fix:**
Design for the skeptical user who will verify everything initially, and gradually reduce verification as trust builds.

---

### 1.5 We're Treating "Extraction" as the Hard Part

**The problem:**
We've focused heavily on extracting data from documents. But extraction is increasingly commoditized.

**The real challenges:**
1. **Interpretation** — What does this clause actually mean?
2. **Completeness** — What's NOT in the document?
3. **Conflict resolution** — When documents disagree, what governs?
4. **Change management** — When documents update, what's affected?
5. **Cross-reference** — How do documents relate to each other?

**The fix:**
Extraction is table stakes. The value is in the knowledge graph of relationships, the detection of gaps, and the interpretation support.

---

## Part 2: Where We're Under-Analyzed

### 2.1 The Actual Data Model

**What we've documented:**
- Lots of artifacts (leases, reports, IMs, etc.)
- Lots of entities mentioned in passing

**What we haven't done:**
- Defined the core entities and relationships
- Identified what's a "fact" vs an "interpretation" vs a "decision"
- Distinguished stable vs volatile data
- Mapped data lineage

**The minimal model we need:**

```
DOCUMENT (immutable source)
    └── has many → EXTRACTION (versioned, confidence-scored)
                       └── supports → CLAIM (interpretation, status)
                                          └── informs → DECISION (recorded, immutable)

ENTITY (tenant, property, fund, person)
    └── has many → ATTRIBUTE (extracted or computed)
    └── participates in → EVENT (date-anchored)

EVENT
    └── has → DEADLINE (calculated from rules)
    └── has → STATUS (pending, actioned, missed)
```

---

### 2.2 The Trust Lifecycle

**What we haven't mapped:**

```
NEW AI OUTPUT
     │
     ▼
[UNTRUSTED] ──verify──→ [ACCEPTED] ──promote──→ [AUTHORITATIVE]
     │                        │                        │
     │                        ▼                        ▼
     └──reject──→ [CORRECTED] ────────────────→ [TRAINING DATA]
```

Every AI output should have this lifecycle, not ad-hoc trust.

---

### 2.3 Multi-Party Data Visibility

**What we've glossed over:**
Different parties see different things. The same data has different views.

| Data | Owner Sees | Buyer Sees | Lender Sees | Tenant Sees |
|------|------------|------------|-------------|-------------|
| Rent | Actual | What seller disclosed | Covenant calc input | Their obligation |
| Valuation | Internal estimate | Broker opinion | LTV denominator | Not visible |
| Tenant credit | Assessment | Disclosed if material | Security assessment | Not visible |
| Break option | Risk to manage | Opportunity or risk | Cashflow risk | Their right |

**The fix:**
First-class support for role-based views of the same underlying data.

---

### 2.4 What Makes CRE Different (And What Doesn't)

**Actually CRE-specific:**
- Lease structures and market conventions
- Valuation methodologies
- Regulatory frameworks (RICS, INREV)
- Property-specific physics (buildings, locations)

**Not CRE-specific (shared with legal, insurance, compliance):**
- Document ingestion and extraction
- Deadline and event management
- Evidence → Claim → Decision patterns
- Multi-party coordination
- Audit and compliance trails

**Implication:**
Build the generic platform, configure it for CRE. Don't build a CRE platform.

---

## Part 3: Universal Abstractions

### Abstraction 1: The Extraction → Claim → Decision Cycle

**Pattern:**
```
DOCUMENT ──extract──→ FACT (with confidence)
                           │
                           ▼
                      CLAIM (interpretation)
                           │
                           ├──support──→ EVIDENCE (linked facts)
                           │
                           ▼
                      DECISION (recorded action)
```

**Why it matters:**
Every CRE workflow is a variant of this:
- DD: Documents → Facts → Issues → Investment Decision
- Lease review: Lease → Terms → Risk Claims → Approval
- Covenant monitoring: Data → Calculation → Compliance Claim → Report

**Build once, configure many:**
- Define extraction schemas per document type
- Define claim types per workflow
- Define decision types per governance model

---

### Abstraction 2: The Event → Alert → Action Cycle

**Pattern:**
```
EVENT (date-anchored)
     │
     └── has → RULE (when to alert)
                  │
                  ▼
              ALERT (tiered priority)
                  │
                  ▼
              ACTION (required response)
                  │
                  ▼
              OUTCOME (recorded result)
```

**Why it matters:**
All deadline management is this:
- Lease breaks, rent reviews, expirations
- Covenant test dates
- Reporting deadlines
- Insurance renewals
- Compliance certificates

**Build once, configure many:**
- Define event types per domain
- Define alert rules per organization
- Define action workflows per event type

---

### Abstraction 3: The Mandate → Score → Route Pattern

**Pattern:**
```
INPUT (deal, request, document)
     │
     ▼
MANDATE (criteria, thresholds, rules)
     │
     ▼
SCORE (per criterion)
     │
     ├── above threshold → AUTO-APPROVE / PROCEED
     ├── near threshold → FLAG FOR REVIEW
     └── below threshold → AUTO-REJECT / ESCALATE
```

**Why it matters:**
All screening and triage is this:
- Deal screening against investment criteria
- Consent request against loan thresholds
- Tenant against credit criteria
- Document against quality requirements

**Build once, configure many:**
- Define criteria per mandate type
- Define scoring per criterion
- Define routing per score outcome

---

### Abstraction 4: The Draft → Review → Approve → Publish Pattern

**Pattern:**
```
GENERATION (AI or human creates draft)
     │
     ▼
DRAFT (versioned, editable)
     │
     ▼
REVIEW (comments, changes, approval/rejection)
     │
     ▼
APPROVED (locked, immutable)
     │
     ▼
PUBLISHED (distributed to recipients)
```

**Why it matters:**
All document production is this:
- IC materials
- Investor reports
- Lease abstracts
- Notices and correspondence
- Valuation reports

**Build once, configure many:**
- Define generation sources per document type
- Define review workflows per governance model
- Define distribution per audience

---

### Abstraction 5: The Document Relationship Graph

**Pattern:**
```
BASE DOCUMENT
     │
     ├── amended by → AMENDMENT (ordered by date)
     ├── modified by → SIDE LETTER
     ├── superseded by → REPLACEMENT
     ├── references → OTHER DOCUMENT
     └── evidences → CLAIM

ENTITY mentioned in DOCUMENT at LOCATION
     │
     └── same as → ENTITY in OTHER DOCUMENT (resolved identity)
```

**Why it matters:**
CRE documents don't exist in isolation:
- Leases have amendments and side letters
- Loans have modifications and waivers
- Properties have title chains
- Tenants appear across multiple leases

**Build once, use everywhere:**
- Document relationship types are generic
- Entity resolution is generic
- "Current state of X" queries are generic

---

## Part 4: What This Means for the Platform

### Don't Build CRE Features, Build Primitives

| Instead of | Build |
|------------|-------|
| Lease abstraction feature | Extraction schema + CRE lease template |
| Rent review tracking | Event system + rent review event type |
| DD issue log | Claim system + DD claim types |
| IC pack generator | Draft/Review/Publish + IC template |
| Covenant calculator | Calculation engine + covenant formulas |

### The "CRE Intelligence" is Configuration

**Platform provides:**
- Document ingestion and extraction engine
- Event and deadline management
- Claim and evidence system
- Decision and audit trail
- Scoring and routing engine
- Draft/review/publish workflow

**CRE configuration provides:**
- Lease extraction schemas
- CRE event types and rules
- CRE claim types and evidence requirements
- CRE-specific calculations
- Industry templates and standards

### The Real Product is Adoption

The platform that wins is not the one with the best extraction. It's the one that:
1. **Fits into existing workflows** — Not a new system, an enhancement
2. **Earns trust gradually** — Starts as assistant, becomes essential
3. **Handles the messy reality** — Real documents, not test cases
4. **Improves from use** — Every correction makes it better
5. **Survives the skeptics** — Works even when users verify everything

---

## Part 5: Recommended Simplifications

### Delete from Scenarios

1. **Excessive process detail** — Focus on decisions, not steps
2. **CRE-specific jargon** — Use generic terms where possible
3. **Separate scenarios for similar patterns** — One pattern, multiple examples

### Add to Requirements

1. **Core data model specification**
2. **Trust lifecycle definition**
3. **Multi-party visibility model**
4. **Abstraction → Configuration framework**
5. **Adoption and change management requirements**

### Consolidate Scenarios Into

1. **Document Intelligence** (extraction, relationships, gaps)
2. **Event Management** (deadlines, alerts, actions)
3. **Decision Support** (claims, evidence, decisions)
4. **Reporting** (generation, review, publish)
5. **Coordination** (multi-party, visibility, handoffs)

Each with:
- Generic pattern
- CRE configuration example
- Other domain examples (legal, insurance)
- Trust requirements
- Adoption considerations

---

## Summary: The Three Insights

### Insight 1: It's Not About CRE

CRE is a domain configuration of generic document intelligence + event management + decision support. Build the platform, configure for CRE (and legal, and insurance, and compliance...).

### Insight 2: It's Not About Extraction

Extraction is increasingly commodity. The value is in:
- Relationships between documents
- Detection of what's missing
- Support for interpretation
- Management of change over time

### Insight 3: It's Not About AI

It's about adoption. The 95% failure rate isn't technology failure—it's adoption failure. Build for the skeptical user, earn trust gradually, integrate into existing workflows.

---

*This analysis should inform a simplification of the scenarios and a focus on the core abstractions.*
