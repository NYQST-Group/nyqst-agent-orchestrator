# Demo Quality Bar

Visible surfaces in Intelli Studio are not done when they merely function. They are done when they create trust, carry context cleanly, survive empty and error states with dignity, and look like parts of the same product. Buyer-grade is a finish standard, not a garnish. I^1 I^2

## North-Star Intent

The quality bar exists to prevent a familiar failure mode: the system technically works, but every screen still feels like engineering scaffolding. Intelli Studio only works as a demo if the visible product looks intentional enough that a buyer can project real usage onto it.

## Current-State Anchor

The repo already makes the distinction between control and finish:

- The execution control framework is explicit about issue packets, acceptance checks, and wrap work. I^1
- The current shell, overview, notebook, and research surfaces are functional, but several modules still present as placeholders or early product surfaces. I^3
- The login page is usable, but it is still a good example of the difference between working and sellable. I^4
- Sources, citations, session lifecycle, and run timeline already exist, which means the raw materials for trust are present even when the product finish is not. I^5

The detailed issue normalization lives in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md) and [intelli-studio-north-star-plan.md](./intelli-studio-north-star-plan.md). This document is narrower: it defines the visible finish bar that the issue corpus does not define for itself. I^6

## Product Rules

- Every visible screen must clearly belong to Intelli Studio. Typography, spacing, color, iconography, and layout rhythm must feel related.
- Empty states must feel deliberate, informative, and calm. They must not look like a missing implementation.
- Loading states must preserve layout confidence and avoid making the product feel unstable.
- Error states must preserve trust: clear language, clear recovery, no stack-smell, no panic tone.
- Context must be legible without extra clicking. Users should know what workspace, project, task, session, bundle, or research object they are looking at.
- Provenance must be visible anywhere the system is making claims, summarizing, comparing, or automating.
- Dark mode and light mode must both feel designed, not merely tolerated.
- Mobile and narrow layouts must still feel like product surfaces, not collapsed desktop leftovers.

## Buyer-Grade Pass Conditions

### Sign-In

- The page feels premium before the user enters credentials.
- Demo and API-key affordances do not cheapen the surface.
- Copy sounds like product language, not internal tooling language.

### Shell

- Navigation feels stable and high-confidence.
- Breadcrumb and current context explain where the user is.
- Settings, model, and theme controls look intentional even when partially implemented.

### Dashboard

- The page looks like a control center, not a card dump or table farm.
- Live activity has hierarchy and tells the user what matters now.
- Empty states make the future obvious without feeling broken.

### Universal Agent Console

- The console feels central, not secondary.
- Citations, domains, timeline, and context are inspectable at a glance.
- Composer, presets, and model controls feel like operator tools, not demo toggles.

### Research

- Document and web evidence feel like one working context.
- The right rail makes provenance easier to inspect, not harder.
- Saved outputs feel like first-class system objects.

### Bundles And Versioning

- History, diffs, and related outputs are easy to understand.
- File preview and evidence relationships feel authoritative.
- Imports do not feel like detached uploads.

### Workflow Studio

- The screen can be read visually before it is interacted with.
- The center canvas is dominant, the inspector is disciplined, and the run log feels grounded.
- Deterministic and agentic work are visibly different.

## Dev-Grade Failure Modes

Reject a surface as incomplete if any of these are true:

- It works, but could easily be mistaken for an internal tool.
- Context is technically available, but not obvious.
- Empty or loading states collapse the layout or expose rough edges.
- The user has to infer provenance rather than inspect it.
- The page uses generic placeholder copy that drains trust.
- A premium target surface still looks like a component demo.
- The right rail exists, but does not carry real decision-making value.
- Dark mode looks like a color inversion rather than a designed theme.

## Judgment Required

Do not use this bar as a checklist to game. Use it as a refusal mechanism against thin work. If a builder would be slightly embarrassed to put the screen in front of a buyer, the builder should assume the work is not done yet. I^1 I^2

The finish wrapper exists because teams routinely stop at the first passing build. This product cannot afford that habit on any visible surface.

## Builder Accountability

The builder closing a visible packet must verify personally:

- that the screen communicates its purpose in under a few seconds
- that the screen still holds together with no data, partial data, and bad data
- that provenance and context are inspectable where claims are made
- that the copy sounds like a product someone is trying to sell
- that the visual result improves the product's overall credibility

Fake completion includes:

- shipping a placeholder page because the route now exists
- leaving a right rail or timeline technically wired but visually low-value
- accepting empty states that confess unfinishedness rather than framing the next step
- shipping a demo screen that only looks good in one theme or one viewport

## Issue Hooks

- `I^1` - [docs/execution/demo-control-framework.md](../../../docs/execution/demo-control-framework.md) makes wrap work mandatory because packet completion alone does not guarantee convincing product finish.
- `I^2` - [studio-north-star.md](./studio-north-star.md) defines the emotional and buyer-facing bar this quality standard is meant to protect.
- `I^3` - `ui/src/layouts/AppShell.tsx`, `ui/src/pages/OverviewPage.tsx`, `ui/src/pages/ModulePlaceholder.tsx`, and `ui/src/pages/ResearchPage.tsx` show the current mix of real and placeholder surfaces that need a shared finish standard.
- `I^4` - `ui/src/components/auth/LoginPage.tsx` is direct evidence of a functional surface that still needs buyer-grade treatment.
- `I^5` - `ui/src/components/chat/SourcesSidebar.tsx`, `ui/src/components/chat/ChatPanel.tsx`, `ui/src/hooks/use-session-lifecycle.ts`, and `src/intelli/api/v1/agent.py` show that trust primitives already exist and should be surfaced better rather than reinvented.
- `I^6` - [finish-wrapper-checklist.md](./finish-wrapper-checklist.md) and live GitHub issues `#109`, `#111`, `#112`, `#92`, `#79`, `#81`, and `#156` show that the issue corpus is rich on visible surfaces but does not, by itself, define a shared finish standard.
