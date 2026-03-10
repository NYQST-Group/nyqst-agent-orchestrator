# Implementation Plan: M0 Foundation: Contracts


## Phase 0: Schema Registry & Backstage Deployment (Week 1)
- [ ] Task: Evaluate and Deploy Backstage
  - [ ] Sub-task: Evaluate Backstage vs alternative schema registries for immediate M0 deployment.
  - [ ] Sub-task: Scaffold the Backstage instance (or equivalent) to act as the centralized catalog for all system contracts, APIs, and components.
- [ ] Task: Integrate Schema Pipelines
  - [ ] Sub-task: Build CI/CD pipelines to publish Pydantic schemas and TypeScript definitions directly into the registry catalog.
- [ ] Task: Conductor - User Manual Verification 'Phase 0: Schema Registry & Backstage Deployment' (Protocol in workflow.md)

## Phase 1: Contract Discovery & Model Generation (Week 1)
- [ ] Task: Generate Backend Pydantic Models
  - [ ] Sub-task: Query GitHub for `epic:epic-contracts` issues to gather requirements.
  - [ ] Sub-task: Write the Python Pydantic models for RunEvents, AST Schemas, and Domain Entities in `src/intelli/schemas/`.
  - [ ] Sub-task: Write strict unit tests verifying schema validation and serialization.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Contract Discovery & Model Generation' (Protocol in workflow.md)

## Phase 2: Frontend Sync & CI/CD Checks (Week 1)
- [ ] Task: Generate TypeScript Interfaces
  - [ ] Sub-task: Build the corresponding `.ts` interfaces for the React frontend in `packages/ui-library/types/` or `ui/src/types/`.
  - [ ] Sub-task: Setup an automated CI check (or pre-commit script) to ensure TS/Python schemas remain backward compatible.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Frontend Sync & CI/CD Checks' (Protocol in workflow.md)
## Phase 3: Security & Testing Standards (Week 2)
- [ ] Task: Formalize V4 Testing & Security Baseline
  - [ ] Sub-task: Draft `docs/SECURITY_BASELINE.md` outlining secrets handling, prompt-injection, and tenant isolation rules.
  - [ ] Sub-task: Audit existing test suites to formally map the testing pyramid (Unit, Contract, Integration, E2E).
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Security & Testing Standards' (Protocol in workflow.md)
