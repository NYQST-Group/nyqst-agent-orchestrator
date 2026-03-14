# Runtime Split

Intelli Studio should not hide architectural confusion behind a polished UI. The product only feels controlled if agentic work, deterministic workflow execution, tool access, and system-of-record behavior each have a clear home. If the split goes soft, the studio becomes muddy, uninspectable, and harder to sell. I^1 I^2

## North-Star Intent

The runtime split exists so the buyer can trust what kind of work the system is doing.

- LangGraph handles agentic, non-deterministic, exploratory, tool-using, chat-like work.
- A separate deterministic workflow runtime handles explicit DAG execution, ordered steps, retries, resume, validation, and predictable semantics.
- MCP remains the shared tool plane when either runtime needs tools.
- The shared substrate remains canonical for outputs, provenance, and inspectable history.

The product should make this distinction visible. A user should be able to tell when the system is reasoning, when it is executing a fixed process, and where the outputs landed.

## Current-State Anchor

The repo already has a substantial agent-side foundation:

- [ADR-005](../../../docs/adr/005-agent-runtime-framework.md) locks LangGraph as the primary agent orchestration runtime and makes the platform substrate authoritative. I^1
- [ADR-008](../../../docs/adr/008-mcp-tool-architecture.md) already defines MCP as the primary tool protocol and LangGraph as a thin consumer of that tool plane. I^2
- `src/intelli/api/v1/agent.py` and `src/intelli/agents/graphs/research_assistant.py` show the current LangGraph-backed research assistant baseline. I^3
- `src/intelli/services/runs/run_service.py`, the run ledger, and SSE streams already give the system a canonical audit spine. I^4
- Workflow builder and runner work is already present in backlog form as `STORY-WF-001` through `STORY-WF-004`, but not yet realized as a buyer-facing surface. I^5

The wider normalization logic lives in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md) and [intelli-studio-north-star-plan.md](./intelli-studio-north-star-plan.md). The key local tension is explicit: live issue `#139` still describes workflow execution as compiling a DAG to LangGraph, while this north-star pack deliberately separates deterministic workflow execution from the agent runtime. The concrete deterministic-side contract now lives in [workflow-runtime-contract.md](./workflow-runtime-contract.md). I^7

This means the split should be sharpened and productized, not invented from scratch.

## Product Rules

- LangGraph is the agent backend for:
  - chat
  - tool-using assistants
  - skill and preset execution
  - research assistants
  - other non-deterministic, reasoning-heavy flows
- Deterministic workflows run elsewhere, under a runtime whose job is predictability, resumability, retries, validation, and ordered control flow.
- Deterministic workflows may call LangGraph only through explicit `Agent Step` nodes.
- Agent Step nodes return outputs back to the deterministic runtime rather than becoming a hidden parallel system.
- MCP is shared infrastructure, not product glue. Both runtimes can use it without owning it.
- The shared substrate remains canonical for:
  - projects
  - tasks
  - sessions
  - pointers
  - manifests
  - artifacts
  - research packs
  - run ledger
  - SSE and activity streams
- Managed services are acceptable for demo speed only when they stay behind internal adapters and do not blur these boundaries.

## Operational Guidance

Use LangGraph when the system needs:

- judgment
- planning
- tool selection
- synthesis
- conversational continuity
- flexible research paths

Use the deterministic runtime when the system needs:

- a declared graph
- fixed step ordering
- per-node validation
- retries and resume
- reliable execution semantics
- a workflow surface a buyer can inspect and understand

Use MCP when a runtime needs:

- a tool boundary
- permissioned access to system capabilities
- a shared tool vocabulary across runtime types

Use the substrate when the system needs:

- authoritative outputs
- replayable provenance
- versioned bundle state
- run-linked evidence
- visible inspection and history

## Consequences Of Violating The Split

If agentic and deterministic work collapse into one blurry runtime, the product pays for it immediately:

- the workflow studio starts feeling magical rather than controlled
- retries and failure behavior become harder to explain
- provenance becomes harder to inspect cleanly
- the buyer cannot tell whether a result was reasoned, executed, or guessed
- implementation packets drift toward convenience wiring instead of clear product semantics

This is not only an engineering problem. It is a trust problem.

## Judgment Required

Do not treat this split as a back-end-only note. The product must express it. If a user cannot tell whether they are running an agentic step or a deterministic step, the studio is not done. If outputs do not land back in obvious system objects, the runtime story is not done. I^1 I^5

## Builder Accountability

The builder responsible for runtime-facing work must verify personally:

- that agentic work and deterministic work have visibly different roles
- that `Agent Step` is explicit in the workflow studio and not hidden inside generic nodes
- that tool calls still flow through governed MCP boundaries where required
- that emitted outputs land back in runs, bundles, artifacts, packs, or activity in a traceable way
- that no "fast demo" shortcut makes the product harder to explain later

Fake completion includes:

- letting the workflow studio silently call agent graphs without surfacing the boundary
- storing important outputs in runtime-local state instead of the substrate
- using managed services directly from UI or feature logic without an adapter boundary
- presenting a deterministic workflow as if it were just another chat trick

## Issue Hooks

- `I^1` - [ADR-005](../../../docs/adr/005-agent-runtime-framework.md) explicitly sets LangGraph as the agent runtime and the substrate as authoritative.
- `I^2` - [ADR-008](../../../docs/adr/008-mcp-tool-architecture.md) makes MCP the primary tool protocol and defines LangGraph tools as thin wrappers over MCP tools.
- `I^3` - `src/intelli/api/v1/agent.py` and `src/intelli/agents/graphs/research_assistant.py` are the current live examples of LangGraph-driven agentic behavior.
- `I^4` - `src/intelli/services/runs/run_service.py`, the run ledger, and stream endpoints are the current audit and activity spine.
- `I^5` - `STORY-WF-001` through `STORY-WF-004` in `staging_issues/issues.json` establish stored workflow definitions, deterministic execution, triggers, and the future workflow builder UI.
- `I^6` - [workflow-runtime-contract.md](./workflow-runtime-contract.md) locks the deterministic-side objects, state machine, retry rules, and `AgentStep` normalization that this split depends on.
- `I^7` - Live GitHub issue `#139` (`STUDIO-007`) explicitly describes a workflow-builder path that compiles DAGs to LangGraph and runs them under the same run ledger, which this spec intentionally tightens into a clearer runtime split.
