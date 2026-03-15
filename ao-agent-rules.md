# AO Agent Rules

## Workflow selection

- Use the `fullstack-code-development` workflow by default when an issue spans multiple layers such as backend, frontend, contracts, persistence, workers, or deployment behavior.
- If the issue is clearly single-surface, stay scoped to that surface rather than widening the change.

## Repo-first context

- Read `docs/START_HERE.md` before substantial work.
- Read `.codex/ao-worker-rules.md` when running as an AO worker.
- In a fresh worktree, run `./tools/bootstrap_worktree.sh` before repo checks.
- Use the issue body and linked docs as the primary task contract.
- Prefer canonical docs under `docs/` and `YOLO1/docs/execution/` over older analysis notes when they disagree.

## Delivery rules

- Keep changes bounded to the issue acceptance criteria.
- Preserve contract-first behavior when changing APIs, schemas, or event payloads.
- If a change spans backend and UI, carry it through end to end rather than stopping at one layer.
- Leave a clear handoff in the PR or issue comment when the work is incomplete.
- Prefer the structured issue templates over ad-hoc issue bodies for new AO work.
- After creating a PR, immediately run `ao session claim-pr <pr-number-or-url>` from inside the AO worktree so the session metadata, dashboard, and follow-up review routing stay attached to the correct PR.
