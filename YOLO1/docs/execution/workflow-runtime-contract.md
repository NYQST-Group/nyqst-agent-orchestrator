# Workflow Runtime Contract

The deterministic runtime should not be a hand-wavy future box behind Workflow Studio. If the studio is going to sell controlled automation, the runtime contract has to be explicit enough that the next builder is not forced to invent state semantics, node I/O, or retry behavior. I^1 I^2

## North-Star Intent

The runtime contract exists so a buyer can trust that deterministic workflows are actually deterministic:

- workflow definitions are inspectable
- published versions are stable
- runs have legible execution state
- node behavior is predictable
- `AgentStep` is explicit and bounded
- outputs land back in substrate-backed system objects

This is the contract that makes the runtime split real rather than rhetorical.

## Current-State Anchor

The repo and issue set already supply the ingredients this contract needs to unify:

- [runtime-split.md](./runtime-split.md) already separates agentic LangGraph work from deterministic workflow execution. I^1
- [workflow-studio-spec.md](./workflow-studio-spec.md) already defines the visible studio surface that depends on this runtime. I^2
- `STORY-WF-001` through `STORY-WF-004` already define workflow definitions, deterministic execution, triggers, and builder UI in staged backlog form. I^3
- Live issue `#139` still describes compiling a DAG to LangGraph under the same run ledger, which is the exact ambiguity this contract resolves. I^4
- `src/intelli/services/runs/run_service.py` and the run ledger already provide the audit spine that workflow execution should plug into rather than replace. I^5

## Product Rules

- Deterministic workflows use a runtime distinct from LangGraph.
- `Workflow Studio` is the buyer-facing surface for that runtime.
- `AgentStep` is the only allowed delegation boundary from deterministic execution into LangGraph.
- Published workflow behavior must be explainable from the workflow graph, node configuration, and run ledger without reconstructing hidden runtime state.
- All workflow-visible outputs must land back in substrate-backed objects such as artifacts, Bundles, ResearchPacks, and project activity.

## Runtime Objects

- `WorkflowDefinition`
  Editable graph draft. This is the mutable working shape in the builder before publish.
- `WorkflowVersion`
  Immutable published snapshot of one `WorkflowDefinition`. Publish freezes topology and node config for that version.
- `WorkflowRun`
  One execution of one `WorkflowVersion`.
- `WorkflowNodeRun`
  One execution record for one node within one `WorkflowRun`.

## Node Taxonomy

V1 node kinds are:

- `Input`
- `Transform`
- `Validation`
- `AgentStep`
- `Publish`
- `Trigger`

Each node kind must declare:

- accepted input envelope
- emitted output envelope
- retry policy
- whether it can produce substrate-backed outputs

## V1 Envelope Table

Use these envelopes as the locked V1 baseline so the next builder does not invent per-node I/O semantics ad hoc:

| Node kind | Consumes | Emits |
| --- | --- | --- |
| `Input` | none beyond run invocation context | `context_refs`, `bundle_refs`, `artifact_refs`, `payload` |
| `Transform` | `payload`, `bundle_refs`, `artifact_refs` | `payload`, optional `artifact_refs` |
| `Validation` | `payload`, optional refs from upstream nodes | `passed`, `issues[]`, `blocking` |
| `AgentStep` | see dedicated `AgentStep` contract below | see dedicated `AgentStep` contract below |
| `Publish` | `payload`, `artifact_refs`, optional upstream refs | `published_object_type`, `published_object_id`, `artifact_refs` |
| `Trigger` | trigger metadata and invocation inputs | `trigger_type`, `trigger_metadata`, `run_inputs` |

Rule:

- V1 node output must remain JSON-serializable and storable in workflow node-run state and the shared run ledger without ad hoc per-node hidden state.

## Graph Rules

- V1 workflows are DAGs only.
- V1 published workflows do not allow cycles.
- Publish freezes a `WorkflowVersion`; edits after publish create a new version.
- A `WorkflowRun` always references one immutable `WorkflowVersion`.
- V1 allows manual runs and trigger-created runs; schedules and event triggers are both recorded as audited workflow runs.

## Run State Machine

`WorkflowRun` states:

- `queued`
- `running`
- `paused`
- `failed`
- `partial`
- `succeeded`
- `cancelled`

`WorkflowNodeRun` states:

- `pending`
- `ready`
- `running`
- `retry_wait`
- `succeeded`
- `failed`
- `skipped`
- `blocked`

Rules:

- `partial` means the workflow completed with at least one non-fatal node failure or skip while still producing some downstream outputs.
- `paused` means operator or policy intervention is required before execution continues.
- `blocked` means a node cannot start because an upstream prerequisite did not produce the required output envelope.

## Retry And Resume Rules

- Deterministic nodes may auto-retry according to node policy with backoff.
- `AgentStep` nodes may auto-retry only for transport/runtime failures, not for semantic failure or low-quality output.
- Resume restarts from the first incomplete node using persisted upstream node outputs.
- Resume must not recompute already-succeeded nodes unless the operator explicitly starts a fresh run.

## AgentStep Contract

`AgentStep` input:

- normalized JSON payload from upstream nodes
- mounted context refs for active Project, Task, Session, Bundle, ResearchPack, or Workflow context as applicable
- explicit model and tool policy

`AgentStep` output:

- normalized envelope containing:
  - structured payload
  - optional operator-facing summary
  - artifact refs
  - citation refs
  - domain refs
  - final status

Rules:

- `AgentStep` output is written back into the deterministic graph as node output.
- `AgentStep` output must not live only inside LangGraph state.
- `AgentStep` may create a child agent run, but the deterministic workflow remains the controlling parent execution.

## Run Ledger Rules

- A workflow run creates one parent run record.
- Each node emits node start, completed, failed, retry, or skipped events.
- `AgentStep` may create a child agent run linked to the parent workflow run and node id.
- Node logs must stay visible from the overall run and from the node itself.
- Trigger-created runs must be auditable in the same ledger as manual runs.

## Judgment Required

Do not leave this contract half-written. If the next builder still has to decide what a workflow version is, how `AgentStep` output is normalized, or when resume starts, the runtime contract has failed. This document exists to remove those decisions from the implementation path. I^1 I^3

## Builder Accountability

The builder responsible for the runtime contract must verify personally:

- that deterministic and agentic work have different execution semantics, not just different labels
- that publish/version/run objects are unambiguous
- that resume and retry behavior are explainable before implementation starts
- that `AgentStep` is explicit, bounded, and normalized back into the deterministic graph
- that the run ledger tells the truth about workflow execution without hidden side state

Fake completion includes:

- calling a graph deterministic without locking version semantics
- treating node output as ad hoc JSON with no contract
- making `AgentStep` a generic escape hatch
- leaving retry or resume behavior to builder interpretation

## Issue Hooks

- `I^1` - [runtime-split.md](./runtime-split.md) establishes the runtime boundary this contract operationalizes.
- `I^2` - [workflow-studio-spec.md](./workflow-studio-spec.md) depends on this contract for its execution semantics.
- `I^3` - `STORY-WF-001` through `STORY-WF-004` in `staging_issues/issues.json` lock versioning, deterministic execution, retries, triggers, and builder expectations that this contract needs to normalize.
- `I^4` - Live GitHub issue `#139` explicitly describes compiling a DAG to LangGraph, which this contract intentionally narrows into a bounded `AgentStep` delegation model.
- `I^5` - `src/intelli/services/runs/run_service.py` and the current run ledger are the existing audit spine that workflow execution should extend rather than bypass.
