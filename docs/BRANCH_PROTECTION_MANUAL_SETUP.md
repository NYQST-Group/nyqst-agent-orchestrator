# Manual Branch Protection Setup

Because this repository is not on GitHub Pro/Enterprise and is not public, the automated GitHub CLI API call to enforce branch protection returned an HTTP 403 error. 

To fulfill the requirements of V4-INFRA-001 manually, the repository administrator must perform the following steps in the GitHub UI:

1. Navigate to **Settings** -> **Branches**.
2. Click **Add branch protection rule**.
3. Set the branch name pattern to `main`.
4. Check **Require status checks to pass before merging**.
5. Enable **Require branches to be up to date before merging**.
6. In the search bar for status checks, add the following exact names (these match the jobs in `.github/workflows/ci.yml`):
   - `Backend Tests`
   - `Frontend Tests`
   - `Lint`
7. Click **Create** to save the rule.

This ensures that no code can be merged into `main` unless the CI/CD pipeline is fully green.
