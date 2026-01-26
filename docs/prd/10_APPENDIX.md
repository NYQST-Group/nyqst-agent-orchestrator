# NYQST: Appendix

**Product:** NYQST - Deterministic Agentic Infrastructure for Commercial Intelligence  
**Company:** NYQST AI Limited  
**Version:** 1.0  
**Last Updated:** 2026-01-25

---

## Glossary

### Platform Concepts

**Agent** - A digital worker that can reason, plan, and execute tasks within defined constraints. Agents operate under AgentDefinitions that specify their capabilities, tools, and policies.

**AgentDefinition** - A versioned specification of an agent's capabilities, allowed tools, retrieval profiles, policy template, and prompt assets.

**Artifact** - Any immutable file or object emitted by the system (PDF, JSON, Parquet, Markdown, HTML, PNG). Artifacts are content-addressed and deduplicated.

**Bundle** - A named pointer to a manifest, representing a working snapshot. Publishing or reverting a bundle moves the pointer.

**Claim** - A requirement, control, mapping, risk, interpretation, or fact asserted by the system. Claims are the unit of assertion and are linked to evidence.

**Corpus** - A governed pointer to a manifest with promotion, evaluation, and approval workflows. Corpora represent validated, production-ready content.

**Deterministic** - Producing the same output given the same input. NYQST calculations are deterministic; AI extractions are probabilistic but with confidence scoring.

**Evidence** - Source material that supports a claim. Evidence is anchored to specific locations in documents (page, paragraph, character offsets).

**EvidenceSpan** - A specific location in a document that provides evidence for a claim. Includes document reference, page, and character offsets.

**Index Service** - The shared knowledge plane that makes content searchable. Provides keyword, semantic, and hybrid search across all platform content.

**Manifest** - An immutable tree of references to artifacts (and optionally nested manifests) plus metadata. Manifests are the unit of versioning.

**MCP (Model Context Protocol)** - A protocol for tool integration that allows agents to call external tools in a standardized way.

**Ontology** - A formal representation of domain knowledge, including concepts, relationships, and rules. The ontology defines how the system understands a domain.

**Pointer** - A mutable HEAD reference to a manifest. Pointer moves are the only "mutation" in the system.

**Policy** - Rules that govern agent behavior, including required provenance, tool permissions, and approval gates. Policies vary by level of care.

**Principal** - A user, service, or agent identity. All actions are attributed to a principal.

**Profile** - A named configuration that binds internal strategies (chunking, reranking, etc.) to a user-facing name. Users select profiles, not implementation details.

**Project** - A container for a client engagement or internal initiative. Projects organize work and control access.

**Run** - An execution instance (agentic, deterministic, or hybrid). Every time work is performed, it happens within a run.

**Run Ledger** - An append-only event stream that records all platform activity for audit and replay.

**Session** - A binding of user + project/objective + compute realm. Sessions have mounts to the substrate and ephemeral filesystems.

**Skill** - A discrete, reusable capability that an agent can use. Skills are versioned and auditable.

**Substrate** - The foundational storage layer that provides "filesystem semantics" for all platform data.

**Tenant** - The organizational boundary for residency, billing, and policies. Each customer organization is a tenant.

**Workspace** - A saved UI layout with pinned resources. A convenience feature, not authoritative storage.

### Domain Concepts (PropSygnal)

**Covenant** - A condition in a loan agreement that the borrower must satisfy. Common covenants include DSCR, LTV, and ICR thresholds.

**DSCR (Debt Service Coverage Ratio)** - Net Operating Income divided by Debt Service. Measures ability to service debt from property income.

**Debt Service** - The total amount of principal and interest payments due on a loan in a given period.

**Debt Yield** - Net Operating Income divided by Loan Balance. Measures the return a lender would receive if they had to foreclose.

**IC Memo** - Investment Committee Memorandum. A document prepared for investment decisions that summarizes the opportunity, risks, and recommendation.

**ICR (Interest Coverage Ratio)** - Net Operating Income divided by Interest Expense. Measures ability to cover interest payments.

**Lender Pack** - A package of documents and data submitted to a lender, typically including rent rolls, operating statements, and covenant calculations.

**LTV (Loan-to-Value)** - Loan Balance divided by Property Value. Measures leverage.

**NOI (Net Operating Income)** - Gross income minus operating expenses, excluding debt service and capital expenditures.

**Operating Statement** - A financial statement showing income and expenses for a property over a period.

**Rent Roll** - A document listing all tenants, their lease terms, and rental amounts.

### Domain Concepts (RegSygnal)

**Ambiguity** - Uncertainty in the interpretation of a regulatory requirement. Ambiguities are explicitly captured and tracked.

**Control** - A measure implemented to satisfy a regulatory requirement.

