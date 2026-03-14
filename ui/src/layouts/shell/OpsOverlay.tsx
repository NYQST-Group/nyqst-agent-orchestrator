import { useNavigate } from 'react-router-dom'
import { Activity, AlertTriangle, Clock3, Loader2 } from 'lucide-react'

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import type { OpsSummary } from '@/types/shell'

interface OpsOverlayProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  summary?: OpsSummary
  isLoading?: boolean
}

export function OpsOverlay({ open, onOpenChange, summary, isLoading }: OpsOverlayProps) {
  const navigate = useNavigate()

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-3xl">
        <DialogHeader>
          <DialogTitle>Operations centre</DialogTitle>
          <DialogDescription>
            Live status from the shared run ledger, surfaced inside the product shell instead of hidden behind tooling.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border bg-card/70 p-4">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <Loader2 className="h-4 w-4" />
              Running now
            </div>
            <div className="mt-2 text-3xl font-semibold">{summary?.running_count ?? 0}</div>
          </div>
          <div className="rounded-2xl border bg-card/70 p-4">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <Clock3 className="h-4 w-4" />
              Queued
            </div>
            <div className="mt-2 text-3xl font-semibold">{summary?.queued_count ?? 0}</div>
          </div>
          <div className="rounded-2xl border bg-card/70 p-4">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <AlertTriangle className="h-4 w-4" />
              Needs attention
            </div>
            <div className="mt-2 text-3xl font-semibold">{summary?.failed_count ?? 0}</div>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <section className="rounded-2xl border bg-card/70 p-4">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <Activity className="h-4 w-4" />
              Active runs
            </div>
            <div className="mt-3 space-y-2">
              {isLoading ? (
                <div className="text-sm text-muted-foreground">Loading live activity…</div>
              ) : summary?.active_runs.length ? (
                summary.active_runs.map((item) => (
                  <button
                    key={item.id}
                    className="w-full rounded-2xl border bg-background/80 px-3 py-3 text-left hover:bg-accent"
                    onClick={() => {
                      onOpenChange(false)
                      if (item.href) navigate(item.href)
                    }}
                  >
                    <div className="text-sm font-medium">{item.label}</div>
                    <div className="mt-1 text-xs text-muted-foreground">{item.detail}</div>
                  </button>
                ))
              ) : (
                <div className="rounded-2xl border border-dashed border-border/70 bg-background/60 px-3 py-4 text-sm text-muted-foreground">
                  No live runs at the moment.
                </div>
              )}
            </div>
          </section>

          <section className="rounded-2xl border bg-card/70 p-4">
            <div className="text-sm font-semibold">Recent activity</div>
            <div className="mt-3 space-y-2">
              {isLoading ? (
                <div className="text-sm text-muted-foreground">Loading recent activity…</div>
              ) : summary?.recent_activity.length ? (
                summary.recent_activity.map((item) => (
                  <button
                    key={item.id}
                    className="w-full rounded-2xl border bg-background/80 px-3 py-3 text-left hover:bg-accent"
                    onClick={() => {
                      onOpenChange(false)
                      if (item.href) navigate(item.href)
                    }}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="text-sm font-medium">{item.label}</div>
                      {item.status ? (
                        <span className="rounded-full border px-2 py-0.5 text-[11px] text-muted-foreground">
                          {item.status}
                        </span>
                      ) : null}
                    </div>
                    <div className="mt-1 text-xs text-muted-foreground">{item.detail}</div>
                  </button>
                ))
              ) : (
                <div className="rounded-2xl border border-dashed border-border/70 bg-background/60 px-3 py-4 text-sm text-muted-foreground">
                  Activity will appear here as research, document, and workflow runs execute.
                </div>
              )}
            </div>
          </section>
        </div>
      </DialogContent>
    </Dialog>
  )
}
