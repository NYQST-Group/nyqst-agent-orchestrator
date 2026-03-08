# Specification: M0.5 Lease CD MVP

## Objective
Deliver a "lender-ready" Lease CD MVP in 8 weeks. This requires focusing on the core lease workflow while deferring advanced platform features. The system must ingest leases, extract terms accurately using the LLM agent, run them through a cashflow rules engine, provide a UI to review the evidence, and export a deterministic Excel lender pack.

## Key Deliverables
1. **Document Ingestion (Basic)**: Support standard PDF/Word uploads with basic parsing.
2. **Term Extraction**: LangGraph agent workflow for extracting key CRE lease terms (rent, dates, tenant info).
3. **Cashflow Engine**: A rule-based engine to project cashflows based on the extracted terms.
4. **Evidence-backed Review UI**: A schema-driven UI to review extracted terms alongside their citations (evidence spans) in the source document.
5. **Excel Export**: A deterministic, template-driven Excel generator for the final lender pack.
6. **Onboarding Templates**: Provide a "first-run" sample project and lease docs package for easy onboarding.

## Architecture Context
- **Substrate**: Extracted terms and reports are saved as immutable Artifacts.
- **RunEvents**: Used for progress tracking and basic state persistence.
- **Frontend**: Schema-driven Review UI and standard Artifact lists.

## Security & Enterprise
- Ensure tenant isolation is maintained (especially in streaming events).
- Base RBAC stub for users (Admin vs Member).