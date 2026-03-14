# Decision Surface Spec

Decisions are not a side note. They are the point where analysis becomes a buyer-facing judgment. If the pack says Intelli Studio supports decisions, the product needs a real decision surface rather than a lingering placeholder route. I^1 I^2

## North-Star Intent

The Decisions surface should feel like a thin but serious business wrapper:

- project-scoped judgments are visible and searchable
- rationale is legible
- citations are inspectable
- linked artifacts and evidence open directly
- stale or degraded decisions are visible when source evidence changes

This is not an internal moderation log. It is a buyer-facing decision record.

## Current-State Anchor

The repo and staged issues already point in the same direction:

- `ui/src/pages/DecisionsPage.tsx` is a placeholder route with the right product hints: confidence, recommendations, evidence spans, approvals, and degradation hooks. I^1
- `staging_issues/STUDIO-003.md` already defines a concrete decisions register with CRUD, citations, and linked artifacts. I^2
- The current shell already exposes Decisions as part of the visible product map, which means the route cannot stay concept-only if the pack is meant to be canonical. I^3

## Product Rules

- `Decision` is a project-scoped judgment object.
- A `Decision` carries:
  - title
  - decision
  - rationale
  - status
  - citations
  - linked artifacts
  - stale flag
- Decisions are buyer-facing business wrappers, not internal moderation logs.
- Decisions must be inspectable from both project context and their own detail surface.

## D2 Thin Surface Rules

`D2` owns the first real Decisions surface:

- list, detail, create, and edit decisions linked to Projects
- show recent decisions on dashboard and project detail
- let a buyer see what was decided, by whom, and in what project context

This first pass should make the route real without pretending the full evidence-linked compliance layer is already complete.

## D4 Evidence Enrichment Rules

`D4` enriches Decisions with evidence seriousness:

- citations become first-class
- linked evidence and artifacts open directly
- decision detail shows why the decision exists, not just that it exists
- decision surfaces should stay connected to Bundle, artifact, and research provenance

## Stale And Degradation Rules

- Decisions become stale or degraded when source Bundles or cited evidence change in a way that can invalidate the judgment.
- D4 owns the first explicit stale/degradation behavior.
- Stale state must be visible in the decision detail and project context rather than hidden in background logic.

## Judgment Required

Do not count the Decisions route as solved because a list/detail page exists. If it does not feel like judgment backed by evidence, it is still just another placeholder with CRUD. The value is not that decisions can be stored. The value is that decisions can be trusted. I^1 I^2

## Builder Accountability

The builder responsible for the Decisions surface must verify personally:

- that the route stops feeling abandoned and starts feeling on-path
- that decisions are clearly project-scoped business objects
- that decision rationale and linked evidence are legible
- that stale/degradation behavior is part of the model, not an afterthought
- that the surface increases buyer trust rather than looking like an admin table

Fake completion includes:

- replacing the placeholder with a generic table and form
- storing decisions with no evidence or artifact linkage
- treating citations as optional garnish
- leaving degradation behavior implied but nowhere visible

## Issue Hooks

- `I^1` - `ui/src/pages/DecisionsPage.tsx` already signals the intended product language: confidence, evidence, approvals, and degradation hooks.
- `I^2` - `staging_issues/STUDIO-003.md` already defines a concrete Decisions register with CRUD, citations, linked artifacts, and a project-scoped data model.
- `I^3` - `ui/src/App.tsx` and the existing shell route map make Decisions a visible part of the buyer-facing product, which means the pack must give that route an explicit destination.
