# Virtual Team Operating System

> How to run multiple AI coding agents as a coordinated virtual team

**Status:** Draft  
**Date:** 2026-01-26  
**Author:** Mark Forster, Devin  
**PRD Reference:** [03_PLATFORM.md](../prd/03_PLATFORM.md), [06_ARCHITECTURE.md](../prd/06_ARCHITECTURE.md)

---

## Overview

This document defines the infrastructure, processes, and tools needed to run multiple AI coding agents (Devin, Claude Code, GitHub Copilot, Cursor, etc.) as a coordinated virtual development team working on NYQST.

The goal is to enable async development where agents can work independently while maintaining consistency, avoiding conflicts, and following standardized practices.

---

## 1. Engineering Playbook (Confluence)

The Engineering Playbook is the single source of truth for operational knowledge. It lives in Confluence and is readable by both humans and AI agents via the Atlassian MCP.

### Confluence Structure

```
/spaces/ENG/
├── Quickstart                    ← Agent entry point ("read this first")
│   ├── How to Start a Task
│   ├── How to Ask Questions
│   └── How to Check In
│
├── Dev-Infrastructure
│   ├── Tools and Environments
│   ├── Local Setup Guide
│   ├── CI/CD Pipeline
│   └── Secrets Management
│
├── Testing-Strategy
│   ├── Unit Testing (pytest, vitest)
│   ├── Integration Testing
│   ├── E2E Testing
│   └── When to Test What
│
├── Linting-and-Formatting
│   ├── Python (ruff, black, mypy)
│   ├── TypeScript (eslint, prettier)
│   └── Pre-commit Hooks
│
├── Documentation
│   ├── What to Document
│   ├── Where to Store Docs
│   ├── When to Update
│   └── Doc Templates
│
├── Repository-Structure
│   ├── Repo Map (which repo for what)
│   ├── Folder Conventions
│   └── File Naming
│
├── Packaging-and-Deployment
│   ├── Build Process
│   ├── Versioning (semver)
│   ├── Release Process
│   └── Deployment Targets
│
├── Naming-Conventions
│   ├── Python (snake_case, etc.)
│   ├── TypeScript (camelCase, etc.)
│   ├── Database (tables, columns)
│   └── API Endpoints
│
├── Principles
│   ├── Code Quality Standards
│   ├── Security Principles
│   ├── Performance Guidelines
│   └── Accessibility
│
├── Escalation
│   ├── When to Ask for Help
│   ├── Who to Ask
│   └── How to Escalate
│
├── Agent-Coordination              ← NEW: For virtual team
│   ├── Project Registry
│   ├── Questions Queue
│   ├── Check-in Log
│   └── Handoff Protocol
│
└── Update-Log
    └── Change History (who, what, when, signed)
```

### Agent Entry Point

Every agent session should start by reading the Quickstart page:

```
Agent calls: get_confluence_page("ENG", "Quickstart")
```

The Quickstart page contains:
1. How to identify yourself (agent type, session ID)
2. How to check the Project Registry for current work
3. How to claim a task
4. How to ask questions
5. How to check in progress
6. How to hand off work

---

## 2. Agent Coordination

### 2.1 Project Registry

A Confluence page (or database) tracking all active work:

| Project | Repo | Agent | Session ID | Status | Started | Last Check-in | Notes |
|---------|------|-------|------------|--------|---------|---------------|-------|
| Index Service | nyqst-intelli | Devin | abc123 | In Progress | 2026-01-25 | 2026-01-26 02:00 | Working on vector search |
| UI Components | nyqst-intelli | Claude Code | def456 | Blocked | 2026-01-25 | 2026-01-25 18:00 | Waiting for API spec |
| Auth Module | nyqst-auth | Copilot | ghi789 | Complete | 2026-01-24 | 2026-01-25 12:00 | PR #45 merged |

**Update Protocol:**
- Agents update status at start of session
- Agents check in every 2 hours of active work
- Agents mark complete/blocked when appropriate
- Human reviews daily

### 2.2 Questions Queue

A structured place for agents to ask questions:

| ID | Agent | Repo | Local Folder | Setup Context | Question | Desired Outcome | Status | Answer |
|----|-------|------|--------------|---------------|----------|-----------------|--------|--------|
| Q001 | Devin | nyqst-intelli | /services/index | Python 3.11, PostgreSQL | Should vector embeddings use 768 or 1536 dimensions? | Clear decision to implement | Open | - |
| Q002 | Claude | nyqst-intelli | /ui/components | React 18, Vite | Which component library for infinite canvas? | Library recommendation | Answered | Use ReactFlow |

