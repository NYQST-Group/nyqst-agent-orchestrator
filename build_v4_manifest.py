import json
import re
import os

# Paths
mapping_file = "/Users/markforster/.gemini/tmp/nyqst-docuintelli-build/NYQST_V4_FULL_DROP/v4/NYQST_BuildPack_V4_FINAL/analysis/V2M_ISSUE_MAPPING.md"
v1_file = "staging_issues/issues.json" # Original V1
v2_file = "staging_issues/V2_issues.json" # Original V2
v2m_file = "staging_issues/V2M_issues.json" # Original V2M
v4_new_file = "staging_issues/V4_NEW_ISSUES.md"

output_json = "staging_issues/v4_final_import.json"
excluded_log = "staging_issues/v4_excluded_issues.log"
included_log = "staging_issues/v4_included_issues.log"

def load_json_issues(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        data = json.load(f)
        if isinstance(data, dict) and "issues" in data:
            return data["issues"]
        elif isinstance(data, list):
            return data
    return []

def get_issue_key(issue):
    return issue.get("key") or issue.get("id") or issue.get("bl_id")

# 1. Parse the V2M Mapping Table to get approved legacy IDs and their assigned V4 Epics
approved_legacy_keys = {}
with open(mapping_file, "r") as f:
    for line in f:
        # Match lines like: | BL-001 | [BL-001] Title | EPIC-NAME |
        match = re.match(r'^\|\s*([A-Za-z0-9\-]+)\s*\|\s*\[.*?\][^\|]*\|\s*([A-Za-z0-9\-]+)\s*\|', line)
        if match:
            issue_key = match.group(1).strip()
            epic = match.group(2).strip()
            approved_legacy_keys[issue_key] = epic

# 2. Load all legacy issues, preferring newer versions (V2M > V2 > V1)
all_legacy_issues = {}

# Load V1
for issue in load_json_issues(v1_file):
    key = get_issue_key(issue)
    if key: all_legacy_issues[key] = {"source": "V1", "data": issue}

# Load V2
for issue in load_json_issues(v2_file):
    key = get_issue_key(issue)
    if key: all_legacy_issues[key] = {"source": "V2", "data": issue}

# Load V2M
for issue in load_json_issues(v2m_file):
    key = get_issue_key(issue)
    if key: all_legacy_issues[key] = {"source": "V2M", "data": issue}

# 3. Filter legacy issues against the approved list
final_issues = []
excluded = []

for key, info in all_legacy_issues.items():
    if key in approved_legacy_keys:
        issue_data = info["data"]
        # Inject the V4 epic mapping as a label or meta field so it's not lost
        v4_epic = approved_legacy_keys[key]
        if "labels" not in issue_data:
            issue_data["labels"] = []
        issue_data["labels"].append(f"epic:{v4_epic.lower()}")
        
        # Format normalization
        normalized = {
            "key": key,
            "title": f"[{key}] {issue_data.get('title', '').replace(f'[{key}]', '').strip()}",
            "body": issue_data.get("body") or issue_data.get("description") or issue_data.get("problem", ""),
            "milestone": issue_data.get("milestone", ""),
            "labels": issue_data.get("labels", []),
            "source_pack": info["source"]
        }
        # If it was a V1/V2 issue, body needs reconstruction
        if not normalized["body"] and "problem" in issue_data:
            parts = []
            if issue_data.get("problem"): parts.append(f"## Problem\n{issue_data['problem']}")
            if issue_data.get("solution"): parts.append(f"## Solution\n{issue_data['solution']}")
            if issue_data.get("acceptance_criteria"):
                ac = issue_data["acceptance_criteria"]
                if isinstance(ac, list):
                    ac = "\n".join([f"- {x}" for x in ac])
                parts.append(f"## Acceptance Criteria\n{ac}")
            normalized["body"] = "\n\n".join(parts)
            
        final_issues.append(normalized)
    else:
        excluded.append(f"{key} (from {info['source']}) - Reason: Not explicitly mapped in V4_FINAL_SPEC")

# 4. Parse V4_NEW_ISSUES.md to inject the 45 new issues
current_epic = ""
with open(v4_new_file, "r") as f:
    lines = f.readlines()

current_issue = None
for i, line in enumerate(lines):
    line = line.strip()
    if line.startswith("## EPIC-"):
        current_epic = line.replace("## ", "").strip()
    elif line.startswith("### V4-"):
        # Save previous issue
        if current_issue:
            final_issues.append(current_issue)
            
        # Parse title: ### V4-BILL-001: Billing Portal screen
        match = re.match(r'^###\s+(V4-[A-Z0-9\-]+):\s*(.*)', line)
        if match:
            key = match.group(1)
            title = match.group(2)
            current_issue = {
                "key": key,
                "title": f"[{key}] {title}",
                "body": "",
                "milestone": "",
                "labels": [f"epic:{current_epic.lower()}"],
                "source_pack": "V4_NEW"
            }
    elif current_issue:
        if line.startswith("Milestone:"):
            current_issue["milestone"] = line.split(":", 1)[1].strip()
        elif line.startswith("Priority:"):
            current_issue["labels"].append(f"priority:{line.split(':', 1)[1].strip().lower()}")
        elif line.startswith("Dependencies:"):
            deps = line.split(":", 1)[1].strip()
            current_issue["body"] += f"**Dependencies:** {deps}\n\n"
        else:
            current_issue["body"] += line + "\n"

# Append the last issue
if current_issue:
    final_issues.append(current_issue)

# 5. Write outputs
with open(output_json, "w") as f:
    json.dump({"issues": final_issues}, f, indent=2)

with open(excluded_log, "w") as f:
    f.write("The following legacy issues were intentionally excluded because they were not mapped in the V4 final architecture:\n\n")
    f.write("\n".join(sorted(excluded)))

with open(included_log, "w") as f:
    f.write(f"Total V4 Issues to Import: {len(final_issues)}\n\n")
    for issue in final_issues:
        f.write(f"{issue['key']} ({issue['source_pack']}) -> {issue['title']}\n")

print(f"Extraction complete. {len(final_issues)} issues saved to {output_json}.")
print(f"{len(excluded)} obsolete issues excluded and logged to {excluded_log}.")