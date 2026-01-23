# Workflow Scenario: Due Diligence Execution

*Date: 2026-01-23*
*Persona: Investment Analyst, Investment Director, External Advisors*
*Phase: Acquisition - Due Diligence*

---

## Context

After a deal passes initial screening and the team decides to pursue it, a comprehensive due diligence process begins. This is typically 4-8 weeks of intensive work across multiple workstreams, coordinated under time pressure with significant cost (advisor fees often $100k-$500k+).

---

## The Due Diligence Challenge

### Scale of the Problem

For a typical institutional-grade acquisition:

**Document Volume:**
- 500-3,000 documents in the data room
- 5,000-20,000 pages total
- Documents arrive in waves (not all at once)
- Updates and amendments throughout process

**Workstreams:**
- Legal: Title, leases, contracts, litigation, corporate
- Technical: Building survey, M&E, environmental, fire safety
- Financial: Rent roll, service charge, capex, insurance
- Commercial: Market, tenant credit, comparable rents
- Tax: Structure, transfer taxes, VAT
- ESG: Energy performance, sustainability, social impact

**Time Pressure:**
- Competitive processes: 3-4 weeks
- Bilateral deals: 6-8 weeks
- Exclusivity periods create hard deadlines
- IC dates don't move

---

## Current State (Without AI)

### Stage 1: Data Room Access and Organization

**What happens:**
1. Seller's lawyers set up virtual data room (Intralinks, Datasite, etc.)
2. Buyer team gets access credentials
3. Documents organized by seller's structure (often illogical)
4. Index provides document names but limited metadata

**Who does it:**
- Analyst manages buyer-side data room access
- May create shadow copy of key documents
- Builds internal tracking spreadsheet

**Time required:** 2-4 hours initial setup; ongoing maintenance

**Pain points:**
- Data room structure doesn't match DD workflow
- Document naming inconsistent ("Lease.pdf" vs "Tenant_ABC_Lease_v2_final.pdf")
- Versions and amendments scattered
- Search functionality often poor
- No automated alerts for new documents

---

### Stage 2: Advisor Instruction and Coordination

**What happens:**
1. Engage advisors (lawyers, surveyors, tax advisors)
2. Issue instruction letters defining scope
3. Grant data room access
4. Kick-off calls to align expectations
5. Set reporting deadlines and format requirements

**Who does it:**
- Director/Principal leads advisor selection
- Analyst coordinates access and communications

**Documents involved:**
- Engagement letters
- Scope of work / instruction letters
- Data room access forms
- Previous reports (for context)

**Time required:** 1-2 days

**Pain points:**
- Scope creep if not precisely defined
- Advisors duplicate each other's work
- Fee estimates vs actuals diverge
- Coordination overhead significant

---

### Stage 3: Document Review and Issue Identification

#### Legal DD - Lease Review (Example)

**What the legal team does:**
1. Identify all lease documents (agreements, side letters, amendments)
2. Read and abstract key terms:
   - Parties, premises, area
   - Term: start, end, break options, renewal options
   - Rent: current, review mechanism, frequency
   - Service charge: recoverable costs, caps
   - Alienation: assignment, subletting rights
   - Alterations: permitted works
   - Repair: full repairing, landlord obligations
   - Security: rent deposit, guarantees
   - Break: dates, conditions, penalties
   - Unusual provisions
3. Identify issues, risks, and deal points
4. Prepare lease summary schedule
5. Draft report of title section

**Time required:**
- Junior lawyer: 2-4 hours per lease
- 30 leases = 60-120 hours of junior time
- Plus senior review time

**Pain points:**
- Every lease is different (even for same building)
- Critical terms in schedules, not main body
- Side letters modify base lease
- Handwritten amendments
- Interpretation requires legal judgment
- Consistency across large team difficult

---

#### Technical DD - Building Survey (Example)

**What the surveyor does:**
1. Review available building information:
   - As-built drawings
   - M&E specifications
   - Maintenance records
   - Previous surveys
   - Warranty documents
2. Conduct site inspection:
   - External fabric
   - Common areas
   - Sample of tenant spaces
   - Plant and equipment
   - Services (electrical, mechanical, plumbing)
