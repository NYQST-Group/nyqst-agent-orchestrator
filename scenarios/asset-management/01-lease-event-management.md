# Workflow Scenario: Lease Event Management

*Date: 2026-01-23*
*Persona: Asset Manager, Property Manager*
*Phase: Asset Management - Lease Administration*

---

## The Stakes Are High

Lease events in commercial real estate have significant financial and operational consequences:

| Event Type | Miss the Deadline | Example Impact |
|------------|-------------------|----------------|
| Tenant break option | Tenant exits, no control | 18-24 month void, $500k+ lost rent |
| Landlord break option | Lose ability to reposition | 5+ years locked in below-market lease |
| Rent review | Default mechanism applies | Below-market rent for 5 years |
| Lease expiry | Holdover/statutory protection | Legal costs, uncertainty |
| Option exercise (renewal) | Rights lapse | Lose tenant or repositioning opportunity |
| Guarantee expiry | Security lost | Increased credit risk |

---

## The Reality of Lease Event Tracking

### Scale of the Problem

A typical institutional portfolio:
- 50 buildings
- 500 tenants
- 2,000+ lease documents
- 10,000+ lease events over a 10-year hold period

Events to track:
- Break options (landlord and tenant)
- Rent reviews
- Lease expiries
- Renewal options
- Service charge true-ups
- Insurance renewals
- Guarantee renewals/expiries
- Rent deposit interest
- Dilapidations
- License conditions

---

## Current State (Without AI)

### How Events Get Tracked Today

#### Initial Setup

**What happens:**
1. Asset acquired; leases reviewed during DD
2. Key dates extracted into lease summary schedule
3. Dates entered into calendar/reminder system:
   - Outlook reminders
   - Property management software (Yardi, MRI)
   - Spreadsheet with manual diary system
   - Monday/Asana for task management
4. Responsibility assigned to property manager or asset manager

**Documents involved:**
- Original lease abstracts (from DD)
- Property management handover pack
- Legacy system data (often incomplete)

**Pain points:**
- DD abstracts may not capture all events
- Lease modifications post-acquisition not reflected
- Different systems don't talk to each other
- Data entry errors propagate
- "Calendar reminder" approach doesn't scale

---

#### Ongoing Monitoring

**Monthly review process:**
1. Asset manager reviews upcoming events (next 12 months)
2. Cross-references with tenant communications
3. Checks with property manager on tenant intentions
4. Escalates significant events to investment team
5. Documents strategy (hold, negotiate, serve notice)

**Who does it:**
- Asset manager (primary responsibility)
- Property manager (tenant liaison)
- Legal (notice drafting and service)

**Time required:**
- 2-4 hours per month per asset manager
- Scales poorly with portfolio size

**Pain points:**
- Events "sneak up" when busy
- Notice periods often tight (6 months for a 3-month review cycle)
- Strategy discussions happen too late
- Tenant intentions unknown until last minute
- Coordination across multiple parties error-prone

---

### The Break Option Workflow (Detailed Example)

#### Scenario: Tenant Break Option in 12 Months

**Lease terms:**
- Tenant can break on 5th anniversary
- 6 months' written notice required
- Break conditioned on: no arrears, compliance with repair obligations
- Break penalty: 3 months' rent

**What should happen:**

| Timeline | Action | Owner | Reality |
|----------|--------|-------|---------|
| T-18 months | Identify event in forward calendar | AM | Sometimes missed |
| T-15 months | Strategy meeting: do we want tenant to stay? | AM/PM | Often doesn't happen |
| T-12 months | If retention desired: approach tenant | PM | Ad hoc |
| T-9 months | Negotiate incentives if needed | AM | Reactive |
| T-6 months | Monitor for notice receipt | PM | Hope tenant forgets |
| T-5 months | If notice received: validate conditions | Legal | Rushed |
| T-4 months | If no notice: tenant stays (relief) | - | - |
| T-3 months | If break confirmed: marketing begins | AM | Already behind |
| T+0 | Lease ends; void begins | - | Void cost accruing |

**What often actually happens:**
- Event noticed at T-9 months ("Oh, we have a break coming up")
- No proactive tenant engagement
- Notice received with minimal time to respond
- Scramble to validate break conditions (maybe find a flaw?)
- Marketing starts too late
- Extended void period

---

### The Rent Review Workflow (Detailed Example)

#### Scenario: Upward-Only Open Market Rent Review

**Lease terms:**
- Rent review every 5 years
- Open market value, upward-only
- Trigger: landlord serves notice, tenant counter-notice
- Default: if no agreement, passing rent continues (bad for landlord if market is up)

**What should happen:**

