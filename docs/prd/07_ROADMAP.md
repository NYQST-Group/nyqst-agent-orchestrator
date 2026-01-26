# NYQST: Roadmap

**Product:** NYQST - Deterministic Agentic Infrastructure for Commercial Intelligence  
**Company:** NYQST AI Limited  
**Version:** 1.0  
**Last Updated:** 2026-01-25

---

## Roadmap Philosophy

The NYQST roadmap follows a "platform first, then products" approach. We must establish the core infrastructure before we can deliver reliable product experiences. This is not about building features; it's about building the foundation that makes features trustworthy.

**Current Priority:** Stand up the core platform with agents, views, config, agentic system, skills system, file storage, session management, assisted workflows, document ingestion from tough sources, and the analysis component with infinite canvas.

Once the platform foundation is solid, we can execute end-to-end use cases with confidence.

---

## Roadmap Overview

```
2026                                                              2027
Q1              Q2              Q3              Q4              Q1+
│               │               │               │               │
├───────────────┼───────────────┼───────────────┼───────────────┤
│               │               │               │               │
│  PLATFORM     │  PLATFORM     │  PROPSYGNAL   │  PROPSYGNAL   │  ECOSYSTEM
│  FOUNDATION   │  COMPLETE     │  EXPANSION    │  FULL SUITE   │  & REGSYGNAL
│               │               │               │               │
│  Core infra   │  All modules  │  Asset Mgmt   │  Dev & PM     │  Integrations
│  Agentic sys  │  operational  │  Investment   │  Property Mgmt│  RegSygnal v1
│  Analysis UI  │  PropSygnal   │  Portfolio    │  Full lifecycle│ API access
│               │  Debt MVP     │  scale        │               │
│               │               │               │               │
└───────────────┴───────────────┴───────────────┴───────────────┘
```

---

## Phase 0: Platform Foundation (Current - Q1 2026)

### Objective

Establish the core platform infrastructure that all products will build upon. This is the "Cognitive ERP" foundation.

### Focus Areas

**Agentic System & Skills Framework**

The agentic system is the heart of NYQST. We need:
- Agent definitions with versioned capabilities
- Skills framework for reusable capabilities
- Tool integration via MCP
- Policy enforcement for agent behavior
- Run ledger for complete audit trail

**Views & Configuration**

Users need to see and control what the system is doing:
- Workbench UI with IDE-like capabilities
- Configuration management for agents, skills, policies
- Session management and state persistence
- Real-time streaming updates

**File Storage & Document Management**

The substrate for all data:
- Immutable artifact storage with content-addressing
- Manifest and pointer system for versioning
- Bundle and corpus organization
- Ingestion pipeline for tough sources (scanned PDFs, legacy formats)

**Analysis Component**

The visual analysis capability:
- Infinite canvas for exploration
- Relationship visualization
- Pattern recognition tools
- Export and sharing capabilities

**Assisted Workflows**

Guided processes that combine AI and human judgment:
- Workflow definition and execution
- Human-in-the-loop checkpoints
- Progress tracking and resumability
- Approval and sign-off flows

### Deliverables

| Deliverable | Description | Status |
|-------------|-------------|--------|
| Artifact substrate | Immutable storage, manifests, pointers | Complete |
| Run ledger | Append-only audit trail | Complete |
| Authentication | Multi-tenant auth and authorization | Complete |
| MCP tools | Agent tool integration | Complete |
| Workbench UI | React-based IDE interface | In Progress |
| Agent runtime | LangGraph-based orchestration | In Progress |
| Skills framework | Reusable capability system | In Progress |
| Document ingestion | PDF, Word, scanned document handling | In Progress |
| Analysis canvas | Infinite canvas UI | Planned |
| Assisted workflows | Guided process execution | Planned |

### Success Criteria

- Platform can ingest documents from multiple formats
- Agents can execute skills with full audit trail
- Users can configure and monitor agent behavior
- Analysis canvas supports basic exploration
- Workflows can be defined and executed with human checkpoints

---

## Phase 1: Platform Complete + PropSygnal Debt MVP (Q2 2026)

### Objective

