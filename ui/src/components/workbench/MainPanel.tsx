/**
 * Main content panel with tab management
 */

import { X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'
import { useWorkbenchStore } from '@/stores/workbench-store'
import { ArtifactViewer } from '@/components/artifacts/ArtifactViewer'
import { RunViewer } from '@/components/runs/RunViewer'
import { PointerViewer } from '@/components/pointers/PointerViewer'
import { ManifestViewer } from '@/components/manifests/ManifestViewer'

function TabBar() {
  const { tabs, activeTabId, setActiveTab, closeTab } = useWorkbenchStore()

  if (tabs.length === 0) {
    return null
  }

  return (
    <div className="flex h-9 items-center gap-0.5 border-b bg-muted/50 px-2">
      {tabs.map((tab) => (
        <div
          key={tab.id}
          className={cn(
            'group flex h-7 items-center gap-1 rounded-t-md border border-b-0 px-3 text-sm cursor-pointer',
            activeTabId === tab.id
              ? 'bg-background border-border'
              : 'bg-muted/50 border-transparent hover:bg-muted'
          )}
          onClick={() => setActiveTab(tab.id)}
        >
          <span className="truncate max-w-[120px]">{tab.title}</span>
          <Button
            variant="ghost"
            size="icon"
            className="h-4 w-4 opacity-0 group-hover:opacity-100"
            onClick={(e) => {
              e.stopPropagation()
              closeTab(tab.id)
            }}
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      ))}
    </div>
  )
}

function TabContent() {
  const { tabs, activeTabId } = useWorkbenchStore()
  const activeTab = tabs.find((t) => t.id === activeTabId)

  if (!activeTab) {
    return (
      <div className="flex h-full items-center justify-center text-muted-foreground">
        <div className="text-center">
          <p className="text-lg">No content selected</p>
          <p className="text-sm mt-2">
            Select a pointer, artifact, or run from the explorer to view details
          </p>
        </div>
      </div>
    )
  }

  switch (activeTab.type) {
    case 'artifact':
      return <ArtifactViewer sha256={activeTab.resourceId} />
    case 'run':
      return <RunViewer runId={activeTab.resourceId} />
    case 'pointer':
      return <PointerViewer pointerId={activeTab.resourceId} />
    case 'manifest':
      return <ManifestViewer sha256={activeTab.resourceId} />
    default:
      return (
        <div className="flex h-full items-center justify-center text-muted-foreground">
          Unknown content type
        </div>
      )
  }
}

export function MainPanel() {
  return (
    <div className="flex h-full flex-col bg-background">
      <TabBar />
      <ScrollArea className="flex-1">
        <TabContent />
      </ScrollArea>
    </div>
  )
}
