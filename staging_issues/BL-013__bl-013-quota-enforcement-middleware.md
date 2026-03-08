# [BL-013] Quota Enforcement Middleware
**Labels:** `type:billing`, `phase:4-billing`, `priority:high`, `track:billing`, `size:S`
**Milestone:** M4: Billing & Polish
**Blocked By:** BL-012
**Blocks:** None

**Body:**
## Overview
Create a FastAPI dependency that checks usage quota before allowing new run creation. Loads the user's subscription, queries current-period usage, compares against plan limits, and returns HTTP 429 when quota is exceeded. Pro accounts allow overage at $0.50/run.

## Acceptance Criteria
- [ ] FastAPI `Depends()` function on run creation endpoints
- [ ] Free account at limit returns HTTP 429 with `{"error": "quota_exceeded", "limit": N, "current": N}`
- [ ] Pro account within limit allows run creation
- [ ] Pro account overage tracked for billing (via Stripe metered billing or manual invoice)
- [ ] Usage record created after successful run creation (not on retry)
- [ ] No quota check on read operations (GET endpoints)

## Technical Notes
- Net-new file: `src/intelli/api/middleware/quota_middleware.py`
- Plan limits: free=5 runs/month + 2 reports, pro=200 runs/month + $0.50/run overage
- Query usage_records table for current billing period
- Frontend should show toast on 429 quota exceeded

## References
- BACKLOG.md: BL-013
- IMPLEMENTATION-PLAN.md: Section 4.2

---

## 4. GitHub CLI Commands

### Label Creation

```bash
# Type labels
gh label create "type:feature" --color "0E8A16" --description "New feature implementation"
gh label create "type:infrastructure" --color "D93F0B" --description "Schema, migration, or platform infrastructure"
gh label create "type:frontend" --color "1D76DB" --description "React/UI component work"
gh label create "type:backend" --color "5319E7" --description "Python/FastAPI backend logic"
gh label create "type:integration" --color "FBCA04" --description "External API or service integration"
gh label create "type:billing" --color "B60205" --description "Stripe billing and quota enforcement"
gh label create "type:test" --color "C5DEF5" --description "Test suite or test infrastructure"
gh label create "type:docs" --color "0075CA" --description "Documentation updates"

# Phase labels
gh label create "phase:0-foundation" --color "BFD4F2" --description "Phase 0: Schema, migration, environment (Weeks 1-2)"
gh label create "phase:1-orchestrator" --color "D4C5F9" --description "Phase 1: Research orchestrator fan-out (Weeks 3-5)"
gh label create "phase:2-deliverables" --color "FEF2C0" --description "Phase 2: Report, website, slides, export pipelines (Weeks 6-8)"
gh label create "phase:3-frontend" --color "C2E0C6" --description "Phase 3: React UI components and views (Weeks 9-11)"
gh label create "phase:4-billing" --color "F9D0C4" --description "Phase 4: Billing, quota, production hardening (Weeks 12-13)"

# Priority labels
gh label create "priority:critical-path" --color "B60205" --description "On the critical dependency chain; blocks other work"
gh label create "priority:high" --color "D93F0B" --description "Important but not on the longest path"
gh label create "priority:medium" --color "FBCA04" --description "Standard priority; can be reordered within phase"
gh label create "priority:low" --color "0E8A16" --description "Nice to have; can slip without impact"

# Track labels
gh label create "track:orchestrator" --color "7057FF" --description "Research orchestrator graph and agent nodes"
gh label create "track:frontend" --color "008672" --description "React components and Zustand stores"
gh label create "track:billing" --color "E4E669" --description "Stripe integration and quota enforcement"
gh label create "track:deliverables" --color "FF7619" --description "Report, website, slides, document generation"
gh label create "track:infrastructure" --color "6F42C1" --description "Schema, models, migrations, services"

# Size labels
gh label create "size:XS" --color "EDEDED" --description "~1 story point: trivial change, < 2 hours"
gh label create "size:S" --color "D4C5F9" --description "~2 story points: small task, half day"
gh label create "size:M" --color "BFD4F2" --description "~3 story points: moderate task, 1-2 days"
gh label create "size:L" --color "FEF2C0" --description "~5 story points: large task, 3-5 days"
gh label create "size:XL" --color "F9D0C4" --description "~8 story points: epic-level, full week+"

# Status labels
gh label create "status:blocked" --color "B60205" --description "Waiting on another issue to complete"
gh label create "status:ready-to-start" --color "0E8A16" --description "All dependencies met; can begin work"
gh label create "status:in-review" --color "FBCA04" --description "PR submitted; awaiting review"
```

### Milestone Creation

```bash
gh milestone create "M0: Foundation" \
  --description "Phase 0: Schema extensions, migration 0005, Markup AST models, dev environment verification. All schema work lands here. (Weeks 1-2)" \
  --due-date "2026-03-14"

gh milestone create "M1: Orchestrator" \
  --description "Phase 1: Extend ResearchAssistantGraph with planner, Send() fan-out, web tools, meta-reasoning, synthesis, and shared data brief. Backend-only; verified via SSE stream. (Weeks 3-5)" \
  --due-date "2026-04-04"

gh milestone create "M2: Deliverables" \
  --description "Phase 2: Report, website, slides generation pipelines and PDF/DOCX export. Entity/citation substrate. All backend deliverable nodes operational. (Weeks 6-8)" \
  --due-date "2026-04-25"

gh milestone create "M3: Frontend" \
  --description "Phase 3: PlanViewer, DeliverableSelector, ReportRenderer, WebsitePreview, GenerationOverlay, enhanced SourcesPanel and RunTimeline, clarification flow UI. (Weeks 9-11)" \
  --due-date "2026-05-16"

gh milestone create "M4: Billing & Polish" \
  --description "Phase 4: Stripe billing system, quota enforcement middleware, production hardening, observability, and final E2E testing. (Weeks 12-13)" \
  --due-date "2026-05-30"
```

### Issue Creation Examples (3 real examples with full commands)

**Example 1: BL-002 (Wave 0, critical path, infrastructure)**

