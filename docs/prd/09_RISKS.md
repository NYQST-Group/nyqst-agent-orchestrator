# NYQST: Risks

**Product:** NYQST - Deterministic Agentic Infrastructure for Commercial Intelligence  
**Company:** NYQST AI Limited  
**Version:** 1.0  
**Last Updated:** 2026-01-25

---

## Risk Management Philosophy

NYQST operates in a domain where errors have real consequences. Our users have fiduciary responsibilities. A miscalculated covenant ratio could trigger a loan default. A missed regulatory requirement could result in fines. We must be honest about risks and systematic about mitigation.

This document catalogs known risks, their potential impact, and our mitigation strategies.

---

## Risk Categories

### Technical Risks

#### T1: Document Extraction Accuracy

**Risk:** AI-powered extraction from complex documents (scanned PDFs, handwritten notes, unusual formats) may not achieve required accuracy levels.

**Impact:** High. Incorrect extracted data flows through to calculations and decisions. Users lose trust. Outputs cannot be relied upon.

**Likelihood:** Medium. Modern document AI is good but not perfect. Edge cases are common in real-world documents.

**Mitigation:**
- Confidence scoring on all extractions
- Human verification workflows for low-confidence extractions
- Continuous feedback loop to improve extraction models
- Fallback to manual entry when extraction fails
- Clear indication of extraction source and confidence in all outputs

**Owner:** Engineering

---

#### T2: Model Provider Dependency

**Risk:** Dependence on third-party AI model providers (OpenAI, Anthropic, etc.) creates supply chain risk. Providers may change pricing, deprecate models, or experience outages.

**Impact:** Medium. Service disruption or cost increases could affect operations.

**Likelihood:** Medium. The AI market is volatile and rapidly evolving.

**Mitigation:**
- Multi-provider architecture (no single provider dependency)
- Model abstraction layer allows swapping providers
- Local model options for critical paths (future)
- Contractual commitments with key providers
- Cost monitoring and budgeting per tenant

**Owner:** Engineering + Operations

---

#### T3: Scaling Challenges

**Risk:** Platform may not scale efficiently to portfolio-level workloads (hundreds of assets, thousands of documents).

**Impact:** Medium. Performance degradation affects user experience and limits market reach.

**Likelihood:** Medium. Scaling is always harder than expected.

**Mitigation:**
- Early load testing with realistic data volumes
- Horizontal scaling architecture from the start
- Async processing for heavy workloads
- Caching at multiple layers
- Performance monitoring and alerting

**Owner:** Engineering

---

#### T4: Integration Complexity

**Risk:** Integrations with legacy systems (Yardi, MRI, SharePoint) may be more complex than anticipated.

**Impact:** Medium. Delayed integrations limit product value and adoption.

**Likelihood:** High. Legacy systems are notoriously difficult to integrate with.

**Mitigation:**
- Prioritize integrations based on customer demand
- Build flexible connector framework
- Partner with integration specialists where needed
- Accept manual data import as fallback
- Document integration requirements clearly for customers

**Owner:** Engineering + Product

---

#### T5: Security Vulnerabilities

**Risk:** Security vulnerabilities could expose sensitive customer data or allow unauthorized access.

**Impact:** Critical. Data breach would be catastrophic for trust and business.

**Likelihood:** Low with proper controls, but always present.

**Mitigation:**
- Security-first architecture design
- Regular security audits and penetration testing
- Encryption at rest and in transit
- Principle of least privilege
- Incident response plan
- Bug bounty program (future)

**Owner:** Engineering + Security

---

### Market Risks

#### M1: Competitive Pressure

**Risk:** Well-funded competitors (established PropTech, Big Tech, or new entrants) may enter the market with similar offerings.

**Impact:** Medium. Price pressure, feature wars, customer acquisition challenges.

**Likelihood:** High. The market opportunity is visible to many players.

**Mitigation:**
- Focus on differentiation (deterministic, auditable, evidence-based)
- Build deep domain expertise that's hard to replicate
- Establish customer relationships and switching costs
- Move fast on product development
- Consider strategic partnerships

**Owner:** Leadership + Product

---

#### M2: Market Timing

**Risk:** Market may not be ready for "Cognitive ERP" positioning. Customers may prefer simpler tools or be skeptical of AI.

**Impact:** High. Slow adoption, longer sales cycles, need to pivot positioning.

**Likelihood:** Medium. AI skepticism is real, especially in regulated industries.

**Mitigation:**
- Lead with concrete value (time savings, accuracy) not abstract positioning
- Prove value with pilot customers before scaling
- Offer "Accelerate" and "Preserve" packages for different risk appetites
- Build trust through transparency and evidence trails
- Be prepared to adjust positioning based on market feedback

**Owner:** Leadership + Sales

---

