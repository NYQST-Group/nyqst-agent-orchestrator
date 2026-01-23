# AI Safety Requirements for CRE Intelligence Platform

*Date: 2026-01-23*
*Status: Initial specification*

---

## Core Philosophy: Safer Than the Alternative

The goal is not "perfect AI" but "AI that reduces total errors compared to the current process."

### Current State (Human-Only)

| Risk | Frequency | Impact |
|------|-----------|--------|
| Missed lease break deadline | 2-5% annually | $500k-$2M per incident |
| Missed rent review trigger | 5-10% | $50k-$500k per incident |
| Data extraction error | 3-5% of fields | Variable |
| Report errors | 5-10% of reports | Reputational |
| Covenant calculation error | 2-5% | Lender relationship, potential default |

### Target State (AI-Assisted)

| Risk | Target | Approach |
|------|--------|----------|
| Missed lease break deadline | <0.1% | AI detection + human confirmation + redundant alerting |
| Missed rent review trigger | <0.5% | AI extraction + calendaring + alerts |
| Data extraction error | <1% | AI extraction + confidence scoring + human review for low confidence |
| Report errors | <2% | AI draft + human review |
| Covenant calculation error | 0% | Deterministic calculation + audit trail |

---

## Safety Requirement Categories

### Category 1: Critical Dates and Deadlines

**Requirement:** The system MUST NOT miss critical dates.

**Implementation:**
- Multi-source extraction (lease + amendments + correspondence)
- Redundant alerting (email + dashboard + push)
- Escalation on non-acknowledgment
- Audit trail of all alerts sent and acknowledged
- Configurable lead times per event type

**Testing:**
- Golden set of complex leases with known dates
- Deliberate obfuscation testing (dates buried in text)
- Amendment override testing
- False positive rate monitoring

**Acceptance Criteria:**
- 99.9% detection rate for critical dates in test corpus
- Zero missed dates in production after human review
- <5% false positive rate

---

### Category 2: Financial Calculations

**Requirement:** Financial calculations MUST be deterministic and auditable.

**Implementation:**
- Rule-based calculation engines (not ML for core calcs)
- Input validation and source linking
- Calculation methodology per loan/lease documented
- Step-by-step audit trail
- Reconciliation tools vs external calculations

**Testing:**
- Known-answer test cases
- Edge case coverage (partial periods, amendments, FX)
- Reconciliation against lender/external calculations
- Round-trip verification

**Acceptance Criteria:**
- 100% reproducibility (same inputs = same outputs)
- Complete audit trail for any calculation
- Variance explanations for external reconciliation

---

### Category 3: Data Extraction

**Requirement:** Extracted data MUST be verifiable and confidence-scored.

**Implementation:**
- Source citation for every extracted field (document, page, location)
- Confidence score per extraction
- Configurable thresholds for auto-accept vs human review
- Visual highlighting in source document
- Correction capture and feedback loop

**Testing:**
- Precision/recall on annotated test corpus
- Cross-document consistency
- Amendment handling
- Format variation tolerance

**Acceptance Criteria:**
- Per-field accuracy targets (see table below)
- <10% of extractions requiring human correction
- Confidence calibration: 95% of "high confidence" extractions are correct

**Accuracy Targets by Field Type:**

| Field Type | Accuracy Target | Human Review Threshold |
|------------|-----------------|------------------------|
| Dates | >99% | Always for critical dates |
| Currency amounts | >98% | <95% confidence |
| Tenant names | >99% | <90% confidence |
| Area measurements | >97% | <90% confidence |
| Free text clauses | >90% | All unusual provisions |

---

### Category 4: Document Intelligence

**Requirement:** The system MUST handle document complexity correctly.

**Implementation:**
- Amendment/side letter relationship detection
- Version tracking and conflict resolution
- "As-of" document state reconstruction
- Gap detection (referenced but missing documents)
- Multi-document entity resolution

**Testing:**
- Complex lease stacks (base + multiple amendments)
- Conflicting provisions across documents
- Missing document handling
- Date-based document state queries

**Acceptance Criteria:**
- Correct relationship detection in 95% of cases
- Gap detection for all referenced documents
- Clear uncertainty flagging for conflicts

---

### Category 5: Monitoring and Alerting

**Requirement:** The system MUST NOT fail silently.

