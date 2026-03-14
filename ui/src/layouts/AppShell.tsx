import { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'

import { shellApi } from '@/api/shell'
import { CenterViewport } from '@/layouts/shell/CenterViewport'
import { CommandPalette } from '@/layouts/shell/CommandPalette'
import { LeftRail } from '@/layouts/shell/LeftRail'
import { OpsOverlay } from '@/layouts/shell/OpsOverlay'
import { RightRail } from '@/layouts/shell/RightRail'
import { SettingsDialog } from '@/layouts/shell/SettingsDialog'
import { TopBar } from '@/layouts/shell/TopBar'
import { getShellModuleFromPath, getShellModuleLabel } from '@/layouts/shell/shell-config'
import { cn } from '@/lib/utils'
import { useShellLayoutStore } from '@/stores/shell-layout-store'
import { TourPanel } from '@/tour/TourPanel'

function MobileOverlay({
  open,
  side,
  onClose,
  children,
}: {
  open: boolean
  side: 'left' | 'right'
  onClose: () => void
  children: React.ReactNode
}) {
  return (
    <div
      className={cn(
        'fixed inset-0 z-40 bg-black/40 transition-opacity xl:hidden',
        open ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'
      )}
      onClick={onClose}
    >
      <div
        className={cn(
          'absolute top-0 h-full w-[86vw] max-w-[360px] bg-background shadow-2xl transition-transform',
          side === 'left' ? 'left-0' : 'right-0',
          open
            ? 'translate-x-0'
            : side === 'left'
              ? '-translate-x-full'
              : 'translate-x-full'
        )}
        onClick={(event) => event.stopPropagation()}
      >
        {children}
      </div>
    </div>
  )
}

export function AppShell() {
  const navigate = useNavigate()
  const location = useLocation()
  const module = getShellModuleFromPath(location.pathname)
  const moduleLabel = getShellModuleLabel(module)
  const {
    commandPaletteOpen,
    opsOverlayOpen,
    settingsOpen,
    leftRailMobileOpen,
    rightRailMobileOpen,
    setCommandPaletteOpen,
    setOpsOverlayOpen,
    setSettingsOpen,
    setLeftRailMobileOpen,
    setRightRailMobileOpen,
  } = useShellLayoutStore()

  const contextQuery = useQuery({
    queryKey: ['shell-context'],
    queryFn: () => shellApi.getContext(),
  })

  const opsSummaryQuery = useQuery({
    queryKey: ['ops-summary'],
    queryFn: () => shellApi.getOpsSummary(),
  })

  const rightRailQuery = useQuery({
    queryKey: ['shell-right-rail', module],
    queryFn: () => shellApi.getRightRail(module),
  })

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        setCommandPaletteOpen(true)
        return
      }

      if ((event.metaKey || event.ctrlKey) && event.shiftKey && event.key.toLowerCase() === 'o') {
        event.preventDefault()
        setOpsOverlayOpen(true)
        return
      }

      if (event.key === 'Escape') {
        setLeftRailMobileOpen(false)
        setRightRailMobileOpen(false)
      }
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [setCommandPaletteOpen, setLeftRailMobileOpen, setOpsOverlayOpen, setRightRailMobileOpen])

  useEffect(() => {
    setLeftRailMobileOpen(false)
    setRightRailMobileOpen(false)
  }, [location.pathname, setLeftRailMobileOpen, setRightRailMobileOpen])

  const openAgent = () => {
    navigate('/research')
    setLeftRailMobileOpen(false)
    setRightRailMobileOpen(false)
  }

  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden bg-[radial-gradient(circle_at_top,_rgba(99,102,241,0.08),_transparent_40%),linear-gradient(to_bottom,_hsl(var(--background)),_hsl(var(--muted)/0.6))]">
      <TopBar
        context={contextQuery.data}
        module={module}
        onOpenCommandPalette={() => setCommandPaletteOpen(true)}
        onOpenOps={() => setOpsOverlayOpen(true)}
        onOpenSettings={() => setSettingsOpen(true)}
        onOpenAgent={openAgent}
        onToggleLeftRailMobile={() => setLeftRailMobileOpen(true)}
        onToggleRightRailMobile={() => setRightRailMobileOpen(true)}
      />

      <div className="min-h-0 flex-1">
        <div className="hidden h-full xl:block">
          <PanelGroup direction="horizontal" autoSaveId="app-shell-layout">
            <Panel defaultSize={19} minSize={14} maxSize={24} className="min-w-[240px]">
              <LeftRail
                onOpenSettings={() => setSettingsOpen(true)}
                workspaceName={contextQuery.data?.workspace_name}
                role={contextQuery.data?.current_user_role}
              />
            </Panel>
            <PanelResizeHandle className="shell-resize-handle" />
            <Panel defaultSize={56} minSize={38}>
              <CenterViewport />
            </Panel>
            <PanelResizeHandle className="shell-resize-handle" />
            <Panel defaultSize={25} minSize={18} maxSize={32} className="min-w-[300px]">
              <RightRail
                data={rightRailQuery.data}
                isLoading={rightRailQuery.isLoading}
                moduleLabel={moduleLabel}
                onOpenAgent={openAgent}
              />
            </Panel>
          </PanelGroup>
        </div>

        <div className="h-full xl:hidden">
          <CenterViewport />
        </div>
      </div>

      <MobileOverlay
        open={leftRailMobileOpen}
        side="left"
        onClose={() => setLeftRailMobileOpen(false)}
      >
        <LeftRail
          onNavigate={() => setLeftRailMobileOpen(false)}
          onOpenSettings={() => {
            setLeftRailMobileOpen(false)
            setSettingsOpen(true)
          }}
          workspaceName={contextQuery.data?.workspace_name}
          role={contextQuery.data?.current_user_role}
        />
      </MobileOverlay>

      <MobileOverlay
        open={rightRailMobileOpen}
        side="right"
        onClose={() => setRightRailMobileOpen(false)}
      >
        <RightRail
          data={rightRailQuery.data}
          isLoading={rightRailQuery.isLoading}
          moduleLabel={moduleLabel}
          onOpenAgent={() => {
            setRightRailMobileOpen(false)
            openAgent()
          }}
        />
      </MobileOverlay>

      <CommandPalette
        open={commandPaletteOpen}
        onOpenChange={setCommandPaletteOpen}
        context={contextQuery.data}
        onOpenOps={() => setOpsOverlayOpen(true)}
        onOpenSettings={() => setSettingsOpen(true)}
        onOpenAgent={openAgent}
      />

      <OpsOverlay
        open={opsOverlayOpen}
        onOpenChange={setOpsOverlayOpen}
        summary={opsSummaryQuery.data}
        isLoading={opsSummaryQuery.isLoading}
      />

      <SettingsDialog
        open={settingsOpen}
        onOpenChange={setSettingsOpen}
        models={contextQuery.data?.available_models ?? []}
      />

      <TourPanel />
    </div>
  )
}
