import { useRef, useState } from 'react'
import {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  Panel,
  ReactFlow,
  ReactFlowProvider,
  SelectionMode,
  useEdgesState,
  useNodesState,
  useReactFlow,
  useViewport,
} from '@xyflow/react'

import '@xyflow/react/dist/style.css'

import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import {
  getNodeKindMeta,
  AnalysisCanvasNode as AnalysisCanvasNodeComponent,
} from '@/components/analysis/AnalysisCanvasNode'
import {
  EDGE_RELATION_LABELS,
  addBoardNode,
  connectBoardNodes,
  type AnalysisBoard,
  type AnalysisCanvasEdge,
  type AnalysisCanvasNode as AnalysisCanvasNodeType,
  type AnalysisEdgeRelation,
} from '@/components/analysis/analysis-canvas-state'
import {
  createBenchmarkBoard,
  createScenarioBoard,
} from '@/components/analysis/analysis-canvas-fixtures'

const nodeTypes = {
  analysisNode: AnalysisCanvasNodeComponent,
}

type BoardMode = 'scenario' | 'benchmark'

const RELATION_OPTIONS = Object.keys(EDGE_RELATION_LABELS) as AnalysisEdgeRelation[]

export function AnalysisCanvas() {
  const [boardMode, setBoardMode] = useState<BoardMode>('scenario')
  const board = boardMode === 'scenario' ? createScenarioBoard() : createBenchmarkBoard(200)

  return (
    <ReactFlowProvider key={boardMode}>
      <AnalysisCanvasWorkspace
        board={board}
        boardMode={boardMode}
        onBoardModeChange={setBoardMode}
      />
    </ReactFlowProvider>
  )
}

function AnalysisCanvasWorkspace({
  board,
  boardMode,
  onBoardModeChange,
}: {
  board: AnalysisBoard
  boardMode: BoardMode
  onBoardModeChange: (mode: BoardMode) => void
}) {
  const wrapperRef = useRef<HTMLDivElement | null>(null)
  const [nodes, setNodes, onNodesChange] = useNodesState<AnalysisCanvasNodeType>(board.nodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState<AnalysisCanvasEdge>(board.edges)
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(board.nodes[0]?.id ?? null)
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null)
  const [relation, setRelation] = useState<AnalysisEdgeRelation>('supports')
  const reactFlow = useReactFlow<AnalysisCanvasNodeType, AnalysisCanvasEdge>()

  function handleAddNode() {
    if (!wrapperRef.current) {
      return
    }

    const bounds = wrapperRef.current.getBoundingClientRect()
    const position = reactFlow.screenToFlowPosition({
      x: bounds.left + bounds.width / 2,
      y: bounds.top + bounds.height / 2,
    })

    setNodes((currentNodes) => addBoardNode(currentNodes, 'note', position))
  }

  function handleResetBoard() {
    setNodes(board.nodes)
    setEdges(board.edges)
    setSelectedNodeId(board.nodes[0]?.id ?? null)
    setSelectedEdgeId(null)
    queueMicrotask(() => {
      reactFlow.fitView({ padding: 0.16 })
    })
  }

  function handleFitView() {
    reactFlow.fitView({ padding: 0.16 })
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4 p-6 xl:flex-row">
      <section className="flex min-h-[640px] min-w-0 flex-1 flex-col overflow-hidden rounded-3xl border bg-card shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b bg-gradient-to-r from-background via-background to-muted/60 px-4 py-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold">{board.name}</h2>
              <span
                data-testid="analysis-node-count"
                className="rounded-full border bg-background px-2 py-0.5 text-[11px] text-muted-foreground"
              >
                {nodes.length} nodes
              </span>
              <span
                data-testid="analysis-edge-count"
                className="rounded-full border bg-background px-2 py-0.5 text-[11px] text-muted-foreground"
              >
                {edges.length} edges
              </span>
            </div>
            <p className="text-xs text-muted-foreground">{board.description}</p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Button
              size="sm"
              variant={boardMode === 'scenario' ? 'default' : 'outline'}
              onClick={() => onBoardModeChange('scenario')}
            >
              Working board
            </Button>
            <Button
              size="sm"
              variant={boardMode === 'benchmark' ? 'default' : 'outline'}
              onClick={() => onBoardModeChange('benchmark')}
            >
              Load 200-node benchmark
            </Button>
            <Button size="sm" variant="outline" onClick={handleAddNode}>
              Add note
            </Button>
            <Button size="sm" variant="outline" onClick={handleFitView}>
              Fit graph
            </Button>
            <Button size="sm" variant="ghost" onClick={handleResetBoard}>
              Reset layout
            </Button>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 border-b px-4 py-3">
          <span className="text-xs font-medium text-muted-foreground">
            New links default to
          </span>
          {RELATION_OPTIONS.map((option) => (
            <Button
              key={option}
              size="sm"
              variant={relation === option ? 'secondary' : 'ghost'}
              className="h-8"
              onClick={() => setRelation(option)}
            >
              {EDGE_RELATION_LABELS[option]}
            </Button>
          ))}
        </div>

        <div
          ref={wrapperRef}
          className="min-h-0 flex-1 bg-[radial-gradient(circle_at_top,_rgba(14,165,233,0.10),transparent_32%),linear-gradient(180deg,rgba(248,250,252,0.96),rgba(241,245,249,0.78))]"
        >
          <ReactFlow
            fitView
            fitViewOptions={{ padding: 0.16 }}
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            selectionMode={SelectionMode.Partial}
            snapToGrid
            snapGrid={[16, 16]}
            minZoom={0.25}
            maxZoom={1.6}
            attributionPosition="bottom-left"
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={(connection) =>
              setEdges((currentEdges) => connectBoardNodes(currentEdges, connection, relation))
            }
            onSelectionChange={({ nodes: selectedNodes, edges: selectedEdges }) => {
              setSelectedNodeId(selectedNodes[0]?.id ?? null)
              setSelectedEdgeId(selectedEdges[0]?.id ?? null)
            }}
          >
            <Background variant={BackgroundVariant.Dots} gap={28} size={1.15} />
            <MiniMap
              pannable
              zoomable
              className="!border !bg-background/90"
              nodeColor={(node) =>
                getNodeKindMeta(
                  (node.data as AnalysisCanvasNodeType['data'] | undefined)?.kind ?? 'note'
                ).minimapColor
              }
            />
            <Controls />
            <Panel
              position="bottom-right"
              className="rounded-2xl border bg-background/90 px-3 py-2 text-[11px] text-muted-foreground shadow-sm backdrop-blur"
            >
              Drag nodes to move them. Drag between handles to create a link.
            </Panel>
          </ReactFlow>
        </div>
      </section>

      <AnalysisCanvasSidebar
        boardMode={boardMode}
        relation={relation}
        nodes={nodes}
        edges={edges}
        selectedNodeId={selectedNodeId}
        selectedEdgeId={selectedEdgeId}
      />
    </div>
  )
}