**Question Format:**
```markdown
## Question from [Agent Type] - [Session ID]

**Repo:** nyqst-intelli-230126
**Local Folder:** /services/index
**Setup Context:** Python 3.11, PostgreSQL 15, using SQLAlchemy 2.0

**Question:**
Should vector embeddings use 768 or 1536 dimensions for document similarity?

**Context:**
- Currently implementing the Index Service
- Need to choose embedding model (OpenAI ada-002 = 1536, sentence-transformers = 768)
- Trade-off is storage/speed vs accuracy

**Desired Outcome:**
A clear decision so I can implement the embedding storage schema.
```

### 2.3 Check-in Log

Agents log progress regularly:

```markdown
## Check-in: Devin - Session abc123
**Time:** 2026-01-26 02:00 UTC
**Project:** Index Service
**Status:** In Progress

**Completed since last check-in:**
- Implemented vector storage schema
- Added embedding generation endpoint
- Created unit tests for similarity search

**Currently working on:**
- Integration with document ingestion pipeline

**Blockers:**
- None

**Questions:**
- None

**Next steps:**
- Complete integration tests
- Create PR
```

### 2.4 Handoff Protocol

When an agent needs to hand off work to another agent or human:

```markdown
## Handoff: Devin → Human Review

**Project:** Index Service
**Repo:** nyqst-intelli-230126
**Branch:** devin/1234567890-index-service

**What was done:**
- Implemented vector storage with pgvector
- Added embedding generation using OpenAI ada-002
- Created similarity search endpoint
- Added 95% test coverage

**What remains:**
- Performance optimization for large corpora
- Integration with document module

**Key decisions made:**
- Used 1536 dimensions (OpenAI ada-002)
- Chose pgvector over Pinecone for cost/control

**Files to review:**
- services/index/vector_store.py
- services/index/embeddings.py
- tests/index/test_similarity.py

**How to test:**
```bash
cd services/index
pytest tests/ -v
```

**PR:** https://github.com/t3rm1nu55/nyqst-intelli-230126/pull/XX
```

---

## 3. Standardized Workflows

### 3.1 Testing Strategy

| Phase | What to Test | How | When |
|-------|--------------|-----|------|
| **Development** | Unit tests for new code | `pytest tests/unit/` | After each function/class |
| **Pre-commit** | Lint + type check | `ruff check . && mypy .` | Before every commit |
| **PR** | Unit + Integration | CI runs full suite | On PR creation |
| **Merge** | E2E tests | CI runs E2E | Before merge to main |
| **Post-merge** | Smoke tests | Automated | After deploy |

**Testing Principles:**
1. Write tests before or alongside code, not after
2. Unit tests should be fast (<1s each)
3. Integration tests can use test database
4. E2E tests run against staging environment
5. Aim for 80%+ coverage on new code

### 3.2 PR/Review Workflow

**Standard PR Flow:**

```
1. Create branch: devin/{timestamp}-{descriptive-slug}
2. Make changes
3. Run lint: ruff check . && ruff format --check .
4. Run type check: mypy .
5. Run tests: pytest tests/
6. Commit with descriptive message
7. Push to remote
8. Create PR via tool (not gh CLI)
9. Wait for CI checks
10. Request review
11. Address feedback
12. Merge when approved
```

**PR Checklist (for agents):**
- [ ] Branch follows naming convention
- [ ] All tests pass locally
- [ ] Lint passes
- [ ] Type check passes
- [ ] PR description explains what and why
- [ ] No secrets committed
- [ ] Documentation updated if needed
- [ ] Breaking changes noted

**Review Checklist (for reviewers):**
- [ ] Code follows conventions
- [ ] Tests are adequate
- [ ] No security issues
- [ ] Performance acceptable
- [ ] Documentation sufficient

### 3.3 Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** feat, fix, docs, style, refactor, test, chore

**Example:**
```
feat(index): add vector similarity search

Implement cosine similarity search using pgvector extension.
Uses OpenAI ada-002 embeddings (1536 dimensions).

Closes #123
```

---

## 4. Agent Comparison: Divergences and Recommendations

### 4.1 Anthropic Claude Code vs Devin

| Aspect | Claude Code | Devin | NYQST Recommendation |
|--------|-------------|-------|---------------------|
| **Context File** | `CLAUDE.md` in repo root | Session context + `requirements.md` | Use both: CLAUDE.md for repo-level, session context for task-level |
| **Task Tracking** | Skills system, subagents | Todo lists | Use todo lists (more visible to humans) |
| **PR Creation** | GitHub Actions triggered by `@claude` | Direct PR creation via `git_create_pr` tool | Use direct PR creation (faster feedback) |
| **Hooks** | Custom `.github/hooks/*.json` | Built-in workflow | Add Copilot hooks for CI integration |
| **Parallelism** | Subagents fan out | Parallel tool calls | Use subagents for investigation, parallel calls for independent tasks |
| **Persistence** | Checkpoints, resume | Session persistence | Use session persistence (simpler) |
| **Testing** | Runs tests in loop, auto-corrects | Manual test runs, checks CI | Adopt auto-correct loop (more autonomous) |
| **Code Review** | Can review PRs via GitHub Action | Creates PRs, waits for human review | Use Claude Code Action for automated review, human for final approval |

