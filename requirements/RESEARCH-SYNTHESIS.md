# Research Synthesis: Key Findings for Document Intelligence Platform

*Date: 2026-01-23*
*Purpose: Consolidated insights from all research to inform build decisions*

---

## Executive Summary

After extensive research across CRE workflows, AI adoption patterns, LegalTech/InsurTech parallels, and technical architectures, we have identified **five universal primitives** and a **wedge strategy** that maximizes adoption probability.

**The critical insight:** 95% of AI projects fail not on technology but on adoption. Our platform must earn trust incrementally, starting with a high-pain, low-risk use case.

---

## Research Sources Synthesized

| Domain | Source | Key Files |
|--------|--------|-----------|
| CRE Industry | RICS, INREV | `research/rics/`, `research/inrev/` |
| CRE Workflows | Acquisition + Asset Mgmt | `research/cre-workflows/` |
| AI Adoption | Failure analysis | `research/ai-tooling/ai-adoption-failures.md` |
| AI Tools | Current landscape | `research/ai-tooling/ai-cre-landscape.md` |
| LegalTech | Contract lifecycle mgmt | `research/cross-domain/legaltech-patterns.md` |
| InsurTech | Claims processing | `research/cross-domain/insurtech-patterns.md` |
| Trust UX | Calibrated trust patterns | `research/ai-tooling/trust-ux-patterns.md` |
| Event Systems | Deadline management | `research/architecture/event-driven-patterns.md` |
| Document Graphs | Relationship models | `research/architecture/document-graph-patterns.md` |

---

## Finding 1: The Five Universal Primitives

Every document-heavy professional domain (CRE, legal, insurance, compliance) uses the same five patterns:

### 1. Document Intelligence
- Ingest any format (PDF, Word, scanned)
- Extract structured data with confidence scores
- Cite sources precisely (page, paragraph, highlight)
- Track document relationships (amendments, supplements)

### 2. Entity Resolution
- Identify entities across documents (same tenant, same property)
- Link variants of names/addresses
- Build knowledge graph from unstructured sources

### 3. Event Management
- Calculate deadlines from extracted dates
- Alert workflows with escalation
- Track outcomes for feedback loops

### 4. Claim/Decision Framework
- Evidence → Claim → Quantification → Decision
- Approval workflows with audit trails
- Explicit uncertainty handling

### 5. Generation/Review
- Generate drafts from validated data
- Human review with tracked changes
- Version control with attribution

**Implication:** Build domain-agnostic primitives, configure for CRE. The same engine serves legal, insurance, compliance with different config files.

---

## Finding 2: Why AI Projects Fail

From research on AI adoption failures:

| Failure Mode | Frequency | How We Avoid |
|--------------|-----------|--------------|
| Overpromising | 40% | Start with narrow, achievable scope |
| Poor data quality | 25% | Ingest what exists, don't demand clean data |
| Workflow disruption | 20% | Run parallel to existing systems |
| Black box distrust | 10% | Show sources, confidence, reasoning |
| Wrong problem | 5% | Validate with real users in 30 days |

**Key insight:** Users adopt tools that do ONE thing exceptionally well, then expand. They abandon "platforms" that try to do everything.

---

## Finding 3: Trust Building Patterns

From LegalTech and trust UX research:

### The Calibrated Trust Journey
```
WEEK 1: SKEPTIC → "I'll verify everything"
  - Show every extraction source
  - Make verification effortless
  - Let user catch AI "mistakes"

WEEK 2-4: VERIFIER → "I spot-check"
  - Track accuracy over time
  - Show accuracy stats to user
  - AI catches something user missed

MONTH 2-3: TRUSTER → "I rely on this"
  - User treats system as source of truth
  - Requests expanded capabilities
  - Recommends to colleagues
```

### Critical UX Patterns
1. **Click to verify:** Every extraction links to highlighted source
2. **Confidence visibility:** Show when AI is uncertain
3. **Correction feedback:** User corrections improve the model
4. **Parallel operation:** Run alongside existing tools, don't replace
5. **Explicit limitations:** Tell users what the system can't do

