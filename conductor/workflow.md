# Project Workflow

## Guiding Principles

1. **The Plan is the Source of Truth:** All work must be tracked in `plan.md`
2. **The Tech Stack is Deliberate:** Changes to the tech stack must be documented in `tech-stack.md` *before* implementation
3. **Test-Driven Development:** Write unit tests before implementing functionality
4. **High Code Coverage:** Aim for >80% code coverage for all modules
5. **User Experience First:** Every decision should prioritize user experience
6. **Non-Interactive & CI-Aware:** Prefer non-interactive commands. Use `CI=true` for watch-mode tools (tests, linters) to ensure single execution.
7. **Issue Tracking:** Every piece of work must correlate to an issue. Commits and PRs must reference these issues (e.g., `Resolves #123`).

## Task Workflow

All tasks follow a strict lifecycle:

### Standard Task Workflow

1. **Select Task:** Choose the next available task from `plan.md` in sequential order. Identify the corresponding issue ticket number if applicable.

2. **Mark In Progress:** Before beginning work, edit `plan.md` and change the task from `[ ]` to `[~]`

3. **Write Failing Tests (Red Phase):**
   - Create a new test file for the feature or bug fix.
   - Write one or more unit tests that clearly define the expected behavior and acceptance criteria for the task.
   - **CRITICAL:** Run the tests and confirm that they fail as expected. This is the "Red" phase of TDD. Do not proceed until you have failing tests.

4. **Implement to Pass Tests (Green Phase):**
   - Write the minimum amount of application code necessary to make the failing tests pass.
   - Run the test suite again and confirm that all tests now pass. This is the "Green" phase.

5. **Refactor (Optional but Recommended):**
   - With the safety of passing tests, refactor the implementation code and the test code to improve clarity, remove duplication, and enhance performance without changing the external behavior.
   - Rerun tests to ensure they still pass after refactoring.

6. **Verify Coverage:** Run coverage reports using the project's chosen tools.
   ```bash
   pytest --cov=app --cov-report=html
   ```
   Target: >80% coverage for new code.

7. **Document Deviations:** If implementation differs from tech stack:
   - **STOP** implementation
   - Update `tech-stack.md` with new design
   - Add dated note explaining the change
   - Resume implementation

8. **Commit Code Changes:**
   - Stage all code changes related to the task.
   - Propose a clear, concise commit message referencing the issue e.g, `feat(ui): Create basic HTML structure for calculator (Closes #42)`.
   - Perform the commit.

9. **Attach Task Summary with Git Notes:**
   - **Step 9.1:** Obtain the hash of the *just-completed commit* (`git log -1 --format="%H"`).
   - **Step 9.2:** Create a detailed summary for the completed task.
   - **Step 9.3:** Attach Note: `git notes add -m "<note content>" <commit_hash>`

10. **Get and Record Task Commit SHA:**
    - Read `plan.md`, update task status from `[~]` to `[x]`, and append the first 7 characters of the *just-completed commit's* hash.

11. **Commit Plan Update:**
    - Stage and commit the modified `plan.md` file.

12. **Pull Request & CI/CD Hygiene:**
    - Push the branch to the remote repository.
    - Open a Pull Request referencing the resolved issue ticket.
    - **CRITICAL:** Ensure the CI/CD pipeline (tests, linting, security scans) passes. Do not merge until all automated checks are green.
    - Resolve the original tracking issue upon successful merge.

### Phase Completion Verification and Checkpointing Protocol

**Trigger:** Executed immediately after a task is completed that also concludes a phase in `plan.md`.

1.  **Announce Protocol Start:** Inform the user that the phase is complete.
2.  **Ensure Test Coverage for Phase Changes:** List changed files and verify corresponding tests exist.
3.  **Execute Automated Tests:** Run the CI/CD test commands locally and verify everything passes.
4.  **Propose a Detailed, Actionable Manual Verification Plan.**
5.  **Await Explicit User Feedback.**
6.  **Create Checkpoint Commit.**
7.  **Attach Auditable Verification Report using Git Notes.**
8.  **Get and Record Phase Checkpoint SHA.**
9.  **Commit Plan Update.**

### Pull Request & Git Hygiene Guidelines

1. **Branch Naming:** Use clear branch names (e.g., `feat/auth-login`, `fix/header-alignment`, `task/setup-ci`).
2. **Rebasing:** Keep feature branches up-to-date with `main` via rebasing, not merge commits.
3. **Squashing:** Squash minor "wip" or "fix typo" commits into logical atomic units before requesting review.
4. **Issue Linking:** Use GitHub keywords (`Closes #12`, `Resolves #15`) in the PR body to automatically manage issue state.
5. **CI/CD Enforcement:** A branch must pass all automated CI actions (Linting, Tests, Typechecks) before it is allowed to merge. No exceptions.

### Quality Gates

Before marking any task complete, verify:

- [ ] All tests pass (Locally and in CI/CD)
- [ ] Code coverage meets requirements (>80%)
- [ ] Code follows project's code style guidelines
- [ ] The tracking issue has been updated or moved to review
- [ ] No linting or static analysis errors
- [ ] No security vulnerabilities introduced

## Commit Guidelines

### Message Format
```
<type>(<scope>): <description>

[optional body]

Closes #<issue_number>
```

### Types
- `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`

## Definition of Done

A task is complete when:

1. All code implemented to specification.
2. Unit and integration tests written and passing.
3. CI/CD pipeline passes completely on the Pull Request.
4. The related issue ticket is closed/resolved.
5. Code passes all configured linting and static analysis checks.
6. Changes committed with proper message and git notes attached.
7. `plan.md` updated with the commit SHA.