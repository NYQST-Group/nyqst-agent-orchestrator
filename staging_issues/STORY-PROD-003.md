---
    key: STORY-PROD-003
    title: Security baseline: rate limits, payload size limits, SSRF protections
    type: story
    milestone: M10 Production hardening
    labels: [phase:8-prod, priority:high, size:M, track:infra, type:story]
    ---

    ## Problem

    Doc uploads and web tools create high-risk attack surfaces.

    ## Proposed solution

    Implement rate limiting, request size limits, strict URL validation and timeouts for outbound requests.

    ## Dependencies

    - EPIC-PROD — Production hardening (deploy, security, observability, perf)
- STORY-AGENT-002 — MCP integration: stdio tool runner + sandboxed HTTP

    ## Acceptance criteria

    - [ ] Upload size limits enforced and configurable
- [ ] Rate limiting enabled on expensive endpoints
- [ ] Outbound HTTP blocks private IP ranges and disallowed schemes

    ## Test plan

    - [ ] Security tests for SSRF and rate limits

    ## Notes / references

    _None_
