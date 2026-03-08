# Implementation Plan: M0.5 Lease CD MVP

## Phase 0: CI/CD & Project Hygiene Setup (Week 1)
- [ ] Task: Configure GitHub Actions CI/CD Pipeline (V4-INFRA-001)
  - [ ] Sub-task: Set up automated unit test workflows (pytest, vitest)
  - [ ] Sub-task: Set up linting, type-checking, and formatting checks
  - [ ] Sub-task: Configure PR templates enforcing issue linking and git hygiene
- [ ] Task: Conductor - User Manual Verification 'Phase 0: CI/CD & Project Hygiene Setup' (Protocol in workflow.md)

## Phase 1: Foundation & Data Model (Week 1)
- [ ] Task: Set up basic entity types and normalization (V4-P0-006)
  - [ ] Sub-task: Create tracking issue and branch for EntityType work
  - [ ] Sub-task: Implement EntityType enum in Pydantic + TS
  - [ ] Sub-task: Implement DB constraints/indexes
  - [ ] Sub-task: Add migration script for existing legacy data
  - [ ] Sub-task: Open PR, ensure CI passes, and resolve issue
- [ ] Task: Project/Workspace switcher & Recents (V4-FE-002)
  - [ ] Sub-task: Create tracking issue and branch for Workspace switcher
  - [ ] Sub-task: Implement backend scope APIs (if not present)
  - [ ] Sub-task: Build React UI switcher with UI tests
  - [ ] Sub-task: Open PR, ensure CI passes, and resolve issue
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Foundation & Data Model' (Protocol in workflow.md)

## Phase 2: Lease Extraction Agent & Rules Engine (Weeks 2-3)
- [ ] Task: Lease term extraction workflow
  - [ ] Sub-task: Create tracking issue and branch for Extraction Workflow
  - [ ] Sub-task: Build document ingestion parser hook (Basic PDF)
  - [ ] Sub-task: Create LangGraph extraction agent for CRE schemas
  - [ ] Sub-task: Open PR, ensure CI passes, and resolve issue
- [ ] Task: Cashflow rules engine
  - [ ] Sub-task: Create tracking issue and branch for Cashflow rules
  - [ ] Sub-task: Implement deterministic cashflow calculator based on schemas
  - [ ] Sub-task: Open PR, ensure CI passes, and resolve issue
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Lease Extraction Agent & Rules Engine' (Protocol in workflow.md)

## Phase 3: Schema-Driven UI & Evidence Review (Weeks 4-6)
- [ ] Task: Provenance citations framework (SP3)
  - [ ] Sub-task: Create tracking issue and branch for citations framework
  - [ ] Sub-task: Backend support for storing `evidence_span` in Run Events/Artifacts
  - [ ] Sub-task: Open PR, ensure CI passes, and resolve issue
- [ ] Task: Schema-Driven Review UI
  - [ ] Sub-task: Create tracking issue and branch for Review UI
  - [ ] Sub-task: Build generic React components for structured validation
  - [ ] Sub-task: Integrate evidence viewer next to extracted fields
  - [ ] Sub-task: Open PR, ensure CI passes, and resolve issue
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Schema-Driven UI & Evidence Review' (Protocol in workflow.md)

## Phase 4: Deterministic Excel Export (Week 7)
- [ ] Task: Export Engine Foundation (V4-EX-001 & V4-EX-002)
  - [ ] Sub-task: Create tracking issue and branch for Export Engine
  - [ ] Sub-task: Setup Golden File testing harness for Excel outputs
  - [ ] Sub-task: Implement `xlsx` mapping layer
  - [ ] Sub-task: Open PR, ensure CI passes, and resolve issue
- [ ] Task: LeaseCD Lender Pack Template (V4-EX-003)
  - [ ] Sub-task: Create tracking issue and branch for Pack Template
  - [ ] Sub-task: Implement template based on CRE standards
  - [ ] Sub-task: Open PR, ensure CI passes, and resolve issue
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Deterministic Excel Export' (Protocol in workflow.md)

## Phase 5: Onboarding & MVP Finalization (Week 8)
- [ ] Task: First-run checklist & Sample Project (V4-ONB-001 & V4-ONB-003)
  - [ ] Sub-task: Create tracking issue and branch for First-run experience
  - [ ] Sub-task: Implement UI checklist state tracking
  - [ ] Sub-task: Create the sample lease package data bundle
  - [ ] Sub-task: Open PR, ensure CI passes, and resolve issue
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Onboarding & MVP Finalization' (Protocol in workflow.md)