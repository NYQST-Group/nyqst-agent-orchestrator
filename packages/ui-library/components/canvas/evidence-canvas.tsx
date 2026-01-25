/**
 * Evidence Canvas Component
 *
 * Based on research into spatial interfaces:
 * - tldraw's infinite canvas with AI features
 * - Heptabase's card-based knowledge mapping
 * - Graph visualization for claims/sources/relationships
 *
 * Key patterns applied:
 * - Semantic zoom (detail changes at different scales)
 * - Force-directed layout for clustering
 * - Progressive disclosure with interactive zooming
 */

import * as React from 'react';
import { useState, useRef, useCallback, useEffect } from 'react';
import { cn } from '../../lib/utils';

export interface EvidenceNode {
  id: string;
  type: 'claim' | 'source' | 'artifact' | 'decision';
  title: string;
  content?: string;
  x: number;
  y: number;
  width?: number;
  height?: number;
  confidence?: number;
  status?: 'verified' | 'disputed' | 'pending' | 'rejected';
  metadata?: Record<string, unknown>;
}

export interface EvidenceEdge {
  id: string;
  source: string;
  target: string;
  type: 'supports' | 'contradicts' | 'derives' | 'references';
  strength?: number; // 0-1
  label?: string;
}

interface EvidenceCanvasProps {
  nodes: EvidenceNode[];
  edges: EvidenceEdge[];
  className?: string;
  onNodeClick?: (node: EvidenceNode) => void;
  onNodeDrag?: (nodeId: string, x: number, y: number) => void;
  onEdgeClick?: (edge: EvidenceEdge) => void;
  selectedNodeId?: string;
  zoomLevel?: number;
  onZoomChange?: (zoom: number) => void;
  minZoom?: number;
  maxZoom?: number;
}

const NODE_TYPE_STYLES: Record<EvidenceNode['type'], { bg: string; border: string; icon: string }> = {
  claim: {
    bg: 'bg-blue-50 dark:bg-blue-900/20',
    border: 'border-blue-300 dark:border-blue-700',
    icon: '!',
  },
  source: {
    bg: 'bg-green-50 dark:bg-green-900/20',
    border: 'border-green-300 dark:border-green-700',
    icon: '@',
  },
  artifact: {
    bg: 'bg-purple-50 dark:bg-purple-900/20',
    border: 'border-purple-300 dark:border-purple-700',
    icon: '#',
  },
  decision: {
    bg: 'bg-orange-50 dark:bg-orange-900/20',
    border: 'border-orange-300 dark:border-orange-700',
    icon: '>',
  },
};

const EDGE_TYPE_STYLES: Record<EvidenceEdge['type'], { color: string; dash?: string }> = {
  supports: { color: 'stroke-green-500' },
  contradicts: { color: 'stroke-red-500', dash: '5,5' },
  derives: { color: 'stroke-blue-500' },
  references: { color: 'stroke-muted-foreground', dash: '2,2' },
};

const STATUS_INDICATORS: Record<NonNullable<EvidenceNode['status']>, string> = {
  verified: 'bg-green-500',
  disputed: 'bg-yellow-500',
  pending: 'bg-blue-500',
  rejected: 'bg-red-500',
};

