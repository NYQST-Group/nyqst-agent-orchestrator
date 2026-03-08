# Initial Concept
Intelli is an agent-first document intelligence platform tailored for the Commercial Real Estate (CRE) sector.

## Vision
The platform's primary value proposition is a trifecta of capabilities: automated agentic extraction where every data point links to immutable evidence, end-to-end workflow automation for deal processing, and serving as a centralized knowledge management repository for corporate CRE data. The immediate focus and commercial wedge is delivering robust General Document Intelligence capabilities across arbitrary document types.

## Target Users
- **CRE Analysts**: The primary operators uploading leases and other documents to generate structured data and reports.
- **Deal Teams & Lenders**: The critical stakeholders and reviewers consuming the exported lender packs and structured outputs.

## Key Non-Functional Requirements
To be enterprise-ready, the platform is built on two foundational pillars:
- **Strict Tenant Isolation**: Data, streams, and checkpoints must never leak across tenant boundaries.
- **Auditability & Provenance**: A complete, immutable ledger (RunEvents) must trace every AI decision and tool call.