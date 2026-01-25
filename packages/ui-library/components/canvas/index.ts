/**
 * Canvas/Spatial Components
 * Based on research into tldraw, Excalidraw, Miro, Heptabase patterns
 */

export { EvidenceCanvas } from './evidence-canvas';
export type { EvidenceNode, EvidenceEdge } from './evidence-canvas';

export { ProvenanceGraph } from './provenance-graph';
export type { ProvenanceNode, ProvenanceEdge } from './provenance-graph';

export { SemanticZoom, SemanticZoomProvider, useZoomContext, ZoomSensitive } from './semantic-zoom';
export type { ZoomLevel } from './semantic-zoom';

export { SpatialCluster } from './spatial-cluster';
export type { ClusterNode } from './spatial-cluster';
