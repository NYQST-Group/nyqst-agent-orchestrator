/**
 * Provenance Graph Component
 *
 * Based on research into data lineage visualization:
 * - DAG structures for transformation tracking
 * - Graph databases for storing lineage as direct relationships
 * - Real-time traversal for querying traces
 *
 * Used for: Document transformations, agent execution paths, audit trails
 */

import * as React from 'react';
import { useState, useMemo } from 'react';
import { cn } from '../../lib/utils';

export interface ProvenanceNode {
  id: string;
  type: 'source' | 'transform' | 'artifact' | 'agent' | 'human';
  label: string;
  description?: string;
  timestamp?: Date;
  metadata?: Record<string, unknown>;
  status?: 'complete' | 'running' | 'failed' | 'pending';
}

export interface ProvenanceEdge {
  id: string;
  source: string;
  target: string;
  operation?: string;
  metadata?: Record<string, unknown>;
}

interface ProvenanceGraphProps {
  nodes: ProvenanceNode[];
  edges: ProvenanceEdge[];
  className?: string;
  orientation?: 'horizontal' | 'vertical';
  onNodeClick?: (node: ProvenanceNode) => void;
  onEdgeClick?: (edge: ProvenanceEdge) => void;
  selectedNodeId?: string;
  highlightPath?: string[]; // Node IDs to highlight
}

const NODE_TYPE_STYLES: Record<ProvenanceNode['type'], { bg: string; icon: string }> = {
  source: { bg: 'bg-green-100 dark:bg-green-900/30', icon: 'S' },
  transform: { bg: 'bg-blue-100 dark:bg-blue-900/30', icon: 'T' },
  artifact: { bg: 'bg-purple-100 dark:bg-purple-900/30', icon: 'A' },
  agent: { bg: 'bg-orange-100 dark:bg-orange-900/30', icon: 'G' },
  human: { bg: 'bg-pink-100 dark:bg-pink-900/30', icon: 'H' },
};

const STATUS_COLORS: Record<NonNullable<ProvenanceNode['status']>, string> = {
  complete: 'border-green-500',
  running: 'border-blue-500 animate-pulse',
  failed: 'border-red-500',
  pending: 'border-muted-foreground',
};

interface LayoutNode extends ProvenanceNode {
  x: number;
  y: number;
  level: number;
}

