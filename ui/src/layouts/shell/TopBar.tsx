import { Bell, Bot, Command, Menu, PanelRightOpen, Search, Settings2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/theme-toggle'
import { getShellModuleLabel, type ShellModule } from '@/layouts/shell/shell-config'
import type { ShellContext } from '@/types/shell'

interface TopBarProps {
  context?: ShellContext
  module: ShellModule
  onOpenCommandPalette: () => void
  onOpenOps: () => void
  onOpenSettings: () => void
  onOpenAgent: () => void
  onToggleLeftRailMobile: () => void
  onToggleRightRailMobile: () => void
}

function ContextChip({ label }: { label: string }) {
  return (
    <span className="inline-flex items-center rounded-full border border-border/70 bg-background/80 px-2.5 py-1 text-xs text-muted-foreground">
      {label}
    </span>
  )
}

export function TopBar({
  context,
  module,
  onOpenCommandPalette,
  onOpenOps,
  onOpenSettings,
  onOpenAgent,
  onToggleLeftRailMobile,
  onToggleRightRailMobile,
}: TopBarProps) {
  const moduleLabel = getShellModuleLabel(module)

  return (
    <header className="border-b border-border/60 bg-background/85 backdrop-blur supports-[backdrop-filter]:bg-background/70">
      <div className="flex items-center gap-2 px-4 py-3 lg:px-6">
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={onToggleLeftRailMobile}
          aria-label="Open navigation"
        >
          <Menu className="h-4 w-4" />
        </Button>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2 text-sm font-medium text-foreground">
            <span className="truncate">{context?.workspace_name || 'Workspace'}</span>
            {context?.initiative_name ? <span className="text-muted-foreground">/</span> : null}
            {context?.initiative_name ? (
              <span className="truncate text-muted-foreground">{context.initiative_name}</span>
            ) : null}
            {context?.active_project ? <span className="text-muted-foreground">/</span> : null}
            {context?.active_project ? (
              <span className="truncate">{context.active_project.label}</span>
            ) : null}
            {context?.active_task ? <span className="text-muted-foreground">/</span> : null}
            {context?.active_task ? (
              <span className="truncate text-muted-foreground">{context.active_task.label}</span>
            ) : null}
          </div>
          <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <ContextChip label={moduleLabel} />
            {context?.active_session ? (
              <ContextChip
                label={
                  context.active_session.objective ||
                  `${context.active_session.module || 'Session'} session`
                }
              />
            ) : null}
            {context?.current_user_role ? (
              <ContextChip label={context.current_user_role} />
            ) : null}
          </div>
        </div>

        <Button
          variant="outline"
          className="hidden min-w-[240px] justify-start text-muted-foreground lg:flex"
          onClick={onOpenCommandPalette}
        >
          <Search className="mr-2 h-4 w-4" />
          Search routes, sessions, and actions
          <span className="ml-auto inline-flex items-center gap-1 rounded-md border bg-muted px-1.5 py-0.5 text-[10px] uppercase">
            <Command className="h-3 w-3" />
            K
          </span>
        </Button>

        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" onClick={onOpenAgent} aria-label="Open agent">
            <Bot className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={onOpenOps} aria-label="Open operations">
            <Bell className="h-4 w-4" />
          </Button>
          <ThemeToggle />
          <Button variant="ghost" size="icon" onClick={onOpenSettings} aria-label="Open settings">
            <Settings2 className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="xl:hidden"
            onClick={onToggleRightRailMobile}
            aria-label="Open context rail"
          >
            <PanelRightOpen className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  )
}