3. Assess condition:
   - Immediate repairs needed
   - Short-term maintenance (0-3 years)
   - Medium-term renewals (3-10 years)
   - Long-term replacements (10+ years)
4. Prepare capex schedule
5. Identify risks and recommendations
6. Draft technical DD report

**Time required:**
- Site inspection: 1-3 days
- Report writing: 3-5 days
- Depends on building size and complexity

**Pain points:**
- Historical documentation often incomplete
- Site access coordination
- Tenant disruption constraints
- Estimating costs without detailed specification
- Report quality varies by surveyor

---

### Stage 4: Issue Tracking and Synthesis

**What the analyst does:**
1. Create master issues log (Excel spreadsheet)
2. Review incoming advisor reports
3. Extract issues from each report
4. Categorize by severity:
   - Showstopper: Cannot proceed without resolution
   - Material: Requires negotiation or price adjustment
   - Housekeeping: Note for completion, minor impact
5. Assign follow-up actions
6. Track status: Open / Investigating / Resolved / Accepted
7. Prepare DD summary for Director/IC

**Documents involved:**
- All advisor reports (draft and final)
- Data room documents (for evidence)
- Issues tracker (Excel)
- Follow-up correspondence

**Time required:**
- Initial population: 1-2 days
- Ongoing maintenance: 2-4 hours daily during DD period

**Pain points:**
- Issues log quickly becomes unwieldy
- Cross-referencing to source documents is manual
- Duplicate issues entered by multiple advisors
- Severity assessments vary by person
- Version control of the tracker itself
- Synthesizing across workstreams is hard

---

### Stage 5: DD Report Compilation

**What happens:**
1. Final advisor reports received
2. Analyst compiles DD summary memo:
   - Executive summary of key issues
   - Issue-by-issue analysis
   - Financial impact quantification
   - Recommendations
3. Director reviews and edits
4. Attached to IC pack

**Time required:** 2-3 days

**Pain points:**
- Last-minute report updates
- Formatting inconsistency across advisors
- Financial impacts often poorly quantified
- Recommendations sometimes vague
- Cross-referencing to source documents tedious

---

## Future State (With AI Intelligence Platform)

### Scenario: AI-Assisted Due Diligence

#### Day 1: Data Room Ingestion

**Agent automatically:**
1. Connects to data room API (or monitors for new documents)
2. Ingests all documents:
   - OCR for scanned documents
   - DocIR conversion for structure extraction
   - Metadata extraction (dates, parties, document type)
3. Classifies documents:
   - Lease agreements (by tenant, date)
   - Financial documents (by year, type)
   - Technical documents (by system, date)
   - Legal documents (by category)
4. Creates searchable knowledge base:
   - Full-text search
   - Semantic search ("find all lease break provisions")
   - Entity search (tenant names, dates, amounts)
5. Flags gaps:
   - "No audited accounts found for 2023"
   - "Fire safety certificate expired"
   - "Lease for Unit 5 not in data room"

**Human review:**
- Analyst reviews document classification
- Confirms/corrects document types
- Notes missing documents for information request

**Time:** 2 hours vs 8+ hours manual

---

#### Week 1: Parallel Automated Extraction

**Agent automatically (Legal - Leases):**
1. Identifies all lease documents per tenant:
   - Base lease
   - Amendments
   - Side letters
   - Rent deposit deeds
   - Guarantees
2. Extracts structured data:
   ```json
   {
     "tenant": "ABC Limited",
     "premises": "Ground floor, 1,250 sqm",
     "term_start": "2019-03-25",
     "term_end": "2029-03-24",
     "break_options": [
       {"date": "2024-03-25", "notice_period": "6 months", "conditions": ["repair obligations satisfied", "no arrears"]}
     ],
     "current_rent": 125000,
     "rent_review": {"mechanism": "open market", "frequency": "5 yearly", "next_review": "2024-03-25"},
     "service_charge": {"contribution": "fixed percentage", "cap": null},
     "unusual_provisions": ["Tenant has first refusal on adjacent unit", "Landlord cannot object to change of use within B1"]
   }
   ```
