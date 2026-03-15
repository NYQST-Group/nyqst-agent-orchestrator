# AO + Codex Pipeline Runbook

This repo supports an AO-managed Codex delivery flow. The product runtime does
not depend on AO; AO is the development execution layer for issue-driven work.

## Supported execution model

- GitHub issues are the task source
- AO manages worktrees, sessions, and PR loops
- Codex is the default orchestrator and worker agent
- Codex auth uses ChatGPT OAuth, not API keys
- AO uses the authenticated `~/.codex` home plus repo-local profiles and `fastMode`

## Required host software

- `ao`
- `codex`
- `gh`
- `git`
- `tmux`
- `node`
- `pnpm`
- `python3`
- Docker Desktop or Docker Engine for the main product stack

## One-time local bootstrap

From the repo root:

```bash
./tools/bootstrap_ao_codex.sh
```

This will:

1. verify `gh auth status`
2. verify `codex login status` reports ChatGPT OAuth
3. run `ao doctor` against this repo config
4. bootstrap the repo worktree dependencies
5. smoke-test the orchestrator and worker profiles

## Daily usage

```bash
AO_CONFIG_PATH=$PWD/agent-orchestrator.yaml ao status --json
AO_CONFIG_PATH=$PWD/agent-orchestrator.yaml ao spawn nyqst <issue-number>
```

Use `--decompose` only when the issue is intentionally broad.

When a worker opens a PR, it must register that PR back to AO from inside the
worktree:

```bash
ao session claim-pr <pr-number-or-url>
```

That keeps the dashboard state, CI handling, and review routing attached to the
correct session instead of leaving it in `working`.

## Expected issue shape

Use the repo issue forms. Every AO-driven issue should include:

- exact outcome or problem statement
- bounded surface area
- spec or source links
- acceptance criteria
- non-goals or out-of-scope notes
- one-PR rule

For experiment issues also include:

- hypothesis
- variant or approach
- success metric
- abandon rule
- expected learning

## Recovery

If the local AO path drifts:

```bash
./tools/ao_doctor_local.sh
gh auth status
codex login status
```

If Codex starts without the expected profile or lane:

- re-run `./tools/bootstrap_ao_codex.sh`
- verify the `codexHome` and `profile` fields in `agent-orchestrator.yaml`
- verify `codex login status` still resolves against `~/.codex`

## Worktree bootstrap

Fresh AO worktrees do not inherit `.venv` or `ui/node_modules`. Before running
repo checks in a new worktree:

```bash
./tools/bootstrap_worktree.sh
./tools/run_repo_checks.sh
```

## Non-goals

- no Codex API-key auth
- no hidden per-user shell setup as repo truth
- no blank GitHub issues for AO packets when a structured template exists
