# [NX-006] Analysis canvas v1 (infinite canvas with entity/run/doc nodes + provenance links)

**Goal**
A first usable “infinite canvas” for analysis:
- place nodes representing artifacts, entities, runs, and notes
- draw links; links carry provenance (why this edge exists)
- embed excerpts + citations

**Leverage**
- Entities + citations tables (MIG-0005B)
- Artifact/pointer primitives

**Implementation**
Backend:
- `canvases` (tenant_id, project_id, name)
- `canvas_nodes` (canvas_id, node_type, entity_id/artifact_id/run_id, x,y,w,h, meta)
- `canvas_edges` (canvas_id, from_node, to_node, relation_type, provenance JSON)
Frontend:
- Canvas UI (ReactFlow or similar):
  - node palette, drag/drop, edge creation
  - side panel shows node details + citations
- Persist layout via API

**Acceptance criteria**
- Create a canvas, add nodes, reload page → layout persists.
- Clicking an entity shows citations; clicking citation opens source doc.

