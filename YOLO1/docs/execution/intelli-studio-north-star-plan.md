# Intelli Studio North-Star Plan

## Summary

Build Intelli Studio as a buyer-facing intelligence workspace that feels expensive, calm, and trustworthy: a polished shell, a strong sense of context, a central agent console, real document and web research, versioned evidence bundles, live activity, and a workflow studio that makes complex work look controlled.

This is not a “complete the checklist and stop” plan. It is a “ship until the product feels like the thing we are trying to sell” plan. Deterministic packet acceptance is necessary for control, but insufficient for completion. Every wave ends with a dedicated finish-wrapper issue whose only job is to close the gap between “implemented” and “convincing.”

For the live issue grounding behind this plan, read [gh-issue-grounding.md](../../notes/gh-issue-grounding.md) first.

## Deployment Companion Pack

This plan defines the product and the execution waves. It does not define the last-mile operating lane for the current single-host demo environment.

For that, read:

- [demo-deployment-brief.md](./demo-deployment-brief.md)
- [demo-env-provider-matrix.md](./demo-env-provider-matrix.md)
- [demo-seed-bootstrap.md](./demo-seed-bootstrap.md)
- [demo-release-smoke-checklist.md](./demo-release-smoke-checklist.md)
- [demo-incident-and-fallback-rules.md](./demo-incident-and-fallback-rules.md)

Those docs make the current demo lane runnable. They do not change the product north star, wave model, or buyer-grade quality bar.

## North-Star Product

The finished demo should feel like this:

- The sign-in screen looks like enterprise software with taste, not a dev login form.
- The shell is stable and legible: left navigation, clear breadcrumb, visible current project/task/session, proper settings, thoughtful dark and light mode.
- The dashboard feels like the morning control surface for an operator: live runs, active workflows, key projects, recent research packs, recent bundle changes, and the things that need attention.
- The Universal Agent Console feels like the center of the system, not a side feature. It can see project, task, session, bundle, and research context. It can use skills. It can read uploaded files. It can cite sources. It can show which web domains it used.
- The research module feels like a serious analyst tool: document retrieval and internet research in one place, with ResearchPacks saved back into the system.
- The bundling/versioning module feels like a differentiator: users can see file history, manifest history, diffs, imports, and how outputs relate back to evidence.
- The Workflow Studio feels modern and compositional: a strong middle canvas, a disciplined right inspector, and a clear separation between deterministic steps and agentic steps.
- Projects, tasks, clients, and decisions exist as thin but real business wrappers so the system feels like a client platform rather than an isolated AI demo.
- Incomplete modules never look broken. They look deliberate, premium, and obviously on the path to completion.

## Core Principles

- Done means buyer-grade: a feature is done when it works, looks intentional, handles empty/loading/error states well, fits the shell, and creates trust.
- Trust comes from visible provenance: sources, domains, bundles, runs, and diffs must remain inspectable.
- Autonomy over babysitting: issues and packets should tell an agent what to do next without relying on operator memory every 12 minutes.
- Judgment is required: implementers should not stop at the first passing check if the surface still feels awkward, thin, or obviously unfinished within packet scope.
- Demo lane beats platform rabbit holes: managed services and thin models are acceptable if they get to a credible demo faster and stay behind adapters.
- Finish wrappers are mandatory: every wave gets a final polish/integration issue that exists purely to make the result feel complete.

## Runtime And System Shape

### LangGraph Is The Agent Backend For

- chat
- skill and preset execution
- tool-using assistants
- research assistants
- other agentic, non-deterministic flows

### Deterministic Workflows Use A Separate Runtime For

- explicit DAG execution
- ordered steps
- retries and resume
- validation
- predictable execution semantics

Deterministic workflows may contain explicit `Agent Step` nodes that call into LangGraph and return structured outputs to the workflow runtime.

Concrete deterministic runtime semantics are locked in [workflow-runtime-contract.md](./workflow-runtime-contract.md).

