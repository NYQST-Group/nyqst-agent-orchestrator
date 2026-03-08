# PLUG-003c — Implement first production connector (Google Drive or SharePoint) + sync job

- Type: **task**
- Milestone: `M5-PLUGINS`
- Repo alignment: **missing**
- Labels: `backend`, `connectors`
- Depends on: `PLUG-003b`, `BL-013`

## Problem

Framework must be proven with a real connector used in workflows.

## Proposed solution

Pick one connector and implement: list folders/files, download docs, store as artifacts, update corpus/notebook, index.

## Acceptance criteria

- Connector sync imports documents into a project notebook and indexes them for retrieval.

## Test plan

- Integration: sync job stores artifacts; retrieval finds imported content.
