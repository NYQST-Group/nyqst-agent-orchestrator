# Workflow Scenario: Deal Sourcing and Initial Screening

*Date: 2026-01-23*
*Persona: Investment Analyst + Investment Director*
*Phase: Acquisition - Deal Sourcing*

---

## The Real Workflow

### Context

A European core-plus real estate fund with a $2B mandate receives 30-50 investment opportunities per week. The team needs to quickly identify which deals fit their criteria and deserve detailed analysis.

### Current State (Without AI)

#### Step 1: Deal Arrives

**What happens:**
- Broker emails IM (Information Memorandum) as PDF attachment
- Sometimes via data room link requiring registration
- Occasionally via WhatsApp or other informal channels
- Off-market deals may be a single-page teaser

**Documents involved:**
- Investment Memorandum (50-200 pages PDF)
- Teaser (2-10 pages)
- Rent roll (Excel or PDF table)
- Photos and floor plans

**Who does it:**
- Admin assistant or analyst logs receipt in deal tracker (often Excel)
- Manual entry: date, source, property name, location, approximate price

**Time required:** 5-15 minutes per deal

**Pain points:**
- Emails get buried
- Attachments save to random locations
- Deal tracker falls out of date
- Same deal from multiple brokers not detected

---

#### Step 2: Initial Review

**What the analyst actually does:**
1. Opens IM PDF
2. Scans executive summary (5-10 pages)
3. Looks for key facts:
   - Location (city, submarket, address)
   - Property type (office, logistics, retail, residential)
   - Size (sqm/sqft, floors)
   - Price guidance
   - Tenancy (single/multi, WALT, vacancy)
   - Key tenant names
   - Asking yield/cap rate
4. Checks against investment mandate:
   - Geography: Is it in our target markets?
   - Size: Is it in our deal size range?
   - Sector: Do we do this property type?
   - Quality: Does it look institutional?
   - Yield: Is it in our target return range?
5. Forms initial view: Pass / Maybe / Review further