export function ProvenanceGraph({
  nodes,
  edges,
  className,
  orientation = 'horizontal',
  onNodeClick,
  onEdgeClick,
  selectedNodeId,
  highlightPath = [],
}: ProvenanceGraphProps) {
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  // Build adjacency list and calculate levels (topological sort)
  const layout = useMemo(() => {
    const adjacency = new Map<string, string[]>();
    const inDegree = new Map<string, number>();

    // Initialize
    nodes.forEach(n => {
      adjacency.set(n.id, []);
      inDegree.set(n.id, 0);
    });

    // Build graph
    edges.forEach(e => {
      adjacency.get(e.source)?.push(e.target);
      inDegree.set(e.target, (inDegree.get(e.target) || 0) + 1);
    });

    // Topological sort with level assignment
    const levels = new Map<string, number>();
    const queue: string[] = [];

    // Find sources (nodes with no incoming edges)
    nodes.forEach(n => {
      if (inDegree.get(n.id) === 0) {
        queue.push(n.id);
        levels.set(n.id, 0);
      }
    });

    while (queue.length > 0) {
      const nodeId = queue.shift()!;
      const currentLevel = levels.get(nodeId) || 0;

      adjacency.get(nodeId)?.forEach(targetId => {
        const targetLevel = levels.get(targetId);
        if (targetLevel === undefined || targetLevel < currentLevel + 1) {
          levels.set(targetId, currentLevel + 1);
        }
        inDegree.set(targetId, (inDegree.get(targetId) || 1) - 1);
        if (inDegree.get(targetId) === 0) {
          queue.push(targetId);
        }
      });
    }

    // Group nodes by level
    const levelGroups = new Map<number, string[]>();
    levels.forEach((level, nodeId) => {
      if (!levelGroups.has(level)) {
        levelGroups.set(level, []);
      }
      levelGroups.get(level)!.push(nodeId);
    });

    // Calculate positions
    const nodeSize = 100;
    const levelGap = 150;
    const nodeGap = 80;

    const layoutNodes: LayoutNode[] = nodes.map(node => {
      const level = levels.get(node.id) || 0;
      const nodesAtLevel = levelGroups.get(level) || [];
      const indexInLevel = nodesAtLevel.indexOf(node.id);
      const totalAtLevel = nodesAtLevel.length;

      const levelOffset = level * levelGap;
      const nodeOffset = (indexInLevel - (totalAtLevel - 1) / 2) * (nodeSize + nodeGap);

      return {
        ...node,
        level,
        x: orientation === 'horizontal' ? levelOffset : nodeOffset + 300,
        y: orientation === 'horizontal' ? nodeOffset + 200 : levelOffset,
      };
    });

    return layoutNodes;
  }, [nodes, edges, orientation]);

  const nodeMap = new Map(layout.map(n => [n.id, n]));
  const highlightSet = new Set(highlightPath);

  // Calculate SVG bounds
  const padding = 50;
  const minX = Math.min(...layout.map(n => n.x)) - padding;
  const maxX = Math.max(...layout.map(n => n.x)) + 120 + padding;
  const minY = Math.min(...layout.map(n => n.y)) - padding;
  const maxY = Math.max(...layout.map(n => n.y)) + 60 + padding;

  return (
    <div className={cn('overflow-auto bg-muted/20 rounded-lg border', className)}>
      <svg
        width={maxX - minX}
        height={maxY - minY}
        viewBox={`${minX} ${minY} ${maxX - minX} ${maxY - minY}`}
        className="min-w-full"
      >
        <defs>
          <marker
            id="prov-arrow"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" className="fill-muted-foreground" />
          </marker>
          <marker
            id="prov-arrow-highlight"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" className="fill-primary" />
          </marker>
        </defs>

        {/* Edges */}
        {edges.map(edge => {
          const source = nodeMap.get(edge.source);
          const target = nodeMap.get(edge.target);
          if (!source || !target) return null;

          const isHighlighted =
            highlightSet.has(edge.source) && highlightSet.has(edge.target);
          const isHovered =
            hoveredNodeId === edge.source || hoveredNodeId === edge.target;

          // Calculate edge path with curve
          const sourceX = source.x + 100;
          const sourceY = source.y + 25;
          const targetX = target.x;
          const targetY = target.y + 25;

          const midX = (sourceX + targetX) / 2;

          const path = orientation === 'horizontal'
            ? `M ${sourceX} ${sourceY} C ${midX} ${sourceY}, ${midX} ${targetY}, ${targetX} ${targetY}`
            : `M ${sourceX} ${sourceY} C ${sourceX} ${(sourceY + targetY) / 2}, ${targetX} ${(sourceY + targetY) / 2}, ${targetX} ${targetY}`;

          return (
            <g key={edge.id}>
              <path
                d={path}
                fill="none"
                className={cn(
                  'transition-all cursor-pointer',
                  isHighlighted ? 'stroke-primary' : 'stroke-muted-foreground/50',
                  isHovered && 'stroke-muted-foreground'
                )}
                strokeWidth={isHighlighted || isHovered ? 2 : 1}
                markerEnd={isHighlighted ? 'url(#prov-arrow-highlight)' : 'url(#prov-arrow)'}
                onClick={() => onEdgeClick?.(edge)}
              />
              {edge.operation && (
                <text
                  x={midX}
                  y={(sourceY + targetY) / 2 - 8}
                  className="fill-muted-foreground text-xs"
                  textAnchor="middle"
                >
                  {edge.operation}
                </text>
              )}
            </g>
          );
        })}

        {/* Nodes */}
        {layout.map(node => {
          const style = NODE_TYPE_STYLES[node.type];
          const isSelected = node.id === selectedNodeId;
          const isHighlighted = highlightSet.has(node.id);
          const isHovered = node.id === hoveredNodeId;

          return (
            <g
              key={node.id}
              transform={`translate(${node.x}, ${node.y})`}
              className="cursor-pointer"
              onClick={() => onNodeClick?.(node)}
              onMouseEnter={() => setHoveredNodeId(node.id)}
              onMouseLeave={() => setHoveredNodeId(null)}
            >
              {/* Node background */}
              <rect
                width={100}
                height={50}
                rx={8}
                className={cn(
                  style.bg,
                  'stroke-2 transition-all',
                  node.status ? STATUS_COLORS[node.status] : 'stroke-border',
                  isSelected && 'stroke-primary stroke-[3]',
                  isHighlighted && 'stroke-primary',
                  isHovered && 'stroke-foreground'
                )}
              />

              {/* Type icon */}
              <circle
                cx={15}
                cy={25}
                r={12}
                className="fill-background stroke-border"
              />
              <text
                x={15}
                y={29}
                className="fill-foreground text-xs font-mono"
                textAnchor="middle"
              >
                {style.icon}
              </text>

              {/* Label */}
              <text
                x={55}
                y={22}
                className="fill-foreground text-xs font-medium"
                textAnchor="middle"
              >
                {node.label.length > 10 ? node.label.slice(0, 10) + '...' : node.label}
              </text>

              {/* Timestamp */}
              {node.timestamp && (
                <text
                  x={55}
                  y={38}
                  className="fill-muted-foreground"
                  textAnchor="middle"
                  style={{ fontSize: '8px' }}
                >
                  {node.timestamp.toLocaleTimeString()}
                </text>
              )}
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="absolute top-2 right-2 bg-background/80 backdrop-blur rounded border p-2 text-xs space-y-1">
        {Object.entries(NODE_TYPE_STYLES).map(([type, style]) => (
          <div key={type} className="flex items-center gap-2">
            <div className={cn('w-4 h-4 rounded flex items-center justify-center text-[8px]', style.bg)}>
              {style.icon}
            </div>
            <span className="capitalize">{type}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
