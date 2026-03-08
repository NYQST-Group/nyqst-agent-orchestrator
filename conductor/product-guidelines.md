# Product Guidelines

## UI/UX Principles
- **Schema-Driven Interfaces**: User interfaces for reviewing extracted data should be dynamically generated based on strict JSON/Pydantic schemas to ensure data predictability and integrity.
- **Provenance First**: Trust is paramount. Every extracted data point, summary, or report block must provide a clear, one-click mechanism to view the source evidence (citation) within the original document.
- **Asynchronous & Streaming**: The platform relies on long-running agentic workflows. The UI must elegantly handle asynchronous operations using real-time streaming (SSE) to provide immediate feedback on run progress, without blocking the user.
- **Data Density & Clarity**: Designed for Commercial Real Estate analysts. Prioritize information density, clear typography, and scannability over spacious, consumer-style layouts.

## Technical & Architecture Principles
- **Pointers over Mutations**: Emulate Git-like behavior. Reversion and history tracking should be achieved by moving pointers, not by overwriting or deleting records.
- **Immutable Run Ledger**: Every AI decision, tool call, and state change must be recorded in an append-only, immutable `RunEvents` ledger for complete auditability.
- **Enterprise-Grade Isolation**: Strict multi-tenant isolation is a core architectural requirement, extending from the database row-level security up through API endpoints and event streams.

## Prose & Communication Style
- **Professional & Authoritative**: Communication within the app (error messages, tooltips, empty states) should be professional, concise, and direct. Avoid conversational fluff.
- **Action-Oriented**: When errors occur, always provide the user with a clear, actionable path to resolution.