# Implementation Plan: M0.5 Lease CD MVP

## Phase 1: Foundation & Data Model (Week 1)
- [ ] Task: Set up basic entity types and normalization (V4-P0-006)
  - [ ] Sub-task: Write Tests for EntityType enum enforcement
  - [ ] Sub-task: Implement EntityType enum in Pydantic + TS
  - [ ] Sub-task: Implement DB constraints/indexes
  - [ ] Sub-task: Add migration script for existing legacy data
- [ ] Task: Project/Workspace switcher & Recents (V4-FE-002)
  - [ ] Sub-task: Write Tests for UI context switch
  - [ ] Sub-task: Implement backend scope APIs (if not present)
  - [ ] Sub-task: Build React UI switcher
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Foundation & Data Model' (Protocol in workflow.md)

## Phase 2: Lease Extraction Agent & Rules Engine (Weeks 2-3)
- [ ] Task: Lease term extraction workflow
  - [ ] Sub-task: Write Tests for LangGraph node outputs
  - [ ] Sub-task: Build document ingestion parser hook (Basic PDF)
  - [ ] Sub-task: Create LangGraph extraction agent for CRE schemas
- [ ] Task: Cashflow rules engine
  - [ ] Sub-task: Write unit tests for cashflow projections
  - [ ] Sub-task: Implement deterministic cashflow calculator based on schemas
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Lease Extraction Agent & Rules Engine' (Protocol in workflow.md)

## Phase 3: Schema-Driven UI & Evidence Review (Weeks 4-6)
- [ ] Task: Provenance citations framework (SP3)
  - [ ] Sub-task: Write Tests for citation linking to source docs
  - [ ] Sub-task: Backend support for storing `evidence_span` in Run Events/Artifacts
- [ ] Task: Schema-Driven Review UI
  - [ ] Sub-task: Write UI Tests for the review component
  - [ ] Sub-task: Build generic React components for structured validation
  - [ ] Sub-task: Integrate evidence viewer next to extracted fields
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Schema-Driven UI & Evidence Review' (Protocol in workflow.md)

## Phase 4: Deterministic Excel Export (Week 7)
- [ ] Task: Export Engine Foundation (V4-EX-001 & V4-EX-002)
  - [ ] Sub-task: Write backend tests for Template Registry
  - [ ] Sub-task: Setup Golden File testing harness for Excel outputs
  - [ ] Sub-task: Implement `xlsx` mapping layer
- [ ] Task: LeaseCD Lender Pack Template (V4-EX-003)
  - [ ] Sub-task: Implement template based on CRE standards
  - [ ] Sub-task: Ensure cashflow calculations populate correctly
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Deterministic Excel Export' (Protocol in workflow.md)

## Phase 5: Onboarding & MVP Finalization (Week 8)
- [ ] Task: First-run checklist & Sample Project (V4-ONB-001 & V4-ONB-003)
  - [ ] Sub-task: Write E2E Tests for sample project creation
  - [ ] Sub-task: Implement UI checklist state tracking
  - [ ] Sub-task: Create the sample lease package data bundle
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Onboarding & MVP Finalization' (Protocol in workflow.md)