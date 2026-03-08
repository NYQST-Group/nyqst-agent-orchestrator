# EPIC-REGSYGNAL — RegSygnal module (regulatory intelligence, reconciliation, alerts)

- Type: **epic**
- Milestone: `M10-REGSYGNAL`
- Repo alignment: **missing**
- Labels: `domain:regsygnal`
- Depends on: `BL-016`, `PLUG-003`, `BL-020`

## Problem

RegSygnal needs continuous monitoring of regulatory sources, mapping to internal policy frameworks, and producing actionable diffs and tasks with provenance.

## Proposed solution

Use web connectors + DocuIntelli pattern engine to ingest regulations, extract obligations, reconcile against internal controls, and output alerts/reports.

## Acceptance criteria

- System can ingest a regulatory update feed and produce a summarized diff with citations and impacted controls.

## Test plan

- Integration: ingest fixture regulatory update → diff report produced.