```bash
gh issue create \
  --title "[BL-002] RunEvent Schema Extensions" \
  --label "type:infrastructure,phase:0-foundation,priority:critical-path,track:infrastructure,size:S,status:ready-to-start" \
  --milestone "M0: Foundation" \
  --body "$(cat <<'EOF'
## Overview
Extend the existing RunEvent type enum with 19 new event types covering planning, subagent fan-out, streaming content, artifacts, clarification, report generation progress, and web research events. This is the foundational schema change that all orchestrator and frontend work depends on.

## Acceptance Criteria
- [ ] All 19 new event types added to `RunEventType` enum in both `schemas/runs.py` and `db/models/runs.py`
- [ ] Typed `log_*` helper methods added to `LedgerService` for each new event type
- [ ] All new event types round-trip through the ledger (create, read back)
- [ ] New events appear correctly in the SSE stream via PG LISTEN/NOTIFY
- [ ] Existing event types and all existing tests remain unaffected
- [ ] Payload shapes documented as Python TypedDict or Pydantic models

## Technical Notes
- Files to modify: `src/intelli/schemas/runs.py`, `src/intelli/db/models/runs.py`, `src/intelli/services/runs/ledger_service.py`
- New types: PLAN_CREATED, PLAN_TASK_STARTED, PLAN_TASK_COMPLETED, PLAN_TASK_FAILED, SUBAGENT_DISPATCHED, SUBAGENT_COMPLETED, SUBAGENT_FAILED, CONTENT_DELTA, ARTIFACT_CREATED, CLARIFICATION_NEEDED, CLARIFICATION_RECEIVED, REPORT_PREVIEW_START, REPORT_PREVIEW_DELTA, REPORT_PREVIEW_DONE, WEB_SEARCH_STARTED, WEB_SEARCH_COMPLETED, WEB_SCRAPE_STARTED, WEB_SCRAPE_COMPLETED, REFERENCES_FOUND
- See IMPLEMENTATION-PLAN.md Section 0.2 for full payload schemas

## Dependencies
- **Blocked by:** None
- **Blocks:** #BL-001, #BL-007, #BL-014, #BL-016, #BL-020, #BL-021

## References
- BACKLOG.md: BL-002
- IMPLEMENTATION-PLAN.md: Section 0.2
EOF
)"
```

**Example 2: BL-001 (Wave 1, XL epic, orchestrator track)**

```bash
gh issue create \
  --title "[BL-001] Research Orchestrator Graph" \
  --label "type:feature,phase:1-orchestrator,priority:critical-path,track:orchestrator,size:XL,status:blocked" \
  --milestone "M1: Orchestrator" \
  --body "$(cat <<'EOF'
## Overview
Extend the existing ResearchAssistantGraph (not replace it) with a planner node, Send() fan-out to parallel research workers, fan-in aggregation, synthesis node, and deliverable router. This transforms the current single-agent loop into a multi-workstream orchestrator that mirrors Superagent's 13+ parallel task pattern.

## Acceptance Criteria
- [ ] Planner node decomposes query into 3-13 ResearchTask dicts and emits PLAN_CREATED event
- [ ] Fan-out dispatches Send() per task, each creating a child Run with parent_run_id FK
- [ ] Research workers execute in parallel using existing agent+tools loop
- [ ] Fan-in node aggregates all TaskResult dicts
- [ ] Synthesis node produces structured DataBrief in graph state
- [ ] Deliverable router routes by deliverable_type to appropriate generation node
- [ ] SSE stream shows: PLAN_CREATED, N x SUBAGENT_DISPATCHED, N x PLAN_TASK_*, STATE_UPDATE
- [ ] AI message hydrated_content contains `<gml-View*>` components
- [ ] Failed tasks emit PLAN_TASK_FAILED without crashing the run
- [ ] All existing graph tests continue to pass

## Sub-Issues
- [ ] [BL-001a] ResearchState Extension
- [ ] [BL-001b] Planner Node
- [ ] [BL-001c] Fan-Out / Fan-In Infrastructure
- [ ] [BL-001d] Synthesis Node and Deliverable Router
- [ ] [BL-001e] Integration Tests and Event Verification

## Technical Notes
- Extends: `src/intelli/agents/graphs/research_assistant.py`
- Existing graph: agent -> (tools_condition) -> tools -> capture_sources -> agent (loop)
- New nodes: planner_node, fan_out, research_worker_node, fan_in_node, synthesis_node, deliverable_router
- research_worker_node creates child Run via `Run(parent_run_id=state["run_id"])`
- See IMPLEMENTATION-PLAN.md Sections 1.1, 1.2 for full graph diagram

## Dependencies
- **Blocked by:** BL-002
- **Blocks:** BL-003, BL-005, BL-006, BL-017, BL-018, BL-021, BL-022

## References
- BACKLOG.md: BL-001
- IMPLEMENTATION-PLAN.md: Sections 1.1, 1.2
EOF
)"
```

**Example 3: BL-009 (Wave 3, frontend track, large)**

```bash
gh issue create \
  --title "[BL-009] ReportRenderer Component" \
  --label "type:frontend,phase:3-frontend,priority:critical-path,track:frontend,size:L,status:blocked" \
  --milestone "M3: Frontend" \
  --body "$(cat <<'EOF'
## Overview
Build a recursive React renderer that transforms MarkupDocument JSON into React elements for all 18 node types. Triggered by `<gml-ViewReport>` tags in AI message hydrated_content. Includes a GmlComponentParser that walks hydrated_content, extracts `<gml-*>` tags, and renders the appropriate React component.

## Acceptance Criteria
- [ ] All 18 MarkupNodeType values render without errors
- [ ] CHART nodes render as Recharts charts (bar, line, pie, etc.)
- [ ] METRIC_CARD nodes render as styled KPI cards with label, value, delta, trend
- [ ] TABLE nodes render as structured HTML tables
- [ ] Citation numbers render as inline superscripts using existing CitationLink.tsx
- [ ] Unknown node types fall back gracefully (render as paragraph)
- [ ] GmlComponentParser extracts `<gml-ViewReport>` from hydrated_content
- [ ] Data fetched from `GET /api/v1/artifacts/{sha256}/content`

## Technical Notes
- Net-new files: `ui/src/components/reports/ReportRenderer.tsx`, `ui/src/types/markup.ts`, `ui/src/components/chat/GmlComponentParser.tsx`
- Chart rendering: recharts (add to package.json if absent)
- Code blocks: react-syntax-highlighter (add if absent)
- Citations: extend existing CitationLink.tsx, do not replace
- See IMPLEMENTATION-PLAN.md Section 3.6 for TypeScript types

## Dependencies
- **Blocked by:** BL-004, BL-005
- **Blocks:** None

## References
- BACKLOG.md: BL-009
- IMPLEMENTATION-PLAN.md: Section 3.6
EOF
)"
```

### Bulk Creation Script