3. Flags for legal review:
   - "Break option conditioned on 'reasonable satisfaction of landlord' - subjective standard"
   - "Alienation clause references schedule not found in data room"
   - "Guarantor company dissolved in 2021"
4. Generates draft lease summary schedule

**Human review (Lawyer):**
- Reviews extracted data against source
- Confirms/corrects interpretations
- Focuses on flagged items and unusual provisions
- Time: 30 min per lease vs 2-4 hours manual

---

**Agent automatically (Financial):**
1. Extracts rent roll:
   - Matches to lease documents
   - Validates against lease terms
   - Flags discrepancies ("Lease says $125k, rent roll shows $130k")
2. Extracts service charge accounts:
   - Historical costs by category
   - Recovery rates
   - Sinking fund balances
3. Extracts operating statements:
   - Historical income and expenses
   - Year-on-year trends
   - Unusual items
4. Flags for financial review:
   - "Service charge deficit $50k in 2022 - landlord contribution"
   - "Insurance cost up 35% YoY - investigate"
   - "Major works reserve appears underfunded vs surveyor capex estimate"

---

**Agent automatically (Technical):**
1. Extracts from technical documents:
   - M&E system ages and specifications
   - Maintenance contract terms
   - Previous survey findings
   - Warranty expirations
2. Cross-references with surveyor report:
   - "Surveyor estimates roof replacement 2027; manufacturer warranty expires 2025"
   - "Chiller capacity may be insufficient based on floor plans - verify site"
3. Builds asset condition database:
   - Component inventory
   - Age/condition/life expectancy
   - Replacement cost estimates (from market data)

---

#### Week 2-3: Intelligent Issue Tracking

**Agent automatically:**
1. Creates master issues log from all sources:
   - Legal advisor report issues
   - Technical advisor report issues
   - Financial analysis flags
   - Direct data room document analysis
2. De-duplicates and links:
   - "Lease break issue mentioned in both legal report and rent roll analysis"
3. Suggests severity ratings:
   - "Break option in 6 months with key tenant (40% of rent) - suggested: Material"
4. Quantifies financial impact where possible:
   - "If tenant exercises break: $500k annual rent loss, 18 month re-letting assumption = $750k impact"
5. Links to evidence:
   - Issue → Source document → Specific page/paragraph
6. Suggests follow-up actions:
   - "Request tenant's intentions on break option"
   - "Seek indemnity from seller for service charge deficit"

**Human review:**
- Analyst reviews AI-generated issues
- Adjusts severity ratings
- Adds qualitative context
- Assigns action owners
- Tracks resolution

---

#### Week 4: Synthesis and Reporting

**Agent generates:**
1. DD Executive Summary:
   - Deal overview
   - Material issues (3-5 key points)
   - Recommended price adjustments / conditions
   - Go/no-go recommendation factors
2. Detailed Issue Analysis:
   - Issue-by-issue breakdown
   - Evidence citations
   - Financial quantification
   - Status and resolution
3. Appendices:
   - Lease summary schedule
   - Capex schedule
   - Financial analysis
4. Evidence Pack:
   - Source documents for each material issue
   - Highlighted relevant sections
   - Ready for IC or legal review

**Human review:**
- Director reviews synthesis
- Modifies recommendations
- Finalizes IC materials
- Time: 4 hours vs 2-3 days manual

---

## Key AI Intervention Points

| Manual Process | AI Intervention | Value Add |
|----------------|-----------------|-----------|
| Data room organization | Auto-classify, index, search | Find anything instantly |
| Lease abstraction | Extract structured data | 90% time saving |
| Issue identification | Pattern matching + flags | Catch missed issues |
| Issue tracking | Auto-populate from reports | Single source of truth |
| Cross-referencing | Link issues to evidence | Audit trail |
| Financial validation | Lease vs rent roll matching | Error detection |
| Report synthesis | Draft generation | Focus on judgment |
| Information requests | Gap analysis | Complete DD faster |

---

## Critical AI Requirements

### 1. Document Handling Excellence

