---
    key: STORY-AGENT-002
    title: MCP integration: stdio tool runner + sandboxed HTTP
    type: story
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:high, size:L, track:agents, type:story]
    ---

    ## Problem

    MCP provides hot-swappable tool providers; it must be safe and predictable.

    ## Proposed solution

    Implement MCP tool runner with stdio transport; wrap HTTP client with allowlist/timeouts/rate limits; capture tool I/O as run events.

    ## Dependencies

    - STORY-AGENT-001 — Backend: skill registry + permissions + versioning

    ## Acceptance criteria

    - [ ] MCP tool processes can be started and invoked
- [ ] Tool invocation emits TOOL_CALL_* events with redaction
- [ ] HTTP is sandboxed (timeouts, size limits)
- [ ] Failure surfaces as WARNING/ERROR events without crashing run

    ## Test plan

    - [ ] Integration: invoke a test MCP tool
- [ ] Security test: SSRF attempt blocked

    ## Notes / references

    _None_
