# EPIC-PROPSYGNAL — PropSygnal module (commercial property signal aggregation and analytics)

- Type: **epic**
- Milestone: `M11-PROPSYGNAL`
- Repo alignment: **missing**
- Labels: `domain:propsygnal`
- Depends on: `BL-016`, `PLUG-003`, `STUDIO-001`

## Problem

PropSygnal requires combining internal property data with market signals, documents, and analytics to support investment decisions.

## Proposed solution

Implement asset model + connectors for market data/news + analysis dashboards + decision workflows with provenance.

## Acceptance criteria

- System can create an asset/project and attach signals and documents; dashboards show key metrics and cited insights.

## Test plan

- Integration: ingest sample signal feed and render dashboard.
