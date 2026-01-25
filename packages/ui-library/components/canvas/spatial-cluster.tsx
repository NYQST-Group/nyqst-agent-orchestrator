/**
 * Spatial Clustering Components
 *
 * Based on research into graph visualization patterns:
 * - Maximize intra-cluster edge density
 * - Minimize inter-cluster connections
 * - Visual encoding: size = importance, color = category
 * - Progressive disclosure and filtering
 */

import * as React from 'react';
import { useState, useMemo } from 'react';
import { cn } from '../../lib/utils';

export interface ClusterNode {
  id: string;
  label: string;
  cluster: string;
  importance?: number; // 0-1, affects size
  metadata?: Record<string, unknown>;
}

interface Cluster {
  id: string;
  label: string;
  color: string;
  nodes: ClusterNode[];
}

interface SpatialClusterProps {
  nodes: ClusterNode[];
  className?: string;
  onNodeClick?: (node: ClusterNode) => void;
  onClusterClick?: (cluster: Cluster) => void;
  selectedNodeId?: string;
  selectedClusterId?: string;
  showLabels?: boolean;
  layout?: 'force' | 'radial' | 'grid';
}

// Color palette for clusters
const CLUSTER_COLORS = [
  'bg-blue-100 border-blue-300 dark:bg-blue-900/30 dark:border-blue-700',
  'bg-green-100 border-green-300 dark:bg-green-900/30 dark:border-green-700',
  'bg-purple-100 border-purple-300 dark:bg-purple-900/30 dark:border-purple-700',
  'bg-orange-100 border-orange-300 dark:bg-orange-900/30 dark:border-orange-700',
  'bg-pink-100 border-pink-300 dark:bg-pink-900/30 dark:border-pink-700',
  'bg-cyan-100 border-cyan-300 dark:bg-cyan-900/30 dark:border-cyan-700',
  'bg-yellow-100 border-yellow-300 dark:bg-yellow-900/30 dark:border-yellow-700',
  'bg-red-100 border-red-300 dark:bg-red-900/30 dark:border-red-700',
];

const NODE_COLORS = [
  'bg-blue-500',
  'bg-green-500',
  'bg-purple-500',
  'bg-orange-500',
  'bg-pink-500',
  'bg-cyan-500',
  'bg-yellow-500',
  'bg-red-500',
];