Complete all platform modules and deliver the first PropSygnal product: Debt & Credit monitoring for single assets.

### Platform Completion

**Research Module**
- Fast search across knowledge base
- Deep research workflows
- Source linking and provenance
- Research session management

**Document Management Module**
- Full bundle/corpus organization
- Version control and history
- Access control at document level
- Format handling for all common types

**Analysis Module**
- Complete infinite canvas
- Relationship visualization
- Timeline views
- Annotation and notes

**Modelling Module**
- Calculation engines (versioned, deterministic)
- Evidence chain generation
- Confidence scoring
- Claim lifecycle management

**Knowledge & Domain Module**
- Ontology management
- Domain model definition
- Context injection for agents
- Version control for ontologies

**Organisational Insight Module**
- Portfolio dashboards
- Alert management
- Trend analysis
- Report generation

### PropSygnal Debt & Credit MVP

**Scope: Single Asset Covenant Monitoring**

| Capability | Description |
|------------|-------------|
| Document ingestion | Rent rolls, operating statements, loan agreements |
| Data extraction | AI-powered extraction with confidence scores |
| Covenant calculations | DSCR, LTV, ICR, Debt Yield |
| Evidence trails | Every calculation traceable to source |
| Lender pack generation | Excel output with full audit trail |
| Alert system | Proactive notification of covenant risks |

**Target Users**
- Asset Managers monitoring covenant compliance
- Financial Controllers preparing lender submissions
- Credit Analysts reviewing loan performance

**Success Criteria**
- 95% extraction accuracy on standard documents
- 100% calculation accuracy (deterministic)
- 80% time reduction vs manual process
- Users confident to submit outputs to lenders

---

## Phase 2: PropSygnal Expansion (Q3 2026)

### Objective

Expand PropSygnal to cover Asset Management and Investment & Acquisitions, with portfolio-scale capabilities.

### Asset Management

**Quarterly Reporting**
- Automated report generation from source data
- Links to underlying financials
- Commentary assistance
- Multi-format output (Excel, PowerPoint, PDF)

**Value-Add Tracking**
- Capex analysis and tracking
- Rental growth monitoring
- Refurbishment timing
- Business plan management

**Portfolio Scale**
- Multi-asset processing
- Multiple facilities per asset
- Cross-portfolio dashboards
- Batch operations

### Investment & Acquisitions

**Deal Screening**
- Automated review against investment criteria
- Quick triage of incoming opportunities
- Fit/no-fit recommendations with evidence

**Due Diligence Automation**
- Property DD workflows
- Technical DD workflows
- Legal DD workflows
- Financial DD workflows

**IC Memo Generation**
- Automated first drafts
- Data-backed assertions
- Risk flag highlighting
- Comparable deal references

### Success Criteria

- Portfolio managers can monitor 50+ assets from single dashboard
- Quarterly reports generated in hours, not days
- Deal screening reduces triage time by 75%
- IC memos include full evidence trails

---

## Phase 3: PropSygnal Full Suite (Q4 2026)

### Objective

Complete the PropSygnal product suite with Development & Project Management and Property Management.

### Development & Project Management

**Development Dashboard**
- Cost monitoring (hard costs, soft costs, contingency)
- Programme tracking and variance alerts
- Risk identification and tracking
- Forecast completion updates

**Building Safety Act Compliance**
- Gateway process support
- Document checking and validation
- Compliance pack generation
- Audit trail for submissions

**Planning Process Support**
- Policy alignment checking
- Application tracking
- Document management for planning submissions

### Property Management

**Leasing & Sales Management**
- Tenant pipeline tracking
- Deal tracking and reporting
- Lease negotiation support

**Operations**
- Tenant management (onboarding, references, turnover)
- Contract and lease administration
- Service charge management
- Rent collection and arrears tracking

**Compliance**
- Regulatory requirement tracking
- Certificate expiry monitoring
- Health and safety documentation
- Audit preparation support

### Lifecycle Integration

With all five product areas complete, PropSygnal delivers full lifecycle coverage:
- Data flows from acquisition through exit
- Single source of truth across all stages
- Complete evidence trails throughout
- Handoffs between stages are seamless

