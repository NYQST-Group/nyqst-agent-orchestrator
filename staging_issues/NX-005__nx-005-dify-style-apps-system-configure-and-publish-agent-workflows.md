# [NX-005] Dify-style “Apps” system (configure and publish agent workflows)

**Goal**
Allow non-engineers to configure and publish an “App”:
- choose base agent graph template
- configure tools + permissions
- attach knowledge bases (pointers)
- set input schema (form)
- define output type (deliverable)
- publish versioned app; run it inside projects

**Key design decisions**
- Apps are versioned manifests/pointers (don’t invent new storage).
- Apps run through the same Run ledger + event stream.
- Apps should be exportable/importable (JSON).

**Implementation**
Backend:
- `apps` table (tenant_id, name, description, latest_version_pointer_id, status)
- `app_versions` as manifests (or explicit table)
- API: create/version/publish/run
Frontend:
- Apps library + App builder:
  - “Configure” screen (tools/knowledge/output)
  - “Run app” screen (inputs + run timeline + deliverable panel)

**Acceptance criteria**
- Can publish an app and run it repeatedly with different inputs.
- Runs are reproducible: rerunning the same app version + inputs yields the same plan structure (within model stochasticity).

