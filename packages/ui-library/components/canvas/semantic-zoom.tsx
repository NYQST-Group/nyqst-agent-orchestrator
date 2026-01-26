/**
 * Semantic Zoom Components
 *
 * Based on research findings:
 * - Information changes at different scales
 * - 80% of users prefer overview for navigation
 * - Users are faster with rich navigation cues
 * - Detail-on-demand controlled by zoom level
 */

import * as React from 'react';
import { createContext, useContext, useState, useCallback } from 'react';
import { cn } from '../../lib/utils';

export type ZoomLevel = 'overview' | 'summary' | 'detail' | 'full';

interface ZoomContextValue {
  zoom: number;
  zoomLevel: ZoomLevel;
  setZoom: (zoom: number) => void;
  zoomIn: () => void;
  zoomOut: () => void;
  resetZoom: () => void;
}

const ZoomContext = createContext<ZoomContextValue | null>(null);

export function useZoomContext() {
  const context = useContext(ZoomContext);
  if (!context) {
    throw new Error('useZoomContext must be used within SemanticZoomProvider');
  }
  return context;
}

function getZoomLevel(zoom: number): ZoomLevel {
  if (zoom < 0.3) return 'overview';
  if (zoom < 0.6) return 'summary';
  if (zoom < 1.2) return 'detail';
  return 'full';
}

interface SemanticZoomProviderProps {
  children: React.ReactNode;
  defaultZoom?: number;
  minZoom?: number;
  maxZoom?: number;
  zoomStep?: number;
}

export function SemanticZoomProvider({
  children,
  defaultZoom = 1,
  minZoom = 0.1,
  maxZoom = 3,
  zoomStep = 0.2,
}: SemanticZoomProviderProps) {
  const [zoom, setZoomState] = useState(defaultZoom);

  const setZoom = useCallback((newZoom: number) => {
    setZoomState(Math.max(minZoom, Math.min(maxZoom, newZoom)));
  }, [minZoom, maxZoom]);

  const zoomIn = useCallback(() => {
    setZoom(zoom + zoomStep);
  }, [zoom, zoomStep, setZoom]);

  const zoomOut = useCallback(() => {
    setZoom(zoom - zoomStep);
  }, [zoom, zoomStep, setZoom]);

  const resetZoom = useCallback(() => {
    setZoom(1);
  }, [setZoom]);

  const zoomLevel = getZoomLevel(zoom);

  return (
    <ZoomContext.Provider value={{ zoom, zoomLevel, setZoom, zoomIn, zoomOut, resetZoom }}>
      {children}
    </ZoomContext.Provider>
  );
}

interface SemanticZoomProps {
  children: React.ReactNode;
  className?: string;
  showControls?: boolean;
  showLevelIndicator?: boolean;
}

export function SemanticZoom({
  children,
  className,
  showControls = true,
  showLevelIndicator = true,
}: SemanticZoomProps) {
  const { zoom, zoomLevel, zoomIn, zoomOut, resetZoom } = useZoomContext();

  return (
    <div className={cn('relative', className)}>
      {children}

      {/* Zoom controls */}
      {showControls && (
        <div className="absolute bottom-4 right-4 flex items-center gap-1 bg-background/90 backdrop-blur rounded-lg border shadow-sm p-1">
          <button
            onClick={zoomOut}
            className="w-8 h-8 flex items-center justify-center rounded hover:bg-muted transition-colors"
            title="Zoom out"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="8" y1="11" x2="14" y2="11" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
          </button>

          <button
            onClick={resetZoom}
            className="px-2 h-8 flex items-center justify-center rounded hover:bg-muted transition-colors text-sm font-mono min-w-[48px]"
            title="Reset zoom"
          >
            {Math.round(zoom * 100)}%
          </button>

          <button
            onClick={zoomIn}
            className="w-8 h-8 flex items-center justify-center rounded hover:bg-muted transition-colors"
            title="Zoom in"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="11" y1="8" x2="11" y2="14" />
              <line x1="8" y1="11" x2="14" y2="11" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
          </button>
        </div>
      )}

      {/* Zoom level indicator */}
      {showLevelIndicator && (
        <div className="absolute top-4 right-4 bg-background/90 backdrop-blur rounded-lg border shadow-sm px-3 py-1.5">
          <div className="flex items-center gap-2">
            {(['overview', 'summary', 'detail', 'full'] as ZoomLevel[]).map((level) => (
              <div
                key={level}
                className={cn(
                  'w-2 h-2 rounded-full transition-colors',
                  level === zoomLevel ? 'bg-primary' : 'bg-muted-foreground/30'
                )}
                title={level}
              />
            ))}
          </div>
          <p className="text-xs text-muted-foreground mt-1 capitalize">{zoomLevel}</p>
        </div>
      )}
    </div>
  );
}

/**
 * Wrapper that renders different content based on zoom level
 */
interface ZoomSensitiveProps {
  overview?: React.ReactNode;
  summary?: React.ReactNode;
  detail?: React.ReactNode;
  full?: React.ReactNode;
  fallback?: React.ReactNode;
}

export function ZoomSensitive({ overview, summary, detail, full, fallback }: ZoomSensitiveProps) {
  const { zoomLevel } = useZoomContext();

  switch (zoomLevel) {
    case 'overview':
      return <>{overview ?? fallback}</>;
    case 'summary':
      return <>{summary ?? detail ?? fallback}</>;
    case 'detail':
      return <>{detail ?? fallback}</>;
    case 'full':
      return <>{full ?? detail ?? fallback}</>;
    default:
      return <>{fallback}</>;
  }
}