### Success Criteria

- Full investment lifecycle supported in single platform
- Development projects tracked from land to PC
- Property operations integrated with asset management
- Compliance requirements tracked automatically

---

## Phase 4: Ecosystem & RegSygnal (2027+)

### Objective

Build the ecosystem of integrations and launch RegSygnal for regulatory intelligence.

### Ecosystem Development

**API Access**
- Programmatic access to platform capabilities
- Webhook notifications
- Bulk operations
- Custom integrations

**Integrations**
- Property management systems (Yardi, MRI)
- Market data providers (CoStar, Bloomberg)
- Document storage (SharePoint, Google Drive)
- Communication tools (Slack, Teams)

**Lender Portal**
- Direct submission to lenders
- Lender-specific formatting
- Submission tracking
- Response management

**White-Label Options**
- Branded deployments
- Custom domain support
- Configurable UI themes

### RegSygnal Launch

**Regulatory Intelligence**
- Regulatory document ingestion
- Requirement extraction and classification
- Change detection and impact analysis
- Cross-regulation mapping

**Reporting Validation**
- Report schema validation
- Data quality checks
- Reconciliation tools
- Exception tracking

**Compliance Modelling**
- Requirement decomposition
- Ambiguity capture and resolution
- Logic modelling
- Implementation mapping

**Target Regulations**
- EMIR (derivatives reporting)
- MiFID II (markets and trading)
- SFTR (securities financing)
- Basel III (capital requirements)
- BCBS 239 (risk data aggregation)

### Success Criteria

- API enables third-party integrations
- Major PM systems integrated
- RegSygnal pilot with selected regulatory framework
- Compliance modelling demonstrates value vs traditional approaches

---

## Technical Roadmap

### Infrastructure Evolution

| Component | Phase 0-1 | Phase 2 | Phase 3+ |
|-----------|-----------|---------|----------|
| MCP servers | Core set | Extended | Full suite |
| Workflows | Basic | Scheduled | Complex |
| Storage | Single-tenant | Multi-tenant | Federated |
| Analytics | Evidence only | Dashboards | ML pipeline |

### Integration Timeline

| Integration | Phase |
|-------------|-------|
| SharePoint/OneDrive | Phase 1 |
| Google Drive | Phase 1 |
| Yardi | Phase 2 |
| MRI | Phase 2 |
| Building Passport | Phase 2 |
| Bloomberg | Phase 3 |
| CoStar | Phase 3 |
| Planning portals | Phase 3 |

---

## Risk-Adjusted Timeline

The roadmap assumes steady progress. Key risks that could affect timing:

**Technical Risks**
- Document extraction accuracy may require more iteration
- Scaling to portfolio level may surface performance issues
- Integration complexity with legacy systems

**Market Risks**
- Customer adoption pace may vary
- Competitive pressure may require feature acceleration
- Regulatory changes may shift priorities

**Resource Risks**
- Team scaling may lag requirements
- Key person dependencies
- Third-party dependency changes

### Mitigation Approach

- Build platform foundation thoroughly before product features
- Validate with real users at each phase
- Maintain flexibility to adjust priorities
- Keep technical debt low to enable pivots

---

## Milestone Summary

| Milestone | Target | Key Deliverable |
|-----------|--------|-----------------|
| Platform Foundation | Q1 2026 | Core infrastructure operational |
| PropSygnal Debt MVP | Q2 2026 | Single asset covenant monitoring |
| Portfolio Scale | Q3 2026 | Multi-asset, multi-facility |
| Full Lifecycle | Q4 2026 | All five PropSygnal areas |
| Ecosystem | 2027 | API, integrations, white-label |
| RegSygnal v1 | 2027 | Regulatory intelligence pilot |

---

**Related Documents:**
- [Executive Summary](01_EXECUTIVE_SUMMARY.md) - Quick overview
- [Platform Modules](03_PLATFORM.md) - Module capabilities
- [Products](04_PRODUCTS.md) - PropSygnal & RegSygnal details
- [Metrics](08_METRICS.md) - Success metrics
