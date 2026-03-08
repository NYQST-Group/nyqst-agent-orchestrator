#!/usr/bin/env bash

set -eo pipefail
# sync-conductor.sh
# This script parses all Conductor plan.md files, finds tasks marked as complete [x],
# and uses the GitHub CLI (gh) to close the corresponding issues on GitHub.

echo "Starting Conductor <-> GitHub Sync..."

# Ensure gh is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed. Please install it to use sync."
    exit 1
fi

REPO="NYQST-Group/NYQST-DocuIntelli-Build"

# Find all plan.md files safely
while IFS= read -r -d '' plan_file; do
    echo "Scanning $plan_file..."
    
    # Grep for completed tasks that reference an issue number (e.g., #123)
    # The format we expect is roughly: - [x] Task: Some description #123
    # Or sub-tasks: - [x] Sub-task: Some description #123
    
    # Use process substitution to avoid subshell variable scoping issues if we need them later
    while IFS= read -r line; do
        # Extract all issue numbers from the line
        issue_nums=$(echo "$line" | grep -o '#[0-9]\+' | tr -d '#')
        
        for issue_num in $issue_nums; do
            # Check current state of the issue
            state=$(gh issue view "$issue_num" --repo "$REPO" --json state --jq .state 2>/dev/null)
            
            if [ "$state" == "OPEN" ]; then
                echo "  Closing Issue #$issue_num (marked [x] in Conductor)"
                gh issue close "$issue_num" --repo "$REPO" -m "Completed via Conductor track"
            elif [ "$state" == "CLOSED" ]; then
                echo "  Issue #$issue_num is already closed. Skipping."
            else
                echo "  Warning: Issue #$issue_num not found or inaccessible."
            fi
        done
    done < <(grep -E "^[[:space:]]*- \[x\].*#[0-9]+" "$plan_file")
done < <(find conductor/tracks -name "plan.md" -print0)

echo "Sync complete."