| Timeline | Action | Owner | Reality |
|----------|--------|-------|---------|
| T-12 months | Identify review date | AM | Often tracked |
| T-9 months | Commission valuation | AM | Sometimes delayed |
| T-6 months | Serve trigger notice | Legal | Critical deadline |
| T-4 months | Negotiate with tenant | Agent/AM | Time-consuming |
| T-2 months | If no agreement: expert determination | Legal | Expensive, slow |
| T+0 | New rent takes effect (backdated) | - | - |

**What often actually happens:**
- Review date noticed late
- Valuation rushed or not commissioned
- Trigger notice served late (or missed entirely!)
- Negotiation compressed
- Landlord accepts lower increase or skips review
- Market upside left on table

**Financial impact of missed review:**
- Market rent: $200k
- Passing rent: $150k
- If review missed: $50k/year x 5 years = $250k value leakage

---

## The Information Problem

### Where Lease Event Data Lives

| Source | Format | Reliability | Accessibility |
|--------|--------|-------------|---------------|
| Original lease | PDF | Authoritative | Hard to search |
| Lease abstract (DD) | Excel/Word | Good (at time of DD) | May be outdated |
| Property management system | Database | Variable | Often incomplete |
| Email | Unstructured | Real-time | Unsearchable |
| Surveyor notes | Various | Real-time | Not centralized |
| Tenant correspondence | Email/Letter | Real-time | Scattered |

### The Core Problem

No single source of truth that is:
- Complete (all events from all lease documents)
- Current (reflects amendments, side letters, variations)
- Connected (links to evidence and context)
- Actionable (triggers workflows at right time)

---

## Future State (With AI Intelligence Platform)

### Scenario: AI-Managed Lease Events

#### Initial Setup: Lease Ingestion

**Agent automatically:**
1. Ingests all lease documents:
   - Original lease agreements
   - Amendments and variations
   - Side letters
   - Deeds of variation
   - Correspondence confirming changes
2. Extracts all events:
   ```json
   {
     "event_type": "tenant_break",
     "trigger_date": "2025-03-25",
     "notice_period": "6 months",
     "notice_deadline": "2024-09-25",
     "conditions": [
       "No material breach",
       "No rent arrears",
       "Repair obligations substantially complied"
     ],
     "penalty": "3 months rent",
     "evidence": {
       "source": "lease_abc_ltd.pdf",
       "page": 47,
       "clause": "24.1"
     }
   }
   ```
3. Validates against known data:
   - Cross-references with property management system
   - Flags discrepancies for human review
4. Creates unified event calendar:
   - All events from all leases
   - Notice deadlines prominently displayed
   - Strategy assignment tracking

**Human review:**
- Asset manager reviews extracted events
- Confirms accuracy or corrects
- Assigns strategic priority

---

#### Ongoing Monitoring: Intelligent Alerts

**Agent continuously:**
1. Monitors calendar for approaching events
2. Generates tiered alerts:
   - **Red (Urgent):** Notice deadline in <30 days, no action recorded
   - **Amber (Attention):** Strategy decision needed in <60 days
   - **Green (On Track):** Event >90 days out, strategy assigned
3. Contextualizes each event:
   - Tenant financial health (from credit monitoring)
   - Market conditions (from comparable data)
   - Portfolio impact (% of rent, strategic importance)
   - Historical context (previous negotiations with this tenant)

**Example Alert:**
```
URGENT: Break Option - ABC Limited

Notice deadline: 25 days away (2024-09-25)
No strategy recorded for this event.

Context:
- Tenant represents 15% of building rent
- Tenant on credit watch (late payments Q3 2024)
- Market comparables suggest 10% rental uplift achievable
- Previous negotiation (2019): tenant extracted 6 months rent-free

Recommended actions:
1. Schedule strategy meeting (Asset Manager + PM)
2. Commission market comparable analysis
3. Prepare incentive options if retention desired

Related documents:
- Original lease [link]
- 2019 negotiation file [link]
- Recent tenant financials [link]
```

---

#### Strategic Decision Support

**Agent assists with:**

1. **Retention analysis:**
   - Current rent vs market
   - Tenant credit assessment
   - Lease flexibility comparison (what would new lease look like?)
   - Cost of void vs cost of incentives

2. **Negotiation preparation:**
   - Historical precedents with this tenant
   - Market comparables (recent deals)
   - Incentive benchmarks (rent-free, capex, break removal)
   - BATNA analysis (best alternative to negotiated agreement)

3. **Risk quantification:**
   - Probability of break exercise (based on patterns)
   - Financial impact scenarios
   - Portfolio concentration risk
   - Covenant implications (if applicable)

---

#### Notice Management

**Agent supports notice process:**

1. **Drafting:**
   - Generates draft notice based on lease requirements
   - Flags specific formatting/service requirements
   - "Lease requires notice by registered post to Registered Office"

