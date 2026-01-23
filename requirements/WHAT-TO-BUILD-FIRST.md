# What to Build First: The Wedge Strategy

*Date: 2026-01-23*
*Purpose: Turn primitives into an adoption-first product strategy*

---

## The Real Problem

We have:
- ✅ Five validated primitives
- ✅ CRE domain knowledge
- ✅ Cross-domain validation
- ✅ Technical architecture ideas

We don't have:
- ❌ A reason for a skeptical professional to try this
- ❌ An "aha moment" that creates advocates
- ❌ A path from first use to dependency
- ❌ An answer to "why you vs doing it manually?"

**The 95% of failed AI projects had good technology. They failed on adoption.**

---

## The Wedge Strategy

### Principle: Win One Job, Then Expand

Don't launch a "platform." Launch a tool that does ONE thing so well that professionals can't live without it.

Then expand.

### Criteria for the Wedge

| Criterion | Why It Matters |
|-----------|----------------|
| **High pain, clear value** | User immediately gets why they need it |
| **Frequent use** | Daily/weekly, not quarterly |
| **Visible to decision-makers** | Success is noticed by people who buy |
| **Low risk to try** | Failure during trial doesn't hurt user |
| **Hard to do manually** | Not just faster, actually better |
| **Natural expansion** | Leads to adjacent use cases |

---

## The Wedge: "Never Miss a Critical Date"

### Why This?

| Criterion | Lease Critical Dates |
|-----------|---------------------|
| High pain | Miss a break = $500k-$2M loss |
| Frequent | Events happening constantly across portfolio |
| Visible | Asset managers, portfolio managers, investors all see |
| Low risk | Running in parallel with existing system = safe |
| Hard manually | 2000+ events across 500 leases, scattered in documents |
| Expansion | Once you trust dates, trust extraction, trust analysis... |

### The "Aha Moment"

**Before:** "I have 500 leases in PDFs and spreadsheets. I think I know all the key dates. I hope nothing falls through."

**After:** "I uploaded my leases. In 20 minutes it found 47 break options, 3 in the next 6 months that I didn't have calendared. It shows me exactly where in each lease. It's already sent me the first alert."

**The moment:** User discovers something they didn't know was there.

---

## The Minimal Product

### What It Does (V1)

1. **Upload leases** (PDF, Word, scanned)
2. **Extract critical dates** (breaks, reviews, expiries, options)
3. **Show confidence + source** (click to verify)
4. **Alert on approaching deadlines** (email + dashboard)
5. **Record outcomes** (what happened when date arrived)

### What It Doesn't Do (V1)

- Full lease abstraction (only dates + essential context)
- Rent roll management
- Financial modeling
- DD workflows
- Investor reporting
- Any other primitive

**Discipline:** Do ONE thing exceptionally well.

### The Trust Journey

```
WEEK 1: SKEPTIC
"I'll try it, but I'll verify everything"
├── User uploads 10 leases
├── System extracts dates
├── User verifies each extraction
├── User finds 1-2 dates they missed
└── User thinks: "Okay, this is useful"

WEEK 2-4: VERIFIER
"It's mostly right, I spot-check"
├── User uploads more leases
├── User verifies less (spot checks)
├── System catches a date user missed
└── User thinks: "This is actually reliable"

MONTH 2-3: TRUSTER
"I trust it for dates, what else can it do?"
├── User relies on alerts
├── User uses dashboard as source of truth
├── User asks: "Can it extract rent amounts too?"
└── User thinks: "I want more of this"

MONTH 4+: ADVOCATE
"Everyone needs this"
├── User tells colleagues
├── User pushes for team adoption
├── User requests new features
└── User is reference customer
```

---

## What To Build: Technical Scope

### Core (Must Have for V1)

**Document Processing:**
```
- PDF/Word/image ingestion
- OCR for scanned documents
- Basic structure extraction (pages, paragraphs)
- Date pattern detection
- Lease identification (is this a lease?)
```

**Event Extraction:**
```
- Break option detection (date, notice period, conditions, party)
- Rent review detection (date, mechanism)
- Lease expiry detection
- Renewal option detection
- Confidence scoring per extraction
- Source citation (page, paragraph, highlighted text)
```

**Event Management:**
```
- Event calendar (all events, filterable)
- Deadline calculation (from notice periods)
- Alert rules (configurable lead times)
- Email notifications
- Dashboard view
```

**Verification UX:**
```
- Click extraction → see source document
- Highlight extraction in document
- Correct/confirm extraction
- Corrections improve future extractions
```

### Not Core (Defer for V1)

- Entity resolution
- Document relationships
- Claim/decision workflows
- Report generation
- External integrations
- Multi-tenant complexity
- Advanced analytics

---

## Success Metrics

