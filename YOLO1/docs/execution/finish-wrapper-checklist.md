# Finish Wrapper Checklist

Finish wrappers exist to close the gap between "implemented" and "sellable." They are not optional cleanup tickets and they are not where a team hides indecision. They are where a wave proves it can turn working surfaces into buyer-grade product. I^1 I^2

## North-Star Intent

Every major wave gets a dedicated wrap issue because the last ten percent of product credibility is rarely captured by the build packets themselves. The finish wrapper is where the team makes the result feel complete, coherent, and trustworthy.

## Current-State Anchor

The repo already has the beginnings of the right execution logic:

- [docs/execution/demo-control-framework.md](../../../docs/execution/demo-control-framework.md) already enforces packet structure and explicitly calls for wrap work. I^1
- The shell and notebook research surfaces are real, while other modules are still placeholders. That means wrap work is necessary to keep the product coherent even while the build is uneven. I^3
- The north-star plan explicitly says deterministic packet acceptance is necessary for control but insufficient for completion. I^2

The wider normalization logic lives in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md) and [intelli-studio-north-star-plan.md](./intelli-studio-north-star-plan.md). This document stays local to the wrapper doctrine the issue corpus does not provide for itself. I^4

## Product Rules

Each `WRAP` issue must explicitly cover:

- UX coherence
- copy cleanup
- visual polish
- empty, loading, and error states
- context propagation
- evidence and provenance visibility
- "does this feel sellable?"

The wrapper is allowed to do small integration, cleanup, and presentational work across the wave's surfaces. It is not allowed to mutate scope into a new platform program.

## CAP / PKT / WRAP Rule

- `CAP` defines the wave and its buyer-facing goal.
- `PKT` issues deliver the scoped capability increments.
- `WRAP` closes the gap between implemented and sellable.

If the live issue corpus does not already express this structure, the next agent should overlay it explicitly rather than assuming capability issues will self-finish.

## Wrapper Rules

Treat the wrapper as the wave's final product review loop:

- pull the visible surfaces back into one coherent product language
- close shallow seams left by packetized implementation
- improve trust cues, context legibility, and provenance visibility
- reject surfaces that are functional but still obviously unfinished

## Escalations Required

- The live GitHub issues do not yet consistently express the `CAP / PKT / WRAP` finish pattern, so the next agent should add that structure explicitly rather than assuming it is already implied.
- Any capability area that spans multiple adjacent issues should get a dedicated wrap issue even if the underlying issue corpus was not written that way.
- Dashboard, universal console, and workflow studio are the most likely surfaces to look complete on paper before they feel sellable in practice, so they should be treated as high-risk wrap candidates.

## Wave Exit Questions

Before closing a wave, the builder must be able to answer yes to all of these:

- Does this feel coherent?
- Does it look intentional?
- Is context obvious?
- Is provenance visible?
- Would a buyer mistake this for unfinished internal tooling?

If the honest answer to any of these is "not quite," the wave should stay open.

## Checklist

### Visual Coherence

- Typography, spacing, iconography, and rhythm match the rest of the shell.
- Dark and light themes both look designed.
- Empty states feel premium and on-purpose.

### Copy

- Labels sound like product language.
- Temporary or internal phrasing has been removed.
- The surface explains itself without sounding apologetic.

### State Handling

- Loading states preserve confidence and layout.
- Error states preserve trust and offer a clear next step.
- Empty states frame the future path rather than exposing absence.

### Context Propagation

- Headers and breadcrumbs expose the right business and working context.
- Session, bundle, project, and task context are visible where they influence behavior.
- Save or publish actions make the destination object legible.

### Provenance

- Citations, passages, domains, bundles, runs, and diffs are inspectable where relevant.
- Evidence visibility gets better, not worse, as surfaces become more polished.

### Sellability

- The page would not embarrass the team in front of a serious buyer.
- The product feels more trustworthy after the wave than before it.

## Judgment Required

Do not use the wrapper to rubber-stamp a wave. Use it to force the uncomfortable question: did we actually make this feel like product? If the answer is only "the acceptance criteria passed," the wrapper has not done its job. I^1 I^2

## Builder Accountability

The agent closing a wrap issue is personally responsible for:

- reviewing the wave as a buyer would experience it, not as the packet author remembers it
- finding awkward seams between packets and closing them
- fixing thin or careless copy that drains trust
- making provenance easier to inspect on the finished surface
- refusing to call the wave done while it still feels obviously unfinished

Fake completion includes:

- closing the wrap because no functional bugs remain
- ignoring visual mismatches because the feature technically works
- leaving context propagation inconsistent across adjacent surfaces
- accepting provenance regressions in the name of polish

## Issue Hooks

- `I^1` - [docs/execution/demo-control-framework.md](../../../docs/execution/demo-control-framework.md) already treats wrap work as a required part of disciplined execution.
- `I^2` - [studio-north-star.md](./studio-north-star.md) defines the core principle that the product is not done when it merely works.
- `I^3` - `ui/src/layouts/AppShell.tsx`, `ui/src/pages/OverviewPage.tsx`, `ui/src/pages/ResearchPage.tsx`, and `ui/src/pages/ModulePlaceholder.tsx` show the current mix of mature and immature surfaces that wrapper work has to reconcile.
- `I^4` - Live GitHub issues `#109`, `#111`, `#135`-`#139`, `#79`-`#82`, and `#156` are strong capability issues, but they still need wrap work to become one believable product.
