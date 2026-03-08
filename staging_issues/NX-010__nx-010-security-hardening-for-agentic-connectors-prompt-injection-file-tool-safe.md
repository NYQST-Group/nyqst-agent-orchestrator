# [NX-010] Security hardening for agentic connectors (prompt injection + file/tool safety)

**Goal**
As the system becomes more agentic (Cowork-like), enforce safety controls:
- least privilege tool permissions
- content security for retrieved web/doc content (prompt injection stripping)
- explicit confirmation for destructive actions
- audit log for every tool invocation

**Implementation**
- Add a “tool firewall” layer:
  - allow/deny, rate limits, sensitive scopes
- Add prompt-injection mitigations:
  - sanitize tool outputs (especially web)
  - separate instruction channels
- Add “destructive action confirmation” events and UI confirmations.

**Acceptance criteria**
- Disallowed tools cannot be invoked even if the model tries.
- Destructive actions require user approval and leave an audit trail.

