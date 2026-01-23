# Workflow Scenario: Debt Financing and Ongoing Loan Management

*Date: 2026-01-23*
*Personas: Investment Director, Analyst, Treasury/Finance, Legal, Lender*
*Phase: Acquisition Financing + Ongoing Debt Management*

---

## The Debt Reality in CRE

### Typical Leverage Structures

| Strategy | LTV Range | Debt Type | Complexity |
|----------|-----------|-----------|------------|
| Core | 30-45% | Investment grade, long-term | Lower |
| Core-Plus | 45-55% | Bank/insurance | Medium |
| Value-Add | 55-70% | Transitional/bridge | Higher |
| Opportunistic | 60-80% | Mezzanine, structured | Highest |

### Scale of Documentation

Typical acquisition financing:
- **Loan documents:** 200-500 pages
- **Conditions precedent:** 50-100 items
- **Ongoing covenants:** 20-50 requirements
- **Reporting requirements:** Quarterly at minimum
- **Amendment/consent requests:** 5-15 per loan life

---

## Stage 1: Debt Origination (Acquisition Financing)

### Lender Selection and Term Sheet

**What happens:**
1. **Financing strategy set:**
   - Target leverage
   - Debt structure (senior/mezz, fixed/floating, recourse)
   - Term and amortization
   - Prepayment flexibility
2. **Lender outreach:**
   - Information memorandum to lenders
   - Lender questions and site visits
   - Term sheet negotiation
3. **Term sheet signed:**
   - Headline terms agreed
   - Exclusivity period
   - Deposit/commitment fee

**Stakeholder perspectives:**

| Stakeholder | Primary Concern | Information Needs |
|-------------|-----------------|-------------------|
| Investment Director | Optimal structure, execution certainty | Market terms, lender appetite |
| CFO/Treasury | Cost of capital, risk management | All-in cost, hedge requirements |
| Analyst | Model accuracy | Final terms for financial model |
| Legal | Documentation, conditions | Term sheet for review |
| Lender | Credit quality, risk | Property DD, sponsor track record |

**Pain points:**
- Multiple lenders, multiple term sheets
- Terms not always comparable
- Commitment timelines misaligned with transaction
- Fee structures complex and varied

---

### Due Diligence (Lender's Perspective)

