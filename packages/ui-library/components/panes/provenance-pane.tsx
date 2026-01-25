import { useState, useMemo } from 'react';
import {
  GitBranch,
  FileText,
  MessageSquare,
  CheckCircle,
  ArrowRight,
  Eye,
  Link2,
  Filter,
  ZoomIn,
  ZoomOut,
  Maximize2,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { EvidenceGraph, EvidenceGraphNode, EvidenceGraphEdge, Claim, EvidenceSpan } from '@/types';

interface ProvenancePaneProps {
  paneId: string;
}

// Mock evidence graph
const MOCK_GRAPH: EvidenceGraph = {
  nodes: [
    { id: 'claim-1', type: 'claim', label: 'GDPR Article 5 Compliance', data: { status: 'approved', confidence: 'high' } },
    { id: 'claim-2', type: 'claim', label: 'Data Minimization Required', data: { status: 'approved', confidence: 'high' } },
    { id: 'evidence-1', type: 'evidence', label: 'Compliance Report p.4', data: { document: 'compliance-report-2024.pdf', page: 4 } },
    { id: 'evidence-2', type: 'evidence', label: 'Policy Document p.12', data: { document: 'data-policy.pdf', page: 12 } },
    { id: 'doc-1', type: 'document', label: 'compliance-report-2024.pdf', data: { pages: 45 } },
    { id: 'doc-2', type: 'document', label: 'data-policy.pdf', data: { pages: 28 } },
    { id: 'decision-1', type: 'decision', label: 'Legal Review Approval', data: { by: 'Jane Doe', date: '2024-01-10' } },
  ],
  edges: [
    { id: 'e1', source: 'evidence-1', target: 'claim-1', type: 'supports', label: 'Strong support', weight: 0.95 },
    { id: 'e2', source: 'evidence-2', target: 'claim-1', type: 'supports', weight: 0.85 },
    { id: 'e3', source: 'evidence-1', target: 'claim-2', type: 'supports', weight: 0.9 },
    { id: 'e4', source: 'doc-1', target: 'evidence-1', type: 'contains' },
    { id: 'e5', source: 'doc-2', target: 'evidence-2', type: 'contains' },
    { id: 'e6', source: 'claim-1', target: 'claim-2', type: 'derived_from' },
    { id: 'e7', source: 'decision-1', target: 'claim-1', type: 'approved_by' },
  ],
};

// Mock claims for list view
const MOCK_CLAIMS: Claim[] = [
  {
    id: 'claim-1',
    tenantId: 'tenant-1',
    projectId: 'project-1',
    type: 'requirement',
    status: 'approved',
    title: 'GDPR Article 5 Compliance',
    content: 'Personal data must be processed lawfully, fairly, and in a transparent manner in relation to the data subject.',
    confidence: 'high',
    tags: ['gdpr', 'data-protection', 'compliance'],
    metadata: { evidenceCount: 2 },
    createdAt: new Date(Date.now() - 86400000).toISOString(),
    updatedAt: new Date(Date.now() - 43200000).toISOString(),
  },
  {
    id: 'claim-2',
    tenantId: 'tenant-1',
    projectId: 'project-1',
    type: 'requirement',
    status: 'approved',
    title: 'Data Minimization Required',
    content: 'Data minimization principles apply to all processing activities within the organization.',
    confidence: 'high',
    tags: ['gdpr', 'data-minimization'],
    metadata: { evidenceCount: 1, parentClaimId: 'claim-1' },
    createdAt: new Date(Date.now() - 86400000).toISOString(),
    updatedAt: new Date(Date.now() - 43200000).toISOString(),
  },
  {
    id: 'claim-3',
    tenantId: 'tenant-1',
    projectId: 'project-1',
    type: 'control',
    status: 'under_review',
    title: 'SOX Internal Controls',
    content: 'Internal controls over financial reporting must be documented and tested quarterly.',
    confidence: 'medium',
    tags: ['sox', 'financial', 'controls'],
    metadata: { evidenceCount: 3 },
    createdAt: new Date(Date.now() - 172800000).toISOString(),
    updatedAt: new Date(Date.now() - 86400000).toISOString(),
  },
];

const NODE_COLORS: Record<string, string> = {
  claim: 'bg-claim/20 border-claim text-claim',
  evidence: 'bg-evidence/20 border-evidence text-evidence',
  document: 'bg-artifact/20 border-artifact text-artifact',
  decision: 'bg-green-100 border-green-500 text-green-700 dark:bg-green-900/20 dark:text-green-400',
};

const NODE_ICONS: Record<string, React.ElementType> = {
  claim: MessageSquare,
  evidence: FileText,
  document: FileText,
  decision: CheckCircle,
};

export function ProvenancePane({ paneId }: ProvenancePaneProps) {
  const [activeTab, setActiveTab] = useState('graph');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  return (
    <div className="h-full flex flex-col">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <div className="border-b px-4">
          <TabsList className="h-10">
            <TabsTrigger value="graph">Evidence Graph</TabsTrigger>
            <TabsTrigger value="claims">Claims List</TabsTrigger>
            <TabsTrigger value="lineage">Data Lineage</TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="graph" className="flex-1 overflow-hidden mt-0">
          <EvidenceGraphView
            graph={MOCK_GRAPH}
            selectedNodeId={selectedNodeId}
            onNodeSelect={setSelectedNodeId}
          />
        </TabsContent>

        <TabsContent value="claims" className="flex-1 overflow-hidden mt-0">
          <ClaimsListView claims={MOCK_CLAIMS} />
        </TabsContent>

        <TabsContent value="lineage" className="flex-1 overflow-hidden mt-0">
          <DataLineageView />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function EvidenceGraphView({
  graph,
  selectedNodeId,
  onNodeSelect,
}: {
  graph: EvidenceGraph;
  selectedNodeId: string | null;
  onNodeSelect: (id: string | null) => void;
}) {
  const [zoom, setZoom] = useState(100);

  const selectedNode = useMemo(
    () => graph.nodes.find((n) => n.id === selectedNodeId),
    [graph.nodes, selectedNodeId]
  );

  const connectedEdges = useMemo(
    () =>
      selectedNodeId
        ? graph.edges.filter((e) => e.source === selectedNodeId || e.target === selectedNodeId)
        : [],
    [graph.edges, selectedNodeId]
  );

  return (
    <div className="h-full flex">
      {/* Graph view */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="h-10 border-b flex items-center justify-between px-3">
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon-sm" onClick={() => setZoom((z) => Math.max(50, z - 25))}>
              <ZoomOut className="h-4 w-4" />
            </Button>
            <span className="text-xs w-12 text-center">{zoom}%</span>
            <Button variant="ghost" size="icon-sm" onClick={() => setZoom((z) => Math.min(200, z + 25))}>
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Separator orientation="vertical" className="h-5 mx-2" />
            <Button variant="ghost" size="icon-sm">
              <Filter className="h-4 w-4" />
            </Button>
          </div>
          <Button variant="ghost" size="icon-sm">
            <Maximize2 className="h-4 w-4" />
          </Button>
        </div>

        {/* Simple node layout (in production, use a proper graph library) */}
        <div className="flex-1 overflow-auto bg-muted/30 p-8">
          <div
            className="relative mx-auto"
            style={{
              transform: `scale(${zoom / 100})`,
              transformOrigin: 'top center',
              width: 800,
              height: 600,
            }}
          >
            {/* Render nodes in a simple layout */}
            {graph.nodes.map((node, index) => {
              const Icon = NODE_ICONS[node.type] || GitBranch;
              const isSelected = node.id === selectedNodeId;

              // Simple positioning based on node type
              const positions: Record<string, { x: number; y: number }> = {
                'doc-1': { x: 100, y: 100 },
                'doc-2': { x: 100, y: 300 },
                'evidence-1': { x: 300, y: 100 },
                'evidence-2': { x: 300, y: 300 },
                'claim-1': { x: 500, y: 150 },
                'claim-2': { x: 500, y: 350 },
                'decision-1': { x: 700, y: 150 },
              };
              const pos = positions[node.id] || { x: 400, y: 200 + index * 100 };

              return (
                <button
                  key={node.id}
                  className={cn(
                    'absolute p-3 rounded-lg border-2 bg-background shadow-sm transition-all cursor-pointer',
                    NODE_COLORS[node.type],
                    isSelected && 'ring-2 ring-primary ring-offset-2'
                  )}
                  style={{
                    left: pos.x,
                    top: pos.y,
                    transform: 'translate(-50%, -50%)',
                  }}
                  onClick={() => onNodeSelect(isSelected ? null : node.id)}
                >
                  <div className="flex items-center gap-2">
                    <Icon className="h-4 w-4" />
                    <span className="text-xs font-medium max-w-[120px] truncate">{node.label}</span>
                  </div>
                </button>
              );
            })}

            {/* Render edges as simple lines (in production, use SVG paths) */}
            <svg className="absolute inset-0 pointer-events-none" style={{ width: 800, height: 600 }}>
              {graph.edges.map((edge) => {
                const positions: Record<string, { x: number; y: number }> = {
                  'doc-1': { x: 100, y: 100 },
                  'doc-2': { x: 100, y: 300 },
                  'evidence-1': { x: 300, y: 100 },
                  'evidence-2': { x: 300, y: 300 },
                  'claim-1': { x: 500, y: 150 },
                  'claim-2': { x: 500, y: 350 },
                  'decision-1': { x: 700, y: 150 },
                };
                const sourcePos = positions[edge.source] || { x: 0, y: 0 };
                const targetPos = positions[edge.target] || { x: 0, y: 0 };

                const isHighlighted =
                  selectedNodeId && (edge.source === selectedNodeId || edge.target === selectedNodeId);

                return (
                  <line
                    key={edge.id}
                    x1={sourcePos.x}
                    y1={sourcePos.y}
                    x2={targetPos.x}
                    y2={targetPos.y}
                    stroke={isHighlighted ? 'hsl(var(--primary))' : 'hsl(var(--border))'}
                    strokeWidth={isHighlighted ? 2 : 1}
                    strokeDasharray={edge.type === 'derived_from' ? '4 2' : undefined}
                  />
                );
              })}
            </svg>
          </div>
        </div>
      </div>

      {/* Details panel */}
      {selectedNode && (
        <div className="w-72 border-l">
          <div className="p-3 border-b">
            <h3 className="text-sm font-medium">Node Details</h3>
          </div>
          <ScrollArea className="h-[calc(100%-48px)]">
            <div className="p-3 space-y-4">
              <div>
                <span className="text-xs text-muted-foreground">Type</span>
                <Badge className={cn('ml-2', NODE_COLORS[selectedNode.type])}>
                  {selectedNode.type}
                </Badge>
              </div>

              <div>
                <span className="text-xs text-muted-foreground block mb-1">Label</span>
                <p className="text-sm font-medium">{selectedNode.label}</p>
              </div>

              {selectedNode.data && (
                <div>
                  <span className="text-xs text-muted-foreground block mb-1">Properties</span>
                  <div className="text-xs space-y-1">
                    {Object.entries(selectedNode.data).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-muted-foreground">{key}:</span>
                        <span>{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <Separator />

              <div>
                <span className="text-xs text-muted-foreground block mb-2">
                  Connections ({connectedEdges.length})
                </span>
                <div className="space-y-2">
                  {connectedEdges.map((edge) => {
                    const isSource = edge.source === selectedNodeId;
                    const connectedId = isSource ? edge.target : edge.source;
                    const connectedNode = graph.nodes.find((n) => n.id === connectedId);

                    return (
                      <div
                        key={edge.id}
                        className="flex items-center gap-2 text-xs p-2 rounded bg-muted/50"
                      >
                        <Badge variant="outline" className="text-xs">
                          {edge.type}
                        </Badge>
                        <ArrowRight className="h-3 w-3 text-muted-foreground" />
                        <span className="truncate">{connectedNode?.label}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="flex gap-2">
                <Button size="sm" variant="outline" className="flex-1 gap-1">
                  <Eye className="h-3.5 w-3.5" />
                  View
                </Button>
                <Button size="sm" variant="outline" className="flex-1 gap-1">
                  <Link2 className="h-3.5 w-3.5" />
                  Link
                </Button>
              </div>
            </div>
          </ScrollArea>
        </div>
      )}
    </div>
  );
}

function ClaimsListView({ claims }: { claims: Claim[] }) {
  return (
    <ScrollArea className="h-full">
      <div className="p-4 space-y-3">
        {claims.map((claim) => (
          <div key={claim.id} className="p-4 rounded-lg border bg-card">
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-medium">{claim.title}</h4>
                  <Badge variant="claim" className="text-xs">
                    {claim.type}
                  </Badge>
                  <Badge
                    variant={claim.status === 'approved' ? 'success' : 'warning'}
                    className="text-xs"
                  >
                    {claim.status}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{claim.content}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 mt-3">
              <Badge variant="outline" className="text-xs">
                Confidence: {claim.confidence}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {claim.metadata.evidenceCount as number} evidence spans
              </span>
              <div className="flex-1" />
              <Button size="sm" variant="ghost" className="h-7 text-xs">
                View Evidence
              </Button>
            </div>

            <div className="flex flex-wrap gap-1 mt-2">
              {claim.tags.map((tag) => (
                <Badge key={tag} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}

function DataLineageView() {
  return (
    <div className="h-full flex items-center justify-center text-muted-foreground">
      <div className="text-center">
        <GitBranch className="h-12 w-12 mx-auto mb-4 opacity-30" />
        <p className="text-sm">Data lineage visualization</p>
        <p className="text-xs mt-1">Track how data flows through the system</p>
      </div>
    </div>
  );
}
