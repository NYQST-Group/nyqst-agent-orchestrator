# Universal Abstractions: The Primitives That Replace Scenarios

*Date: 2026-01-23*
*Purpose: Define the core patterns that apply across all workflows*

---

## The Core Insight

Every CRE workflow (and legal, insurance, compliance, etc.) is a composition of five primitives:

1. **Document Intelligence** — Extract, relate, interpret
2. **Entity Resolution** — Who/what is this across documents
3. **Event Management** — Deadlines, alerts, actions
4. **Claim/Decision** — Interpretation, evidence, judgment
5. **Generation/Review** — Draft, review, approve, publish

Master these five, and every scenario is configuration.

---

## Primitive 1: Document Intelligence

### The Pattern

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DOCUMENT INTELLIGENCE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  SOURCE DOCUMENT                                                    │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────┐    ┌─────────────┐    ┌────────────┐                  │
│  │ INGEST  │───▶│  STRUCTURE  │───▶│  EXTRACT   │                  │
│  └─────────┘    └─────────────┘    └────────────┘                  │
│       │              │                   │                          │
│       ▼              ▼                   ▼                          │
│   DocStore       DocIR             Extractions                      │
│   (blobs)        (structure)       (facts + confidence)             │
│                                          │                          │
│                                          ▼                          │
│                                    ┌──────────┐                     │
│                                    │  RELATE  │                     │
│                                    └──────────┘                     │
│                                          │                          │
│                                          ▼                          │
│                                    Document Graph                   │
│                                    (relationships)                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

| Concept | Definition | Example |
|---------|------------|---------|
| **Source Document** | Immutable original file | PDF lease, scanned survey |
| **DocIR** | Structured representation (pages, blocks, spans) | Parsed lease with labeled sections |
| **Extraction** | Fact pulled from document (with confidence + location) | "Rent: $150,000" from page 5, para 3 |
| **Relationship** | Connection between documents | Amendment modifies base lease |
| **Gap** | Expected but missing information | "No service charge schedule found" |

### Extraction Schema (Generic)

```yaml
extraction_schema:
  name: string
  description: string
  fields:
    - name: string
      type: string | number | date | boolean | array | object
      required: boolean
      validation: regex | range | enum
      source_hint: string  # Where to look in document
```

### CRE Configuration Example

```yaml
extraction_schema:
  name: uk_lease_core
  description: Core terms from UK commercial lease
  fields:
    - name: tenant_name
      type: string
      required: true
      source_hint: parties clause

    - name: term_start
      type: date
      required: true

    - name: term_end
      type: date
      required: true

    - name: current_rent
      type: number
      required: true

    - name: break_options
      type: array
      items:
        type: object
        properties:
          date: date
          notice_period: duration
          conditions: array[string]
          party: enum[tenant, landlord, mutual]
```

### What This Replaces

Instead of:
- "Lease abstraction feature"
- "IM data extraction"
- "Technical report parsing"
- "Loan document extraction"

Build:
- One extraction engine
- Many extraction schemas
- Domain templates

---

## Primitive 2: Entity Resolution

### The Pattern

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ENTITY RESOLUTION                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  MENTION (in document)                                              │
│       │                                                             │
│       ▼                                                             │
│  ┌──────────┐    ┌─────────────┐    ┌────────────┐                 │
│  │ IDENTIFY │───▶│   RESOLVE   │───▶│   ENRICH   │                 │
│  └──────────┘    └─────────────┘    └────────────┘                 │
│       │                │                   │                        │
│       ▼                ▼                   ▼                        │
│   Candidate       Canonical           Enriched                      │
│   matches         entity              entity                        │
│                                                                     │
│  ENTITY TYPES:                                                      │
│  - Organization (tenant, landlord, lender, guarantor)              │
│  - Property (building, unit, land parcel)                          │
│  - Person (signatory, contact, key person)                         │
│  - Agreement (lease, loan, contract)                               │
│  - Date/Period (term, deadline, review)                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

