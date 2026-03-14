# ResearchPack Spec

Research in Intelli Studio should feel like analyst work with visible provenance, not a pleasant chat transcript. `ResearchPack` is the reusable saved object, and `ResearchPackRevision` is the immutable snapshot that keeps analyst iteration from destroying inspectability. I^1 I^2

## North-Star Intent

The research surface should combine document retrieval and internet research in one working context. The output should not disappear into thread history. It should become a ResearchPack:

- saved
- versioned
- linked to project, session, bundle, and run context
- rich with citations, passages, domains, and source relationships

The user should feel like they are building a premium analyst work product, not bookmarking a chat answer.

## Current-State Anchor

The repo already has partial ingredients:

- `src/intelli/services/knowledge/rag_service.py` supports manifest-scoped retrieval and answer generation over uploaded evidence. I^1
- `ui/src/pages/ResearchPage.tsx` and `ui/src/components/chat/SourcesSidebar.tsx` already make cited document evidence visible inside the current research assistant. I^2
- `src/intelli/api/v1/agent.py` already links runs, messages, and session context. I^3
- Web research provider work is already anticipated in [BL-003](../../../staging_issues/BL-003__bl-003-web-research-mcp-tools.md). I^4
- The orchestrator direction for richer research behavior is already anticipated in [BL-001](../../../staging_issues/BL-001__bl-001-research-orchestrator-graph.md). I^5

The wider issue normalization lives in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md) and [intelli-studio-north-star-plan.md](./intelli-studio-north-star-plan.md). This document stays local to the missing product object: the saved research surface that should behave like the rest of the substrate by using a stable head and immutable revisions. I^7

## Product Rules

- `ResearchPack` is the mutable head or pointer object for saved research.
- `ResearchPackRevision` is the immutable saved snapshot.
- A `ResearchPack` may be created from a research session, console action, or workflow output.
- A `ResearchPackRevision` must be linkable to:
  - project
  - task, when relevant
  - session
  - originating run or runs
  - active bundle or bundles
- A `ResearchPackRevision` must carry, at minimum:
  - a summary
  - saved outputs or linked artifacts
  - cited documents
  - cited passages
  - web domains used
  - source provenance
  - origin session and run references
- Web research should start with Tavily behind an adapter boundary.
- Document retrieval and web research must be usable within the same research context rather than split across separate tools or pages.

## Save And Revision Rules

- First save creates a new `ResearchPack` head plus revision `v1`.
- Saving again to the same pack creates a new immutable revision and advances `latest_revision_id`.
- “Save as new pack” creates a new head.
- Provenance, citations, passages, domains, and linked outputs live on the revision, not on the head.
- The head stores identity and navigation concerns only.
- `pinned_revision_id` is optional and is used when a dashboard, Bundle relation, or workflow needs a stable reference while the pack keeps evolving.

## Research Behavior Rules

- Document evidence and web evidence should appear as parts of the same research session, not competing channels.
- The system should distinguish between bundle-backed evidence and outside-web evidence without making the user reconstruct the difference.
- Domains used should be visible in the right rail and in the saved `ResearchPackRevision`.
- Save actions should be obvious and should preserve context rather than flattening the result into free text.
- ResearchPack save behavior should feel like publishing a useful result, not exporting a chat transcript.

## Provenance Rules

- Every claim saved into a `ResearchPackRevision` should preserve enough provenance to inspect where it came from.
- Bundle context, cited passages, and domains used should remain visible after saving.
- Related runs and follow-on workflow outputs should be traceable back to the revision and its parent pack.
- ResearchPack should strengthen trust by compressing useful work without destroying inspectability.

## Escalations Required

- `ResearchPack` is not yet a named first-class object in the live GitHub issue corpus. If the north-star plan keeps it, the next agent should create or normalize issues around it rather than assuming notebooks or artifacts cover it sufficiently.
- The current issue set contains strong ingredients for notebook workflow, artifacts, provenance, and corpus organization, but not yet one explicit saved-research-object story.
- The head-plus-revisions model should stay aligned with the substrate pattern rather than becoming a one-off exception object.
- Domains-used visibility should be treated as mandatory acceptance language in any web-research implementation packet.

## Judgment Required

Do not confuse "we can show citations" with "research feels serious." The research module is not done if domains used are invisible, if saved outputs are vague, or if web and document evidence feel like separate disconnected tools. Research should feel like a premium analyst workspace, not chat plus search with a save button. I^2 I^4 I^5

## Builder Accountability

The D4 builder is personally responsible for making sure:

- research outputs can be turned into durable system objects
- provenance remains inspectable after saving
- mixed-source research feels unified rather than bolted together
- domain visibility becomes a real trust surface
- the user can understand what evidence came from uploads versus the web
- the pack head does not become a mutable bag of evidence fields that should really live on revisions

Fake completion includes:

- adding web search but not surfacing domains used
- saving chat answers without preserving cited passages or source context
- smearing citations, passages, domains, and linked outputs across a mutable head instead of storing them on immutable revisions
- making the right rail richer during chat but losing that fidelity when the output is saved

## Issue Hooks

- `I^1` - `src/intelli/services/knowledge/rag_service.py` is the current document-retrieval backbone over manifests.
- `I^2` - `ui/src/pages/ResearchPage.tsx` and `ui/src/components/chat/SourcesSidebar.tsx` show the current assistant already has document-citation behavior to build on.
- `I^3` - `src/intelli/api/v1/agent.py`, session APIs, and the run ledger already give research sessions durable context and traceability hooks.
- `I^4` - [BL-003](../../../staging_issues/BL-003__bl-003-web-research-mcp-tools.md) is direct backlog evidence for web research tools and related run events.
- `I^5` - [BL-001](../../../staging_issues/BL-001__bl-001-research-orchestrator-graph.md) establishes the richer orchestrated research direction that should eventually feed ResearchPack outputs.
- `I^6` - [studio-north-star.md](./studio-north-star.md) and [agent-console-spec.md](./agent-console-spec.md) define the product expectation that research is central, inspectable, and saveable.
- `I^7` - Live GitHub issues `#79`, `#112`, `#145`, and `#146` show that notebook workflow, artifact provenance, corpus organization, and locator-rich document processing are already converging toward a stronger saved-research object model even though `ResearchPack` is not yet named directly.
