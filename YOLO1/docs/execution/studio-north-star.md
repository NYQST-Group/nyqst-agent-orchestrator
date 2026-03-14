# Intelli Studio North-Star Narrative

Intelli Studio should feel like a buyer-facing intelligence workspace that costs real money: calm, legible, premium, controlled, and trustworthy. This is not a “wire everything together and declare victory” spec. It is a “ship until the product feels like the thing we are trying to sell” spec. I^1 I^2

## North-Star Intent

The buyer journey should read like one composed product:

- sign in to a polished product entrance, not a dev utility
- land in a shell that immediately explains where they are and what work is in scope
- open a dashboard that feels like an operator’s morning control surface
- move into the Universal Agent Console and see that project, task, session, Bundle, and ResearchPack context are already mounted
- run research across uploaded evidence and the web without losing provenance
- inspect Bundle history, version diffs, and related outputs without feeling dropped into storage plumbing
- open Workflow Studio and see that complex work is controlled, inspectable, and visibly separated into deterministic and agentic lanes

The buyer should leave with the sense that Intelli Studio already has a point of view about trust, context, provenance, and controlled automation. If the flow works but still feels thin, awkward, or developer-basic, it is not done. I^1

## Current-State Anchor

The repo already has enough backbone that this is a product-composition problem, not a greenfield problem:

- the current buyer-facing shell already exists in `ui/src/layouts/AppShell.tsx` and `ui/src/App.tsx` I^3
- the login surface exists, but it still reads as functional rather than premium in `ui/src/components/auth/LoginPage.tsx` I^4
- sessions already exist as real persisted context objects across the API, schemas, and models I^5
- pointer, manifest, artifact, and notebook flows already provide real Bundle-like substrate behavior I^6
- the current research assistant already streams chat, citations, and run timeline, but it is still scoped like a page feature rather than the Universal Agent Console I^7
- Projects and Clients remain intentionally thin placeholder surfaces, which is useful because the business wrappers can still be shaped cleanly I^8

The broader issue normalization lives in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md) and [intelli-studio-north-star-plan.md](./intelli-studio-north-star-plan.md). This document stays focused on the finished experience rather than re-listing the corpus.

## Product Rules

- The current Intelli app remains the only buyer-facing shell. Do not fork a second product shell. I^3
- The shell must always expose enough context that a user knows where they are, what work they are in, and what object the system will act on.
- The dashboard must show live and recent operational truth, not filler cards.
- The Universal Agent Console must feel like the center of gravity, not a sidecar.
- Document retrieval and web research must live in the same working context.
- Saved outputs must become real system objects such as Bundles, ResearchPacks, artifacts, and project activity.
- Provenance must stay inspectable everywhere: citations, domains, runs, Bundle history, diffs, and source relationships.
- Incomplete modules must look deliberate and on-path, not broken, abandoned, or casually stubbed.

## Judgment Required

Do not read this document as permission to stop when the acceptance boxes pass. The work is done when the product feels composed, inspectable, and intentional. A surface that technically functions but still looks generic, context-light, or visually unconvincing is incomplete. I^1 I^2

If a builder cannot explain why a buyer would trust the surface more after the packet than before it, the packet is not done.

## Builder Accountability

The builder responsible for a north-star stage must verify personally:

- that the surface helps the buyer understand what Intelli Studio is for
- that context is visible without requiring memory or inference
- that provenance is inspectable rather than implied
- that the product looks more premium after the change, not merely more functional
- that placeholder states still protect trust

Fake completion includes:

- a route that works but still looks like scaffolding
- a control surface that is technically live but visually noisy or table-heavy
- a chat feature that can answer questions but does not make its context or sources legible
- a workflow screen that is runnable but still feels like internal tooling

## Issue Hooks

- `I^1` - [docs/execution/demo-control-framework.md](../../../docs/execution/demo-control-framework.md) already distinguishes packet control from broader delivery quality.
- `I^2` - [GAP-045](../../../staging_issues/GAP-045__gap-045-memory-md-pending-work-section-notes-slice-structure-plan-plan-mode-10-c.md) is direct evidence that execution artifacts must carry context and next-step clarity for agents.
- `I^3` - `ui/src/layouts/AppShell.tsx` and `ui/src/App.tsx` show that the current buyer-facing shell already exists and should be evolved, not replaced.
- `I^4` - `ui/src/components/auth/LoginPage.tsx` shows a functional but visibly dev-grade sign-in surface.
- `I^5` - [ADR-006](../../../docs/adr/006-session-workspace-architecture.md), `src/intelli/db/models/conversations.py`, and `src/intelli/schemas/sessions.py` establish that session context is already a real substrate concept.
- `I^6` - `ui/src/pages/NotebookPage.tsx`, `src/intelli/services/substrate/manifest_service.py`, `src/intelli/services/substrate/pointer_service.py`, and live issue `#145` together show that Bundle-like versioning primitives already exist but are not yet presented as a premium buyer surface.
- `I^7` - `ui/src/pages/ResearchPage.tsx`, `ui/src/components/chat/ChatPanel.tsx`, `src/intelli/api/v1/agent.py`, and live issues `#6`, `#8`, `#22`, and `#27` show the current assistant baseline and the richer research direction behind it.
- `I^8` - `ui/src/pages/ProjectsPage.tsx`, `ui/src/pages/ClientsPage.tsx`, and live issues `#135` and `#136` show that these business wrappers are intentionally thin today but already defined as real end-to-end entities in the issue corpus.
