import { useNavigate } from 'react-router-dom'
import { ArrowRight, ExternalLink } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

type Props = {
  title: string
  tagline: string
  bullets: string[]
  status?: 'now' | 'next' | 'later'
}

function StatusPill({ status }: { status: NonNullable<Props['status']> }) {
  const map = {
    now: { label: 'Now', cls: 'bg-emerald-500/10 text-emerald-700 border-emerald-500/20' },
    next: { label: 'Next', cls: 'bg-amber-500/10 text-amber-700 border-amber-500/20' },
    later: { label: 'Later', cls: 'bg-slate-500/10 text-slate-700 border-slate-500/20' },
  }[status]

  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] ${map.cls}`}>
      {map.label}
    </span>
  )
}

export function ModulePlaceholder({ title, tagline, bullets, status = 'next' }: Props) {
  const navigate = useNavigate()

  return (
    <div className="mx-auto max-w-5xl px-6 py-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
            <StatusPill status={status} />
          </div>
          <p className="mt-2 max-w-2xl text-sm text-muted-foreground">{tagline}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => navigate('/docs')}>
            Open Doc Intelligence
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            onClick={() => window.open('/workbench', '_blank', 'noopener,noreferrer')}
          >
            Dev Workbench
            <ExternalLink className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="mt-6 rounded-xl border bg-card">
        <div className="px-5 py-4">
          <div className="text-sm font-semibold">What this module becomes</div>
          <div className="mt-1 text-xs text-muted-foreground">
            Built on the same backbone: artifacts, manifests, pointers, runs, and policy.
          </div>
        </div>
        <Separator />
        <div className="p-5">
          <ul className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {bullets.map((b) => (
              <li key={b} className="rounded-lg border bg-background px-4 py-3 text-sm">
                {b}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

