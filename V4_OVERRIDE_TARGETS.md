# V4 Override Targets Mapping

Based on `DECISION_REGISTER_V4.md` and legacy issue analysis, the following legacy V1/V2/V2M markdown files require explicit V4 override injections during the sanitization phase:

## 1. Charting Library (DEC-V4-048 / GAP-001)
- **Override:** Must use `Plotly.js`, not `Recharts`.
- **Target Files:**
  - `packs/V2/issues/BL-004.md` (and `BL-004a`, `BL-004b`)
  - `packs/V2/issues/BL-005.md`
  - `packs/V2/issues/BL-009.md`
  - `packs/V2/issues/BL-019.md`

## 2. Scheduling & Workers (DEC-V4-008)
- **Override:** Must use `arq` + `cron`, not `Temporal`.
- **Target Files:**
  - `packs/V2/issues/EPIC-P0.md`
  - `packs/V2M/issues/STORY-PROD-004.md` (if exists)

## 3. Streaming & Events (DEC-V4-001, DEC-V4-003)
- **Override:** Plan storage is event-sourced (`RunEvents`); SSE must be tenant-aware.
- **Target Files:**
  - `packs/V2/issues/BL-007.md` (PlanViewer)
  - `packs/V2/issues/P0-002.md`
  - `packs/V2/issues/OBS-002.md`

## 4. Unnecessary Integrations / Scope Cuts (DEC-V4-010)
- **Override:** Scope cut (~30%); defer visual workflow editors, Ory Kratos, PostHog, etc.
- **Target Files:**
  - `packs/V2/issues/STUDIO-001.md` through `STUDIO-005.md`

*(This list will be used by the Python sanitization script in Phase 2 to automatically inject the `> V4 OVERRIDE:` headers.)*