```bash
#!/usr/bin/env bash
# bulk-create-issues.sh
# Creates all 22 BL issues in dependency order (Wave 0 first, then Wave 1, etc.)
# Run from the nyqst-intelli-230126 repository root.
#
# Prerequisites:
#   1. gh CLI authenticated (gh auth status)
#   2. Labels created (run label creation commands above)
#   3. Milestones created (run milestone creation commands above)
#
# Usage: bash bulk-create-issues.sh 2>&1 | tee issue-creation.log

set -euo pipefail

# Map BL-IDs to GitHub issue numbers as they are created
declare -A ISSUE_MAP

create_issue() {
  local bl_id="$1"
  local title="$2"
  local labels="$3"
  local milestone="$4"
  local body="$5"

  echo "Creating issue: ${title}..."
  local issue_url
  issue_url=$(gh issue create \
    --title "${title}" \
    --label "${labels}" \
    --milestone "${milestone}" \
    --body "${body}" \
    2>&1 | tail -1)

  # Extract issue number from URL
  local issue_num
  issue_num=$(echo "${issue_url}" | grep -oE '[0-9]+$')
  ISSUE_MAP["${bl_id}"]="${issue_num}"
  echo "  -> Created #${issue_num} for ${bl_id}"
  sleep 1  # Rate limit courtesy
}

echo "=========================================="
echo "WAVE 0: No dependencies (can start immediately)"
echo "=========================================="

create_issue "BL-002" \
  "[BL-002] RunEvent Schema Extensions" \
  "type:infrastructure,phase:0-foundation,priority:critical-path,track:infrastructure,size:S,status:ready-to-start" \
  "M0: Foundation" \
  "$(cat <<'BODY'
## Overview
Extend RunEvent type enum with 19 new event types for planning, subagent fan-out, content streaming, artifacts, clarification, report progress, and web research.

## Acceptance Criteria
- [ ] 19 new event types in both schemas/runs.py and db/models/runs.py
- [ ] Typed log_* helpers in LedgerService
- [ ] Round-trip through ledger and SSE stream
- [ ] Existing tests unaffected

## Dependencies
- **Blocked by:** None
- **Blocks:** BL-001, BL-007, BL-014, BL-016, BL-020, BL-021
BODY
)"

create_issue "BL-004" \
  "[BL-004] NYQST Markup AST Schema" \
  "type:infrastructure,phase:0-foundation,priority:critical-path,track:deliverables,size:M,status:ready-to-start" \
  "M0: Foundation" \
  "$(cat <<'BODY'
## Overview
Pydantic models for the NYQST Markup AST document tree with 18 node types plus MarkupHealer.

## Acceptance Criteria
- [ ] 18 node types in MarkupNodeType enum
- [ ] MarkupNode, MarkupDocument models
- [ ] MarkupHealer.heal() and validate()
- [ ] Round-trip JSON stability

## Dependencies
- **Blocked by:** None
- **Blocks:** BL-005, BL-009, BL-019
BODY
)"

create_issue "BL-008" \
  "[BL-008] DeliverableSelector Component" \
  "type:frontend,phase:0-foundation,priority:medium,track:frontend,size:S,status:ready-to-start" \
  "M0: Foundation" \
  "$(cat <<'BODY'
## Overview
Segmented control for deliverable type selection (Report|Website|Slides|Document) above the chat composer.

## Acceptance Criteria
- [ ] 4-segment toggle with Lucide icons
- [ ] Syncs to DeliverableStore
- [ ] deliverable_type included in message payload
- [ ] Auto-clears after submission

## Dependencies
- **Blocked by:** BL-015 (weak — DeliverableSelector writes to useDeliverableStore)
- **Blocks:** None
BODY
)"

create_issue "BL-015" \
  "[BL-015] DeliverableStore (Zustand)" \
  "type:frontend,phase:0-foundation,priority:medium,track:frontend,size:XS,status:ready-to-start" \
  "M0: Foundation" \
  "$(cat <<'BODY'
## Overview
6th Zustand store for deliverable selection and generation progress state.

## Acceptance Criteria
- [ ] selectedType, activePreview state shape
- [ ] All action methods typed
- [ ] Compiles, exports correctly

## Dependencies
- **Blocked by:** None
- **Blocks:** None
BODY
)"

create_issue "BL-012" \
  "[BL-012] Billing System" \
  "type:billing,phase:4-billing,priority:high,track:billing,size:L" \
  "M4: Billing & Polish" \
  "$(cat <<'BODY'
## Overview
Stripe billing: checkout, webhooks, subscriptions, usage tracking. Port from okestraai/DocuIntelli.

## Acceptance Criteria
- [ ] Checkout session creation
- [ ] Webhook processing with signature verification
- [ ] Subscription and usage endpoints
- [ ] Usage record per run (not retry)

## Dependencies
- **Blocked by:** MIG-0005C (billing tables)
- **Blocks:** BL-013
BODY
)"

echo ""
echo "=========================================="
echo "WAVE 1: Depends on Wave 0"
echo "=========================================="

create_issue "BL-001" \
  "[BL-001] Research Orchestrator Graph" \
  "type:feature,phase:1-orchestrator,priority:critical-path,track:orchestrator,size:XL,status:blocked" \
  "M1: Orchestrator" \
  "$(cat <<'BODY'
## Overview
Extend ResearchAssistantGraph with planner, Send() fan-out, fan-in, synthesis, and deliverable router.

## Acceptance Criteria
- [ ] Planner -> fan-out -> parallel workers -> fan-in -> synthesis -> deliverable router
- [ ] PLAN_CREATED and SUBAGENT_* events in SSE
- [ ] DataBrief populated in final state
- [ ] Child Runs with parent_run_id
- [ ] Existing tests pass

## Dependencies
- **Blocked by:** BL-002 (#${ISSUE_MAP[BL-002]})
- **Blocks:** BL-003, BL-005, BL-006, BL-017, BL-018, BL-021, BL-022
BODY
)"

create_issue "BL-007" \
  "[BL-007] PlanViewer Component" \
  "type:frontend,phase:3-frontend,priority:high,track:frontend,size:M,status:blocked" \
  "M3: Frontend" \
  "$(cat <<'BODY'
## Overview
Numbered task cards with live status indicators in a Plan tab in DetailsPanel.

## Acceptance Criteria
- [ ] Cards on PLAN_CREATED, live status updates
- [ ] Phase grouping, error tooltips, duration display
- [ ] New Plan tab in DetailsPanel

## Dependencies
- **Blocked by:** BL-002 (#${ISSUE_MAP[BL-002]})
- **Blocks:** None
BODY
)"

create_issue "BL-014" \
  "[BL-014] Enhanced RunTimeline" \
  "type:frontend,phase:3-frontend,priority:medium,track:frontend,size:M,status:blocked" \
  "M3: Frontend" \
  "$(cat <<'BODY'
## Overview
Enhance RunTimeline with icons/labels for 19 new event types, phase grouping, and subagent cards.

## Acceptance Criteria
- [ ] All new event types have icons and labels
- [ ] Phase grouping when PLAN_CREATED present
- [ ] Backward compatible for non-plan runs

## Dependencies
- **Blocked by:** BL-002 (#${ISSUE_MAP[BL-002]})
- **Blocks:** None
BODY
)"

create_issue "BL-020" \
  "[BL-020] Generation Progress Overlay" \
  "type:frontend,phase:3-frontend,priority:high,track:frontend,size:M,status:blocked" \
  "M3: Frontend" \
  "$(cat <<'BODY'
## Overview
Full-screen overlay with dual-status display and progress during deliverable generation.

## Acceptance Criteria
- [ ] Show on REPORT_PREVIEW_START, hide on DONE
- [ ] Phase label updates from DELTA events
- [ ] Async entity "Creating notes..." indicator

## Dependencies
- **Blocked by:** BL-002 (#${ISSUE_MAP[BL-002]})
- **Blocks:** None
BODY
)"

create_issue "BL-016" \
  "[BL-016] Entity/Citation Substrate" \
  "type:feature,phase:2-deliverables,priority:high,track:infrastructure,size:M,status:blocked" \
  "M2: Deliverables" \
  "$(cat <<'BODY'
## Overview
Entity/citation service layer: create entity artifacts from REFERENCES_FOUND events, dedup, per-run entities API.

## Acceptance Criteria
- [ ] create_entity_artifact helper
- [ ] Async creation via arq job
- [ ] GET /api/v1/runs/{run_id}/entities endpoint
- [ ] Citation IDs resolve to entities

## Dependencies
- **Blocked by:** BL-002 (#${ISSUE_MAP[BL-002]}), MIG-0005A (entity_type + tags columns)
- **Blocks:** BL-011

> **Note:** BL-005 is a soft dependency for citation-binding integration testing only.
BODY
)"

echo ""
echo "=========================================="
echo "WAVE 2: Depends on BL-001 and/or BL-004"
echo "=========================================="

create_issue "BL-003" \
  "[BL-003] Web Research MCP Tools" \
  "type:integration,phase:1-orchestrator,priority:critical-path,track:orchestrator,size:M,status:blocked" \
  "M1: Orchestrator" \
  "$(cat <<'BODY'
## Overview
Brave Search and Jina Reader MCP tools for web research with RunEvent emission.

## Acceptance Criteria
- [ ] brave_web_search returns results
- [ ] jina_web_scrape returns cleaned text
- [ ] Both registered in MCP server
- [ ] WEB_SEARCH_*/WEB_SCRAPE_* events emitted

## Dependencies
- **Blocked by:** None (standalone tools); BL-001 (integration wiring into orchestrator)
- **Blocks:** BL-011

> **Note:** Brave/Jina API wrappers can be built and tested independently in Wave 0. Integration into research_worker_node requires BL-001 (Wave 2).
BODY
)"

create_issue "BL-022" \
  "[BL-022] Shared Data Brief" \
  "type:feature,phase:1-orchestrator,priority:high,track:orchestrator,size:S,status:blocked" \
  "M1: Orchestrator" \
  "$(cat <<'BODY'
## Overview
Structured data brief as LangGraph state field for cross-deliverable data consistency.

## Acceptance Criteria
- [ ] DataBrief shape: key_facts, entities, financial_figures, summary
- [ ] Populated by synthesis_node
- [ ] Available in final state
- [ ] Downstream nodes reference without re-fetch

## Dependencies
- **Blocked by:** None (design phase)
- **Blocks:** None

> **Note:** DataBrief schema design must precede BL-001 (feeds into ResearchState). Integration testing requires BL-001.
BODY
)"

create_issue "BL-017" \
  "[BL-017] Meta-Reasoning Node" \
  "type:feature,phase:1-orchestrator,priority:high,track:orchestrator,size:M,status:blocked" \
  "M1: Orchestrator" \
  "$(cat <<'BODY'
## Overview
Research quality evaluator node with recovery dispatch for data gaps and failed tasks.

## Acceptance Criteria
- [ ] Evaluates plan vs results, identifies gaps
- [ ] Dispatches recovery tasks when gaps found
- [ ] Skip heuristic for simple queries
- [ ] Latency < 30s for meta-reasoning call

## Dependencies
- **Blocked by:** BL-001 (#${ISSUE_MAP[BL-001]})
- **Blocks:** None
BODY
)"

create_issue "BL-005" \
  "[BL-005] Report Generation Node" \
  "type:feature,phase:2-deliverables,priority:critical-path,track:deliverables,size:L,status:blocked" \
  "M2: Deliverables" \
  "$(cat <<'BODY'
## Overview
4-pass report generation: outline, parallel sections, review, assembly into MarkupDocument artifact.

## Acceptance Criteria
- [ ] Valid MarkupDocument passing MarkupHealer.validate()
- [ ] Stored as GENERATED_REPORT artifact
- [ ] hydrated_content contains gml-ViewReport
- [ ] Citation IDs reference data brief entities
- [ ] Co-generation for website requests

## Dependencies
- **Blocked by:** BL-001 (#${ISSUE_MAP[BL-001]}), BL-004 (#${ISSUE_MAP[BL-004]}), MIG-0005A
- **Blocks:** BL-016, BL-019, BL-009
BODY
)"

create_issue "BL-006" \
  "[BL-006] Website Generation Pipeline" \
  "type:feature,phase:2-deliverables,priority:high,track:deliverables,size:L,status:blocked" \
  "M2: Deliverables" \
  "$(cat <<'BODY'
## Overview
7-stage website generation producing multi-file HTML/CSS/JS bundle as Manifest with co-generation.

## Acceptance Criteria
- [ ] 7-stage pipeline: planning through bundle
- [ ] Manifest with index.html + styles.css minimum
- [ ] Both gml-ViewWebsite and gml-ViewReport in response
- [ ] entity_type=GENERATED_WEBSITE

## Dependencies
- **Blocked by:** BL-001 (#${ISSUE_MAP[BL-001]}), MIG-0005A
- **Blocks:** BL-010
BODY
)"

create_issue "BL-018" \
  "[BL-018] Slides Deliverable Pipeline" \
  "type:feature,phase:2-deliverables,priority:medium,track:deliverables,size:M,status:blocked" \
  "M2: Deliverables" \
  "$(cat <<'BODY'
## Overview
Slides generation producing reveal.js HTML bundle from research results.

## Acceptance Criteria
- [ ] 4-stage pipeline: outline, content, assembly, storage
- [ ] Valid reveal.js HTML as single artifact
- [ ] entity_type=GENERATED_PRESENTATION

## Dependencies
- **Blocked by:** BL-001 (#${ISSUE_MAP[BL-001]}), MIG-0005A
- **Blocks:** None
BODY
)"

create_issue "BL-021" \
  "[BL-021] Clarification Flow" \
  "type:feature,phase:3-frontend,priority:medium,track:orchestrator,size:M,status:blocked" \
  "M3: Frontend" \
  "$(cat <<'BODY'
## Overview
Mid-run pause/resume via CLARIFICATION_NEEDED events with AsyncPostgresSaver checkpoint.

## Acceptance Criteria
- [ ] CLARIFICATION_NEEDED pauses run
- [ ] POST /api/v1/runs/{run_id}/clarify resumes
- [ ] ClarificationPrompt.tsx in chat UI
- [ ] needs_clarification_message populated

## Dependencies
- **Blocked by:** BL-001 (#${ISSUE_MAP[BL-001]}), BL-002 (#${ISSUE_MAP[BL-002]})
- **Blocks:** None
BODY
)"

create_issue "BL-019" \
  "[BL-019] Document Deliverable (PDF/DOCX Export)" \
  "type:feature,phase:2-deliverables,priority:medium,track:deliverables,size:M,status:blocked" \
  "M2: Deliverables" \
  "$(cat <<'BODY'
## Overview
Export pipeline: MarkupDocument AST to PDF (weasyprint) and DOCX (python-docx).

## Acceptance Criteria
- [ ] POST /api/v1/artifacts/{sha256}/export with format=pdf returns valid PDF
- [ ] format=docx returns valid DOCX
- [ ] Preserves heading hierarchy, tables, charts (as images in PDF)
- [ ] Output stored as new artifact

## Dependencies
- **Blocked by:** BL-004 (#${ISSUE_MAP[BL-004]}), BL-005 (#${ISSUE_MAP[BL-005]})
- **Blocks:** None
BODY
)"

echo ""
echo "=========================================="
echo "WAVE 3: Depends on Wave 2"
echo "=========================================="

create_issue "BL-009" \
  "[BL-009] ReportRenderer Component" \
  "type:frontend,phase:3-frontend,priority:critical-path,track:frontend,size:L,status:blocked" \
  "M3: Frontend" \
  "$(cat <<'BODY'
## Overview
Recursive React renderer for MarkupDocument JSON with 18 node types and GmlComponentParser.

## Acceptance Criteria
- [ ] All 18 node types render
- [ ] Charts via Recharts, code via react-syntax-highlighter
- [ ] Citations via existing CitationLink.tsx
- [ ] GmlComponentParser extracts gml-ViewReport tags

## Dependencies
- **Blocked by:** BL-004 (#${ISSUE_MAP[BL-004]}), BL-005 (#${ISSUE_MAP[BL-005]})
- **Blocks:** None
BODY
)"

create_issue "BL-010" \
  "[BL-010] WebsitePreview Component" \
  "type:frontend,phase:3-frontend,priority:medium,track:frontend,size:M,status:blocked" \
  "M3: Frontend" \
  "$(cat <<'BODY'
## Overview
Website preview via sandboxed iframe loading Manifest bundle as blob URL.

## Acceptance Criteria
- [ ] Fetches Manifest, loads index.html as blob URL
- [ ] Sandboxed iframe rendering
- [ ] Blob URL revoked on unmount
- [ ] Loading state during fetch

## Dependencies
- **Blocked by:** BL-006 (#${ISSUE_MAP[BL-006]})
- **Blocks:** None
BODY
)"

create_issue "BL-011" \
  "[BL-011] Enhanced SourcesPanel" \
  "type:frontend,phase:3-frontend,priority:medium,track:frontend,size:M,status:blocked" \
  "M3: Frontend" \
  "$(cat <<'BODY'
## Overview
Add Web Sources tab to existing SourcesPanel with favicon, title, URL, snippet per source.

## Acceptance Criteria
- [ ] Web Sources tab when WEB_SOURCE entities exist
- [ ] Favicon, title, URL, snippet display
- [ ] Count badge, click-to-open
- [ ] Existing RAG tab unaffected

## Dependencies
- **Blocked by:** BL-003 (#${ISSUE_MAP[BL-003]}), BL-016 (#${ISSUE_MAP[BL-016]})
- **Blocks:** None
BODY
)"

create_issue "BL-013" \
  "[BL-013] Quota Enforcement Middleware" \
  "type:billing,phase:4-billing,priority:high,track:billing,size:S,status:blocked" \
  "M4: Billing & Polish" \
  "$(cat <<'BODY'
## Overview
FastAPI Depends() quota check on run creation: 429 when quota exceeded.

## Acceptance Criteria
- [ ] Free at limit -> 429
- [ ] Pro within limit -> allowed
- [ ] Pro overage tracked
- [ ] No check on read ops

## Dependencies
- **Blocked by:** BL-012 (#${ISSUE_MAP[BL-012]})
- **Blocks:** None
BODY
)"

echo ""
echo "=========================================="
echo "DONE: All 22 issues created"
echo "=========================================="
echo ""
echo "Issue Map:"
for bl_id in $(echo "${!ISSUE_MAP[@]}" | tr ' ' '\n' | sort); do
  echo "  ${bl_id} -> #${ISSUE_MAP[${bl_id}]}"
done
```

