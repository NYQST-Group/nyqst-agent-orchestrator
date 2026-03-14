import { useNavigate } from 'react-router-dom'
import { ArrowRight, FolderOpen, Sparkles } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import type { RightRailPayload } from '@/types/shell'

interface RightRailProps {
  data?: RightRailPayload
  isLoading?: boolean
  moduleLabel: string
  onOpenAgent: () => void
}

export function RightRail({ data, isLoading, moduleLabel, onOpenAgent }: RightRailProps) {
  const navigate = useNavigate()

  return (
    <div className="flex h-full flex-col bg-muted/20">
      <div className="px-4 pb-4 pt-5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-sm font-semibold">Context rail</div>
            <div className="mt-1 text-xs text-muted-foreground">
              Live context for {moduleLabel.toLowerCase()} drawn from sessions, runs, and source libraries.
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={onOpenAgent}>
            <Sparkles className="mr-2 h-4 w-4" />
            Ask
          </Button>
        </div>
      </div>

      <Separator />

      <div className="flex-1 space-y-4 overflow-auto px-4 py-4">
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, index) => (
              <div key={index} className="rounded-2xl border bg-card p-4">
                <div className="h-4 w-28 animate-pulse rounded bg-muted" />
                <div className="mt-3 h-3 w-full animate-pulse rounded bg-muted" />
                <div className="mt-2 h-3 w-2/3 animate-pulse rounded bg-muted" />
              </div>
            ))}
          </div>
        ) : data?.sections?.length ? (
          data.sections.map((section) => (
            <section key={section.kind} className="rounded-2xl border bg-card/90 p-4 shadow-sm">
              <div className="flex items-center justify-between gap-2">
                <div className="text-sm font-semibold">{section.title}</div>
                <span className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
                  {section.kind.replace('_', ' ')}
                </span>
              </div>
              {section.description ? (
                <p className="mt-1 text-xs leading-5 text-muted-foreground">{section.description}</p>
              ) : null}

              {section.items.length > 0 ? (
                <div className="mt-3 space-y-2">
                  {section.items.map((item) => (
                    <button
                      key={item.id}
                      className="flex w-full items-start justify-between gap-3 rounded-2xl border border-border/60 bg-background/80 px-3 py-3 text-left transition-colors hover:bg-accent"
                      onClick={() => {
                        if (item.href) navigate(item.href)
                      }}
                    >
                      <div className="min-w-0">
                        <div className="truncate text-sm font-medium">{item.title}</div>
                        {item.subtitle ? (
                          <div className="mt-1 text-xs text-muted-foreground">{item.subtitle}</div>
                        ) : null}
                        {item.meta ? (
                          <div className="mt-1 text-[11px] text-muted-foreground">{item.meta}</div>
                        ) : null}
                      </div>
                      <div className="flex shrink-0 items-center gap-2">
                        {item.badge ? (
                          <span className="rounded-full border px-2 py-0.5 text-[11px] text-muted-foreground">
                            {item.badge}
                          </span>
                        ) : null}
                        {item.href ? <ArrowRight className="h-4 w-4 text-muted-foreground" /> : null}
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="mt-3 rounded-2xl border border-dashed border-border/70 bg-background/60 px-3 py-4 text-xs leading-5 text-muted-foreground">
                  This surface will populate as more activity lands in the workspace.
                </div>
              )}
            </section>
          ))
        ) : (
          <div className="rounded-2xl border border-dashed border-border/70 bg-card/70 p-6 text-sm text-muted-foreground">
            <FolderOpen className="mb-3 h-5 w-5" />
            No live context yet for this route.
          </div>
        )}
      </div>
    </div>
  )
}
