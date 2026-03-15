import {
  createBoardEdge,
  createBoardNode,
  type AnalysisBoard,
  type AnalysisCanvasEdge,
  type AnalysisCanvasNode,
  type AnalysisEdgeRelation,
  type AnalysisNodeKind,
} from '@/components/analysis/analysis-canvas-state'

const BENCHMARK_KINDS: AnalysisNodeKind[] = [
  'artifact',
  'note',
  'reportSnippet',
  'decision',
  'chartPlaceholder',
]

const BENCHMARK_RELATIONS: AnalysisEdgeRelation[] = [
  'supports',
  'derived-from',
  'supports',
  'contradicts',
]

export function createScenarioBoard(): AnalysisBoard {
  const leaseSchedule = createBoardNode({
    id: 'artifact-lease-schedule',
    kind: 'artifact',
    position: { x: 80, y: 80 },
    title: 'Lease schedule',
    summary: 'Primary source bundle covering rent rolls, covenant thresholds, and expiry risk.',
    owner: 'Research',
    status: 'Source',
  })

  const covenantDelta = createBoardNode({
    id: 'report-covenant-delta',
    kind: 'reportSnippet',
    position: { x: 420, y: 40 },
    title: 'Coverage delta',
    summary: 'Draft narrative describing cash coverage compression in the downside case.',
    owner: 'Reporting',
    status: 'Review',
  })

  const valuationPressure = createBoardNode({
    id: 'note-valuation-pressure',
    kind: 'note',
    position: { x: 740, y: 110 },
    title: 'Valuation pressure',
    summary: 'Potential NAV pressure if expiring units re-let below current assumptions.',
    owner: 'Analyst',
    status: 'Working',
  })

  const decisionReview = createBoardNode({
    id: 'decision-escalate-review',
    kind: 'decision',
    position: { x: 740, y: 360 },
    title: 'Escalate committee review',
    summary: 'Decision gate for whether the credit committee needs a formal watchlist review.',
    owner: 'Investment committee',
    status: 'Pending',
  })

  const sensitivityChart = createBoardNode({
    id: 'chart-sensitivity',
    kind: 'chartPlaceholder',
    position: { x: 380, y: 340 },
    title: 'Sensitivity chart',
    summary: 'Reserved frame for debt yield and covenant headroom once chart output is wired.',
    owner: 'Studio',
    status: 'Scaffold',
  })

  const renewalRisk = createBoardNode({
    id: 'note-renewal-risk',
    kind: 'note',
    position: { x: 80, y: 360 },
    title: 'Renewal risk cluster',
    summary: 'Group expiring tenants by rent reversion risk and capture linked evidence.',
    owner: 'Analyst',
    status: 'Draft',
  })

  const nodes = [
    leaseSchedule,
    covenantDelta,
    valuationPressure,
    decisionReview,
    sensitivityChart,
    renewalRisk,
  ]

  const edges = [
    createBoardEdge(
      { source: leaseSchedule.id, target: covenantDelta.id },
      'derived-from'
    ),
    createBoardEdge(
      { source: covenantDelta.id, target: valuationPressure.id },
      'supports'
    ),
    createBoardEdge(
      { source: valuationPressure.id, target: decisionReview.id },
      'supports'
    ),
    createBoardEdge(
      { source: renewalRisk.id, target: decisionReview.id },
      'contradicts'
    ),
    createBoardEdge(
      { source: sensitivityChart.id, target: decisionReview.id },
      'supports'
    ),
  ].filter(Boolean) as AnalysisCanvasEdge[]

  return {
    name: 'Working board',
    description:
      'Curated starter board for linked evidence, analysis notes, and decision framing.',
    nodes,
    edges,
  }
}

export function createBenchmarkBoard(nodeCount = 200): AnalysisBoard {
  const columns = 10
  const xGap = 230
  const yGap = 150

  const nodes: AnalysisCanvasNode[] = Array.from({ length: nodeCount }, (_, index) => {
    const row = Math.floor(index / columns)
    const column = index % columns
    const kind = BENCHMARK_KINDS[index % BENCHMARK_KINDS.length]

    return createBoardNode({
      id: `benchmark-node-${index + 1}`,
      kind,
      position: { x: column * xGap, y: row * yGap },
      title: `Benchmark node ${index + 1}`,
      summary: 'Seeded canvas item for viewport pan, zoom, drag, and edge interaction checks.',
      owner: row % 2 === 0 ? 'Studio' : 'Analyst',
      status: row % 3 === 0 ? 'Active' : 'Tracked',
    })
  })

  const edges: AnalysisCanvasEdge[] = []

  for (let index = 1; index < nodes.length; index += 1) {
    const sequential = createBoardEdge(
      { source: nodes[index - 1].id, target: nodes[index].id },
      BENCHMARK_RELATIONS[(index - 1) % BENCHMARK_RELATIONS.length]
    )

    if (sequential) {
      edges.push(sequential)
    }

    if (index >= columns && index % 3 === 0) {
      const columnAnchor = createBoardEdge(
        { source: nodes[index - columns].id, target: nodes[index].id },
        'supports'
      )

      if (columnAnchor) {
        edges.push(columnAnchor)
      }
    }
  }

  return {
    name: '200-node benchmark',
    description:
      'Stress board for confirming the viewport and drag baseline before persistence work.',
    nodes,
    edges,
  }
}
