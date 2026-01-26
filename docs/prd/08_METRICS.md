# NYQST: Metrics

**Product:** NYQST - Deterministic Agentic Infrastructure for Commercial Intelligence  
**Company:** NYQST AI Limited  
**Version:** 1.0  
**Last Updated:** 2026-01-25

---

## Metrics Philosophy

NYQST metrics are designed around the core value proposition: **trustworthy AI that makes organizations smarter**. We measure not just usage and engagement, but trust, accuracy, and business impact.

The hierarchy of what matters:
1. **Accuracy** - Are outputs correct?
2. **Trust** - Do users rely on the system?
3. **Efficiency** - Does it save time?
4. **Adoption** - Is it being used?
5. **Growth** - Is usage expanding?

---

## Platform Metrics

### Accuracy Metrics

These are the most critical metrics. If accuracy fails, nothing else matters.

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| **Extraction Accuracy** | Percentage of extracted values that match ground truth | 95%+ | Sampled verification against human review |
| **Calculation Accuracy** | Percentage of calculations that are mathematically correct | 100% | Deterministic engines guarantee this |
| **Claim Accuracy** | Percentage of claims that are verified as correct | 95%+ | User verification feedback |
| **False Positive Rate** | Percentage of flagged issues that are not actually issues | <10% | User dismissal tracking |
| **False Negative Rate** | Percentage of real issues that were not flagged | <5% | Post-hoc audit comparison |

### Trust Metrics

Trust is earned through consistent accuracy and transparency.

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| **Verification Rate** | Percentage of outputs that users verify before using | Decreasing over time | UI interaction tracking |
| **Override Rate** | Percentage of AI outputs that users modify | <15% | Edit tracking |
| **Confidence Calibration** | Correlation between stated confidence and actual accuracy | >0.9 | Confidence vs verification outcome |
| **Evidence Click-Through** | Percentage of users who view source evidence | >50% initially, decreasing | UI interaction tracking |
| **Trust Score (Survey)** | User-reported trust in system outputs | >4/5 | Periodic user surveys |

### Efficiency Metrics

Time savings are the tangible benefit users experience.

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| **Time to First Output** | Time from document upload to first structured output | <5 minutes | System timing |
| **Time Saved vs Manual** | Estimated time saved compared to manual process | 80%+ | User surveys + benchmarking |
| **Workflow Completion Time** | Time to complete standard workflows | Baseline -50% | Workflow timing |
| **Rework Rate** | Percentage of outputs requiring significant rework | <10% | User feedback + edit tracking |

### Adoption Metrics

Usage indicates whether the product is delivering value.

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| **Daily Active Users (DAU)** | Users who perform at least one action per day | Growing | Authentication logs |
| **Weekly Active Users (WAU)** | Users who perform at least one action per week | Growing | Authentication logs |
| **Feature Adoption** | Percentage of users using each major feature | >50% for core features | Feature usage tracking |
| **Session Duration** | Average time spent in platform per session | Stable or growing | Session tracking |
| **Return Rate** | Percentage of users who return within 7 days | >80% | Cohort analysis |

### System Health Metrics

The platform must be reliable and performant.

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| **Uptime** | Percentage of time system is available | 99.9% | Monitoring |
| **Response Time (P50)** | Median response time for user actions | <500ms | APM |
| **Response Time (P99)** | 99th percentile response time | <2s | APM |
| **Error Rate** | Percentage of requests that result in errors | <0.1% | Error tracking |
| **Processing Queue Depth** | Number of documents waiting to be processed | <100 | Queue monitoring |

---

## PropSygnal Metrics

### Debt & Credit MVP Metrics

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| **Covenant Calculation Accuracy** | Percentage of covenant calculations matching manual verification | 100% | Deterministic + audit |
| **Extraction Accuracy (Rent Rolls)** | Accuracy of rent roll data extraction | 95%+ | Sampled verification |
| **Extraction Accuracy (Op Statements)** | Accuracy of operating statement extraction | 95%+ | Sampled verification |
| **Extraction Accuracy (Loan Agreements)** | Accuracy of loan agreement extraction | 90%+ | Sampled verification |
| **Lender Pack Generation Time** | Time to generate complete lender pack | <30 minutes | System timing |
| **User Confidence to Submit** | Users willing to submit outputs to lenders without additional review | >80% | User survey |

### Asset Management Metrics

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| **Report Generation Time** | Time to generate quarterly report | <2 hours | System timing |
| **Data Freshness** | Age of most recent data in dashboards | <24 hours | Data timestamps |
| **Alert Accuracy** | Percentage of alerts that are actionable | >90% | User feedback |
| **Portfolio Coverage** | Percentage of portfolio assets actively monitored | 100% | Asset tracking |

### Investment & Acquisitions Metrics

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| **Deal Screening Time** | Time to initial fit/no-fit decision | <30 minutes | System timing |
| **DD Completion Time** | Time to complete standard DD workflow | Baseline -50% | Workflow timing |
| **IC Memo Generation Time** | Time to generate first draft IC memo | <4 hours | System timing |
| **Red Flag Detection Rate** | Percentage of material issues identified by system | >95% | Post-close audit |