**Documents involved:**
- IM (focus on exec summary, rent roll, location map)
- Internal mandate/criteria document (often in analyst's head)

**Time required:** 30-90 minutes per deal

**Pain points:**
- IMs are inconsistent in structure
- Key information buried (e.g., lease breaks in appendix)
- No standardized screening checklist
- Different analysts assess differently
- Broker spin obscures reality

---

#### Step 3: Deal Logging and Initial Classification

**What the analyst does:**
1. Updates deal tracker with:
   - Property details (address, type, size)
   - Asking price
   - Key tenancy metrics (WALT, occupancy)
   - Source/broker
   - Initial view (Pass/Review)
   - Brief notes on rationale
2. Flags for Director review if "Maybe" or interesting

**Documents involved:**
- Deal tracker (Excel/Monday/Salesforce)
- IM for reference

**Time required:** 10-20 minutes per deal

**Pain points:**
- Tracker has 50 columns, most left empty
- Data entry is tedious and error-prone
- Historical deals hard to search/filter
- No link back to source documents

---

#### Step 4: Director Triage

**What the Director does:**
1. Reviews analyst's initial assessments (usually weekly)
2. For "Maybe" deals:
   - Skims IM or asks analyst for verbal briefing
   - Applies strategic lens (market timing, portfolio fit, seller dynamics)
   - Decides: Pass / Request more info / Begin detailed analysis
3. For "Pass" deals:
   - Confirms rejection
   - May request polite decline email to broker

**Documents involved:**
- Deal tracker
- IM (quick reference)
- Mental model of current portfolio and strategy

**Time required:** 30-60 minutes for weekly review of 30-50 deals

**Pain points:**
- Analyst summaries vary in quality and format
- No easy way to compare deals side-by-side
- Strategic fit assessment is intuitive, not systematic
- Good deals may be missed due to poor initial screening

---

### Pain Point Deep Dive

#### 1. Information Extraction is Manual and Slow

**The problem:**
Every IM has the same information, but in different places with different labels:
- "Rent roll" vs "Tenancy schedule" vs "Lease summary"
- Sqm vs sqft (and sometimes mixed within document)
- Different currency formats
- ERV vs passing rent vs headline rent

**The cost:**
- 30-60 minutes per deal just for basic data extraction
- Errors propagate into models and memos
- Comparison across deals requires normalization

**What good looks like:**
- Structured data extracted automatically
- Confidence levels and source page references
- Normalization applied (standard units, currencies)
- Extraction errors flagged for human review

---

#### 2. Mandate Fit Assessment is Inconsistent

**The problem:**
Investment criteria are often:
- Written once and forgotten
- Interpreted differently by team members
- Have soft boundaries ("typically $50-100M but could go smaller for right deal")
- Evolve over time without documentation

**The cost:**
- Deals passed that should have been pursued
- Deals analyzed that clearly didn't fit
- New team members struggle to calibrate

**What good looks like:**
- Mandate codified as structured criteria
- Automatic scoring against criteria
- Edge cases flagged for human judgment
- Mandate evolution tracked over time

---

#### 3. Duplicate Deals Not Detected

**The problem:**
Same property offered by:
- Multiple brokers
- At different times
- With different marketing names ("The Hub" vs "50 Main Street")

**The cost:**
- Wasted analysis time
- Confusing broker relationships
- Historical context lost

**What good looks like:**
- Automatic matching on address/coordinates
- Alert when duplicate detected
- Historical information surfaced

---

#### 4. Screening Rationale Not Captured

**The problem:**
"Why did we pass on this?"
- Answer is usually "I don't remember" or buried in old emails
- No systematic learning from passed deals
- Same deals come back later

**The cost:**
- Repeat work when deal re-emerges
- Lost opportunity to learn from market
- Junior team can't learn from decisions

**What good looks like:**
- Every Pass decision has captured rationale
- Searchable database of passed deals
- "Deals like this one" analysis possible

---

## Future State (With AI Intelligence Platform)

### Scenario: A Day in the Life

**8:30 AM - Deal Intake**

*Agent automatically:*
1. Monitors deal intake channels (email, data rooms, messaging)
2. Detects new deal arrival
3. Extracts and parses IM/teaser
4. Creates structured deal record:
   - Property identification (address, lat/long, type, size)
   - Financial summary (price, yield, rent, WALT)
   - Tenancy overview (occupancy, key tenants, lease events)
   - Flags any extraction uncertainties

*Human review:*
- Analyst receives notification: "3 new deals overnight"
- Dashboard shows extracted data with source citations
- Analyst can verify/correct any flagged extractions
- Time: 5 minutes vs 60+ minutes manual

---

**9:00 AM - Mandate Screening**

*Agent automatically:*
1. Scores deal against codified investment criteria:
   - Geography: Score 1 (target market)
   - Size: Score 0.8 (slightly below typical range)
   - Sector: Score 1 (target sector)
   - Quality: Score 0.7 (B+ building, limited ESG)
   - Return: Score 0.9 (meets yield target)
2. Generates mandate fit summary:
   - "82% mandate fit. Geography and sector aligned. Size slightly below typical range ($45M vs $50M minimum). ESG data limited - will require verification."
3. Flags specific concerns:
   - "Lease to anchor tenant expires in 24 months with no renewal option documented"
   - "Service charge structure unclear - see page 87"
4. Suggests comparable deals from database

*Human review:*
- Analyst reviews AI assessment
- Agrees/modifies scoring
- Adds qualitative notes
- Marks as: Auto-pass / Analyst review / Director review
- Time: 10 minutes vs 30 minutes manual

---

**10:00 AM - Director Briefing**

*Agent prepares:*
1. Weekly deal summary dashboard:
   - 45 deals received
   - 12 auto-passed (clear mandate misfit, with rationale)
   - 8 recommended for detailed analysis
   - 25 pending analyst review
2. For each recommended deal:
   - One-page summary with key metrics
   - Risk flags with evidence
   - Comparable transaction data
   - Market context

*Director interaction:*
- Reviews AI-generated summaries
- Asks clarifying questions: "What are the ESG risks specifically?"
- Agent provides: "Building has EPC D rating, no renewable energy, limited sustainability certifications. Comparable buildings with C or better rating have traded at 15-20bps yield premium. Estimated capex for EPC improvement: $2-3M based on similar upgrades."
- Director decides: "Run numbers assuming $2.5M ESG capex in year 1"

---

### Key AI Intervention Points

| Manual Step | AI Intervention | Value |
|-------------|-----------------|-------|
| Document receipt logging | Auto-detect, extract, log | Time savings, completeness |
| IM data extraction | Parse PDF, extract structured data | Accuracy, speed |
| Mandate scoring | Rule-based + ML scoring | Consistency, coverage |
| Duplicate detection | Address/geo matching | Avoid rework |
| Rationale capture | Auto-summarize discussions | Learning, audit trail |
| Comparable sourcing | Semantic search on deal history | Better decisions |
| Director briefing | Generated summaries | Focus on judgment |

---

## Critical AI Requirements for This Workflow

### 1. Extraction Accuracy

**Why it matters:**
- Wrong rent figure → wrong valuation → wrong decision
- Missed lease break → unexpected vacancy → investment loss
- Errors in IC materials → career damage

**Requirement:**
- Extraction accuracy >98% for key fields
- Confidence scoring on every extraction
- Source citation (page, paragraph) for verification
- Human-in-the-loop for low confidence items

---

### 2. Uncertainty Handling

**Why it matters:**
- IMs are marketing documents - they omit bad news
- Some information is genuinely ambiguous
- Better to flag uncertainty than guess

**Requirement:**
- Distinguish: "Found" / "Not found" / "Ambiguous"
- Surface what's NOT in the document
- Flag unusual patterns: "This IM doesn't mention service charge structure"

---

### 3. Evidence Linkage

**Why it matters:**
- Professionals must verify AI outputs
- Audit trail required for decisions
- Trust built through transparency

**Requirement:**
- Every data point linked to source document
- Click-through to highlighted source
- Change tracking if source documents update

---

### 4. Learning and Feedback

**Why it matters:**
- Analyst corrections improve future extraction
- Passed deals inform mandate refinement
- Outcome data (deals won/lost) enables learning

**Requirement:**
- Capture analyst corrections
- Track deal outcomes
- Periodic model refinement
- Feedback loop visibility

---

## Metrics for Success

| Metric | Current State | Target State |
|--------|---------------|--------------|
| Time to log new deal | 15 min | 2 min |
| Time for initial screening | 45 min | 10 min |
| Data extraction accuracy | Variable/unknown | >98% |
| Mandate fit consistency | Low | >90% agreement |
| Duplicate detection rate | 20% caught | 95% caught |
| Rationale capture rate | 10% | 100% |
| Director review time | 60 min/week | 20 min/week |

---

## Edge Cases and Risks

### Edge Cases to Handle

1. **Complex assets:** Mixed-use, portfolios, development sites
2. **Limited information:** Early teasers with minimal data
3. **Non-standard documents:** Handwritten notes, spreadsheets, multiple files
4. **Languages:** Multi-language IMs in cross-border deals
5. **Confidentiality:** Blind teasers with location obscured

### Risks to Mitigate

1. **Over-reliance:** Users skip verification, errors propagate
   - *Mitigation:* Required confirmation for key fields; periodic audit

2. **Gaming:** Brokers learn to structure IMs to game AI scoring
   - *Mitigation:* Human oversight; multiple scoring approaches

3. **Bias:** Model learns historical biases in deal selection
   - *Mitigation:* Regular bias audits; outcome-based feedback

4. **Confidentiality:** Deals processed through cloud systems
   - *Mitigation:* Data residency controls; client-specific isolation

---

*Next scenario: Detailed Due Diligence Workflow*