**What the lender requires:**
1. **Property DD:**
   - Valuation (lender's own, or approved valuer)
   - Technical/building survey
   - Environmental assessment
   - Legal title review
2. **Tenant DD:**
   - Rent roll verification
   - Tenant credit analysis
   - Lease review (key terms impacting security)
3. **Sponsor DD:**
   - Financial statements
   - Track record
   - Corporate structure
   - Management team
4. **Market DD:**
   - Market report
   - Comparable transactions
   - Supply/demand dynamics

**Pain points:**
- Lender DD overlaps with buyer DD (but not identical)
- Different valuers, different values
- Information requests fragmented
- Lender timeline often shorter than transaction

---

### Loan Documentation

**Key documents:**
1. **Facility Agreement:**
   - Loan amount, currency
   - Interest (margin, reference rate)
   - Fees (commitment, arrangement, exit)
   - Repayment and prepayment
   - Covenants (financial and non-financial)
   - Events of default
   - Representations and warranties
2. **Security documents:**
   - Mortgage/charge over property
   - Share charge (if SPV structure)
   - Assignment of rents
   - Assignment of insurance
   - Account pledges
3. **Corporate documents:**
   - Board resolutions
   - Certificate of incumbency
   - Legal opinions
4. **Hedging documents (if required):**
   - ISDA master agreement
   - Interest rate swap/cap confirmation

**Pain points:**
- Negotiation of 500+ pages of documentation
- Cross-referencing between documents
- CP lists that grow during negotiation
- Definitions inconsistent across documents

---

### Conditions Precedent (CP) Satisfaction

**Typical CPs for drawdown:**
1. **Documentary:**
   - Executed facility agreement
   - Executed security documents
   - Legal opinions
   - Corporate authorizations
2. **Property-related:**
   - Satisfactory valuation
   - Insurance in place
   - Property management agreement
   - Lease documentation
3. **Financial:**
   - Equity contribution
   - Hedging in place (if required)
   - Opening financial covenants satisfied
4. **Technical:**
   - Environmental report
   - Building survey
   - Title insurance (if required)

**CP tracking challenges:**
- 50-100 items across multiple parties
- Responsibility unclear (sponsor/lawyer/lender)
- Parallel processing but with dependencies
- Documentation scattered

---

## Stage 2: Ongoing Debt Management

### Financial Covenant Monitoring

**Common covenants:**

| Covenant | Definition | Typical Threshold | Breach Consequence |
|----------|------------|-------------------|---------------------|
| LTV | Loan / Value | 50-70% | Mandatory prepayment or cash trap |
| ICR | NOI / Debt Service | 1.5x-2.0x | Cash trap, potential default |
| DSCR | NOI / (P+I) | 1.25x-1.5x | Cash trap |
| Debt Yield | NOI / Loan | 7-10% | Mandatory prepayment |

**Monitoring requirements:**
- Quarterly covenant certificate
- Annual valuation
- Calculation methodology per loan docs
- Cure provisions if applicable

**Pain points:**
- Manual calculation from multiple sources
- Definitions in loan docs vs actual calculation
- Multiple loans with different definitions
- Early warning of potential breach

---

### Reporting Requirements

**Typical lender reporting:**
| Report | Frequency | Content |
|--------|-----------|---------|
| Rent roll | Quarterly | Current tenancy, arrears |
| Financial statements | Quarterly/Annual | SPV accounts, management accounts |
| Covenant certificate | Quarterly | Covenant calculations, compliance confirmation |
| Capex report | Quarterly | Spend vs budget |
| Leasing report | Quarterly | New leases, renewals, vacations |
| Insurance certificate | Annual | Coverage confirmation |
| Valuation | Annual | External valuation |
| Business plan | Annual | Asset strategy, projections |

**Pain points:**
- Different lenders, different formats
- Manual compilation from property data
- Deadline tracking across loans
- Data consistency across reports

---

### Consent and Amendment Requests

**Common consent requests:**
- New lease (if above threshold or to specific tenant)
- Assignment or subletting
- Alterations/capex (above threshold)
- Property management change
- Hedging adjustments
- Distributions (if restricted)

**Amendment requests:**
- Covenant waiver (temporary breach)
- Covenant reset (refinancing)
- Extension/modification
- Release of security

**Process:**
1. Identify need for consent/amendment
2. Review facility agreement for requirements
3. Prepare request and supporting documentation
4. Submit to lender (agent if syndicated)
5. Lender review and questions
6. Negotiation of terms/fees
7. Documentation of consent/amendment
8. Implementation

**Pain points:**
- Consent thresholds buried in documentation
- Lead time for lender response uncertain
- Fee negotiations
- Documentation for simple consents

---

### Cash Management and Distributions

**Waterfall structures:**
Typical priority of payments:
1. Operating expenses
2. Property taxes
3. Insurance
4. Property management fees
5. Debt service (interest)
6. Debt service (principal)
7. Reserve accounts (capex, TI/LC)
8. Cash trap (if covenants breached)
9. Distribution to sponsor

**Pain points:**
- Waterfall calculations complex
- Reserve requirements vary
- Cash trap triggers monitoring
- Distribution restrictions not always clear

---

## Future State (With AI Intelligence Platform)

### Scenario: AI-Assisted Debt Management

#### Loan Documentation Analysis

**Agent automatically:**
1. **Ingests loan documents:**
   - Facility agreement
   - Security documents
   - Amendments and waivers
   - Side letters

2. **Extracts key terms:**
   ```json
   {
     "facility": {
       "amount": 50000000,
       "currency": "GBP",
       "margin": 1.75,
       "reference_rate": "SONIA",
       "maturity": "2028-03-15",
       "extension_options": [{"term": "12 months", "fee": "0.25%"}]
     },
     "covenants": {
       "ltv": {"threshold": 0.60, "test_frequency": "quarterly"},
       "icr": {"threshold": 1.75, "test_frequency": "quarterly"},
       "definitions": {
         "net_operating_income": "per clause 1.1.45",
         "value": "per most recent valuation"
       }
     },
     "reporting": [
       {"report": "Rent roll", "frequency": "quarterly", "deadline": "Q+30 days"},
       {"report": "Covenant certificate", "frequency": "quarterly", "deadline": "Q+45 days"}
     ],
     "consent_thresholds": {
       "new_lease": {"area": 1000, "term": 10, "rent": 100000},
       "capex": {"amount": 500000}
     }
   }
   ```

3. **Creates covenant monitoring dashboard:**
   - Current covenant position
   - Trend over time
   - Forecast based on business plan
   - Headroom to breach

4. **Calendars all obligations:**
   - Reporting deadlines
   - Testing dates
   - Maturity and extension dates
   - Hedging expiry

---

#### Covenant Monitoring and Early Warning

**Agent continuously:**
1. **Calculates current covenant position:**
   - Uses actual property data
   - Applies loan-specific definitions
   - Generates compliant calculation

2. **Forecasts future position:**
   - Based on business plan
   - Sensitivity analysis
   - "If occupancy drops 10%, ICR breaches in Q3"

3. **Alerts on risks:**
   - Threshold approach (within 10% of breach)
   - Trend deterioration
   - External factors (interest rate changes)

---

#### Consent Request Automation

**Agent assists:**
1. **Identifies consent requirements:**
   - "New lease to tenant A for 2,000 sqm at $150k requires lender consent (threshold: 1,000 sqm)"
   - Links to specific clause in facility agreement

2. **Prepares consent request:**
   - Template populated with relevant data
   - Supporting documentation assembled
   - Precedent consents referenced

3. **Tracks process:**
   - Request submitted date
   - Lender response deadline
   - Questions and responses
   - Approval and documentation

---

#### Reporting Automation

**Agent generates:**
1. **Standard lender reports:**
   - Rent roll in lender format
   - Covenant certificate with calculations
   - Capex report
   - Leasing activity summary

2. **Compliance package:**
   - All required reports bundled
   - Certificate of compliance
   - Cover letter

3. **Distribution calculation:**
   - Waterfall calculation
   - Reserve adequacy
   - Distributable amount
   - Supporting documentation

---

### Key AI Intervention Points

| Manual Process | AI Intervention | Value |
|----------------|-----------------|-------|
| Loan term extraction | Auto-extract to structured data | Searchable, queryable |
| Covenant calculation | Auto-calculate from property data | Accuracy, consistency |
| Covenant monitoring | Continuous monitoring, early warning | No surprise breaches |
| Reporting preparation | Auto-generate lender reports | Time savings |
| Consent identification | Flag when consent required | Compliance |
| Cash waterfall | Auto-calculate distributions | Accuracy |

---

## Gate 2: Debt Documentation and Covenant Setup

### Purpose
Ensure complete extraction and monitoring setup for all debt facilities at acquisition.

### Gate Criteria

| Category | Requirement | Validation |
|----------|-------------|------------|
| **Documents** | All loan documents ingested and indexed | Document checklist complete |
| **Terms** | Key terms extracted and verified | Human review sign-off |
| **Covenants** | All covenants identified and definitions confirmed | Covenant schedule reviewed |
| **Reporting** | All reporting requirements calendared | Report calendar populated |
| **Consents** | Consent thresholds documented | Threshold table verified |
| **Initial** | Opening covenant position calculated | Calculation reviewed |

---

## Lender Stakeholder Perspective

### What Lenders Actually Care About

| Priority | Concern | Information Need |
|----------|---------|------------------|
| 1 | Debt service coverage | NOI, interest costs, amortization |
| 2 | Collateral value | Valuation, market conditions |
| 3 | Tenant quality | Credit ratings, lease terms |
| 4 | Sponsor capability | Track record, financial strength |
| 5 | Market dynamics | Supply, demand, rents |

### Lender Experience Today

**Frustrations:**
- Inconsistent reporting formats
- Late submissions
- Covenant calculations that don't match
- Difficulty getting information
- Consent requests incomplete

**What would help:**
- Standardized reporting
- Automatic alerts on issues
- Complete consent packages
- Proactive communication
- Real-time data access

### Opportunity: Lender Portal

**Agent could provide:**
- Lender-facing dashboard
- Real-time covenant monitoring (with appropriate permissions)
- Document repository access
- Report retrieval
- Consent request workflow

**Value proposition:**
- Reduced lender monitoring costs
- Earlier issue identification
- Streamlined consent process
- Better sponsor-lender relationship

---

## Critical AI Requirements

### 1. Definition Precision

**The challenge:**
Loan documents contain specific definitions:
- "Net Operating Income" defined in clause 1.1.45
- Definition may differ from accounting NOI
- Definitions vary between loans

**Requirement:**
- Extract exact definitions
- Apply loan-specific definitions in calculations
- Flag when actual data doesn't match definition
- Support multiple definition sets across loans

---

### 2. Document Interconnection

**The challenge:**
Loan documents reference each other:
- Facility agreement defines covenants
- Security documents defined by facility agreement
- Amendments modify original terms
- Side letters create exceptions

**Requirement:**
- Maintain document relationships
- Track amendments to original terms
- Consolidate current state of loan

---

### 3. Calculation Accuracy

**The challenge:**
Covenant calculations must be precise:
- Errors can trigger false positives (unnecessary action)
- Errors can trigger false negatives (missed breach)
- Lender calculations may differ

**Requirement:**
- Calculation methodology documented
- Reconciliation to lender calculations
- Audit trail for all inputs
- Version control of calculation logic

---

## Sensitivities

### Confidentiality

**The risk:**
- Loan terms are commercially sensitive
- Default information is particularly sensitive
- Multi-bank syndications have information barriers

**Mitigation:**
- Strict access controls
- Audit logging
- Data isolation per loan
- Lender-specific views (if portal provided)

---

### Accuracy of Covenant Calculations

**The risk:**
- Incorrect calculation → incorrect action
- False compliance → lender event of default
- Disputes with lenders

**Mitigation:**
- Calculation methodology transparency
- Human review of calculations
- Reconciliation with lender calculations
- Clear data sourcing

---

## Success Metrics

| Metric | Current State | Target State |
|--------|---------------|--------------|
| Covenant calculation time | 4-8 hours/loan/quarter | 30 minutes |
| Reporting preparation | 2-3 days/loan | 2-4 hours |
| Covenant breach surprises | 10-20% caught late | 0% |
| Consent request cycle time | 2-4 weeks | 1 week |
| Lender report accuracy | 90-95% | >99% |
| Cash trapped incorrectly | Occasional | Never |

---

*Next: Comprehensive Stakeholder Perspective Map*
