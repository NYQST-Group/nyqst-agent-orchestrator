# ADR-003: Virtual Team Architecture for AI Agent Coordination

**Status:** Proposed  
**Date:** 2026-01-26  
**Deciders:** Mark Forster, Engineering Team  
**PRD Reference:** [03_PLATFORM.md](../prd/03_PLATFORM.md), [06_ARCHITECTURE.md](../prd/06_ARCHITECTURE.md)

---

## Context

NYQST needs to run multiple AI coding agents (Devin, Claude Code, GitHub Copilot, Cursor) as a coordinated virtual development team. Each agent has different capabilities, workflows, and conventions. Without coordination infrastructure, agents will:

- Generate inconsistent code (different naming, patterns, styles)
- Conflict on the same files/features
- Duplicate work
- Lack context about project decisions and conventions
- Have no way to ask questions or escalate issues

The challenge is to create infrastructure that enables async development while maintaining consistency and avoiding conflicts.

---

## Decision

Implement a **Virtual Team Operating System** with four components:

1. **Engineering Playbook (Confluence)** - Single source of truth for operational knowledge
2. **Agent Coordination Layer** - Project registry, questions queue, check-in log
3. **Standardized Workflows** - Testing, PR, review, commit conventions
4. **Tool Integration** - CLAUDE.md, Copilot hooks, Claude Code Action

See [VIRTUAL_TEAM_OPERATING_SYSTEM.md](../planning/VIRTUAL_TEAM_OPERATING_SYSTEM.md) for full specification.

---

## Options Considered

### Option 1: No Coordination (Status Quo)

**Description:** Let each agent work independently with no shared context or coordination.

**Pros:**
- No setup overhead
- Maximum flexibility

**Cons:**
- Inconsistent code quality
- Conflicts and duplicated work
- No visibility into agent activity
- Questions go unanswered

### Option 2: Single Agent Only

**Description:** Use only one AI agent (e.g., Devin) for all development.

**Pros:**
- Consistent approach
- No coordination needed

**Cons:**
- Limited by single agent's capabilities
- No parallelism
- Single point of failure
- Can't leverage best-of-breed tools

### Option 3: Virtual Team Operating System (Selected)

**Description:** Build coordination infrastructure that enables multiple agents to work together.

**Pros:**
- Leverage multiple agents' strengths
- Parallel development
- Consistent output via shared conventions
- Visibility and auditability
- Scalable to more agents

**Cons:**
- Setup overhead
- Maintenance burden
- Agents must follow protocols

---

## Decision Rationale

Option 3 (Virtual Team Operating System) was chosen because:

1. **Leverage strengths:** Different agents excel at different tasks. Devin for complex multi-step work, Claude Code for PR review, Copilot for inline suggestions.

2. **Scalability:** As NYQST grows, we need to parallelize development. A single agent can't scale.

3. **Consistency:** Shared conventions and workflows ensure consistent output regardless of which agent does the work.

4. **Visibility:** Project registry and check-in logs give humans visibility into what agents are doing.

5. **Quality:** Standardized testing and review workflows ensure quality regardless of agent.

---

## Agent Comparison: Key Divergences

| Aspect | Claude Code | Devin | GitHub Copilot | Recommendation |
|--------|-------------|-------|----------------|----------------|
| **Context** | CLAUDE.md | Session + requirements.md | .github/copilot-instructions.md | Use all three |
| **Task Tracking** | Skills, subagents | Todo lists | N/A | Todo lists (visible) |
| **PR Creation** | GitHub Actions | Direct tool | N/A | Direct (faster) |
| **Code Review** | Can review PRs | Creates PRs | Inline suggestions | Claude for review |
| **Testing** | Auto-correct loop | Manual + CI | N/A | Adopt auto-correct |
| **Parallelism** | Subagents | Parallel tools | N/A | Both approaches |

### When to Use Each Agent

| Task | Best Agent | Rationale |
|------|------------|-----------|
| Complex multi-step features | Devin | Best at long-running autonomous work |
| PR review | Claude Code Action | Designed for this via GitHub Actions |
| Quick fixes, inline suggestions | GitHub Copilot | Fast, integrated in IDE |
| Refactoring | Claude Code or Devin | Both handle multi-file changes well |
| Documentation | Any | All capable |
| Investigation/research | Devin | Browser access, persistent sessions |

---

## Implementation Plan

### Phase 1: Foundation (Week 1)
- Create Confluence space with Engineering Playbook structure
- Add CLAUDE.md to repository
- Create Project Registry and Questions Queue pages

### Phase 2: Workflows (Week 2)
- Document standardized testing strategy
- Document PR workflow
- Add pre-commit hooks
- Create PR template

### Phase 3: Integration (Week 3)
- Add GitHub Copilot hooks (.github/hooks/)
- Add Claude Code Action workflow (.github/workflows/)
- Create agent session scripts
- Test coordination with multiple agents

### Phase 4: Refinement (Week 4)
- Gather feedback from agent sessions
- Refine workflows
- Document lessons learned

---

## Consequences

### Positive

- Multiple agents can work in parallel
- Consistent code quality regardless of agent
- Visibility into agent activity
- Questions get answered
- Handoffs are smooth
- Audit trail for compliance

### Negative

- Setup and maintenance overhead
- Agents must follow protocols (may slow them down)
- Confluence dependency
- Learning curve for new agents/workflows

### Risks

- **Risk:** Agents don't follow protocols
  - **Mitigation:** Enforce via CI checks, hooks, and review

- **Risk:** Confluence becomes stale
  - **Mitigation:** Update-Log with signed changes, regular reviews

- **Risk:** Coordination overhead exceeds benefits
  - **Mitigation:** Start simple, add complexity only as needed

---

## GitHub Copilot Hooks Specification

Add `.github/hooks/nyqst-hooks.json`:

```json
{
  "hooks": [
    {
      "type": "sessionStart",
      "command": "scripts/agent-session-start.sh",
      "description": "Initialize agent session, log to registry"
    },
    {
      "type": "sessionEnd", 
      "command": "scripts/agent-session-end.sh",
      "description": "Cleanup, generate session report"
    },
    {
      "type": "beforeToolCall",
      "tools": ["write_file", "execute_command"],
      "command": "scripts/validate-tool-call.sh",
      "description": "Validate tool calls, check for secrets"
    }
  ]
}
```

---

## Claude Code Action Specification

Add `.github/workflows/claude-review.yml`:

```yaml
name: Claude Code Review
on:
  pull_request:
    types: [opened, synchronize]
  issue_comment:
    types: [created]

jobs:
  claude-review:
    if: contains(github.event.comment.body, '@claude') || github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          claude_md_path: CLAUDE.md
```

---

## Related ADRs

- [ADR-001: Data Model Strategy](./001-data-model-strategy.md)
- [ADR-002: Code Generation Strategy](./002-code-generation-strategy.md)

---

## References

- [Anthropic Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [GitHub Copilot Hooks Documentation](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-hooks)
- [Claude Code GitHub Actions](https://github.com/anthropics/claude-code-action)
- [Virtual Team Operating System](../planning/VIRTUAL_TEAM_OPERATING_SYSTEM.md)
