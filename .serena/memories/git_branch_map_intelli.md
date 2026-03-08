# Git Branch Map — nyqst-intelli-230126

**Remote:** `https://github.com/NYQST-Group/NYQST-DocuIntelli-Build.git`

## Active Branches

| Branch | Base | Status | Content |
|--------|------|--------|---------|
| `origin/main` | — | Merged PRs #1-3 | PRDs, ADRs 001-009, build plan. No app code. |
| `origin/devin/..-track-a-week1-agent-chat` | main | Synced | Full app: LangGraph research assistant, AI SDK adapter, UI with agent chat, doc intelligence |
| `origin/fix/ai-sdk-v3-sse-streaming` | devin agent-chat | **NEW - pushed 2026-01-31** | v3 SSE streaming fix + tour/demo mode |

## Unmerged Work Worth Keeping

| Branch | Lines Added | Content | Mergeable? |
|--------|-------------|---------|------------|
| `origin/claude/review-and-build-async-D5DLE` | 16,212 | Events calendar, verification UI, backend services, repos, migrations, 9 test files with factories | Yes — no conflicts with agent-chat |
| `origin/codex/..devcontainer-ai-sdk-v3-fix` | 1,510 | Devcontainer setup + inferior v3 fix attempt (still uses v2 protocol on backend) | Cherry-pick .devcontainer/ and scripts/dev/ only |

## Research/Archive

| Branch | Content | Action |
|--------|---------|--------|
| `origin/claude/agent-first-doc-intelligence-*` | Full Phase 0 rewrite (deleted 60k lines, added 15k). Has useful storage abstraction, workbench viewers | Cherry-pick selectively, don't merge |
| `origin/claude/async-ui-components-*` | Standalone component library prototype (evidence canvas, provenance graph) | Tag and archive |
| `origin/claude/cre-intelligence-workflows-*` | Pure domain research: CRE schemas, RICS/INREV, personas, workflows (20k lines) | Move to NYQST-MCP research repo |

## Delete

| Branch | Reason |
|--------|--------|
| `origin/claude/platform-foundation-adrs-*` | Already merged into main via PR #3 |
| `origin/demo-clean` | Tagged as `milestone-demo-clean-2026-01-24`, branch not needed |
| `origin/demo-working-2026-01-24` | Tagged as `milestone-demo-working-2026-01-24`, branch not needed |
| `origin/merged-branch` | Stale |

## Tags

- `milestone-demo-clean-2026-01-24`
- `milestone-demo-working-2026-01-24`
