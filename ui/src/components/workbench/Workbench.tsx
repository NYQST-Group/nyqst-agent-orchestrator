/**
 * Main Workbench layout component
 *
 * IDE-like layout with resizable panels:
 * - Left: Explorer (pointers, artifacts, runs)
 * - Center: Main content (tabs with viewers/editors)
 * - Right: Details/properties panel
 * - Bottom: Timeline/events panel (collapsible)
 */

import {
  Panel,
  PanelGroup,
  PanelResizeHandle,
} from 'react-resizable-panels'
import { useWorkbenchStore } from '@/stores/workbench-store'
import { ExplorerPanel } from './ExplorerPanel'
import { MainPanel } from './MainPanel'
import { DetailsPanel } from './DetailsPanel'
import { TimelinePanel } from './TimelinePanel'
import { WorkbenchHeader } from './WorkbenchHeader'
import { cn } from '@/lib/utils'

export function Workbench() {
  const {
    leftPanelCollapsed,
    rightPanelCollapsed,
    bottomPanelCollapsed,
    leftPanelSize,
    rightPanelSize,
    bottomPanelSize,
    setLeftPanelSize,
    setRightPanelSize,
    setBottomPanelSize,
  } = useWorkbenchStore()

  return (
    <div className="flex h-screen flex-col bg-background">
      <WorkbenchHeader />

      <PanelGroup direction="vertical" className="flex-1">
        {/* Main horizontal layout */}
        <Panel defaultSize={100 - bottomPanelSize}>
          <PanelGroup direction="horizontal">
            {/* Left Explorer Panel */}
            {!leftPanelCollapsed && (
              <>
                <Panel
                  defaultSize={leftPanelSize}
                  minSize={15}
                  maxSize={40}
                  onResize={setLeftPanelSize}
                >
                  <ExplorerPanel />
                </Panel>
                <PanelResizeHandle className={cn('w-1 resize-handle')} />
              </>
            )}

            {/* Center Main Panel */}
            <Panel minSize={30}>
              <MainPanel />
            </Panel>

            {/* Right Details Panel */}
            {!rightPanelCollapsed && (
              <>
                <PanelResizeHandle className={cn('w-1 resize-handle')} />
                <Panel
                  defaultSize={rightPanelSize}
                  minSize={15}
                  maxSize={50}
                  onResize={setRightPanelSize}
                >
                  <DetailsPanel />
                </Panel>
              </>
            )}
          </PanelGroup>
        </Panel>

        {/* Bottom Timeline Panel */}
        {!bottomPanelCollapsed && (
          <>
            <PanelResizeHandle className={cn('h-1 resize-handle')} />
            <Panel
              defaultSize={bottomPanelSize}
              minSize={10}
              maxSize={50}
              onResize={setBottomPanelSize}
            >
              <TimelinePanel />
            </Panel>
          </>
        )}
      </PanelGroup>
    </div>
  )
}