**Multi-format ingestion:**
- Native PDF (searchable)
- Scanned PDF (OCR required)
- Word documents
- Excel spreadsheets
- Images (floor plans, photos)
- Email files (.msg, .eml)

**Document relationship understanding:**
- Amendments modify base documents
- Side letters create exceptions
- Multiple documents comprise single lease
- Version/date ordering

---

### 2. Legal Document Intelligence

**Lease complexity handling:**
- UK leases (FRI, IRI variations)
- European lease structures
- US lease formats
- Cross-border variations

**Interpretation support:**
- Flag ambiguous provisions
- Cite relevant case law (optional)
- Identify unusual terms vs market standard
- Track side letter modifications

**Liability boundaries:**
- AI assists, does not replace legal advice
- Flagged items require legal review
- Clear extraction vs interpretation distinction

---

### 3. Cross-Workstream Intelligence

**The power of connected analysis:**
- Lease says service charge capped → Is landlord exposed to shortfall?
- Technical report says roof needs work → Which leases allow recovery?
- Tenant financials weak → Break option risk increases
- ESG capex required → Which leases permit alterations?

**Requirement:**
- Knowledge base spans all documents
- Semantic links between related items
- Alert when findings in one area affect another

---

### 4. Collaboration and Workflow

**Multi-user access:**
- Internal team (analyst, director)
- External advisors (lawyers, surveyors, tax)
- Different permission levels
- Activity tracking

**Issue resolution workflow:**
- Assign owners
- Track status
- Record resolution
- Notify stakeholders

---

## Sensitivities and Risks

### Professional Liability

**The risk:**
- Lawyers and surveyors carry professional indemnity
- AI errors that propagate into advice create liability questions
- "AI told us it was fine" is not a defense

**Mitigation:**
- AI outputs clearly marked as draft/assistance
- Human review required for all material items
- Audit trail of human verification
- Clear liability terms in platform agreements

---

### Confidentiality

**The risk:**
- DD documents are highly confidential
- Deals are often market-sensitive
- Multi-tenant platform raises conflict concerns

**Mitigation:**
- Client/deal isolation at data level
- No cross-deal learning without consent
- Clear data residency and retention
- Audit logs for all access

---

### Accuracy in Adversarial Context

**The risk:**
- Sellers structure data rooms to obscure issues
- Document naming may be misleading
- Critical information buried or omitted

**Mitigation:**
- Gap analysis ("What's NOT here?")
- Pattern matching ("Similar deals usually have X")
- Anomaly detection ("This looks unusual")
- Human expert oversight

---

## Success Metrics

| Metric | Current State | Target State |
|--------|---------------|--------------|
| Document classification time | 8 hours | 1 hour |
| Lease abstraction time | 3 hrs/lease | 30 min/lease |
| Issues missed in DD | Unknown (often found post-close) | <5% |
| DD report preparation | 3 days | 4 hours |
| Cross-reference accuracy | Manual/variable | 100% linked |
| Information request completeness | Often incomplete | Gap analysis automated |

---

## Real Example: The Missed Break Option

### What Actually Happened (Pre-AI)

A fund acquired a multi-tenant office building. During DD:
- 45 leases reviewed by external lawyers
- Lease summary schedule prepared
- Key dates captured

Six months after acquisition:
- Major tenant (35% of rent) exercises break
- Break option was in a side letter, not main lease
- Side letter was in data room but not reviewed with main lease
- Loss: ~$2M in value (2+ years void assumed)

### How AI Would Have Helped

1. **Document relationship mapping:**
   - AI links side letter to main lease automatically
   - "Warning: Side letter modifies break provisions in main lease"

2. **Automatic extraction from all related documents:**
   - Break options extracted from main lease AND side letter
   - Conflict flagged: "Main lease has no break; side letter grants break in year 5"

3. **Risk quantification:**
   - "Break option in 12 months for tenant representing 35% of gross rent"
   - "Estimated impact if exercised: $1.8M-$2.2M"

4. **Investment decision support:**
   - Issue surfaced prominently in DD summary
   - Price negotiation or deal terms adjusted accordingly

---

*Next scenario: Financial Modeling and Underwriting*
