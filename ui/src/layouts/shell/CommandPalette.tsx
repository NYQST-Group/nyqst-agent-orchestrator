import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Bell,
  Bot,
  BriefcaseBusiness,
  Command,
  LayoutGrid,
  Search,
  Settings2,
} from 'lucide-react'

import {
  Dialog,
  DialogContent,
  DialogTitle,
} from '@/components/ui/dialog'
import { SHELL_NAV_ITEMS } from '@/layouts/shell/shell-config'
import type { ShellContext } from '@/types/shell'
import { useShellLayoutStore } from '@/stores/shell-layout-store'

interface CommandPaletteProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  context?: ShellContext
  onOpenOps: () => void
  onOpenSettings: () => void
  onOpenAgent: () => void
}

type CommandItem = {
  id: string
  label: string
  description: string
  group: string
  icon: React.ComponentType<{ className?: string }>
  action: () => void
}

export function CommandPalette({
  open,
  onOpenChange,
  context,
  onOpenOps,
  onOpenSettings,
  onOpenAgent,
}: CommandPaletteProps) {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const { preferredModelId } = useShellLayoutStore()

  const commands = useMemo<CommandItem[]>(() => {
    const routeCommands = SHELL_NAV_ITEMS.map((item) => ({
      id: item.to,
      label: item.label,
      description: item.description,
      group: 'Navigate',
      icon: item.icon,
      action: () => {
        navigate(item.to)
        onOpenChange(false)
      },
    }))

    const recentCommands = (context?.recent_entities ?? []).map((entity) => ({
      id: `recent-${entity.id}`,
      label: entity.label,
      description: entity.subtitle || 'Recent workspace entity',
      group: 'Recent',
      icon: BriefcaseBusiness,
      action: () => {
        if (entity.href) navigate(entity.href)
        onOpenChange(false)
      },
    }))

    return [
      ...routeCommands,
      ...recentCommands,
      {
        id: 'open-agent',
        label: 'Open agent workspace',
        description: preferredModelId
          ? `Launch the assistant with ${preferredModelId}`
          : 'Jump into the research assistant',
        group: 'Actions',
        icon: Bot,
        action: () => {
          onOpenAgent()
          onOpenChange(false)
        },
      },
      {
        id: 'open-ops',
        label: 'Open operations centre',
        description: 'Review live runs, queued work, and failures',
        group: 'Actions',
        icon: Bell,
        action: () => {
          onOpenOps()
          onOpenChange(false)
        },
      },
      {
        id: 'open-settings',
        label: 'Open studio settings',
        description: 'Change theme and default model preference',
        group: 'Actions',
        icon: Settings2,
        action: () => {
          onOpenSettings()
          onOpenChange(false)
        },
      },
      {
        id: 'overview',
        label: 'Return to overview',
        description: 'Open the dashboard and current workspace summary',
        group: 'Quick jump',
        icon: LayoutGrid,
        action: () => {
          navigate('/overview')
          onOpenChange(false)
        },
      },
    ]
  }, [context?.recent_entities, navigate, onOpenAgent, onOpenChange, onOpenOps, onOpenSettings, preferredModelId])

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return commands
    return commands.filter((item) =>
      `${item.label} ${item.description} ${item.group}`.toLowerCase().includes(term)
    )
  }, [commands, search])

  const grouped = useMemo(() => {
    return filtered.reduce<Record<string, CommandItem[]>>((acc, item) => {
      acc[item.group] ??= []
      acc[item.group].push(item)
      return acc
    }, {})
  }, [filtered])

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="overflow-hidden border-none bg-transparent p-0 shadow-none sm:max-w-2xl">
        <DialogTitle className="sr-only">Command palette</DialogTitle>
        <div className="overflow-hidden rounded-3xl border bg-popover text-popover-foreground shadow-2xl">
          <div className="flex items-center gap-3 border-b px-4 py-3">
            <Search className="h-4 w-4 text-muted-foreground" />
            <input
              autoFocus
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search routes, sessions, source libraries, and commands"
              className="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
            />
            <span className="hidden rounded-md border bg-muted px-1.5 py-0.5 text-[10px] uppercase text-muted-foreground sm:inline-flex sm:items-center sm:gap-1">
              <Command className="h-3 w-3" />
              K
            </span>
          </div>

          <div className="max-h-[420px] space-y-4 overflow-auto px-3 py-3">
            {Object.keys(grouped).length === 0 ? (
              <div className="px-3 py-8 text-center text-sm text-muted-foreground">
                No matching command.
              </div>
            ) : (
              Object.entries(grouped).map(([group, items]) => (
                <section key={group}>
                  <div className="px-3 pb-2 text-[11px] uppercase tracking-[0.2em] text-muted-foreground">
                    {group}
                  </div>
                  <div className="space-y-1">
                    {items.map((item) => {
                      const Icon = item.icon
                      return (
                        <button
                          key={item.id}
                          className="flex w-full items-start gap-3 rounded-2xl px-3 py-3 text-left transition-colors hover:bg-accent"
                          onClick={item.action}
                        >
                          <div className="rounded-xl bg-muted p-2 text-muted-foreground">
                            <Icon className="h-4 w-4" />
                          </div>
                          <div className="min-w-0">
                            <div className="text-sm font-medium">{item.label}</div>
                            <div className="mt-1 text-xs text-muted-foreground">
                              {item.description}
                            </div>
                          </div>
                        </button>
                      )
                    })}
                  </div>
                </section>
              ))
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
