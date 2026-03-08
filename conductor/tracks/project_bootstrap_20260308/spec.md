# Specification: Project Bootstrap & GitHub Sync

## Objective
Before any domain feature work begins on the Intelli platform, we must establish a rock-solid project foundation. This track ensures that the current codebase (V4 drop) is successfully transitioned into a fresh GitHub repository, all legacy and new V4 issues are tracked formally, and our local Conductor planner stays automatically synchronized with the GitHub Project board.

## Key Deliverables
1. **GitHub Repository**: A fresh, properly configured GitHub repo containing the `nyqst-intelli-230126` code.
2. **Issue Migration**: All V4 epics configured as GitHub Milestones/Projects, and all V4 issues (and their V2M mapped dependencies) populated into the repo.
3. **Conductor-GitHub Sync**: A script (`sync-conductor.sh`) that parses `plan.md` files and utilizes the GitHub CLI (`gh`) to ensure that marking a Conductor task `[x]` resolves the issue in GitHub (and vice versa).
4. **CI/CD Hygiene**: The initial GitHub Actions pipeline for testing and linting, ensuring PRs cannot be merged without passing.

## Security & Architecture Context
- Uses GitHub CLI (`gh`) for safe API interactions.
- CI/CD secrets should be properly vaulted in GitHub Actions Secrets.