### Shared Platform Rules

- MCP remains the tool plane for both runtimes where tool access is needed.
- Shared substrate remains canonical for projects, tasks, sessions, pointers, manifests, artifacts, ResearchPacks, run ledger, and SSE/activity streams.
- Managed services are allowed for demo speed behind internal adapters:
  - document parsing and OCR
  - web research
  - optional retrieval and indexing acceleration

## Delivery Waves

### D1: Shell, Identity, And Context

Build the premium shell first.

- polish sign-in, theme behavior, under-construction states, settings, and model-selector surfaces
- add the context model as a two-line treatment:
  - business line: `Workspace > Initiative > Project > Task`
  - working line: `Module > Session > Bundle > ResearchPack > Workflow`
- refine the left rail so it feels like a stable operating system for the product
- add thin native context objects:
  - Workspace
  - Initiative
  - Project
  - Task
  - Session

Finish wrapper:

- typography, spacing, labels, iconography, mobile behavior, empty states, and “this looks like a real product” cleanup

### D2: Dashboard, Projects, Clients, And Decisions

Make the app feel operational.

- replace the front page with a real dashboard driven by existing run/session/bundle data
- show live and recent activity:
  - active runs
  - workflow activity
  - recent bundle changes
  - recent research packs
  - key projects
- build thin native Projects first, then thin Clients
- add a thin Decisions surface:
  - list, detail, create, and edit decisions linked to Projects
  - visible recent decisions on dashboard and project detail
- borrow patterns from CRM-style workspaces, but do not port a separate app wholesale

Finish wrapper:

- make the dashboard feel like a control center, not a table farm

### D3: Universal Agent Console

Promote chat to the main intelligence surface.

- generalize the existing research assistant into a global agent console
- context comes from project, task, session, bundle, and research pack
- add visible skill presets:
  - Research
  - Summarize
  - Compare
  - Draft
  - Bundle
  - Prepare Dashboard
- add a real allowed-model catalog and session-scoped selector
- keep run timeline, citations, and SSE first-class

Finish wrapper:

- make the console feel powerful, inspectable, and central

### D4: Research And Research Packs

Make research genuinely strong.

- add web research through provider adapters, with Tavily as the first provider
- combine document retrieval and internet research in one session
- add `ResearchPack` as a saved head object with immutable `ResearchPackRevision` snapshots linked to projects, sessions, bundles, and runs
- fix the right rail contract:
  - cited documents
  - cited passages
  - web domains used
  - bundle context
  - save/pin actions
- enrich Decisions with evidence-linked citations, linked artifacts, and stale/degradation hooks when source evidence changes

Finish wrapper:

- research should feel like a premium analyst workspace, not “chat plus search”

### D5: Bundles And Versioning

Expose the substrate as a product strength.

- turn notebooks/bundles into a visibly serious versioning surface:
  - bundle detail
  - manifest history
  - diff view
  - file preview
  - related runs
  - related research packs
- add imports from:
  - local upload
  - GitHub repository
  - Git LFS-backed content where practical
- rule: external systems are ingestion sources; once imported, our substrate is authoritative

Finish wrapper:

- versioning, diffs, and provenance should feel like one of the reasons to buy the system

### D6: Workflow Studio

Ship the most ambitious visible surface last, but make it fully real.

- build a polished middle-view workflow and analysis studio
- layout is fixed:
  - left palette
  - center canvas
  - right inspector
  - bottom run log and timeline
- style target:
  - modern
  - clean
  - Google Opal-like compositional feel
  - aligned to the Intelli shell
- workflow nodes are deterministic by default
- `Agent Step` nodes explicitly delegate into LangGraph
- outputs land back in bundles, artifacts, ResearchPacks, and project activity

Finish wrapper:

- the page must feel premium and coherent, not just runnable

### G1: Demo Guardrails