#### M3: Customer Concentration

**Risk:** Early revenue may be concentrated in a small number of customers, creating dependency.

**Impact:** Medium. Loss of a major customer could significantly impact revenue.

**Likelihood:** High in early stages. Inevitable for a new product.

**Mitigation:**
- Diversify customer base as quickly as possible
- Avoid over-customization for single customers
- Build product for the market, not individual customers
- Maintain strong customer relationships
- Monitor customer health proactively

**Owner:** Sales + Customer Success

---

#### M4: Pricing Pressure

**Risk:** Customers may resist ~$200k/annum pricing, especially if competitors offer cheaper alternatives.

**Impact:** Medium. Lower prices reduce margins and sustainability.

**Likelihood:** Medium. Price sensitivity varies by customer segment.

**Mitigation:**
- Anchor pricing to value delivered (analyst replacement cost)
- Offer tiered pricing for different use cases
- Demonstrate clear ROI in sales process
- Be willing to negotiate for strategic accounts
- Monitor competitive pricing

**Owner:** Sales + Finance

---

### Operational Risks

#### O1: Team Scaling

**Risk:** Difficulty hiring and retaining talent with required skills (AI/ML, domain expertise, enterprise software).

**Impact:** High. Slow hiring delays product development and customer support.

**Likelihood:** Medium. Talent market is competitive.

**Mitigation:**
- Build strong employer brand
- Offer competitive compensation
- Create compelling mission and culture
- Invest in training and development
- Consider remote/distributed team

**Owner:** Leadership + HR

---

#### O2: Key Person Dependency

**Risk:** Critical knowledge or capabilities concentrated in a small number of individuals.

**Impact:** High. Loss of key person could significantly impact operations.

**Likelihood:** Medium. Common in early-stage companies.

**Mitigation:**
- Document critical knowledge and processes
- Cross-train team members
- Build redundancy in critical roles
- Retention programs for key personnel
- Succession planning

**Owner:** Leadership

---

#### O3: Customer Support Scaling

**Risk:** Support burden may grow faster than support capacity, leading to poor customer experience.

**Impact:** Medium. Poor support leads to churn and reputation damage.

**Likelihood:** Medium. Support needs are hard to predict.

**Mitigation:**
- Build self-service capabilities (documentation, in-app help)
- Invest in support tooling and automation
- Monitor support metrics closely
- Hire support staff proactively
- Establish clear SLAs and expectations

**Owner:** Customer Success

---

### Regulatory and Compliance Risks

#### R1: Data Protection Compliance

**Risk:** Failure to comply with data protection regulations (GDPR, etc.) could result in fines and reputational damage.

**Impact:** High. Regulatory fines can be significant. Reputational damage affects sales.

**Likelihood:** Low with proper controls.

**Mitigation:**
- Privacy-by-design architecture
- Data residency controls
- Clear data processing agreements
- Regular compliance audits
- Data protection officer (DPO) role
- Customer data handling documentation

**Owner:** Legal + Engineering

---

#### R2: AI Regulation

**Risk:** Emerging AI regulations (EU AI Act, etc.) may impose new requirements on AI systems.

**Impact:** Medium. Compliance costs, potential product changes required.

**Likelihood:** High. AI regulation is accelerating globally.

**Mitigation:**
- Monitor regulatory developments closely
- Design for transparency and explainability (already core to product)
- Maintain audit trails (already core to product)
- Engage with industry groups on regulatory matters
- Build compliance into product roadmap

**Owner:** Legal + Product

---

#### R3: Professional Liability

**Risk:** Customers may hold NYQST liable for errors in outputs that lead to financial losses.

**Impact:** High. Legal costs, settlements, reputational damage.

**Likelihood:** Low with proper controls and contracts.

**Mitigation:**
- Clear terms of service limiting liability
- Emphasis on human verification for critical decisions
- Confidence scoring and uncertainty communication
- Professional liability insurance
- Clear documentation of system limitations

**Owner:** Legal

---

### Product Risks

#### P1: Feature Creep

**Risk:** Pressure to add features may dilute focus and delay core product delivery.

**Impact:** Medium. Slower time to market, increased complexity, technical debt.

**Likelihood:** High. Feature requests are constant.

**Mitigation:**
- Maintain clear product vision and priorities
- Say no to features that don't align with strategy
- Validate feature requests against user research
- Maintain product roadmap discipline
- Regular prioritization reviews

**Owner:** Product

---

#### P2: User Adoption

**Risk:** Users may resist adopting new workflows, preferring familiar (if inefficient) processes.

**Impact:** High. Low adoption means low value delivery and churn.

**Likelihood:** Medium. Change management is always challenging.

**Mitigation:**
- Design for minimal workflow disruption
- Provide excellent onboarding and training
- Show clear value early in user journey
- Build champions within customer organizations
- Iterate based on user feedback

