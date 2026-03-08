# STUDIO-002 — Clients/CRM: backend model + API + UI list/detail (replace placeholder ClientsPage)

- Type: **story**
- Milestone: `M5-STUDIO`
- Repo alignment: **missing**
- Labels: `backend`, `frontend`, `crm`
- Depends on: `STUDIO-001`

## Problem

CRM is required for commercial property workflows, but Clients page is placeholder and no client entity model exists.

## Proposed solution

Implement Clients/CRM MVP:
- DB: `clients` table (tenant_id, name, type, sector, notes, identifiers), optional `contacts`.
- API: CRUD endpoints `/api/v1/clients` (+ `/contacts` optional).
- UI: ClientsPage list; ClientDetail with related projects, documents, decisions.

## Repo touchpoints

- `ui/src/pages/ClientsPage.tsx`
- `src/intelli/db/models/* (new clients model)`

## Acceptance criteria

- User can create clients and attach projects to a client.
- Client detail shows related projects and recent runs.

## Test plan

- Integration: client CRUD with tenant scoping.
