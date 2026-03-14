# Universal Agent Console Spec

The agent console is the center of Intelli Studio. If it feels like a page-specific chat widget, the product is underselling itself. It should feel like the place where context, research, provenance, skill presets, and controlled execution come together. I^1 I^2

## North-Star Intent

The finished console should feel powerful, inspectable, and central.

- It understands project, task, session, bundle, and research-pack context.
- It can read uploaded evidence and use tools.
- It can run web research in the same working lane.
- It shows citations, passages, domains used, and run timeline clearly.
- It gives the user visible presets that make the product feel purposeful rather than open-ended.
- It lets the user select from an allowed model catalog at session scope.

The console is where the buyer should most clearly feel that Intelli Studio is not "just chat."

## Current-State Anchor

The repo already has a meaningful baseline:

- `ui/src/components/chat/ChatPanel.tsx` provides a conversation sidebar, message surface, right panel slot, and run timeline toggle. I^1
- `ui/src/pages/ResearchPage.tsx` uses that panel with notebook context and a sources rail, proving the basic interaction loop exists. I^2
- `ui/src/components/chat/SourcesSidebar.tsx` already renders cited document chunks. I^3
- `src/intelli/api/v1/agent.py` already binds agent chat to pointer or manifest context, streams messages, and records runs. I^4
- Session lifecycle already exists in the UI and API, but model selection, presets, web domains used, and broader context presentation are still missing or thin. I^5

The wider issue normalization lives in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md) and [intelli-studio-north-star-plan.md](./intelli-studio-north-star-plan.md). This document stays focused on the console itself: the central surface that should generalize what exists rather than replace it with a disconnected new page. I^6

## Product Rules

- The console is a first-class global surface, not a module-local feature.
- Every console session carries visible context chips or header state for:
  - project
  - task
  - session
  - active bundle
  - active research pack, when present
- The user can choose from visible skill presets:
  - Research
  - Summarize
  - Compare
  - Draft
  - Bundle
  - Prepare Dashboard
- The user can choose from an allowed-model catalog scoped to the session.
- Model selection must be explicit and inspectable, not hidden in settings or environment defaults.
- Run timeline and SSE activity remain first-class and easy to inspect.
- Citations remain first-class and link to passages or evidence objects, not just footnote text.
- Web domains used must be shown whenever web research was part of the response.
- Save and pin actions must let useful outputs land back into system objects, not remain trapped in the thread.

## Right Rail Contract

The right rail is not optional decoration. It is the console's trust surface.

It must support:

- cited documents
- cited passages
- web domains used
- active bundle context
- save and pin actions

The rail should help the user answer:

- "What evidence is this answer grounded in?"
- "What outside domains did the system use?"
- "What working set is in play?"
- "What can I save from this interaction?"

## Session And Context Rules

- Sessions remain the continuity object for console work.
- The console must show when it is continuing a session versus starting a fresh one.
- Switching major context objects should be visible and deliberate.
- The console should not silently inherit a bundle or pack the user cannot see.
- Saved console outputs should be linkable back to session, run, bundle, and pack context.

## Escalations Required

- The live issue corpus should probably gain a dedicated parent issue for the universal agent console rather than relying on the user or next agent to mentally combine runs, notebook, apps, skills, tool directory, and transport issues.
- If model selection is a real buyer-facing control, it should be named in issue structure explicitly rather than hidden inside a generic app or agent-management story.
- Domains-used visibility and save-to-ResearchPack behavior should be explicit acceptance language, not assumed to emerge from notebook or streaming work.

## Judgment Required

Do not ship a universal console that is only universal in routing. The console must feel more serious than the current research chat, not just broader. If the right rail remains document-only, if model choice remains hidden, or if web domains remain invisible, the console is not done. I^2 I^4

The test is not whether the agent can answer. The test is whether the buyer can inspect how and where the answer came from.

## Builder Accountability

The D3 builder is personally responsible for making sure:

- the console feels like the center of the product
- visible context is rich enough that the user understands what the agent is operating over
- presets make the product feel intentional rather than generic
- model choice is inspectable and session-scoped
- provenance is easier to inspect after the change than before it

Fake completion includes:

- renaming the research page without broadening its context model
- keeping citations but not adding domains used
- adding presets as dead UI with no meaningful behavioral or contextual framing
- hiding model choice in a settings corner while calling it a console feature

## Issue Hooks

- `I^1` - `ui/src/components/chat/ChatPanel.tsx` already provides the conversation layout, right panel slot, and run timeline.
- `I^2` - `ui/src/pages/ResearchPage.tsx` shows the current console baseline is a research-specific assistant tied to notebook context.
- `I^3` - `ui/src/components/chat/SourcesSidebar.tsx` proves cited document passages already exist as a trust primitive.
- `I^4` - `src/intelli/api/v1/agent.py` shows the current agent endpoint already binds to pointer and manifest scope, records runs, and streams metadata.
- `I^5` - `ui/src/hooks/use-session-lifecycle.ts`, `src/intelli/api/v1/sessions.py`, and [ADR-006](../../../docs/adr/006-session-workspace-architecture.md) show the current session baseline the console should elevate.
- `I^6` - [BL-001](../../../staging_issues/BL-001__bl-001-research-orchestrator-graph.md), [BL-003](../../../staging_issues/BL-003__bl-003-web-research-mcp-tools.md), and [BL-022](../../../staging_issues/BL-022__bl-022-shared-data-brief.md) establish the richer orchestrator path, web research tools, and shared output shape behind the current assistant.
- `I^7` - Live GitHub issues `#111`, `#76`, `#77`, `#79`, `#80`, `#83`, and `#87` describe runs detail, skills, tool directory, research notebook behavior, reusable apps, agent configuration, and alternate streaming transports that together imply a more central console surface even though no single parent issue names it yet.