**Owner:** Product + Customer Success

---

#### P3: Trust Calibration

**Risk:** Users may either over-trust (not verify) or under-trust (verify everything) AI outputs, both of which reduce value.

**Impact:** Medium. Over-trust leads to errors. Under-trust eliminates efficiency gains.

**Mitigation:**
- Confidence scoring helps calibrate trust
- Evidence trails enable efficient verification
- Training on appropriate verification levels
- Gradual trust building through consistent accuracy
- Clear communication of system limitations

**Owner:** Product

---

## Risk Matrix

| Risk | Impact | Likelihood | Priority | Owner |
|------|--------|------------|----------|-------|
| T5: Security Vulnerabilities | Critical | Low | High | Engineering |
| T1: Document Extraction Accuracy | High | Medium | High | Engineering |
| M2: Market Timing | High | Medium | High | Leadership |
| O1: Team Scaling | High | Medium | High | Leadership |
| P2: User Adoption | High | Medium | High | Product |
| R3: Professional Liability | High | Low | Medium | Legal |
| R1: Data Protection Compliance | High | Low | Medium | Legal |
| T2: Model Provider Dependency | Medium | Medium | Medium | Engineering |
| T3: Scaling Challenges | Medium | Medium | Medium | Engineering |
| T4: Integration Complexity | Medium | High | Medium | Engineering |
| M1: Competitive Pressure | Medium | High | Medium | Leadership |
| M3: Customer Concentration | Medium | High | Medium | Sales |
| M4: Pricing Pressure | Medium | Medium | Medium | Sales |
| O2: Key Person Dependency | High | Medium | Medium | Leadership |
| O3: Customer Support Scaling | Medium | Medium | Medium | Customer Success |
| R2: AI Regulation | Medium | High | Medium | Legal |
| P1: Feature Creep | Medium | High | Medium | Product |
| P3: Trust Calibration | Medium | Medium | Medium | Product |

---

## Assumptions

The following assumptions underpin the product strategy. If these prove false, significant adjustments may be required.

### Market Assumptions

1. **Mid-cap enterprises need this.** Organizations with fiduciary responsibilities will pay for trustworthy AI infrastructure.

2. **Accuracy matters more than speed.** Users will prefer slower, accurate outputs over faster, unreliable ones.

3. **Evidence trails are valued.** Users will pay a premium for explainable, auditable AI.

4. **The market is ready for "Cognitive ERP."** Organizations are prepared to invest in knowledge infrastructure, not just tools.

### Technical Assumptions

1. **Document AI is good enough.** Current document extraction technology can achieve required accuracy levels with appropriate verification workflows.

2. **LLMs will continue to improve.** Model capabilities will increase while costs decrease.

3. **Multi-provider strategy is viable.** We can maintain provider independence without significant overhead.

4. **The architecture will scale.** The platform design will support portfolio-level workloads.

### Operational Assumptions

1. **We can hire the team.** Required talent is available and we can attract them.

2. **Customers will engage.** Customers will invest time in onboarding and feedback.

3. **Partners will cooperate.** Integration partners will provide necessary access and support.

---

## Dependencies

### External Dependencies

| Dependency | Type | Risk if Unavailable | Mitigation |
|------------|------|---------------------|------------|
| OpenAI/Anthropic APIs | Model Provider | High - core functionality | Multi-provider support |
| Cloud Infrastructure (AWS/GCP) | Infrastructure | Critical - platform unavailable | Multi-region, DR planning |
| Document Processing (Docling) | Library | Medium - extraction degraded | Alternative processors |
| Vector Database | Infrastructure | Medium - search degraded | Multiple options available |

### Internal Dependencies

| Dependency | Type | Risk if Delayed | Mitigation |
|------------|------|-----------------|------------|
| Artifact Substrate | Platform | Critical - nothing works | Prioritize in Phase 0 |
| Agent Runtime | Platform | High - no AI capabilities | Prioritize in Phase 0 |
| Index Service | Platform | High - no search | Prioritize in Phase 0 |
| Workbench UI | Platform | High - no user interface | Prioritize in Phase 0 |

---

## Risk Review Process

Risks are reviewed and updated:
- **Weekly:** Engineering reviews technical risks
- **Monthly:** Leadership reviews all risks
- **Quarterly:** Full risk assessment with all stakeholders

Risk owners are responsible for:
- Monitoring their risks
- Implementing mitigations
- Escalating when risk levels change
- Reporting on risk status

---

**Related Documents:**
- [Executive Summary](01_EXECUTIVE_SUMMARY.md) - Quick overview
- [Roadmap](07_ROADMAP.md) - Delivery plan
- [Metrics](08_METRICS.md) - Success metrics