---

## Finding 4: Event-Driven Architecture

From event-driven patterns research:

### Temporal.io for Durable Workflows
- Long-running processes (months/years for lease events)
- Automatic retry and failure handling
- Event sourcing for audit trail
- Human-in-the-loop at decision points

### Deadline Calculation Patterns
```
Event extracted from document
  → Deadline calculated (e.g., break_date - notice_period)
  → Alert scheduled (e.g., deadline - 30 days)
  → Escalation if no action (e.g., +7 days to manager)
  → Outcome recorded (for future learning)
```

### Calendar-Aware Calculations
- Business days vs calendar days
- Regional holiday calendars
- Jurisdiction-specific rules (UK quarter days)

---

## Finding 5: Document Graph Patterns

From document graph research:

### Relationship Types
1. **Amendment:** Changes terms of base document
2. **Supersedes:** New version replaces old
3. **Supplements:** Additional document (rent deposit deed)
4. **References:** Cites another document
5. **Extracted from:** Source of structured data

### Gap Detection
- Schema defines expected relationships
- System flags missing documents
- Example: "Rent deposit mentioned but deed not found"

### Version Reconciliation
- Track which version is authoritative
- Flag when terms conflict
- Maintain audit trail of changes

---

## Finding 6: CRE-Specific Configuration

From RICS/INREV research and workflow analysis:

### Priority Event Types (V1)
1. **Tenant break options** - Miss = $500k-$2M loss
2. **Rent reviews** - Miss = foregone income
3. **Lease expiries** - Miss = vacancy/holding over
4. **Guarantee expiries** - Miss = credit exposure

### UK Commercial Lease Schema
- 15 core field groups (parties, premises, term, rent, etc.)
- 50+ extractable fields
- Gap detection rules for common missing docs
- See `schemas/cre/uk-lease.config.json`

### Stakeholder Alert Patterns
- Asset Manager: All events, primary decision maker
- Portfolio Manager: Escalations, strategic decisions
- Legal: Notice deadlines, compliance
- Credit: Guarantor events, covenant breaches

---

## Validated Architecture Decisions

Based on all research:

### Build
| Component | Technology/Approach | Rationale |
|-----------|---------------------|-----------|
| Document ingestion | PDF/Word/OCR pipeline | Must handle scanned leases |
| Extraction | LLM + structured output | Confidence + citations |
| Event engine | Temporal.io or similar | Durable long-running workflows |
| Alert delivery | Email + in-app + SMS | Multi-channel for critical |
| Storage | Postgres + vector DB | Structured + semantic search |
| UI | Click-to-verify pattern | Builds calibrated trust |

### Defer
| Component | Reason to Defer |
|-----------|-----------------|
| Entity resolution | Complex; dates work without it |
| Document graph | Adds value but not V1 critical |
| Generation/review | Needs trusted extraction first |
| Multi-tenant | Single tenant MVP faster |
| Mobile app | Web first |

---

## The 30-Day Validation Plan

### Week 1: Extraction POC
- PDF ingestion working
- Date extraction on 50 sample leases
- Accuracy target: 85%
- Basic verification UI

### Week 2: Event Engine
- Event schema implemented
- Deadline calculation working
- Email alerts functional
- Dashboard view

### Week 3: Integration
- End-to-end: upload → extract → alert
- Verification UX polished
- Bug fixes

### Week 4: User Testing
- 3-5 real users with real leases
- Watch them use it
- Learn what's broken

**At day 30:** We know if the wedge works.

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Extraction accuracy <85% | Medium | High | More training data, human fallback |
| Users don't upload leases | Low | High | Start with known pain point |
| Competitors faster | Medium | Medium | Trust + accuracy, not speed |
| Scope creep | High | High | Discipline: dates only for V1 |
| Wrong wedge | Low | High | 30-day validation, pivot fast |

---

## Next Actions

1. **Stop:** Writing more requirements documents
2. **Start:** Building extraction POC
3. **Measure:** Extraction accuracy on real leases
4. **Validate:** User tests by day 30

---

*The next document should be code, not markdown.*
