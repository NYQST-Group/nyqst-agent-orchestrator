# EPIC-W1 — Wave 1 — GenUI + report rendering + planning UX (PlanViewer + ReportPanel)

- Type: **epic**
- Milestone: `M2-W1`
- Repo alignment: **missing**
- Labels: `milestone:M2`, `wave:1`

## Problem

Spec requires a structured UI generation contract (GenUI descriptors) and a GML-based ReportPanel that can be incrementally streamed, healed, and cited.

## Proposed solution

Implement GenUI descriptor validators + component library, then a robust GML renderer with healer, plus UI surfaces to inspect plan state and report draft during the run.

## Acceptance criteria

- GenUI descriptors validated at runtime; renderer can mount at least: text, table, callout, chart, citations.
- ReportPanel can render partial GML, re-render on deltas, and surface validation/healing outcomes to the user.
- PlanViewer shows PlanSet with live task status updates.

## Test plan

- Unit: GenUI schema validators; GML parser + renderer; healer behaviour on malformed tags.
- E2E: report preview updates while run progresses; plan tasks tick through states.