| Concept | Definition | Example |
|---------|------------|---------|
| **Mention** | Reference to entity in a document | "ABC Limited" in lease |
| **Candidate** | Possible matching entity | ABC Limited (UK company #12345) |
| **Canonical** | Resolved single identity | Entity ID: tenant_12345 |
| **Alias** | Alternative name for same entity | "ABC Ltd", "ABC Limited", "the Tenant" |

### Resolution Rules (Generic)

```yaml
resolution_rules:
  organization:
    match_on:
      - exact_name
      - registered_number
      - address_similarity
    disambiguate_by:
      - document_context
      - jurisdiction
      - relationship_to_known_entities
```

### What This Replaces

Instead of:
- "Tenant database"
- "Property master data"
- "Contact management"

Build:
- One entity store
- Resolution rules per entity type
- Cross-document identity linking

---

## Primitive 3: Event Management

### The Pattern

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EVENT MANAGEMENT                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  SOURCE (document, system, external)                                │
│       │                                                             │
│       ▼                                                             │
│  ┌──────────┐    ┌─────────────┐    ┌────────────┐                 │
│  │  DETECT  │───▶│  CALENDAR   │───▶│   ALERT    │                 │
│  └──────────┘    └─────────────┘    └────────────┘                 │
│       │                │                   │                        │
│       ▼                ▼                   ▼                        │
│   Event            Deadlines          Notifications                 │
│   extracted        calculated         sent                          │
│                                            │                        │
│                                            ▼                        │
│                                       ┌─────────┐                   │
│                                       │ ACTION  │                   │
│                                       └─────────┘                   │
│                                            │                        │
│                                            ▼                        │
│                                       ┌─────────┐                   │
│                                       │ OUTCOME │                   │
│                                       └─────────┘                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

| Concept | Definition | Example |
|---------|------------|---------|
| **Event** | Date-anchored occurrence | Break option on 2025-03-25 |
| **Trigger Date** | When event occurs | 2025-03-25 |
| **Deadline** | When action required by | Notice by 2024-09-25 |
| **Alert Rule** | When to notify whom | Email AM at T-90, T-30, T-7 days |
| **Action** | Required response | Decide on strategy, serve notice |
| **Outcome** | What happened | Break exercised / not exercised |

### Event Type Schema (Generic)

```yaml
event_type:
  name: string
  description: string
  trigger_field: string  # Field in extraction that defines event date
  deadline_rules:
    - name: string
      calculation: expression  # e.g., "trigger_date - 6 months"
      action_required: string
  alert_rules:
    - trigger: expression  # e.g., "deadline - 90 days"
      recipients: array[role]
      priority: low | medium | high | critical
      message_template: string
```

### CRE Configuration Example

```yaml
event_type:
  name: tenant_break_option
  description: Tenant right to terminate lease early
  trigger_field: break_options[].date
  deadline_rules:
    - name: notice_deadline
      calculation: "trigger_date - break_options[].notice_period"
      action_required: "Serve break notice if exercising"
    - name: strategy_deadline
      calculation: "notice_deadline - 90 days"
      action_required: "Decide retention strategy"
  alert_rules:
    - trigger: "strategy_deadline - 30 days"
      recipients: [asset_manager]
      priority: medium
      message_template: "Break option strategy decision needed for {tenant} at {property}"
    - trigger: "notice_deadline - 7 days"
      recipients: [asset_manager, legal]
      priority: critical
      message_template: "URGENT: Break notice deadline in 7 days for {tenant}"
```

### What This Replaces

Instead of:
- "Lease event tracking"
- "Covenant monitoring"
- "Reporting deadline management"
- "Certificate expiry tracking"

Build:
- One event engine
- Many event types
- Configurable alert rules

---

## Primitive 4: Claim/Decision

### The Pattern

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLAIM / DECISION                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  EXTRACTION (fact from document)                                    │
│       │                                                             │
│       ▼                                                             │
│  ┌──────────┐    ┌─────────────┐    ┌────────────┐                 │
│  │  CLAIM   │───▶│  EVIDENCE   │───▶│  DECISION  │                 │
│  └──────────┘    └─────────────┘    └────────────┘                 │
│       │                │                   │                        │
│       ▼                ▼                   ▼                        │
│   Interpretation   Supporting          Judgment                     │
│   of fact          facts               recorded                     │
│                                                                     │
│  CLAIM TYPES:                                                       │
│  - Issue (DD finding, risk, defect)                                │
│  - Compliance (covenant met/breached, regulation satisfied)        │
│  - Interpretation (clause means X)                                 │
│  - Recommendation (suggest action Y)                               │
│                                                                     │
│  DECISION TYPES:                                                   │
│  - Acceptance (claim is valid, proceed)                            │
│  - Rejection (claim is invalid, dismiss)                           │
│  - Mitigation (claim valid, action to reduce)                      │
│  - Escalation (needs higher authority)                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

| Concept | Definition | Example |
|---------|------------|---------|
| **Claim** | Interpretation or assertion | "Break option creates vacancy risk" |
| **Evidence** | Facts that support claim | Break date, tenant %, market void |
| **Decision** | Recorded judgment | "Accept risk, adjust price by $500k" |
| **Rationale** | Why decision was made | "Tenant likely to stay based on expansion" |

### Claim Type Schema (Generic)

```yaml
claim_type:
  name: string
  description: string
  severity_levels: array[string]
  required_evidence: array[evidence_type]
  resolution_options: array[decision_type]
  escalation_rules:
    - severity: string
      requires: role
```

### CRE Configuration Example

```yaml
claim_type:
  name: dd_issue
  description: Due diligence finding requiring attention
  severity_levels:
    - showstopper    # Cannot proceed without resolution
    - material       # Requires negotiation or price adjustment
    - housekeeping   # Note for completion, minor impact
  required_evidence:
    - source_document
    - extraction_reference
    - quantification  # Optional
  resolution_options:
    - resolve_before_closing
    - price_adjustment
    - seller_indemnity
    - accept_risk
    - walk_away
  escalation_rules:
    - severity: showstopper
      requires: investment_director
    - severity: material
      requires: analyst_senior
```

### What This Replaces

Instead of:
- "DD issues log"
- "Covenant compliance tracking"
- "Risk register"
- "Approval workflows"

Build:
- One claim/decision engine
- Many claim types
- Configurable evidence and resolution

---

## Primitive 5: Generation/Review

### The Pattern

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GENERATION / REVIEW                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  INPUTS (data, extractions, claims)                                │
│       │                                                             │
│       ▼                                                             │
│  ┌──────────┐    ┌─────────────┐    ┌────────────┐    ┌─────────┐ │
│  │ GENERATE │───▶│   REVIEW    │───▶│  APPROVE   │───▶│ PUBLISH │ │
│  └──────────┘    └─────────────┘    └────────────┘    └─────────┘ │
│       │                │                   │               │       │
│       ▼                ▼                   ▼               ▼       │
│   Draft            Comments            Approved        Distributed │
│   (AI or human)    (changes)           (locked)        (sent)     │
│                                                                     │
│  OUTPUT TYPES:                                                     │
│  - Report (investor, lender, internal)                            │
│  - Summary (lease abstract, deal summary)                          │
│  - Communication (notice, letter, email)                           │
│  - Package (evidence pack, closing bundle)                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

| Concept | Definition | Example |
|---------|------------|---------|
| **Template** | Structure for generated output | Quarterly investor report template |
| **Draft** | Initial version (AI or human) | Generated Q3 report |
| **Review** | Comments, edits, approval/rejection | "Update market section" |
| **Approval** | Sign-off that locks version | Director approved |
| **Distribution** | Delivery to recipients | Sent to investor portal |

### Output Type Schema (Generic)

```yaml
output_type:
  name: string
  template: template_reference
  inputs:
    - name: string
      source: extraction | claim | computed | external
  review_workflow:
    stages:
      - name: string
        reviewers: array[role]
        required_approvals: number
  distribution:
    channels: array[channel]
    recipients: array[role | explicit]
```

### CRE Configuration Example

```yaml
output_type:
  name: quarterly_investor_report
  template: templates/investor_quarterly.md
  inputs:
    - name: nav_data
      source: computed
    - name: performance_metrics
      source: computed
    - name: portfolio_summary
      source: extraction
    - name: market_commentary
      source: external
  review_workflow:
    stages:
      - name: draft_review
        reviewers: [fund_manager]
        required_approvals: 1
      - name: compliance_review
        reviewers: [compliance]
        required_approvals: 1
      - name: final_approval
        reviewers: [cio]
        required_approvals: 1
  distribution:
    channels: [investor_portal, email]
    recipients: [all_investors]
```

### What This Replaces

Instead of:
- "IC pack generation"
- "Investor reporting module"
- "Lease summary generator"
- "Notice drafting"

Build:
- One generation/review engine
- Many output templates
- Configurable workflows

---

## How Scenarios Become Configurations

### Example: Lease Break Option (Before)

**Previous approach:** 3-page scenario describing the entire workflow.

### Example: Lease Break Option (After)

**Primitive composition:**

```yaml
workflow:
  name: lease_break_management
  components:

    # Document Intelligence
    extraction:
      schema: uk_lease_core
      relationship: amendment_modifies_base

    # Event Management
    events:
      - type: tenant_break_option
        source: extraction.break_options

    # Claim/Decision
    claims:
      - type: retention_decision
        trigger: event.strategy_deadline
        options: [retain, let_go, negotiate]

    # Generation
    outputs:
      - type: break_notice
        trigger: decision.let_go
        template: templates/break_notice.md
```

**Result:** The entire workflow is defined in ~20 lines of configuration, not 20 pages of scenario.

---

## The Platform Architecture Implied

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CONFIGURATION LAYER                          │
│  (CRE schemas, event types, claim types, templates)                │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        PRIMITIVE ENGINES                            │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐       │
│  │ Document  │  │  Entity   │  │   Event   │  │   Claim   │       │
│  │   Intel   │  │Resolution │  │   Mgmt    │  │ /Decision │       │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘       │
│  ┌───────────┐                                                      │
│  │Generation │                                                      │
│  │  /Review  │                                                      │
│  └───────────┘                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        SUBSTRATE LAYER                              │
│  (Artifacts, Manifests, Pointers, Run Ledger)                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Next Steps

1. **Define primitive schemas formally** — JSON Schema or similar
2. **Create CRE configuration pack** — The schemas, event types, claim types, templates
3. **Identify non-CRE domains** — Legal, insurance, compliance configurations
4. **Design configuration UI** — How users customize without code
5. **Build primitive engines** — The reusable core

---

*This abstraction should eliminate the need for scenario-per-workflow documentation.*
