# Specification: M0 Foundation: Contracts & Standards

## Objective
Implement the foundational data schemas and testing baselines for the platform. This track bridges the architectural intent of the V4 Build Pack (`EPIC-CONTRACTS` and `EPIC-STANDARDS`) with pragmatic, professional engineering practices.

## Execution Directives
1. **Data Source Integration**: The implementing developer/agent should query the GitHub repository for open issues labeled `epic:epic-contracts` (e.g., `BL-002`, `BL-004`, `BL-022`, `STUDIO-003`) to understand the required Acceptance Criteria.
2. **Engineering Judgment**: While the GitHub issues provide the constraints, use professional judgment to design elegant, scalable Pydantic models and TypeScript interfaces that fit naturally into the existing `src/intelli/schemas` structure.
3. **Standard Enforcement**: All generated code must adhere to the `conductor/tech-stack.md` and the established `conductor/workflow.md` (including the strict TDD verification for Python/TS files).

## Scope
- Define canonical Pydantic models for core entities: `Artifacts`, `RunEvents`, `Evidence`, `Entities`, and `Exports`.
- Ensure TS interfaces are generated or perfectly mapped to support the React UI.
- Formally implement the testing pyramid and security baselines required by `EPIC-STANDARDS`.