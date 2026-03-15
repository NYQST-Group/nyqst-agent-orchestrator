# Codex Team Config

This directory is the repo-local Codex configuration used by AO-managed workers in
`nyqst-agent-orchestrator`.

What lives here:

- `config.toml`: shared profiles for orchestrator, worker, and research lanes
- `managed_config.toml`: repo-managed defaults
- `requirements.toml`: guardrails for supported sandbox / approval modes
- `ao-worker-rules.md`: extra AO worker behavior layered on top of `ao-agent-rules.md`

The same files are also synced into dedicated `CODEX_HOME` directories for the AO
runner lanes by `tools/sync_codex_team_config.sh`.
