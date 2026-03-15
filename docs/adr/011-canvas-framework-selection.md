# ADR-011: Analysis Canvas Framework Selection

**Status:** Proposed
**Date:** 2026-03-15
**Deciders:** Mark Forster
**PRD Reference:** [06_ARCHITECTURE.md - Analysis module](../prd/06_ARCHITECTURE.md)

---

## Context

Issue `#192` requires the first non-placeholder canvas implementation for the Studio
surface. The slice is intentionally narrow:

- choose the base canvas implementation
- deliver pan and zoom
- support node drag
- support typed edge creation
- stay responsive at a 200-node interaction baseline

The repo already points toward graph-centric canvas work:

- `docs/RESEARCH_SYNTHESIS.md` recommends React Flow for DAG and provenance views
- `docs/prd/06_ARCHITECTURE.md` explicitly calls for an ADR on the canvas framework
- `STUDIO-004b` is the follow-on slice for persistence, so this decision should not
  pull autosave or backend work into the current issue

---

## Decision

Use **React Flow** (`@xyflow/react`) as the analysis canvas foundation for the Studio
MVP and defer any broader whiteboard capability decision until collaboration,
freeform drawing, or export requirements become concrete.

---

## Options Considered

### Option 1: React Flow

**Description:** Graph-focused React canvas library with built-in viewport, drag, and
connection primitives.

**Pros:**
- MIT licensed
- Direct support for pan, zoom, drag, handles, and edge creation
- Strong fit for provenance, workflow, and decision graph use cases
- Documented performance guidance for larger node sets

**Cons:**
- Graph-first, not a full whiteboard SDK
- Styling and node chrome still need app-specific work

### Option 2: Custom canvas engine

**Description:** Build pan, zoom, drag, and link behavior directly in the app.

**Pros:**
- Full control over interaction and rendering model
- No dependency on third-party abstractions

**Cons:**
- Recreates non-trivial viewport and hit-testing work
- Higher regression risk before persistence is even in place
- Slows delivery of the Studio roadmap for little immediate product gain

### Option 3: tldraw or Excalidraw-first

**Description:** Choose a whiteboard SDK before graph and provenance needs are fully
specified.

**Pros:**
- Better long-term fit if the canvas becomes freeform and collaborative
- Strong drawing ergonomics

**Cons:**
- Mismatch for the current graph-linking acceptance criteria
- Adds whiteboard capability surface area before there is a board persistence contract

---

## Decision Rationale

React Flow best matches the current problem shape. The issue is about stable board
interactions for linked analysis objects, not about freehand drawing or multiplayer
whiteboarding. React Flow gives the project a proven viewport, node drag, and edge
creation baseline now, while keeping the board state aligned with the later
`board/node/edge` persistence slice.

---

## Consequences

### Positive

- The placeholder analysis route now has a concrete interaction model
- Later persistence work can serialize graph state directly
- The framework choice stays aligned with provenance and workflow use cases

### Negative

- If the Studio evolves into a broad whiteboard product, a second ADR may still be needed
- Some whiteboard behaviors will need custom work on top of the graph primitives

### Risks

- Risk: node chrome or layout choices could become too React Flow-specific
  Mitigation: keep board data typed in app-level helpers rather than coupling logic to
  view components
- Risk: performance could regress once richer node content lands
  Mitigation: keep a 200-node benchmark board in the UI and preserve React Flow's
  recommended performance practices

---

## Implementation Notes

- The initial UI ships with a curated working board and a 200-node benchmark board
- Edge relations are typed now (`supports`, `derived-from`, `contradicts`) so
  persistence can reuse the same contract
- Persistence, autosave, and server CRUD remain explicitly deferred to `STUDIO-004b`

---

## Related ADRs

- [ADR-005: Agent Runtime Framework](./005-agent-runtime-framework.md)

---

## References

- [React Flow npm package metadata](https://www.npmjs.com/package/@xyflow/react)
- [React Flow performance guide](https://reactflow.dev/learn/advanced-use/performance)
- [Research synthesis notes](../RESEARCH_SYNTHESIS.md)