---

## 5. GitHub Project Board Structure

### Project Setup

Create a GitHub Projects (v2) board named **"Superagent Parity"** in the repository.

### Custom Fields

| Field Name | Field Type | Options |
|------------|-----------|---------|
| Status | Single select | Backlog, Ready, In Progress, In Review, Done, Blocked |
| Phase | Single select | 0-Foundation, 1-Orchestrator, 2-Deliverables, 3-Frontend, 4-Billing |
| Track | Single select | Orchestrator, Frontend, Billing, Deliverables, Infrastructure |
| Size | Number | 1, 2, 3, 5, 8 (story points) |
| Priority | Single select | Critical Path, High, Medium, Low |
| Wave | Number | 0, 1, 2, 3 (dependency wave) |
| BL-ID | Text | BL-001 through BL-022 |

### Views

#### View 1: Sprint Board (default)
- **Layout:** Board
- **Group by:** Status
- **Columns:** Backlog | Ready | In Progress | In Review | Done | Blocked
- **Sort within columns:** Priority (Critical Path first), then Size (largest first)
- **Filter:** None (shows all)

#### View 2: By Phase
- **Layout:** Board
- **Group by:** Phase
- **Columns:** 0-Foundation | 1-Orchestrator | 2-Deliverables | 3-Frontend | 4-Billing
- **Sort within columns:** Priority, then Size
- **Use case:** Sprint planning -- see what is in each milestone

