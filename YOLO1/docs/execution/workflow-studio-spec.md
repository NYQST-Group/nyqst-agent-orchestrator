# Workflow Studio Spec

Workflow Studio is the most ambitious visible surface in Intelli Studio, which means it is also the easiest place to ship something technically impressive but visually unconvincing. The standard here is not "it runs." The standard is "complex work looks controlled." I^1 I^2

## North-Star Intent

The studio should feel modern, compositional, and disciplined.

- left palette
- center canvas
- right inspector
- bottom run log and timeline

The center canvas is the hero. The inspector gives precision. The run log gives confidence. The whole surface should feel aligned to the Intelli shell and close to a Google Opal-like sense of deliberate composition, not node-editor chaos.

## Current-State Anchor

The repo is honest about where it stands:

- `ui/src/pages/AnalysisPage.tsx` is still a placeholder, which is useful because the next agent can define the studio cleanly instead of inheriting a muddled partial implementation. I^1
- The current dev workbench already has explorer, details, main panel, and timeline ideas that can inform interaction patterns without being mistaken for the buyer-facing studio. I^3
- Workflow backlog work already exists in `STORY-WF-001` through `STORY-WF-004`. I^2
- The runtime split is already grounded in ADRs, so the studio does not need to invent its own execution model. I^4

The wider issue normalization lives in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md) and [intelli-studio-north-star-plan.md](./intelli-studio-north-star-plan.md). This document stays local to the unified studio surface rather than re-listing every neighboring issue family. The concrete execution contract it depends on is locked in [workflow-runtime-contract.md](./workflow-runtime-contract.md). I^5

## Product Rules

- The layout is fixed:
  - left palette
  - center canvas
  - right inspector
  - bottom run log or timeline
- Workflow nodes are deterministic by default.
- `Agent Step` nodes are explicit and visually distinct from deterministic nodes.
- The studio should make it obvious which parts of a workflow are controlled process and which parts call into reasoning-heavy agent behavior.
- Outputs must land back into visible system objects such as bundles, artifacts, research packs, and project activity.
- The run log must preserve confidence by showing execution progress, failures, retries, and outputs in a readable way.
- The studio must feel like part of Intelli Studio, not a foreign embedded tool.

## Node Taxonomy

At minimum, the surface should support a readable taxonomy such as:

- Input nodes
- Deterministic transform nodes
- Validation nodes
- Publish or save nodes
- Trigger or event nodes
- `Agent Step` nodes

The taxonomy should help the buyer read intent from the canvas before they inspect implementation details.

## Inspector Rules

- The inspector is where configuration becomes disciplined rather than cluttered.
- It should show node purpose, inputs, outputs, validation settings, and mounted context.
- For `Agent Step` nodes, it must show what context, model policy, and save behavior are in play.
- It should not become a dumping ground for every possible field.

## Execution Rules

- Deterministic workflows run under the deterministic runtime.
- `Agent Step` nodes explicitly delegate into LangGraph and return structured outputs to the workflow runtime.
- Retries, resume behavior, validation, and node-level progress must be part of the execution semantics.
- Workflow runs should generate visible activity that ties back to projects, bundles, artifacts, and research packs.

## Escalations Required

- The live issue set currently distributes the studio across apps, canvas, workflows, and later product-module issues. That likely needs one normalized product parent before the UI work scales further.
- `#139` should be reconciled with the runtime split because it explicitly describes workflow execution as compiling the DAG to LangGraph and storing artifacts under the same run ledger.
- If the studio is meant to be a premium middle-view surface rather than a generic node editor, its finish bar should become explicit issue language early, not only wrapper language later.

## Visual Rules

- The center canvas must dominate the page and feel calm under complexity.
- The palette should feel curated, not overstuffed.
- The inspector should feel disciplined, not chatty.
- The run log should feel grounded and trustworthy, not like a debug console.
- Empty and loading states must still make the page feel intentional.

## Judgment Required

Do not ship a workflow builder that is merely a runnable node canvas. Runnable-but-chaotic is failure. If the studio looks like internal plumbing, if agentic and deterministic work are visually blurred, or if the inspector feels like raw form sprawl, the page is not done. I^2 I^4

## Builder Accountability

The D6 builder is personally responsible for making sure:

- the studio can be understood visually before it is used
- the deterministic versus agentic split is visible, not just documented elsewhere
- the page remains part of the Intelli product language
- run outputs land back in visible system objects
- logs and status surfaces increase confidence instead of broadcasting implementation noise

Fake completion includes:

- shipping a generic graph editor with Intelli colors applied
- hiding agent delegation inside generic workflow nodes
- letting the inspector bloat until the canvas loses clarity
- treating the bottom run log like an engineer-only panel rather than a buyer-facing trust surface

## Issue Hooks

- `I^1` - `ui/src/pages/AnalysisPage.tsx` shows the studio is still an open surface and should be shaped deliberately.
- `I^2` - `STORY-WF-001` through `STORY-WF-004` in `staging_issues/issues.json` are the direct backlog basis for workflow definitions, execution, triggers, and builder UI.
- `I^3` - `ui/src/components/workbench/Workbench.tsx`, `ExplorerPanel.tsx`, `DetailsPanel.tsx`, `MainPanel.tsx`, and `TimelinePanel.tsx` show existing interaction primitives that can inform the studio without becoming the studio.
- `I^4` - [runtime-split.md](./runtime-split.md), [workflow-runtime-contract.md](./workflow-runtime-contract.md), [ADR-005](../../../docs/adr/005-agent-runtime-framework.md), and [ADR-008](../../../docs/adr/008-mcp-tool-architecture.md) define the runtime boundaries the studio must make legible.
- `I^5` - Live GitHub issues `#137`, `#138`, `#139`, `#157`, `#158`, `#159`, `#80`, and `#81` show that the studio concept is currently distributed across canvas, apps, workflows, and analysis surfaces that need product-level unification.