**Regulatory Requirement** - A specific obligation imposed by a regulation that an organization must satisfy.

**Traceability** - The ability to trace from a regulatory requirement through to the controls that satisfy it.

---

## Acronyms

| Acronym | Meaning |
|---------|---------|
| ABAC | Attribute-Based Access Control |
| API | Application Programming Interface |
| APM | Application Performance Monitoring |
| ARR | Annual Recurring Revenue |
| ACV | Average Contract Value |
| BCBS | Basel Committee on Banking Supervision |
| BM25 | Best Matching 25 (ranking function) |
| CAC | Customer Acquisition Cost |
| CRE | Commercial Real Estate |
| CSAT | Customer Satisfaction |
| DAU | Daily Active Users |
| DD | Due Diligence |
| DocIR | Document Intermediate Representation |
| DR | Disaster Recovery |
| DSCR | Debt Service Coverage Ratio |
| EMIR | European Market Infrastructure Regulation |
| ERP | Enterprise Resource Planning |
| GDPR | General Data Protection Regulation |
| IC | Investment Committee |
| ICR | Interest Coverage Ratio |
| IR | Intermediate Representation |
| LLM | Large Language Model |
| LTV | Loan-to-Value |
| MCP | Model Context Protocol |
| MiFID | Markets in Financial Instruments Directive |
| ML | Machine Learning |
| NLU | Natural Language Understanding |
| NOI | Net Operating Income |
| NPS | Net Promoter Score |
| NRR | Net Revenue Retention |
| OIDC | OpenID Connect |
| P50/P99 | 50th/99th Percentile |
| PC | Practical Completion |
| PM | Property Management / Project Management |
| PRD | Product Requirements Document |
| RBAC | Role-Based Access Control |
| ROI | Return on Investment |
| SFTR | Securities Financing Transactions Regulation |
| SLA | Service Level Agreement |
| UI | User Interface |
| VPC | Virtual Private Cloud |
| WAU | Weekly Active Users |

---

## References

### Internal Documents

| Document | Location | Description |
|----------|----------|-------------|
| Platform Reference Design | `/docs/PLATFORM_REFERENCE_DESIGN.md` | Detailed technical architecture |
| Research Synthesis | `/docs/RESEARCH_SYNTHESIS.md` | Research findings from investigation streams |
| Master Analysis | `/docs/analysis/MASTER_ANALYSIS.md` | Consolidated analysis and decisions |
| CRE User Personas | `/scenarios/personas/cre-user-personas.md` | Detailed persona research |
| Wedge Strategy | `/requirements/WHAT-TO-BUILD-FIRST.md` | Critical dates wedge strategy |

### External References

| Reference | Description |
|-----------|-------------|
| LangGraph Documentation | Orchestration framework for agent workflows |
| Docling Documentation | Document processing library |
| MCP Specification | Model Context Protocol for tool integration |

### Regulatory References (RegSygnal)

| Regulation | Jurisdiction | Domain |
|------------|--------------|--------|
| EMIR | EU | Derivatives reporting |
| MiFID II | EU | Markets and trading |
| SFTR | EU | Securities financing |
| Basel III | Global | Capital requirements |
| BCBS 239 | Global | Risk data aggregation |
| GDPR | EU | Data protection |
| EU AI Act | EU | AI regulation |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-25 | NYQST | Initial PRD suite creation |

---

## PRD Suite Structure

This PRD suite consists of 11 documents:

| Document | Purpose | Primary Audience |
|----------|---------|------------------|
| 00_INDEX.md | Navigation and document architecture | All |
| 01_EXECUTIVE_SUMMARY.md | 2-page overview for quick understanding | Executives, Investors |
| 02_VISION.md | Strategic thesis and long-term direction | Leadership, Investors |
| 03_PLATFORM.md | Platform modules and capabilities | Product, Engineering |
| 04_PRODUCTS.md | PropSygnal and RegSygnal details | Product, Sales, Customers |
| 05_USERS.md | User personas and requirements | Product, Design, Sales |
| 06_ARCHITECTURE.md | Technical architecture overview | Engineering, Technical Buyers |
| 07_ROADMAP.md | Phased delivery plan | All |
| 08_METRICS.md | Success metrics and KPIs | Product, Leadership |
| 09_RISKS.md | Risk factors and mitigations | Leadership, Investors |
| 10_APPENDIX.md | Glossary, references, supporting material | All |

---

## Contact

**NYQST AI Limited**  
London, United Kingdom

For questions about this PRD suite, contact the Product team.

---

**Related Documents:**
- [Index](00_INDEX.md) - Document navigation
- [Executive Summary](01_EXECUTIVE_SUMMARY.md) - Quick overview