### 4.2 GitHub Copilot Hooks Proposal

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
      "description": "Cleanup, generate session report, update registry"
    },
    {
      "type": "beforeToolCall",
      "tools": ["write_file", "execute_command"],
      "command": "scripts/validate-tool-call.sh",
      "description": "Validate tool calls, check for secrets, enforce conventions"
    },
    {
      "type": "afterToolCall",
      "command": "scripts/audit-tool-call.sh",
      "description": "Log tool calls for audit trail"
    }
  ]
}
```

**Hook Scripts:**

`scripts/agent-session-start.sh`:
```bash
#!/bin/bash
# Log session start to Confluence via API
# Check Project Registry for conflicts
# Initialize local environment
echo "Session started: $AGENT_SESSION_ID"
```

`scripts/validate-tool-call.sh`:
```bash
#!/bin/bash
# Check for secrets in file writes
# Validate file paths are within allowed directories
# Enforce naming conventions
```

### 4.3 Claude Code Action Integration

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
          skills:
            - code-review
            - security-scan
            - test-coverage
```

---

## 5. CLAUDE.md Template for NYQST

Create `CLAUDE.md` in repo root:

```markdown
# CLAUDE.md - NYQST Project Context

## Project Overview
NYQST is an Agent First Commercial Intelligence Platform. This repo contains the core platform.

## Quick Commands
- Lint: `ruff check . && ruff format --check .`
- Type check: `mypy .`
- Test: `pytest tests/ -v`
- Run dev server: `uvicorn main:app --reload`

## Architecture
- Backend: Python 3.11, FastAPI, SQLAlchemy 2.0, PostgreSQL
- Frontend: TypeScript, React 18, Vite
- Vector DB: pgvector extension

## Key Directories
- `/services/` - Backend services
- `/ui/` - Frontend application
- `/docs/` - Documentation
- `/tests/` - Test suites

## Conventions
- Python: snake_case, type hints required, docstrings for public functions
- TypeScript: camelCase, strict mode, no any
- Commits: conventional commits format
- PRs: require tests, lint pass, type check pass

## Before You Code
1. Read the relevant PRD section in `/docs/prd/`
2. Check ADRs in `/docs/adr/` for architectural decisions
3. Look at existing code for patterns
4. Run tests to ensure environment works

## Common Patterns
- API endpoints: See `/services/api/routes/` for examples
- Pydantic models: See `/services/models/` for examples
- React components: See `/ui/src/components/` for examples

## Do Not
- Commit secrets or API keys
- Skip tests
- Force push
- Modify generated files directly
- Use `Any` type in Python
```

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Create Confluence space structure
- [ ] Write Quickstart page
- [ ] Create Project Registry page
- [ ] Create Questions Queue page
- [ ] Add CLAUDE.md to repo

### Phase 2: Workflows (Week 2)
- [ ] Document Testing Strategy in Confluence
- [ ] Document PR Workflow in Confluence
- [ ] Add pre-commit hooks to repo
- [ ] Create PR template

### Phase 3: Integration (Week 3)
- [ ] Add GitHub Copilot hooks
- [ ] Add Claude Code Action workflow
- [ ] Create agent session scripts
- [ ] Test with multiple agents

### Phase 4: Refinement (Week 4)
- [ ] Gather feedback from agent sessions
- [ ] Refine workflows based on experience
- [ ] Document lessons learned
- [ ] Create training materials

---

## 7. Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Agent consistency | 90%+ code follows conventions | Lint pass rate on PRs |
| Conflict rate | <5% of sessions have conflicts | Project Registry conflicts |
| Question resolution | <24h average | Questions Queue timestamps |
| PR quality | <2 review cycles average | PR review iterations |
| Handoff success | 95%+ successful handoffs | Handoff completion rate |

---

## Related Documents

- [Platform Foundation Plan](./PLATFORM_FOUNDATION.md)
- [ADR-001: Data Model Strategy](../adr/001-data-model-strategy.md)
- [ADR-002: Code Generation Strategy](../adr/002-code-generation-strategy.md)
- [PRD - Architecture](../prd/06_ARCHITECTURE.md)
