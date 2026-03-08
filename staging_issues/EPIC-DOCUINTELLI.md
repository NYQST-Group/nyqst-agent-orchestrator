# EPIC-DOCUINTELLI — DocuIntelli domain module (document intelligence and corpus analysis)

- Type: **epic**
- Milestone: `M7-DOCUINTELLI`
- Repo alignment: **missing**
- Labels: `domain:docuintelli`
- Depends on: `EPIC-STUDIO`, `BL-016`, `PLUG-002`

## Problem

DocuIntelli requires multi-phase corpus analysis, dimension discovery, anomaly detection, and explainable outputs. It depends on platform primitives (context, provenance, streaming, tools) and introduces module-specific capabilities.

## Proposed solution

Implement DocuIntelli as the first deep domain module: corpus ingestion, profiling, framework selection, dimension discovery, anomaly/gap detection, visualization, and report exports.

## Acceptance criteria

- DocuIntelli can ingest a corpus (docs + metadata), profile it, run at least one framework, and output a cited analysis report + anomalies list.
- DocuIntelli UI exists inside Studio with corpus explorer, dimension builder, and anomaly dashboards.

## Test plan

- Integration: run DocuIntelli analysis on fixture corpus; verify outputs and citations.

## Notes

DocuIntelli-specific BL extensions are captured as BL-023..BL-030.