function AnalysisCanvasSidebar({
  boardMode,
  relation,
  nodes,
  edges,
  selectedNodeId,
  selectedEdgeId,
}: {
  boardMode: BoardMode
  relation: AnalysisEdgeRelation
  nodes: AnalysisCanvasNodeType[]
  edges: AnalysisCanvasEdge[]
  selectedNodeId: string | null
  selectedEdgeId: string | null
}) {
  const viewport = useViewport()
  const selectedNode = nodes.find((node) => node.id === selectedNodeId) ?? null
  const selectedEdge = edges.find((edge) => edge.id === selectedEdgeId) ?? null

  return (
    <aside className="flex w-full shrink-0 flex-col rounded-3xl border bg-card shadow-sm xl:w-[320px]">
      <div className="px-5 py-4">
        <h2 className="text-sm font-semibold">Canvas telemetry</h2>
        <p className="mt-1 text-xs text-muted-foreground">
          React Flow is carrying viewport, drag, and graph-link interactions so later
          persistence can stay focused on board data contracts.
        </p>
      </div>

      <Separator />

      <div className="grid grid-cols-3 gap-3 px-5 py-4">
        <MetricCard label="Mode" value={boardMode === 'scenario' ? 'Curated' : 'Benchmark'} />
        <MetricCard label="Zoom" value={`${Math.round(viewport.zoom * 100)}%`} />
        <MetricCard label="Link type" value={EDGE_RELATION_LABELS[relation]} />
      </div>

      <Separator />

      <div className="space-y-4 px-5 py-4 text-sm">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
            Viewport
          </div>
          <div className="mt-2 grid grid-cols-2 gap-3">
            <MetricCard label="X" value={Math.round(viewport.x).toString()} />
            <MetricCard label="Y" value={Math.round(viewport.y).toString()} />
          </div>
        </div>

        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
            Selection
          </div>
          {selectedNode ? (
            <div className="mt-2 rounded-2xl border bg-background p-4">
              <div className="flex items-center justify-between gap-2">
                <span
                  className={`rounded-full border px-2 py-0.5 text-[11px] font-medium ${
                    getNodeKindMeta(selectedNode.data.kind).badge
                  }`}
                >
                  {getNodeKindMeta(selectedNode.data.kind).label}
                </span>
                <span className="text-[11px] text-muted-foreground">
                  {selectedNode.position.x}, {selectedNode.position.y}
                </span>
              </div>
              <div className="mt-3 text-sm font-semibold">{selectedNode.data.title}</div>
              <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
                {selectedNode.data.summary}
              </p>
              <div className="mt-3 text-[11px] text-muted-foreground">
                Owner: {selectedNode.data.owner}
              </div>
            </div>
          ) : selectedEdge ? (
            <div className="mt-2 rounded-2xl border bg-background p-4 text-xs text-muted-foreground">
              <div className="font-medium text-foreground">
                {EDGE_RELATION_LABELS[selectedEdge.data?.relation ?? 'supports']}
              </div>
              <div className="mt-2">
                {selectedEdge.source} to {selectedEdge.target}
              </div>
            </div>
          ) : (
            <div className="mt-2 rounded-2xl border bg-background p-4 text-xs text-muted-foreground">
              Select a node or edge to inspect it here.
            </div>
          )}
        </div>

        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
            Interaction contract
          </div>
          <div className="mt-2 space-y-2 rounded-2xl border bg-background p-4 text-xs text-muted-foreground">
            <p>Pan and zoom stay on the canvas, not the page shell.</p>
            <p>Node drag updates position state for future persistence.</p>
            <p>Edge creation is typed now so the next slice can persist relations directly.</p>
          </div>
        </div>
      </div>
    </aside>
  )
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border bg-background px-3 py-2">
      <div className="text-[11px] text-muted-foreground">{label}</div>
      <div className="mt-1 text-sm font-semibold">{value}</div>
    </div>
  )
}