#### View 3: By Track
- **Layout:** Board
- **Group by:** Track
- **Columns:** Orchestrator | Frontend | Billing | Deliverables | Infrastructure
- **Sort within columns:** Phase (ascending), then Priority
- **Use case:** Team assignment -- each dev owns a track

#### View 4: Dependency Map
- **Layout:** Table
- **Columns visible:** BL-ID, Title, Status, Wave, Phase, Blocked By (text field), Priority
- **Sort:** Wave (ascending), then Priority
- **Filter:** Status != Done
- **Use case:** Identify what can start next, what is blocked

#### View 5: Burndown (By Size)
- **Layout:** Table
- **Columns visible:** BL-ID, Title, Size, Status, Phase
- **Group by:** Status
- **Use case:** Track total story points remaining per status

### Automation Rules

| Trigger | Action |
|---------|--------|
| Issue added to project | Set Status = "Backlog" |
| Pull request linked to issue | Set Status = "In Progress" |
| Pull request marked ready for review | Set Status = "In Review" |
| Pull request merged | Set Status = "Done" |
| Label `status:blocked` added | Set Status = "Blocked" |
| Label `status:blocked` removed | Set Status = "Ready" |
| Label `status:ready-to-start` added | Set Status = "Ready" |

### Setup Commands

```bash
# Create the project (v2)
gh project create --title "Superagent Parity" --owner $(gh repo view --json owner -q '.owner.login')

# Note: Custom fields and views must be configured via the GitHub web UI
# or the GraphQL API. The gh CLI does not yet support project field creation.
# See: https://docs.github.com/en/issues/planning-and-tracking-with-projects
```

