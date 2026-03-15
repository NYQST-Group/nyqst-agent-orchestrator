import { BarChart3 } from 'lucide-react'

import { AnalysisCanvas } from '@/components/analysis/AnalysisCanvas'

export function AnalysisPage() {
  return (
    <div className="flex h-full flex-col">
      <header className="border-b bg-background/95 px-6 py-5 backdrop-blur">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
          <div className="flex items-start gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary/10 text-primary">
              <BarChart3 className="h-5 w-5" />
            </div>
            <div className="space-y-2">
              <div>
                <h1 className="text-lg font-semibold tracking-tight">Analysis Canvas</h1>
                <p className="max-w-2xl text-sm text-muted-foreground">
                  Graph-first workspace for provenance, decisions, and linked analysis.
                  This slice establishes base pan, zoom, drag, and edge creation before
                  persistence lands.
                </p>
              </div>
              <div className="flex flex-wrap gap-2 text-[11px] font-medium">
                <span className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-emerald-700">
                  React Flow selected
                </span>
                <span className="rounded-full border border-sky-500/20 bg-sky-500/10 px-2.5 py-1 text-sky-700">
                  DAG and provenance ready
                </span>
                <span className="rounded-full border border-amber-500/20 bg-amber-500/10 px-2.5 py-1 text-amber-700">
                  200-node benchmark seeded
                </span>
              </div>
            </div>
          </div>

          <div className="max-w-sm rounded-2xl border bg-card/80 px-4 py-3 text-xs text-muted-foreground shadow-sm">
            Start on the curated board, then switch to the benchmark board to validate the
            interaction baseline against the issue target without dragging persistence into
            this slice.
          </div>
        </div>
      </header>

      <AnalysisCanvas />
    </div>
  )
}