---

## RegSygnal Metrics

### Regulatory Intelligence Metrics

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| **Requirement Extraction Accuracy** | Accuracy of extracted regulatory requirements | 95%+ | Expert review |
| **Change Detection Latency** | Time from regulatory publication to system awareness | <24 hours | Publication tracking |
| **Impact Assessment Accuracy** | Accuracy of predicted impact on organization | >85% | Post-implementation review |

### Compliance Modelling Metrics

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| **Requirement Coverage** | Percentage of requirements with modelled logic | >95% | Coverage analysis |
| **Ambiguity Capture Rate** | Percentage of ambiguities explicitly captured | >90% | Expert review |
| **Implementation Traceability** | Percentage of requirements traceable to controls | 100% | Traceability matrix |

---

## Business Metrics

### Revenue Metrics

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| **Annual Recurring Revenue (ARR)** | Total annualized subscription revenue | Growing | Billing system |
| **Average Contract Value (ACV)** | Average annual value per customer | ~$200k | Billing system |
| **Net Revenue Retention (NRR)** | Revenue from existing customers year-over-year | >110% | Cohort analysis |
| **Customer Acquisition Cost (CAC)** | Cost to acquire a new customer | <1x ACV | Sales + marketing spend |

### Customer Metrics

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| **Customer Count** | Number of paying customers | Growing | CRM |
| **Logo Churn** | Percentage of customers who cancel | <10% annually | CRM |
| **Net Promoter Score (NPS)** | Customer likelihood to recommend | >50 | Periodic surveys |
| **Customer Satisfaction (CSAT)** | Customer satisfaction with product | >4/5 | Periodic surveys |

### Engagement Metrics

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| **Documents Processed** | Total documents processed per month | Growing | System logs |
| **Workflows Completed** | Total workflows completed per month | Growing | System logs |
| **Claims Generated** | Total claims generated per month | Growing | System logs |
| **Evidence Links Created** | Total evidence links created per month | Growing | System logs |

---

## Success Criteria by Phase

### Phase 0: Platform Foundation

| Criterion | Target | How Measured |
|-----------|--------|--------------|
| Core infrastructure operational | All components deployed | Deployment verification |
| Document ingestion working | 5+ formats supported | Format testing |
| Agent execution with audit trail | 100% of runs logged | Run ledger verification |
| Analysis canvas functional | Basic exploration possible | User testing |

### Phase 1: PropSygnal Debt MVP

| Criterion | Target | How Measured |
|-----------|--------|--------------|
| Extraction accuracy | 95%+ | Sampled verification |
| Calculation accuracy | 100% | Deterministic verification |
| Time savings | 80% vs manual | User benchmarking |
| User confidence | Ready to submit to lenders | User survey |
| Paying customers | 3+ | Sales tracking |

### Phase 2: PropSygnal Expansion

| Criterion | Target | How Measured |
|-----------|--------|--------------|
| Portfolio scale | 50+ assets per customer | Usage tracking |
| Report generation | <2 hours | System timing |
| Deal screening | 75% time reduction | User benchmarking |
| Customer expansion | Existing customers add modules | Sales tracking |

### Phase 3: PropSygnal Full Suite

| Criterion | Target | How Measured |
|-----------|--------|--------------|
| Full lifecycle coverage | All 5 areas operational | Feature verification |
| Data continuity | Seamless handoffs between stages | User testing |
| Customer satisfaction | NPS >50 | Survey |
| Revenue growth | ARR growing >50% | Billing system |

---

## Metric Collection and Reporting

### Data Collection

All metrics are collected automatically where possible:
- System logs capture timing and usage
- UI instrumentation captures user interactions
- Run ledger captures all AI operations
- Surveys capture subjective measures

### Reporting Cadence

| Report | Frequency | Audience |
|--------|-----------|----------|
| System Health Dashboard | Real-time | Engineering |
| Weekly Metrics Summary | Weekly | Product + Engineering |
| Monthly Business Review | Monthly | Leadership |
| Quarterly Customer Review | Quarterly | All stakeholders |

### Metric Ownership

| Metric Category | Owner |
|-----------------|-------|
| Accuracy Metrics | Product |
| Trust Metrics | Product |
| Efficiency Metrics | Product |
| Adoption Metrics | Product + Growth |
| System Health | Engineering |
| Business Metrics | Finance + Sales |

---

## Anti-Metrics

Things we explicitly do NOT optimize for:

| Anti-Metric | Why We Avoid It |
|-------------|-----------------|
| **Raw throughput** | Speed without accuracy is dangerous |
| **Feature count** | Features without value add complexity |
| **AI autonomy** | More autonomy without more trust is risky |
| **Engagement time** | We want efficiency, not stickiness |

---

**Related Documents:**
- [Executive Summary](01_EXECUTIVE_SUMMARY.md) - Quick overview
- [Roadmap](07_ROADMAP.md) - Delivery plan
- [Risks](09_RISKS.md) - Risk factors
