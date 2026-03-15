# AO Codex Worker Rules

You are running as an AO-managed Codex worker in the `nyqst-agent-orchestrator`
repo.

## Operating rules

- Start from the linked GitHub issue and any linked spec or packet note before
  changing code.
- In a fresh worktree, run `./tools/bootstrap_worktree.sh` before tests or lint.
- Keep the change bounded to the issue objective and acceptance criteria.
- Prefer repo-documented behavior over chat-only assumptions.
- Do not introduce Codex API-key auth. Runner auth is ChatGPT OAuth on the host.
- Record what you verified in the PR or issue update, not only in terminal
  output.
- After opening a PR, run `ao session claim-pr <pr-number-or-url>` before you
  stop. AO uses that claim to keep the session, dashboard, CI loop, and review
  routing attached to the right PR.

## Learning mode

- If the issue is marked as an experiment, preserve the stated hypothesis and
  success metric.
- When you discover something reusable, capture it in docs or the issue/PR
  narrative.
- When a path fails, record it clearly so the same dead end is not retried.

## Coordination

- If the work changes repo truth, update the canonical doc or contract.
- If the work is incomplete, leave a clean handoff with blockers and next steps.