**Implementation:**
- Health monitoring for all AI components
- Alert on extraction failures or timeouts
- Dashboard visibility for system status
- Graceful degradation with manual fallback
- SLA tracking and reporting

**Testing:**
- Failure injection testing
- Load testing beyond normal parameters
- Recovery time verification
- Alert delivery verification

**Acceptance Criteria:**
- <1% undetected failures
- <5 minute detection time for component failures
- 99.9% alert delivery rate
- Clear fallback procedures documented

---

### Category 6: Human-in-the-Loop

**Requirement:** Critical actions MUST require human confirmation.

**Implementation:**

| Action Category | Human Requirement |
|-----------------|-------------------|
| Critical date extraction | Confirmation required |
| Covenant calculation for reporting | Review before submission |
| Consent threshold triggers | Confirmation before action |
| Report publication | Approval workflow |
| Data correction | Audit trail, optional approval |

**Testing:**
- Workflow enforcement testing
- Bypass attempt detection
- Audit trail completeness

**Acceptance Criteria:**
- 100% enforcement of required approvals
- Complete audit trail for all human actions
- Clear accountability assignment

---

### Category 7: Confidentiality and Access Control

**Requirement:** Data MUST be isolated and access controlled.

**Implementation:**
- Tenant/client data isolation
- Role-based access control
- Audit logging for all data access
- No cross-client ML training without consent
- Data retention and deletion controls

**Testing:**
- Cross-tenant access attempt testing
- Permission enforcement verification
- Audit log completeness
- Data deletion verification

**Acceptance Criteria:**
- Zero cross-tenant data exposure
- 100% audit log coverage
- Verified data deletion within SLA

---

## Failure Mode Analysis

### Failure Mode 1: Missed Critical Date

**Scenario:** Break option deadline passes without notification.

**Consequence:** $500k-$2M financial loss.

**Prevention:**
1. Multiple extraction sources
2. Confidence flagging
3. Human confirmation requirement
4. Redundant notification channels
5. Escalation on non-acknowledgment
6. Periodic audit of upcoming events

**Detection:**
- Dashboard showing events without confirmation
- Automated audit of events that have passed

**Recovery:**
- Incident investigation
- Root cause analysis
- System improvement

---

### Failure Mode 2: Incorrect Extraction Accepted

**Scenario:** Rent figure extracted incorrectly, used in valuation model.

**Consequence:** Incorrect investment decision.

**Prevention:**
1. Confidence scoring
2. Source citation
3. Cross-validation (rent roll vs lease)
4. Anomaly detection (unusual values)

**Detection:**
- Reconciliation against other data sources
- Variance analysis in downstream usage
- User correction feedback

**Recovery:**
- Correction mechanism
- Impact assessment
- Downstream update propagation

---

### Failure Mode 3: System Unavailable

**Scenario:** Platform unavailable during critical reporting period.

**Consequence:** Missed reporting deadlines.

**Prevention:**
1. High availability architecture
2. Data export/backup
3. Documented manual procedures
4. SLA monitoring

**Detection:**
- Uptime monitoring
- User-reported issues
- Alert systems

**Recovery:**
- Fallback to manual procedures
- Data recovery from backups
- Post-incident review

---

## Safety Metrics Dashboard

**Real-time Monitoring:**
- Extraction accuracy (rolling 7-day)
- Critical date detection rate
- Human override rate
- System availability
- Alert delivery rate

**Periodic Review:**
- Monthly accuracy audits
- Quarterly incident review
- Annual safety assessment

**Reporting:**
- Safety metrics in product reporting
- Incident disclosure to affected clients
- Continuous improvement tracking

---

## Professional Liability Considerations

### Clear Boundaries

| AI Provides | Human Provides |
|-------------|----------------|
| Data extraction | Verification of critical data |
| Alerting | Decision to act |
| Draft analysis | Final judgment |
| Calculations | Sign-off on outputs |

### Documentation Requirements

- All AI outputs marked as "AI-assisted"
- Human review/approval tracked
- Source citations available
- Methodology transparent
- Limitations documented

### Terms of Use

- AI as assistant, not advisor
- Human responsibility for decisions
- Accuracy targets disclosed (not guaranteed)
- Feedback mechanism for errors
- Clear escalation path

---

*This document should be reviewed with legal/compliance and updated based on operational experience.*