---

## 6. Dependency Tracking Strategy

### Approach: Multi-Layer Dependency Tracking

GitHub Issues does not have native dependency enforcement. We use three complementary strategies:

#### Layer 1: Issue Body "Dependencies" Section

Every issue includes a structured Dependencies section:

```markdown
## Dependencies
- **Blocked by:** #12, #15 (BL-002, BL-004)
- **Blocks:** #18, #22 (BL-005, BL-019)
```

GitHub auto-links issue numbers, making cross-navigation easy.

#### Layer 2: Task Lists in Milestone Epic Issues

Create one "epic" tracking issue per milestone that uses task lists to track constituent issues:

```bash
gh issue create \
  --title "[EPIC] M1: Orchestrator" \
  --label "type:docs" \
  --milestone "M1: Orchestrator" \
  --body "$(cat <<'EOF'
## Phase 1: Research Orchestrator (Weeks 3-5)

### Wave 1 (unblocked after BL-002)
- [ ] #XX [BL-001] Research Orchestrator Graph

### Wave 2 (unblocked after BL-001)
- [ ] #XX [BL-003] Web Research MCP Tools
- [ ] #XX [BL-022] Shared Data Brief
- [ ] #XX [BL-017] Meta-Reasoning Node

### Completion Criteria
- [ ] SSE stream shows full PLAN_CREATED -> SUBAGENT_* -> synthesis flow
- [ ] DataBrief populated in final graph state
- [ ] Meta-reasoning fires for complex queries, skips for simple
- [ ] All integration tests passing
EOF
)"
```

Create 5 epic issues (one per milestone). As issues are completed, check them off in the epic. The task list progress bar provides at-a-glance milestone completion tracking.

#### Layer 3: "Blocked by" Label Discipline

- When an issue's dependencies are NOT all closed, apply `status:blocked` label
- When all blocking issues close, remove `status:blocked` and apply `status:ready-to-start`
- This can be partially automated via GitHub Actions:

```yaml
# .github/workflows/dependency-check.yml
name: Dependency Check
on:
  issues:
    types: [closed]
jobs:
  unblock:
    runs-on: ubuntu-latest
    steps:
      - name: Check if closing this unblocks others
        uses: actions/github-script@v7
        with:
          script: |
            // Parse all open issues for "Blocked by: #N" references
            // If #N matches the just-closed issue, check if ALL blockers are now closed
            // If so, remove status:blocked and add status:ready-to-start
            // (Implementation left as exercise -- or use a community action)
```

#### Layer 4: PR-to-Issue Auto-Close

Use conventional branch naming and PR body references:

```
Branch: feat/BL-002-runevent-schema
PR body: Closes #12
```

When the PR merges, GitHub auto-closes #12 and the dependency check workflow fires.

#### Layer 5: Wave-Based Work Ordering

The `Wave` field on the project board provides a simple numeric ordering:

| Wave | Issues | Can Start When |
|------|--------|----------------|
| 0 | BL-002, BL-004, BL-008, BL-015, BL-012, BL-022 (design), BL-003 (API wrapper) | Immediately |
| 1 | BL-001, BL-007, BL-014, BL-020, BL-016 | Wave 0 items they depend on are done |
| 2 | BL-003 (integration), BL-017, BL-005, BL-006, BL-018, BL-021, BL-019 | Wave 0-1 items they depend on are done |
| 3 | BL-009, BL-010, BL-011, BL-013 | Wave 0-2 items they depend on are done |

In sprint planning, only pull from the lowest available wave with unblocked items.

### Dependency Graph Summary

```
Wave 0 (no deps or design-phase only):
  BL-002 ──┬──────────────────────────────────────────────────────┐
  BL-004 ──┤                                                      │
  BL-008   │ (weak dep on BL-015)                                 │
  BL-015   │ (independent)                                        │
  BL-012 ──┤ (needs Mig-0005c)                                    │
  BL-022   │ (design phase; integration wiring needs BL-001)      │
  BL-003   │ (API wrappers; integration wiring needs BL-001)      │
            │                                                      │
Wave 1:     │                                                      │
  BL-001 ◄─┤ (needs BL-002)                                      │
  BL-007 ◄─┤ (needs BL-002)                                      │
  BL-014 ◄─┤ (needs BL-002)                                      │
  BL-020 ◄─┤ (needs BL-002)                                      │
  BL-016 ◄─┤ (needs BL-002 + Mig-0005a)                          │
            │                                                      │
Wave 2:     │                                                      │
  BL-003 ◄─┤ (integration: needs BL-001)                         │
  BL-017 ◄─┤ (needs BL-001)                                      │
  BL-005 ◄─┤ (needs BL-001, BL-004, Mig-0005a)                   │
  BL-006 ◄─┤ (needs BL-001, Mig-0005a)                           │
  BL-018 ◄─┤ (needs BL-001, Mig-0005a)                           │
  BL-021 ◄─┤ (needs BL-001, BL-002)                              │
  BL-019 ◄─┤ (needs BL-004, BL-005)                              │
            │                                                      │
Wave 3:     │                                                      │
  BL-009 ◄──── (needs BL-004, BL-005)                            │
  BL-010 ◄──── (needs BL-006)                                    │
  BL-011 ◄──── (needs BL-003, BL-016)                            │
  BL-013 ◄──── (needs BL-012)                                    │
```

**Note on BL-016:** It depends on BL-002 (Wave 0) and MIG-0005A (Wave 0). BL-005 is a soft dependency for citation-binding integration testing only; service layer work can begin after BL-002 + Mig-0005a. In practice, treat as two sub-phases.

**Note on BL-003:** API wrappers (Brave/Jina) can be built and tested in Wave 0. Integration into research_worker_node requires BL-001 (Wave 2).

**Note on BL-022:** DataBrief schema design is Wave 0 (feeds into ResearchState design). Integration testing requires BL-001.

---

## 7. Machine-Readable Index