export function EvidenceCanvas({
  nodes,
  edges,
  className,
  onNodeClick,
  onNodeDrag,
  onEdgeClick,
  selectedNodeId,
  zoomLevel: controlledZoom,
  onZoomChange,
  minZoom = 0.1,
  maxZoom = 3,
}: EvidenceCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [internalZoom, setInternalZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragNodeId, setDragNodeId] = useState<string | null>(null);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const zoom = controlledZoom ?? internalZoom;

  const handleZoom = useCallback((delta: number) => {
    const newZoom = Math.max(minZoom, Math.min(maxZoom, zoom + delta));
    if (onZoomChange) {
      onZoomChange(newZoom);
    } else {
      setInternalZoom(newZoom);
    }
  }, [zoom, minZoom, maxZoom, onZoomChange]);

  const handleWheel = useCallback((e: React.WheelEvent) => {
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault();
      handleZoom(-e.deltaY * 0.001);
    } else {
      setPan(prev => ({
        x: prev.x - e.deltaX,
        y: prev.y - e.deltaY,
      }));
    }
  }, [handleZoom]);

  const handleMouseDown = useCallback((e: React.MouseEvent, nodeId?: string) => {
    if (nodeId) {
      setDragNodeId(nodeId);
    } else {
      setIsDragging(true);
    }
    setDragStart({ x: e.clientX, y: e.clientY });
  }, []);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (dragNodeId && onNodeDrag) {
      const dx = (e.clientX - dragStart.x) / zoom;
      const dy = (e.clientY - dragStart.y) / zoom;
      const node = nodes.find(n => n.id === dragNodeId);
      if (node) {
        onNodeDrag(dragNodeId, node.x + dx, node.y + dy);
      }
      setDragStart({ x: e.clientX, y: e.clientY });
    } else if (isDragging) {
      setPan(prev => ({
        x: prev.x + (e.clientX - dragStart.x),
        y: prev.y + (e.clientY - dragStart.y),
      }));
      setDragStart({ x: e.clientX, y: e.clientY });
    }
  }, [dragNodeId, isDragging, dragStart, zoom, nodes, onNodeDrag]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
    setDragNodeId(null);
  }, []);

  // Calculate viewport bounds for culling
  const viewportBounds = containerRef.current ? {
    left: -pan.x / zoom,
    top: -pan.y / zoom,
    right: (-pan.x + containerRef.current.clientWidth) / zoom,
    bottom: (-pan.y + containerRef.current.clientHeight) / zoom,
  } : null;

  // Filter visible nodes (viewport culling for performance)
  const visibleNodes = viewportBounds
    ? nodes.filter(node => {
        const nodeRight = node.x + (node.width || 200);
        const nodeBottom = node.y + (node.height || 100);
        return (
          nodeRight >= viewportBounds.left &&
          node.x <= viewportBounds.right &&
          nodeBottom >= viewportBounds.top &&
          node.y <= viewportBounds.bottom
        );
      })
    : nodes;

  // Build node lookup for edge rendering
  const nodeMap = new Map(nodes.map(n => [n.id, n]));

  // Determine detail level based on zoom (semantic zoom)
  const detailLevel: 'minimal' | 'compact' | 'full' =
    zoom < 0.3 ? 'minimal' : zoom < 0.7 ? 'compact' : 'full';

  return (
    <div
      ref={containerRef}
      className={cn(
        'relative overflow-hidden bg-muted/30 rounded-lg border',
        isDragging ? 'cursor-grabbing' : 'cursor-grab',
        className
      )}
      onWheel={handleWheel}
      onMouseDown={(e) => handleMouseDown(e)}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      {/* SVG layer for edges */}
      <svg
        className="absolute inset-0 pointer-events-none"
        style={{
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
          transformOrigin: '0 0',
        }}
      >
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" className="fill-muted-foreground" />
          </marker>
        </defs>
        {edges.map((edge) => {
          const sourceNode = nodeMap.get(edge.source);
          const targetNode = nodeMap.get(edge.target);
          if (!sourceNode || !targetNode) return null;

          const style = EDGE_TYPE_STYLES[edge.type];
          const sourceX = sourceNode.x + (sourceNode.width || 200) / 2;
          const sourceY = sourceNode.y + (sourceNode.height || 100) / 2;
          const targetX = targetNode.x + (targetNode.width || 200) / 2;
          const targetY = targetNode.y + (targetNode.height || 100) / 2;

          return (
            <g key={edge.id}>
              <line
                x1={sourceX}
                y1={sourceY}
                x2={targetX}
                y2={targetY}
                className={cn(style.color, 'pointer-events-auto cursor-pointer')}
                strokeWidth={2 / zoom}
                strokeDasharray={style.dash}
                markerEnd="url(#arrowhead)"
                onClick={() => onEdgeClick?.(edge)}
              />
              {detailLevel === 'full' && edge.label && (
                <text
                  x={(sourceX + targetX) / 2}
                  y={(sourceY + targetY) / 2 - 8}
                  className="fill-muted-foreground text-xs"
                  textAnchor="middle"
                  style={{ fontSize: `${10 / zoom}px` }}
                >
                  {edge.label}
                </text>
              )}
            </g>
          );
        })}
      </svg>

      {/* Nodes layer */}
      <div
        className="absolute inset-0"
        style={{
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
          transformOrigin: '0 0',
        }}
      >
        {visibleNodes.map((node) => {
          const typeStyle = NODE_TYPE_STYLES[node.type];
          const isSelected = node.id === selectedNodeId;

          return (
            <div
              key={node.id}
              className={cn(
                'absolute rounded-lg border-2 transition-shadow',
                typeStyle.bg,
                typeStyle.border,
                isSelected && 'ring-2 ring-primary ring-offset-2',
                dragNodeId === node.id ? 'cursor-grabbing' : 'cursor-grab'
              )}
              style={{
                left: node.x,
                top: node.y,
                width: node.width || 200,
                minHeight: detailLevel === 'minimal' ? 40 : detailLevel === 'compact' ? 60 : 100,
              }}
              onMouseDown={(e) => {
                e.stopPropagation();
                handleMouseDown(e, node.id);
              }}
              onClick={() => onNodeClick?.(node)}
            >
              {/* Status indicator */}
              {node.status && (
                <div
                  className={cn(
                    'absolute -top-1 -right-1 w-3 h-3 rounded-full border-2 border-background',
                    STATUS_INDICATORS[node.status]
                  )}
                />
              )}

              {/* Content based on detail level */}
              <div className="p-2">
                <div className="flex items-center gap-1">
                  <span className="text-xs font-mono opacity-50">{typeStyle.icon}</span>
                  <span className={cn(
                    'font-medium truncate',
                    detailLevel === 'minimal' ? 'text-xs' : 'text-sm'
                  )}>
                    {node.title}
                  </span>
                </div>

                {detailLevel === 'full' && node.content && (
                  <p className="mt-1 text-xs text-muted-foreground line-clamp-3">
                    {node.content}
                  </p>
                )}

                {detailLevel !== 'minimal' && node.confidence !== undefined && (
                  <div className="mt-2 flex items-center gap-1">
                    <div className="flex-1 h-1 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary"
                        style={{ width: `${node.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {Math.round(node.confidence * 100)}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Zoom controls */}
      <div className="absolute bottom-4 right-4 flex items-center gap-1 bg-background/80 backdrop-blur rounded-lg border p-1">
        <button
          onClick={() => handleZoom(-0.2)}
          className="w-8 h-8 flex items-center justify-center rounded hover:bg-muted"
        >
          -
        </button>
        <span className="w-12 text-center text-sm">{Math.round(zoom * 100)}%</span>
        <button
          onClick={() => handleZoom(0.2)}
          className="w-8 h-8 flex items-center justify-center rounded hover:bg-muted"
        >
          +
        </button>
        <button
          onClick={() => {
            setPan({ x: 0, y: 0 });
            handleZoom(1 - zoom);
          }}
          className="w-8 h-8 flex items-center justify-center rounded hover:bg-muted text-xs"
        >
          1:1
        </button>
      </div>

      {/* Legend */}
      <div className="absolute top-4 left-4 bg-background/80 backdrop-blur rounded-lg border p-2 text-xs space-y-1">
        {Object.entries(NODE_TYPE_STYLES).map(([type, style]) => (
          <div key={type} className="flex items-center gap-2">
            <div className={cn('w-3 h-3 rounded border', style.bg, style.border)} />
            <span className="capitalize">{type}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