### Leading Indicators (Adoption)

| Metric | Week 1 | Month 1 | Month 3 |
|--------|--------|---------|---------|
| Leases uploaded | 20 | 200 | 1000 |
| Extraction accuracy | 85% | 92% | 96% |
| User corrections/week | 50 | 20 | 5 |
| Return users | 60% | 80% | 95% |
| Time in product/week | 30 min | 2 hrs | 5 hrs |

### Lagging Indicators (Value)

| Metric | Month 3 | Month 6 | Month 12 |
|--------|---------|---------|----------|
| Critical dates caught user would have missed | 5 | 25 | 100 |
| Users who say "can't work without it" | 2 | 10 | 50 |
| Feature requests (expansion signal) | 20 | 100 | 500 |
| Referrals to colleagues | 3 | 15 | 75 |

### The North Star

**Zero missed critical dates for any user, ever.**

If we achieve this, we win. Everything else follows.

---

## The Expansion Path

### After Critical Dates Work

```
V1: Critical Dates
     ↓
V2: Full Lease Extraction
    (Now they trust our extraction)
     ↓
V3: Covenant Monitoring
    (Same pattern: extract + monitor + alert)
     ↓
V4: DD Acceleration
    (They already have extracted lease data)
     ↓
V5: Investor Reporting
    (Generate from trusted data)
     ↓
V6: Platform
    (They're dependent; now we're a platform)
```

Each step only works if the previous step earned trust.

---

## What This Means for Architecture

### Build for the Wedge, Design for the Platform

**Build now:**
- Document ingestion pipeline
- Date/event extraction model
- Event management engine
- Alert system
- Verification UX

**Design now, build later:**
- Entity resolution hooks
- Document relationship model
- Claim/decision framework
- Generation/review workflow

**The schemas we wrote are right.** But we implement them incrementally:
- Event schema: V1
- Document schema (extraction part): V1
- Document schema (relationships): V2
- Claim schema: V3
- Entity schema: V2-V3

---

## The Demo That Sells

### The 10-Minute Demo

1. **Setup (30 sec):** "Let me show you something. Can I upload a few of your leases?"

2. **Upload (60 sec):** User provides 5 real leases (ideally ones they know well)

3. **Processing (90 sec):** System processes, shows progress, shows confidence

4. **Results (120 sec):**
   - "Here are the 23 critical dates we found"
   - "Click any one to see exactly where it is in the lease"
   - User clicks, sees highlighted source

5. **The Hook (60 sec):**
   - "Did you know this tenant has a break option in 4 months?"
   - "The notice deadline is in 6 weeks"
   - "Was that in your tracker?"

6. **The Alert (60 sec):**
   - "We'll email you 30 days before every notice deadline"
   - "And 7 days before if no action recorded"
   - "With a link directly to the clause in the lease"

7. **Close (60 sec):**
   - "Want to upload the rest of your portfolio?"
   - "Let's set up your alerts"

**The demo only works if it finds something they missed.** That's the aha moment.

---

## What We Stop Doing

### Stop
- Writing more scenario documents
- Designing more primitives
- Researching more patterns
- Perfecting schemas

### Start
- Building the extraction model
- Building the alert engine
- Testing with real leases
- Getting in front of users

---

## The 30-Day Plan

### Week 1: Extraction POC
- [ ] Build basic PDF ingestion
- [ ] Train/configure date extraction on 50 sample leases
- [ ] Measure accuracy: can we hit 85%?
- [ ] Build basic verification UI

### Week 2: Event Engine
- [ ] Implement event schema (simplified for dates only)
- [ ] Build deadline calculation
- [ ] Build basic alert system (email)
- [ ] Build dashboard view

### Week 3: Integration
- [ ] Connect extraction to event engine
- [ ] Build end-to-end: upload → extract → alert
- [ ] Add verification UX
- [ ] Fix bugs, improve UX

### Week 4: User Testing
- [ ] Get 3-5 real users
- [ ] Upload their real leases
- [ ] Watch them use it
- [ ] Learn what's broken, what's missing

**At end of 30 days:** Either we have something users want, or we learn why not.

---

## The Bet

**We bet that:**
1. Lease critical date management is painful enough to create demand
2. We can extract dates with 90%+ accuracy
3. Finding dates users missed creates "aha moment"
4. Users who trust dates will trust more extraction
5. Trust in extraction leads to platform adoption

**If we're wrong:**
- Wrong on #1: Pick different wedge (covenant monitoring?)
- Wrong on #2: Improve extraction before launch
- Wrong on #3: Need different value hook
- Wrong on #4: Each use case stays isolated
- Wrong on #5: We have a feature, not a platform

**We'll know in 60 days.**

---

*Stop designing. Start building. The next document should be code.*
