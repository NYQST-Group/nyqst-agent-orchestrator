import {
  MarkerType,
  addEdge,
  type Edge,
  type Node,
  type XYPosition,
} from '@xyflow/react'

export type AnalysisNodeKind =
  | 'note'
  | 'artifact'
  | 'reportSnippet'
  | 'decision'
  | 'chartPlaceholder'

export type AnalysisEdgeRelation = 'supports' | 'derived-from' | 'contradicts'

export type AnalysisNodeData = {
  kind: AnalysisNodeKind
  title: string
  summary: string
  owner: string
  status: string
}

export type AnalysisEdgeData = {
  relation: AnalysisEdgeRelation
}

export type AnalysisCanvasNode = Node<AnalysisNodeData, 'analysisNode'>
export type AnalysisCanvasEdge = Edge<AnalysisEdgeData, 'smoothstep'>
export type BoardConnection = {
  source: string | null
  target: string | null
  sourceHandle?: string | null
  targetHandle?: string | null
}

export type AnalysisBoard = {
  name: string
  description: string
  nodes: AnalysisCanvasNode[]
  edges: AnalysisCanvasEdge[]
}

export const EDGE_RELATION_LABELS: Record<AnalysisEdgeRelation, string> = {
  supports: 'Supports',
  'derived-from': 'Derived from',
  contradicts: 'Contradicts',
}

const NODE_COPY: Record<
  AnalysisNodeKind,
  { label: string; summary: string; owner: string; status: string }
> = {
  note: {
    label: 'Working note',
    summary: 'Quick synthesis point that can be moved and linked as evidence arrives.',
    owner: 'Analyst',
    status: 'Draft',
  },
  artifact: {
    label: 'Artifact',
    summary: 'Source artifact or output frame that anchors linked reasoning.',
    owner: 'Ingest',
    status: 'Tracked',
  },
  reportSnippet: {
    label: 'Report snippet',
    summary: 'A report fragment or claim block that needs provenance and review.',
    owner: 'Reporting',
    status: 'Review',
  },
  decision: {
    label: 'Decision',
    summary: 'Decision node capturing a choice, owner, and follow-up work.',
    owner: 'Decision desk',
    status: 'Pending',
  },
  chartPlaceholder: {
    label: 'Chart placeholder',
    summary: 'Reserved space for chart output once the data contract is wired in.',
    owner: 'Studio',
    status: 'Scaffold',
  },
}

type CreateBoardNodeOptions = {
  id?: string
  kind: AnalysisNodeKind
  position: XYPosition
  title?: string
  summary?: string
  owner?: string
  status?: string
}

export function createBoardNode(options: CreateBoardNodeOptions): AnalysisCanvasNode {
  const copy = NODE_COPY[options.kind]

  return {
    id: options.id ?? crypto.randomUUID(),
    type: 'analysisNode',
    position: options.position,
    data: {
      kind: options.kind,
      title: options.title ?? copy.label,
      summary: options.summary ?? copy.summary,
      owner: options.owner ?? copy.owner,
      status: options.status ?? copy.status,
    },
  }
}

export function addBoardNode(
  nodes: AnalysisCanvasNode[],
  kind: AnalysisNodeKind,
  position: XYPosition
): AnalysisCanvasNode[] {
  const nextIndex = nodes.filter((node) => node.data.kind === kind).length + 1

  return [
    ...nodes,
    createBoardNode({
      kind,
      position,
      title: `${NODE_COPY[kind].label} ${nextIndex}`,
      status: 'New',
    }),
  ]
}

export function moveBoardNode(
  nodes: AnalysisCanvasNode[],
  nodeId: string,
  position: XYPosition
): AnalysisCanvasNode[] {
  return nodes.map((node) => (node.id === nodeId ? { ...node, position } : node))
}

export function createBoardEdge(
  connection: BoardConnection,
  relation: AnalysisEdgeRelation = 'supports'
): AnalysisCanvasEdge | null {
  if (!connection.source || !connection.target) {
    return null
  }

  const stroke =
    relation === 'contradicts'
      ? '#dc2626'
      : relation === 'derived-from'
        ? '#2563eb'
        : '#0f766e'

  return {
    id: `${connection.source}-${connection.target}-${relation}-${crypto.randomUUID()}`,
    source: connection.source,
    target: connection.target,
    sourceHandle: connection.sourceHandle,
    targetHandle: connection.targetHandle,
    type: 'smoothstep',
    label: EDGE_RELATION_LABELS[relation],
    animated: relation === 'derived-from',
    markerEnd: {
      type: MarkerType.ArrowClosed,
      width: 18,
      height: 18,
      color: stroke,
    },
    style: {
      stroke,
      strokeWidth: relation === 'contradicts' ? 2.5 : 2,
    },
    labelStyle: {
      fill: '#475569',
      fontSize: 11,
      fontWeight: 600,
    },
    data: {
      relation,
    },
  }
}

export function connectBoardNodes(
  edges: AnalysisCanvasEdge[],
  connection: BoardConnection,
  relation: AnalysisEdgeRelation = 'supports'
): AnalysisCanvasEdge[] {
  const edge = createBoardEdge(connection, relation)

  return edge ? (addEdge(edge, edges) as AnalysisCanvasEdge[]) : edges
}
