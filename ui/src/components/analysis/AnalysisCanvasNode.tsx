import { Handle, Position, type NodeProps } from '@xyflow/react'

import { cn } from '@/lib/utils'
import type {
  AnalysisCanvasNode,
  AnalysisNodeKind,
} from '@/components/analysis/analysis-canvas-state'

const NODE_KIND_META: Record<
  AnalysisNodeKind,
  {
    label: string
    accent: string
    badge: string
    minimapColor: string
  }
> = {
  note: {
    label: 'Note',
    accent: 'bg-sky-500',
    badge: 'border-sky-500/20 bg-sky-500/10 text-sky-700',
    minimapColor: '#0ea5e9',
  },
  artifact: {
    label: 'Artifact',
    accent: 'bg-emerald-500',
    badge: 'border-emerald-500/20 bg-emerald-500/10 text-emerald-700',
    minimapColor: '#10b981',
  },
  reportSnippet: {
    label: 'Snippet',
    accent: 'bg-violet-500',
    badge: 'border-violet-500/20 bg-violet-500/10 text-violet-700',
    minimapColor: '#8b5cf6',
  },
  decision: {
    label: 'Decision',
    accent: 'bg-amber-500',
    badge: 'border-amber-500/20 bg-amber-500/10 text-amber-700',
    minimapColor: '#f59e0b',
  },
  chartPlaceholder: {
    label: 'Chart',
    accent: 'bg-rose-500',
    badge: 'border-rose-500/20 bg-rose-500/10 text-rose-700',
    minimapColor: '#f43f5e',
  },
}

export function getNodeKindMeta(kind: AnalysisNodeKind) {
  return NODE_KIND_META[kind]
}

export function AnalysisCanvasNode({
  data,
  selected,
}: NodeProps<AnalysisCanvasNode>) {
  const meta = getNodeKindMeta(data.kind)

  return (
    <div
      className={cn(
        'min-w-[220px] max-w-[240px] rounded-2xl border bg-background/95 shadow-[0_12px_30px_-18px_rgba(15,23,42,0.45)] backdrop-blur',
        selected ? 'border-primary/60 ring-2 ring-primary/20' : 'border-border/70'
      )}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!h-3 !w-3 !border-2 !border-background !bg-slate-700"
      />

      <div className="flex gap-3 p-4">
        <div className={cn('w-1 rounded-full', meta.accent)} />
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between gap-2">
            <span
              className={cn(
                'rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.18em]',
                meta.badge
              )}
            >
              {meta.label}
            </span>
            <span className="text-[10px] text-muted-foreground">{data.status}</span>
          </div>

          <div className="mt-3 text-sm font-semibold leading-snug text-foreground">
            {data.title}
          </div>

          <p className="mt-2 text-xs leading-relaxed text-muted-foreground">{data.summary}</p>

          <div className="mt-3 flex items-center justify-between text-[11px] text-muted-foreground">
            <span>{data.owner}</span>
            <span>{selected ? 'Selected' : 'Drag to move'}</span>
          </div>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="!h-3 !w-3 !border-2 !border-background !bg-slate-700"
      />
    </div>
  )
}