2. **Validation:**
   - Checks all conditions for notice validity
   - "Warning: Tenant in arrears as of last month - break may be ineffective"
   - Recommends remediation actions

3. **Tracking:**
   - Records notice service details
   - Calculates response deadlines
   - Monitors for responses

---

### Key AI Intervention Points

| Manual Process | AI Intervention | Value |
|----------------|-----------------|-------|
| Lease date extraction | Auto-extract all events | Completeness |
| Calendar maintenance | Unified event database | Accuracy |
| Deadline monitoring | Intelligent tiered alerts | No missed deadlines |
| Strategy preparation | Context and comparables | Better decisions |
| Notice drafting | Template + validation | Reduced errors |
| Condition checking | Auto-monitor conditions | Risk mitigation |

---

## Critical AI Requirements

### 1. Extraction Completeness

**The challenge:**
Lease events are scattered across:
- Main lease body
- Schedules and annexes
- Side letters
- Subsequent amendments
- Even email correspondence

**Requirement:**
- Process ALL related documents as a set
- Resolve conflicts (later document takes precedence)
- Flag ambiguities for human review
- Continuous updates as new documents added

---

### 2. Condition Monitoring

**The challenge:**
Many break and other rights are conditional:
- "No material breach"
- "Rent paid and up to date"
- "Repair obligations complied with"
- "Not in occupation of any sublettee"

**Requirement:**
- Monitor relevant condition states
- Alert when condition at risk ("Tenant payment 5 days late")
- Track condition compliance history
- Support tactical use of conditions

---

### 3. Date and Deadline Accuracy

**The challenge:**
Date calculation can be complex:
- "6 months prior to the 5th anniversary"
- "Not less than 3 months and not more than 6 months"
- Working days vs calendar days
- "Next quarter day following"
- English vs Scottish vs European conventions

**Requirement:**
- Accurate date calculation from any format
- Explicit handling of ambiguous specifications
- Configurable business calendars
- Audit trail of calculations

---

### 4. Integration with Operations

**The challenge:**
Lease events require coordination:
- Asset manager (strategy)
- Property manager (tenant liaison)
- Legal (notices and documentation)
- Finance (rent, arrears, provisions)

**Requirement:**
- Role-based workflows and assignments
- Integration with property management systems
- Audit trail of actions and decisions
- Escalation rules and notification chains

---

## Sensitivities and Risks

### Legal Liability

**The risk:**
- Missed deadline → lost right → financial loss → liability claim
- "The system said it was fine" is not a defense
- Notice defects can have major consequences

**Mitigation:**
- AI assists, does not replace legal judgment
- Multiple alert levels with escalation
- Human confirmation required for critical actions
- Clear audit trail of who saw what when

---

### Data Currency

**The risk:**
- Extracted data becomes stale
- Lease variations not reflected
- Decisions made on outdated information

**Mitigation:**
- Document ingestion pipeline for updates
- Clear provenance (extracted from version X on date Y)
- Periodic reconciliation against source documents
- User-flagged discrepancies

---

### Over-reliance

**The risk:**
- Users stop reading leases
- Critical nuances missed by extraction
- Unusual provisions overlooked

**Mitigation:**
- Confidence indicators on extractions
- "Unusual provisions" flagging
- Required human review for material events
- Periodic audit samples

---

## Success Metrics

| Metric | Current State | Target State |
|--------|---------------|--------------|
| Lease events captured | 80% | 99% |
| Deadlines missed | 2-5% annually | 0% |
| Strategy lead time | 3-6 months avg | 12 months |
| Time spent on manual tracking | 20 hrs/month/portfolio | 2 hrs/month |
| Notice defects | 5-10% | <1% |
| Rent review value captured | 70-80% of market | 95% |

---

## Real Example: The Rent Review Left on the Table

### What Actually Happened (Pre-AI)

A fund owned a retail property with a 5-yearly rent review. Market rents had increased 15% since last review.

Timeline:
- Review date: March 2023
- Asset manager noticed in February 2023 (too late for trigger notice)
- Valuation never commissioned
- Trigger notice not served
- Result: Review defaulted to passing rent under lease terms
- Loss: $30k/year for 5 years = $150k in rental value

### How AI Would Have Helped

1. **Event extracted and calendared at acquisition**
2. **Alert at T-12 months:** "Rent review approaching, strategy required"
3. **Market analysis:** "Comparables suggest 12-18% uplift achievable"
4. **Alert at T-6 months:** "Trigger notice deadline 30 days away"
5. **Draft notice:** Generated and flagged for legal review
6. **Result:** Review triggered, negotiation conducted, value captured

---

*Next scenario: Investor Reporting and ESG Compliance*
