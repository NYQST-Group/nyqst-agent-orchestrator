# Product Guidelines

## UI/UX Principles
- **Schema-Driven**: UI generated and reviewed based on schemas.
- **Provenance First**: Every extracted data point must link back to source evidence.
- **Tenant Isolation**: Strict boundaries for enterprise deployments.
- **Asynchronous Workflows**: Built for long-running agentic tasks with real-time streaming updates.

## Technical Principles
- **Pointers over Mutations**: Reversion is moving pointers (Git-like), not rewriting records.
- **Traceability**: Comprehensive audit logging and event ledgers (RunEvents).
- **Security**: SAST/DAST/dependency scanning, SOC 2 readiness.