```json
{
  "metadata": {
    "document_id": "GIT-ISSUES",
    "version": 1,
    "date": "2026-02-18",
    "target_repo": "nyqst-intelli-230126",
    "total_issues": 22,
    "total_story_points": 72
  },
  "milestones": [
    {"id": "M0", "title": "M0: Foundation", "due_date": "2026-03-14", "story_points": 5},
    {"id": "M1", "title": "M1: Orchestrator", "due_date": "2026-04-04", "story_points": 16},
    {"id": "M2", "title": "M2: Deliverables", "due_date": "2026-04-25", "story_points": 18},
    {"id": "M3", "title": "M3: Frontend", "due_date": "2026-05-16", "story_points": 23},
    {"id": "M4", "title": "M4: Billing & Polish", "due_date": "2026-05-30", "story_points": 7}
  ],
  "issues": [
    {
      "bl_id": "BL-001",
      "title": "[BL-001] Research Orchestrator Graph",
      "labels": ["type:feature", "phase:1-orchestrator", "priority:critical-path", "track:orchestrator", "size:XL"],
      "milestone": "M1",
      "size_points": 8,
      "wave": 1,
      "blocked_by": ["BL-002"],
      "blocks": ["BL-003", "BL-005", "BL-006", "BL-017", "BL-018", "BL-021", "BL-022"],
      "has_sub_issues": true,
      "sub_issue_count": 5
    },
    {
      "bl_id": "BL-002",
      "title": "[BL-002] RunEvent Schema Extensions",
      "labels": ["type:infrastructure", "phase:0-foundation", "priority:critical-path", "track:infrastructure", "size:S"],
      "milestone": "M0",
      "size_points": 2,
      "wave": 0,
      "blocked_by": [],
      "blocks": ["BL-001", "BL-007", "BL-014", "BL-016", "BL-020", "BL-021"],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-003",
      "title": "[BL-003] Web Research MCP Tools",
      "labels": ["type:integration", "phase:1-orchestrator", "priority:critical-path", "track:orchestrator", "size:M"],
      "milestone": "M1",
      "size_points": 3,
      "wave": 2,
      "blocked_by": ["BL-001 (integration only)"],
      "blocks": ["BL-011"],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-004",
      "title": "[BL-004] NYQST Markup AST Schema",
      "labels": ["type:infrastructure", "phase:0-foundation", "priority:critical-path", "track:deliverables", "size:M"],
      "milestone": "M0",
      "size_points": 3,
      "wave": 0,
      "blocked_by": [],
      "blocks": ["BL-005", "BL-009", "BL-019"],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-005",
      "title": "[BL-005] Report Generation Node",
      "labels": ["type:feature", "phase:2-deliverables", "priority:critical-path", "track:deliverables", "size:L"],
      "milestone": "M2",
      "size_points": 5,
      "wave": 2,
      "blocked_by": ["BL-001", "BL-004", "Migration-0005a"],
      "blocks": ["BL-016", "BL-019", "BL-009"],
      "has_sub_issues": true,
      "sub_issue_count": 3
    },
    {
      "bl_id": "BL-006",
      "title": "[BL-006] Website Generation Pipeline",
      "labels": ["type:feature", "phase:2-deliverables", "priority:high", "track:deliverables", "size:L"],
      "milestone": "M2",
      "size_points": 5,
      "wave": 2,
      "blocked_by": ["BL-001", "Migration-0005a"],
      "blocks": ["BL-010"],
      "has_sub_issues": true,
      "sub_issue_count": 3
    },
    {
      "bl_id": "BL-007",
      "title": "[BL-007] PlanViewer Component",
      "labels": ["type:frontend", "phase:3-frontend", "priority:high", "track:frontend", "size:M"],
      "milestone": "M3",
      "size_points": 3,
      "wave": 1,
      "blocked_by": ["BL-002"],
      "blocks": [],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-008",
      "title": "[BL-008] DeliverableSelector Component",
      "labels": ["type:frontend", "phase:0-foundation", "priority:medium", "track:frontend", "size:S"],
      "milestone": "M0",
      "size_points": 2,
      "wave": 0,
      "blocked_by": ["BL-015 (weak)"],
      "blocks": [],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-009",
      "title": "[BL-009] ReportRenderer Component",
      "labels": ["type:frontend", "phase:3-frontend", "priority:critical-path", "track:frontend", "size:L"],
      "milestone": "M3",
      "size_points": 5,
      "wave": 3,
      "blocked_by": ["BL-004", "BL-005"],
      "blocks": [],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-010",
      "title": "[BL-010] WebsitePreview Component",
      "labels": ["type:frontend", "phase:3-frontend", "priority:medium", "track:frontend", "size:M"],
      "milestone": "M3",
      "size_points": 3,
      "wave": 3,
      "blocked_by": ["BL-006"],
      "blocks": [],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-011",
      "title": "[BL-011] Enhanced SourcesPanel",
      "labels": ["type:frontend", "phase:3-frontend", "priority:medium", "track:frontend", "size:M"],
      "milestone": "M3",
      "size_points": 3,
      "wave": 3,
      "blocked_by": ["BL-003", "BL-016"],
      "blocks": [],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-012",
      "title": "[BL-012] Billing System",
      "labels": ["type:billing", "phase:4-billing", "priority:high", "track:billing", "size:L"],
      "milestone": "M4",
      "size_points": 5,
      "wave": 0,
      "blocked_by": ["Migration-0005c"],
      "blocks": ["BL-013"],
      "has_sub_issues": true,
      "sub_issue_count": 4
    },
    {
      "bl_id": "BL-013",
      "title": "[BL-013] Quota Enforcement Middleware",
      "labels": ["type:billing", "phase:4-billing", "priority:high", "track:billing", "size:S"],
      "milestone": "M4",
      "size_points": 2,
      "wave": 3,
      "blocked_by": ["BL-012"],
      "blocks": [],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-014",
      "title": "[BL-014] Enhanced RunTimeline",
      "labels": ["type:frontend", "phase:3-frontend", "priority:medium", "track:frontend", "size:M"],
      "milestone": "M3",
      "size_points": 3,
      "wave": 1,
      "blocked_by": ["BL-002"],
      "blocks": [],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-015",
      "title": "[BL-015] DeliverableStore (Zustand)",
      "labels": ["type:frontend", "phase:0-foundation", "priority:medium", "track:frontend", "size:XS"],
      "milestone": "M0",
      "size_points": 1,
      "wave": 0,
      "blocked_by": [],
      "blocks": [],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-016",
      "title": "[BL-016] Entity/Citation Substrate",
      "labels": ["type:feature", "phase:2-deliverables", "priority:high", "track:infrastructure", "size:M"],
      "milestone": "M2",
      "size_points": 3,
      "wave": 1,
      "blocked_by": ["BL-002", "Migration-0005a"],
      "blocks": ["BL-011"],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-017",
      "title": "[BL-017] Meta-Reasoning Node",
      "labels": ["type:feature", "phase:1-orchestrator", "priority:high", "track:orchestrator", "size:M"],
      "milestone": "M1",
      "size_points": 3,
      "wave": 2,
      "blocked_by": ["BL-001"],
      "blocks": [],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-018",
      "title": "[BL-018] Slides Deliverable Pipeline",
      "labels": ["type:feature", "phase:2-deliverables", "priority:medium", "track:deliverables", "size:M"],
      "milestone": "M2",
      "size_points": 3,
      "wave": 2,
      "blocked_by": ["BL-001", "Migration-0005a"],
      "blocks": [],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-019",
      "title": "[BL-019] Document Deliverable (PDF/DOCX Export)",
      "labels": ["type:feature", "phase:2-deliverables", "priority:medium", "track:deliverables", "size:M"],
      "milestone": "M2",
      "size_points": 3,
      "wave": 2,
      "blocked_by": ["BL-004", "BL-005"],
      "blocks": [],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-020",
      "title": "[BL-020] Generation Progress Overlay",
      "labels": ["type:frontend", "phase:3-frontend", "priority:high", "track:frontend", "size:M"],
      "milestone": "M3",
      "size_points": 3,
      "wave": 1,
      "blocked_by": ["BL-002"],
      "blocks": [],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-021",
      "title": "[BL-021] Clarification Flow",
      "labels": ["type:feature", "phase:3-frontend", "priority:medium", "track:orchestrator", "size:M"],
      "milestone": "M3",
      "size_points": 3,
      "wave": 2,
      "blocked_by": ["BL-001", "BL-002"],
      "blocks": [],
      "has_sub_issues": false,
      "sub_issue_count": 0
    },
    {
      "bl_id": "BL-022",
      "title": "[BL-022] Shared Data Brief",
      "labels": ["type:feature", "phase:1-orchestrator", "priority:high", "track:orchestrator", "size:S"],
      "milestone": "M1",
      "size_points": 2,
      "wave": 0,
      "blocked_by": [],
      "blocks": [],
      "has_sub_issues": false,
      "sub_issue_count": 0
    }
  ],
  "waves": {
    "0": ["BL-002", "BL-004", "BL-008", "BL-015", "BL-012", "BL-022", "BL-003 (API wrapper)"],
    "1": ["BL-001", "BL-007", "BL-014", "BL-020", "BL-016"],
    "2": ["BL-003 (integration)", "BL-017", "BL-005", "BL-006", "BL-018", "BL-021", "BL-019"],
    "3": ["BL-009", "BL-010", "BL-011", "BL-013"]
  },
  "critical_path": ["BL-002", "BL-001", "BL-005", "BL-009"],
  "story_points_by_milestone": {
    "M0": 5,
    "M1": 16,
    "M2": 19,
    "M3": 23,
    "M4": 7
  },
  "story_points_by_track": {
    "orchestrator": 19,
    "frontend": 23,
    "billing": 7,
    "deliverables": 19,
    "infrastructure": 5
  }
}
```

