# PROP-002 — Signal ingestion: news/market feeds + web research into asset context packs

- Type: **story**
- Milestone: `M11-PROPSYGNAL`
- Repo alignment: **missing**
- Labels: `backend`, `domain:propsygnal`
- Depends on: `PROP-001`, `PLUG-003`

## Problem

Need to ingest signals with provenance and attach to assets.

## Proposed solution

- Connectors for news feeds and market data providers.
- Store signal items as entities/artifacts.
- Index into context packs for asset/project.

## Acceptance criteria

- Signals ingested and searchable; linked to assets with citations.

## Test plan

- Integration: ingest fixture feed and retrieve signals by asset.
