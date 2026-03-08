# [NX-001] Skills framework v1 (registry, versioning, permissions)

**Inspiration**
- “Skills” in products like Claude/Cowork are essentially: packaged toolchains + permissions + a context bundle.
- NYQST already has primitives to do this (MCP tools, pointers, manifests, runs). This issue makes them first-class.

**Goal**
- Define, store, and run “skills” as versioned assets:
  - A skill declares required tools, allowed connectors, default prompts, and optional UI surfaces.
  - A skill can be attached to a project/workspace and used by agents.

**Scope**
Backend:
- Skill model + migrations:
  - `skills` (id, tenant_id, name, description, version, manifest_pointer_id, permissions JSON, created_by, created_at)
  - `skill_versions` (optional if versions are manifests)
- CRUD API:
  - list/create/update/publish (publish = pin a version)
- Permission model:
  - explicit allowlist of tools/connectors; no implicit access.

Frontend:
- Skills library page:
  - list skills, view versions, publish/unpublish
- Skill detail page:
  - show tools, permissions, linked knowledge pointers, test-run button

**Acceptance criteria**
- You can create a skill, version it, and attach it to a run.
- A run fails fast if a skill requests a tool that is not permitted.
- Skills are tenant-scoped; cross-tenant access blocked.

**References**
- Repo PRD docs under `docs/prd/` (skills + platform primitives).
