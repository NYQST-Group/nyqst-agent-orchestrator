import { NavLink } from 'react-router-dom'
import { ArrowUpRight, LogOut, Sparkles } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/auth-store'
import { SHELL_NAV_ITEMS } from '@/layouts/shell/shell-config'

interface LeftRailProps {
  onNavigate?: () => void
  onOpenSettings: () => void
  workspaceName?: string | null
  role?: string | null
}

export function LeftRail({
  onNavigate,
  onOpenSettings,
  workspaceName,
  role,
}: LeftRailProps) {
  const { logout } = useAuthStore()

  return (
    <div className="flex h-full flex-col bg-background/90 backdrop-blur">
      <div className="px-4 pb-4 pt-5">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-2xl bg-primary text-primary-foreground shadow-sm">
            <Sparkles className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <div className="truncate text-sm font-semibold">Intelli Studio</div>
            <div className="truncate text-xs text-muted-foreground">
              Evidence-led intelligence workspace
            </div>
          </div>
        </div>

        <div className="mt-4 rounded-2xl border border-border/60 bg-card/80 p-3 shadow-sm">
          <div className="text-[11px] uppercase tracking-[0.2em] text-muted-foreground">
            Workspace
          </div>
          <div className="mt-1 truncate text-sm font-medium">
            {workspaceName || 'Current organisation'}
          </div>
          <div className="mt-1 text-xs text-muted-foreground">
            {role ? `${role} access` : 'Professional access'}
          </div>
        </div>
      </div>

      <Separator />

      <nav className="flex-1 space-y-1 overflow-auto px-3 py-4">
        {SHELL_NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                'group flex items-start gap-3 rounded-2xl border px-3 py-3 transition-all',
                isActive
                  ? 'border-primary/20 bg-primary/10 text-foreground shadow-sm'
                  : 'border-transparent text-muted-foreground hover:border-border/60 hover:bg-card hover:text-foreground'
              )
            }
          >
            {({ isActive }) => {
              const Icon = item.icon
              return (
                <>
                  <div
                    className={cn(
                      'mt-0.5 rounded-xl p-2',
                      isActive ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium">{item.label}</div>
                    <div className="truncate text-xs opacity-80">{item.description}</div>
                  </div>
                </>
              )
            }}
          </NavLink>
        ))}
      </nav>

      <div className="border-t px-4 py-4">
        <div className="rounded-2xl border border-dashed border-border/70 bg-muted/30 p-3">
          <div className="text-sm font-medium">Buyer demo mode</div>
          <div className="mt-1 text-xs leading-5 text-muted-foreground">
            Incomplete modules stay visible, but they should still feel deliberate and navigable.
          </div>
        </div>

        <div className="mt-4 flex items-center gap-2">
          <Button variant="outline" className="flex-1 justify-between" onClick={onOpenSettings}>
            Settings
            <ArrowUpRight className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={logout} aria-label="Sign out">
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
