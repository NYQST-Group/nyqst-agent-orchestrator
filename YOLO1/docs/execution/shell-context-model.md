# Shell Context Model

The shell is not a decorative frame around features. It is the product's orientation system. If users can get lost, lose context, or stop trusting what object the system is acting on, the shell is failing even when every route still technically works. I^1 I^2

## North-Star Intent

Intelli Studio should feel like a stable operating system for buyer work. The shell should communicate:

- where the user is
- what business context they are in
- what session or bundle is active
- what the current task is
- what the agent or workflow is allowed to act on

The shell should make the rest of the product feel controlled before the user runs anything.

## Current-State Anchor

The repo already has a real shell and real context primitives:

- `ui/src/layouts/AppShell.tsx` defines the current left-rail shell and buyer-facing route surface. I^1
- `ui/src/App.tsx` shows the current module map and confirms that the current Intelli app is already the buyer-facing shell. I^1
- Theme switching is real; settings are present as a stub; mobile has a separate top bar treatment. I^1
- Sessions already exist as persisted objects with module, scope, objective, mounts, and workspace state. I^3
- Projects and clients are currently placeholders, which is useful because the next agent can introduce them as thin native wrappers rather than inherited complexity. I^4
- Notebooks already behave like early bundle surfaces, and research already binds itself to session and pointer context. I^5

The wider sequencing and normalization logic lives in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md) and [intelli-studio-north-star-plan.md](./intelli-studio-north-star-plan.md). This document stays local to context propagation, breadcrumb rules, and shell orientation.

## Context Chain

Use two related but distinct ideas:

### Business Hierarchy

This is the native operating context:

`Workspace -> Initiative -> Project -> Task`

These are the business wrappers that make the product feel like a client system rather than a raw AI workbench.

### Working Context

This is what changes as the user moves through the product:

`Module -> Session -> Bundle -> ResearchPack -> Workflow`

These are the active execution surfaces that bind a piece of work to a specific screen, live conversation, or evidence object.

### Context Presentation Rule

The shell should present both layers together, but not flatten them into one awkward line.

Use a two-line treatment:

- business line:
  `Workspace / Initiative / Project / Task`
- working line:
  `Module / Session / Bundle / ResearchPack / Workflow`

Rules:

- show only active working objects
- preserve the order from broader working context to current object
- do not place `Module` inside the business hierarchy
- missing context should be a deliberate omission, not an accident

## Product Rules

- `Workspace` is the top-level shell and tenant-facing operating environment.
- `Initiative` is a thin planning and selling wrapper that groups related projects or demo tracks. It should stay lightweight in the demonstrator phase.
- `Project` is the main client or internal work container visible to the buyer.
- `Task` is the unit of purposeful work inside a project. It should be visible in headers, console context, and dashboards when relevant.
- `Module` is the current product surface, such as Dashboard, Agent Console, Research, Bundles, or Workflow Studio.
- `Session` is the live execution and continuity object for agent work.
- `Bundle` is the live evidence container and versioned working set.
- `ResearchPack` is the saved research object that may be active alongside session or bundle context.
- `Workflow` is the active workflow context when the user is in Workflow Studio or viewing a workflow run.
- The shell must always show enough current context that the user can answer, without guesswork, "What am I looking at?" and "What will the system act on if I press go?"
- Context must propagate into the business line, working line, right rails, console chips, workflow inspector state, and save actions.
- Placeholder modules must still inherit shell context and look natively attached to the rest of the product.

## Page Rules

### Global Shell

- Left navigation is stable and product-like.
- The top region carries the two-line context treatment, not only a page title.
- Settings, theme, and model surfaces should look intentional even before full capability exists.

### Dashboard

- The dashboard should clearly state what workspace, initiative, and project the activity belongs to.

### Agent Console

- The console header must show project, task, session, and active Bundle or ResearchPack context.

### Bundles

- Bundle detail should show where the bundle belongs and which project or task it is serving.

### Workflow Studio

- The studio should expose the workflow's project/task ownership and which bundle or pack inputs are mounted.

## Escalations Required

- `#135` and `#136` are correctly shaped, but their current `M5-STUDIO` placement is later than the north-star shell-context model really wants.
- A general dashboard context surface exists only implicitly across shell, runs, activity feed, and domain dashboards. If D2 stays in scope, that should be elevated into a first-class cross-product issue rather than left distributed.
- The shell should absorb project and workspace switching, authenticated tenant context, recents, and live run inspection earlier than the wider studio wave if the product is meant to feel stable from the start.

## Judgment Required

Do not treat context treatment as cosmetic. Orientation is part of trust. If the user can technically navigate but still has to infer what context is active, the shell is not done. If a Session, Bundle, ResearchPack, or Workflow can change system behavior without being visible, the shell is not done. I^2 I^3

## Builder Accountability

The D1 builder is personally responsible for making sure:

- users can never lose track of business context
- active execution context is visible before an action is taken
- shell placeholders do not punch holes in credibility
- headers and breadcrumbs reduce cognitive load instead of adding it
- mobile layouts keep context legible rather than hiding it

Fake completion includes:

- shipping a polished left rail without a real context banner
- showing module titles without exposing project or task state
- treating sessions as a back-end concern instead of a visible working context
- making bundle context discoverable only after extra clicks

## Issue Hooks

- `I^1` - `ui/src/layouts/AppShell.tsx` and `ui/src/App.tsx` are the live shell baseline and prove the product already has a single buyer-facing shell.
- `I^2` - [studio-north-star.md](./studio-north-star.md) defines the shell as a major trust and orientation surface in the overall product story.
- `I^3` - [ADR-006](../../../docs/adr/006-session-workspace-architecture.md), `src/intelli/db/models/conversations.py`, and `src/intelli/schemas/sessions.py` establish sessions as real persisted context objects with mounts and workspace state.
- `I^4` - `ui/src/pages/ProjectsPage.tsx` and `ui/src/pages/ClientsPage.tsx` show the current thin-wrapper opportunity for native business objects.
- `I^5` - `ui/src/pages/ResearchPage.tsx`, `ui/src/pages/NotebookPage.tsx`, and `ui/src/hooks/use-session-lifecycle.ts` show that bundle and session context is already partially present and should be elevated into the shell.
- `I^6` - Live GitHub issues `#109`, `#110`, `#111`, `#123`, `#125`, `#135`, and `#136` together define the practical shell and context surface the north-star shell needs to unify: authenticated tenant shell, project/workspace switcher with recents, live runs detail, guided first-run path, sample project seeding, and real Project/Client ownership.