Keep a narrow parallel lane for stability only.

- session persistence
- run and SSE correctness
- provider adapter hygiene
- build and review discipline
- indexing and retrieval reliability
- auth good enough for demos

## Issue Normalization

The live issue corpus is strong, but it is not already shaped like this plan. The final structure here is a deliberate normalization.

### Which Live Issue Clusters Already Support The Waves

- `D1` is already partially supported by early shell, runs, onboarding, and artifact-explorer work.
- `D2` is already partially supported by dashboard, activity, project, client, and decision-register work, but it still needs clearer early-wave normalization.
- `D3` is already partially supported by runs detail, notebook, skills, tool directory, agent-management, and app configuration work.
- `D4` is already partially supported by orchestrated research, web-research tools, notebook behavior, artifact provenance, and richer corpus work.
- `D5` is already partially supported by notebook substrate behavior, bundle/corpus organization, artifact explorer, structured diffing, and deliverable-version work.
- `D6` is already partially supported by canvas, apps, workflows, and builder-related issue families, but the runtime contract still needs explicit tightening.
- `G1` is already partially supported by streaming, observability, security, CI, and critical cleanup work.

### Concepts That Need Explicit Promotion

- Dashboard as a first-class D2 operator surface
- Universal Agent Console as a named product parent
- `ResearchPack` plus `ResearchPackRevision` as the saved research object model
- `Bundle` as the buyer-facing product layer over pointer/manifest/artifact substrate
- `Decision` as an explicit buyer-facing business surface with a dedicated companion spec
- `Workflow Studio` as one unified surface spanning canvas/apps/workflows
- `workflow-runtime-contract.md` as the deterministic execution contract behind the studio
- `CAP / PKT / WRAP` as the intended issue overlay

### Live Issues To Treat As Inputs, Not Literal Final Structure

- early shell and onboarding issue families are useful inputs to D1, but not the final shell contract on their own
- later studio issue families are useful inputs to D2 and D6, but not the final sequencing or runtime model on their own
- notebook, corpus, artifact, and provenance work are ingredients for D4 and D5, not the final product taxonomy on their own
- later domain dashboards are inspiration for drilldown patterns, not substitutes for the main Intelli dashboard

Exact issue-number mapping belongs in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md), not in this stable narrative plan.

## Issue Structure To Create

Use one parent, a run of build packets, and one finish wrapper per wave.

Naming scheme:

- `[CAP][D1] Shell, Identity, and Context`
- `[PKT][D1-01] ...`
- `[PKT][D1-02] ...`
- `[PKT][D1-03] ...`
- `[WRAP][D1] Buyer-grade finish wrapper`

Apply the same pattern through `D6` and `G1`.

Each wrap issue should explicitly cover:

- UX coherence
- copy cleanup
- visual polish
- empty/loading/error states
- context propagation
- evidence/provenance visibility
- “does this feel sellable?”

## Acceptance Standard

The main demo should allow a buyer to:

- sign in to a polished product
- open a project and task
- upload or import files into a bundle
- inspect bundle history and diffs
- use the Universal Agent Console over uploaded files
- run internet research in the same context
- see cited passages and web domains in the right rail
- save outputs into a ResearchPack with revision history
- see the resulting activity on the dashboard
- run a deterministic workflow with at least one `Agent Step`
- see outputs land back in the system as real artifacts, packs, and project activity

If that flow works but still looks thin, awkward, or dev-grade, the work is not done yet.

## Assumptions And Defaults

- the current Intelli app remains the only buyer-facing shell
- LangGraph remains the agent backend only
- deterministic workflows use a separate runtime
- MCP remains mandatory
- Projects and Clients are native thin modules in Intelli
- managed providers are acceptable behind adapters for demo speed
- Tavily is the first web research provider
- deep CRM, billing, SSO, and enterprise-grade multi-tenant hardening remain out of scope for this demonstrator phase