export function SpatialCluster({
  nodes,
  className,
  onNodeClick,
  onClusterClick,
  selectedNodeId,
  selectedClusterId,
  showLabels = true,
  layout = 'radial',
}: SpatialClusterProps) {
  const [hoveredClusterId, setHoveredClusterId] = useState<string | null>(null);

  // Group nodes by cluster
  const clusters = useMemo(() => {
    const clusterMap = new Map<string, ClusterNode[]>();

    nodes.forEach(node => {
      const existing = clusterMap.get(node.cluster) || [];
      clusterMap.set(node.cluster, [...existing, node]);
    });

    return Array.from(clusterMap.entries()).map(([id, clusterNodes], index): Cluster => ({
      id,
      label: id,
      color: CLUSTER_COLORS[index % CLUSTER_COLORS.length],
      nodes: clusterNodes,
    }));
  }, [nodes]);

  // Calculate cluster positions based on layout
  const clusterPositions = useMemo(() => {
    const centerX = 300;
    const centerY = 300;
    const radius = 200;

    return clusters.map((cluster, index) => {
      const angle = (2 * Math.PI * index) / clusters.length - Math.PI / 2;

      if (layout === 'radial') {
        return {
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle),
        };
      } else if (layout === 'grid') {
        const cols = Math.ceil(Math.sqrt(clusters.length));
        const row = Math.floor(index / cols);
        const col = index % cols;
        return {
          x: 100 + col * 200,
          y: 100 + row * 200,
        };
      } else {
        // Force-directed would require more complex simulation
        return {
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle),
        };
      }
    });
  }, [clusters, layout]);

  return (
    <div className={cn('relative overflow-auto', className)}>
      <svg width="600" height="600" className="min-w-full">
        {/* Cluster backgrounds */}
        {clusters.map((cluster, clusterIndex) => {
          const pos = clusterPositions[clusterIndex];
          const nodeCount = cluster.nodes.length;
          const clusterRadius = Math.max(60, Math.sqrt(nodeCount) * 30);
          const isSelected = cluster.id === selectedClusterId;
          const isHovered = cluster.id === hoveredClusterId;

          return (
            <g key={cluster.id}>
              {/* Cluster circle */}
              <circle
                cx={pos.x}
                cy={pos.y}
                r={clusterRadius}
                className={cn(
                  cluster.color,
                  'fill-current stroke-current stroke-2 transition-all cursor-pointer',
                  isSelected && 'stroke-primary stroke-[3]',
                  isHovered && 'stroke-foreground'
                )}
                fillOpacity={0.3}
                onClick={() => onClusterClick?.(cluster)}
                onMouseEnter={() => setHoveredClusterId(cluster.id)}
                onMouseLeave={() => setHoveredClusterId(null)}
              />

              {/* Cluster label */}
              {showLabels && (
                <text
                  x={pos.x}
                  y={pos.y + clusterRadius + 20}
                  className="fill-foreground text-sm font-medium"
                  textAnchor="middle"
                >
                  {cluster.label}
                </text>
              )}

              {/* Nodes within cluster */}
              {cluster.nodes.map((node, nodeIndex) => {
                const nodeAngle = (2 * Math.PI * nodeIndex) / nodeCount - Math.PI / 2;
                const nodeRadius = clusterRadius * 0.6;
                const nodeX = pos.x + nodeRadius * Math.cos(nodeAngle);
                const nodeY = pos.y + nodeRadius * Math.sin(nodeAngle);
                const nodeSize = 8 + (node.importance || 0.5) * 12;
                const isNodeSelected = node.id === selectedNodeId;

                return (
                  <g
                    key={node.id}
                    transform={`translate(${nodeX}, ${nodeY})`}
                    className="cursor-pointer"
                    onClick={(e) => {
                      e.stopPropagation();
                      onNodeClick?.(node);
                    }}
                  >
                    <circle
                      r={nodeSize}
                      className={cn(
                        NODE_COLORS[clusterIndex % NODE_COLORS.length],
                        'fill-current transition-all',
                        isNodeSelected && 'stroke-foreground stroke-2'
                      )}
                    />
                    {showLabels && nodeSize > 10 && (
                      <text
                        y={nodeSize + 12}
                        className="fill-muted-foreground text-xs"
                        textAnchor="middle"
                      >
                        {node.label.length > 8 ? node.label.slice(0, 8) + '...' : node.label}
                      </text>
                    )}
                  </g>
                );
              })}
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="absolute top-4 left-4 bg-background/90 backdrop-blur rounded-lg border p-3 space-y-2">
        <p className="text-xs font-medium text-muted-foreground">Clusters</p>
        {clusters.map((cluster, index) => (
          <button
            key={cluster.id}
            onClick={() => onClusterClick?.(cluster)}
            className={cn(
              'flex items-center gap-2 w-full px-2 py-1 rounded text-sm transition-colors',
              'hover:bg-muted',
              cluster.id === selectedClusterId && 'bg-muted'
            )}
          >
            <div
              className={cn(
                'w-3 h-3 rounded-full',
                NODE_COLORS[index % NODE_COLORS.length]
              )}
            />
            <span>{cluster.label}</span>
            <span className="text-xs text-muted-foreground ml-auto">
              {cluster.nodes.length}
            </span>
          </button>
        ))}
      </div>

      {/* Stats */}
      <div className="absolute bottom-4 left-4 bg-background/90 backdrop-blur rounded-lg border px-3 py-2 text-xs text-muted-foreground">
        {nodes.length} nodes in {clusters.length} clusters
      </div>
    </div>
  );
}
