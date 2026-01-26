import { Suspense, lazy, useCallback } from 'react';
import {
  Panel,
  PanelGroup,
  PanelResizeHandle,
} from 'react-resizable-panels';
import { ErrorBoundary } from 'react-error-boundary';
import {
  Menu,
  Search,
  Settings,
  ChevronLeft,
  ChevronRight,
  Command,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useWorkspaceStore } from '@/stores/workspace-store';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { ComponentErrorFallback } from '@/components/async/error-fallback';
import { PanelLoader } from '@/components/async/loading-states';
import { PaneTabBar } from './pane-tab-bar';
import { WorkbenchSidebar } from './workbench-sidebar';
import { CommandPalette } from './command-palette';
import type { PaneType } from '@/stores/workspace-store';

// Lazy load pane content components for code splitting
const ChatPane = lazy(() => import('@/components/panes/chat-pane').then(m => ({ default: m.ChatPane })));
const RunExplorerPane = lazy(() => import('@/components/panes/run-explorer-pane').then(m => ({ default: m.RunExplorerPane })));
const ArtifactBrowserPane = lazy(() => import('@/components/panes/artifact-browser-pane').then(m => ({ default: m.ArtifactBrowserPane })));
const DocumentViewerPane = lazy(() => import('@/components/panes/document-viewer-pane').then(m => ({ default: m.DocumentViewerPane })));
const GovernancePane = lazy(() => import('@/components/panes/governance-pane').then(m => ({ default: m.GovernancePane })));
const ProvenancePane = lazy(() => import('@/components/panes/provenance-pane').then(m => ({ default: m.ProvenancePane })));

// Pane component mapping
const PANE_COMPONENTS: Record<PaneType, React.LazyExoticComponent<React.ComponentType<{ paneId: string }>>> = {
  'chat': ChatPane,
  'planner': ChatPane, // Reuse chat for now
  'run-explorer': RunExplorerPane,
  'artifact-browser': ArtifactBrowserPane,
  'document-viewer': DocumentViewerPane,
  'table-viewer': DocumentViewerPane, // Placeholder
  'graph-viewer': DocumentViewerPane, // Placeholder
  'diff-viewer': DocumentViewerPane, // Placeholder
  'context-pinboard': ArtifactBrowserPane, // Placeholder
  'evaluations': GovernancePane, // Placeholder
  'provenance': ProvenancePane,
  'governance': GovernancePane,
  'admin': GovernancePane, // Placeholder
};

export function WorkbenchShell() {
  const {
    layout,
    sidebarCollapsed,
    commandPaletteOpen,
    toggleSidebar,
    setCommandPaletteOpen,
    setActivePane,
    removePane,
    resizeGroup,
  } = useWorkspaceStore();

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      // Cmd/Ctrl + K for command palette
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(true);
      }
    },
    [setCommandPaletteOpen]
  );

  return (
    <TooltipProvider>
      <div
        className="h-screen w-screen flex flex-col bg-background overflow-hidden"
        onKeyDown={handleKeyDown}
        tabIndex={-1}
      >
        {/* Top bar */}
        <header className="h-12 flex items-center justify-between px-4 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={toggleSidebar}
              aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              {sidebarCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
            </Button>
            <Separator orientation="vertical" className="h-6" />
            <span className="font-semibold text-sm">NYQST Intelli</span>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="w-64 justify-start text-muted-foreground"
              onClick={() => setCommandPaletteOpen(true)}
            >
              <Search className="h-4 w-4 mr-2" />
              <span>Search or run command...</span>
              <kbd className="ml-auto text-xs bg-muted px-1.5 py-0.5 rounded">
                <Command className="h-3 w-3 inline" />K
              </kbd>
            </Button>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon-sm">
                  <Settings className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Settings</TooltipContent>
            </Tooltip>
          </div>
        </header>

        {/* Main content area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Sidebar */}
          <aside
            className={cn(
              'border-r bg-muted/30 transition-all duration-200 overflow-hidden',
              sidebarCollapsed ? 'w-12' : 'w-60'
            )}
          >
            <WorkbenchSidebar collapsed={sidebarCollapsed} />
          </aside>

          {/* Pane groups */}
          <main className="flex-1 overflow-hidden">
            <PanelGroup
              direction={layout.orientation}
              onLayout={(sizes) => {
                // Update group sizes in store
                layout.groups.forEach((group, index) => {
                  if (sizes[index] !== undefined) {
                    resizeGroup(group.id, sizes[index]);
                  }
                });
              }}
            >
              {layout.groups.map((group, groupIndex) => (
                <Suspense key={group.id} fallback={<PanelLoader />}>
                  {groupIndex > 0 && (
                    <PanelResizeHandle className="w-1 hover:bg-primary/20 transition-colors" />
                  )}
                  <Panel
                    id={group.id}
                    defaultSize={group.size ?? 100 / layout.groups.length}
                    minSize={10}
                  >
                    <div className="h-full flex flex-col">
                      {/* Tab bar */}
                      <PaneTabBar
                        groupId={group.id}
                        panes={group.panes}
                        activePane={group.activePane}
                        onTabSelect={(paneId) => setActivePane(group.id, paneId)}
                        onTabClose={(paneId) => removePane(group.id, paneId)}
                      />

                      {/* Pane content */}
                      <div className="flex-1 overflow-hidden">
                        <ErrorBoundary
                          FallbackComponent={ComponentErrorFallback}
                          resetKeys={[group.activePane]}
                        >
                          <Suspense fallback={<PanelLoader />}>
                            {group.activePane && group.panes.find(p => p.id === group.activePane) && (
                              <PaneContent
                                paneId={group.activePane}
                                paneType={group.panes.find(p => p.id === group.activePane)!.type}
                              />
                            )}
                            {(!group.activePane || !group.panes.find(p => p.id === group.activePane)) && (
                              <div className="h-full flex items-center justify-center text-muted-foreground">
                                <p>No pane selected</p>
                              </div>
                            )}
                          </Suspense>
                        </ErrorBoundary>
                      </div>
                    </div>
                  </Panel>
                </Suspense>
              ))}
            </PanelGroup>
          </main>
        </div>

        {/* Status bar */}
        <footer className="h-6 flex items-center justify-between px-4 border-t bg-muted/30 text-xs text-muted-foreground">
          <div className="flex items-center gap-4">
            <span>Ready</span>
          </div>
          <div className="flex items-center gap-4">
            <span>v0.1.0</span>
          </div>
        </footer>

        {/* Command palette */}
        <CommandPalette
          open={commandPaletteOpen}
          onOpenChange={setCommandPaletteOpen}
        />
      </div>
    </TooltipProvider>
  );
}

function PaneContent({ paneId, paneType }: { paneId: string; paneType: PaneType }) {
  const Component = PANE_COMPONENTS[paneType];

  if (!Component) {
    return (
      <div className="h-full flex items-center justify-center text-muted-foreground">
        <p>Unknown pane type: {paneType}</p>
      </div>
    );
  }

  return <Component paneId={paneId} />;
}