---

## Appendix A: Complete Dependency Matrix

| BL-ID | Blocked By | Blocks | Wave | Phase | Size |
|-------|-----------|--------|------|-------|------|
| BL-001 | BL-002 | BL-003, BL-005, BL-006, BL-017, BL-018, BL-021, BL-022 | 1 | 1 | XL(8) |
| BL-002 | -- | BL-001, BL-007, BL-014, BL-016, BL-020, BL-021 | 0 | 0 | S(2) |
| BL-003 | None (standalone); BL-001 (integration) | BL-011 | 0/2 | 1 | M(3) |
| BL-004 | -- | BL-005, BL-009, BL-019 | 0 | 0 | M(3) |
| BL-005 | BL-001, BL-004, Mig-0005a | BL-016, BL-019, BL-009 | 2 | 2 | L(5) |
| BL-006 | BL-001, Mig-0005a | BL-010 | 2 | 2 | L(5) |
| BL-007 | BL-002 | -- | 1 | 3 | M(3) |
| BL-008 | BL-015 (weak) | -- | 0 | 0 | S(2) |
| BL-009 | BL-004, BL-005 | -- | 3 | 3 | L(5) |
| BL-010 | BL-006 | -- | 3 | 3 | M(3) |
| BL-011 | BL-003, BL-016 | -- | 3 | 3 | M(3) |
| BL-012 | Mig-0005c | BL-013 | 0 | 4 | L(5) |
| BL-013 | BL-012 | -- | 3 | 4 | S(2) |
| BL-014 | BL-002 | -- | 1 | 3 | M(3) |
| BL-015 | -- | -- | 0 | 0 | XS(1) |
| BL-016 | BL-002, Mig-0005a | BL-011 | 1* | 2 | M(3) |
| BL-017 | BL-001 | -- | 2 | 1 | M(3) |
| BL-018 | BL-001, Mig-0005a | -- | 2 | 2 | M(3) |
| BL-019 | BL-004, BL-005 | -- | 2 | 2 | M(3) |
| BL-020 | BL-002 | -- | 1 | 3 | M(3) |
| BL-021 | BL-001, BL-002 | -- | 2 | 3 | M(3) |
| BL-022 | None (design phase) | -- | 0 | 1 | S(2) |

*BL-016 is Wave 1 for the service scaffolding (needs BL-002 only) but Wave 2+ for citation binding (needs BL-005). In practice, start early and complete after BL-005 lands.

**Totals:** 22 issues, 70 story points across 5 milestones and 4 dependency waves.

---

## Appendix B: Quick Reference Card

### Sprint Planning Checklist

1. Check milestone due date -- are we on track?
2. Look at Wave 0/1/2/3 -- what is unblocked?
3. Look at critical path items first (BL-002 -> BL-001 -> BL-005 -> BL-009)
4. Assign by track: orchestrator dev gets BL-001/003/017/022, frontend dev gets BL-007/008/009/010, etc.
5. Check `status:blocked` label -- anything newly unblocked?
6. Update epic tracking issues with checkmarks

### Branch Naming Convention

```
feat/BL-002-runevent-schema
feat/BL-001a-research-state-extension
feat/BL-005-report-generation
fix/BL-009-chart-rendering
```

### PR Title Convention

```
feat(BL-002): add 19 new RunEvent types to schema
feat(BL-001): extend research orchestrator with fan-out
fix(BL-009): handle unknown node types in ReportRenderer
```

### PR Body Convention

```markdown
## Summary
[What changed and why]

## Backlog Item
Closes #XX (BL-YYY)

## Testing
- [ ] Unit tests added/updated
- [ ] Integration test passes
- [ ] Existing tests unaffected

## Dependencies
Unblocks: #AA (BL-ZZZ), #BB (BL-WWW)
```