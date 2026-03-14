import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Activity,
  ArrowRight,
  BarChart3,
  BookOpen,
  BriefcaseBusiness,
  ClipboardCheck,
  FileSearch,
  Loader2,
  Users,
} from 'lucide-react'

import { pointersApi } from '@/api/client'
import { shellApi } from '@/api/shell'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useTourStore } from '@/stores/tour-store'

type Card = {
  title: string
  description: string
  to: string
  icon: React.ReactNode
  status: 'now' | 'next' | 'later'
}

const CARDS: Card[] = [
  {
    title: 'Research',
    description: 'Run grounded analysis over source libraries and keep every answer inspectable.',
    to: '/research',
    icon: <FileSearch className="h-5 w-5" />,
    status: 'next',
  },
  {
    title: 'Source Library',
    description: 'Upload, version, and curate the files that drive research and workflows.',
    to: '/docs',
    icon: <BookOpen className="h-5 w-5" />,
    status: 'now',
  },
  {
    title: 'Workflow Studio',
    description: 'Build repeatable operational flows that stay linked to evidence.',
    to: '/analysis',
    icon: <BarChart3 className="h-5 w-5" />,
    status: 'next',
  },
  {
    title: 'Decisions',
    description: 'Capture recommendations, confidence, and review state for stakeholders.',
    to: '/decisions',
    icon: <ClipboardCheck className="h-5 w-5" />,
    status: 'later',
  },
  {
    title: 'Clients',
    description: 'Keep client context, deliverables, and activity close to the work.',
    to: '/clients',
    icon: <Users className="h-5 w-5" />,
    status: 'later',
  },
  {
    title: 'Projects',
    description: 'Track objectives, deliverables, and the outputs that support them.',
    to: '/projects',
    icon: <BriefcaseBusiness className="h-5 w-5" />,
    status: 'later',
  },
]

function formatCost(costMicros: number): string {
  const usd = costMicros / 1_000_000
  if (usd === 0) return '$0.00'
  if (usd >= 0.01) return `$${usd.toFixed(4)}`
  return `$${usd.toFixed(6)}`.replace(/0+$/, '').replace(/\.$/, '')
}

function StatusPill({ status }: { status: Card['status'] }) {
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

export function OverviewPage() {
  const navigate = useNavigate()
  const openTour = useTourStore((s) => s.openTour)

  const notebooksQuery = useQuery({
    queryKey: ['pointers', 'notebooks'],
    queryFn: () => pointersApi.list('notebooks'),
  })

  const notebooksCount = useMemo(() => (notebooksQuery.data ?? []).length, [notebooksQuery.data])
  const opsSummaryQuery = useQuery({
    queryKey: ['ops-summary'],
    queryFn: () => shellApi.getOpsSummary(),
  })
  const shellContextQuery = useQuery({
    queryKey: ['shell-context'],
    queryFn: () => shellApi.getContext(),
  })

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold tracking-tight">
          {shellContextQuery.data?.workspace_name || 'Overview'}
        </h1>
        <p className="text-sm text-muted-foreground max-w-2xl">
          Track live work across research, source libraries, and workflow execution from one operating surface.
        </p>
        <Button variant="outline" size="sm" className="mt-2 w-fit" onClick={openTour}>
          Take the guided tour
        </Button>
      </div>

      <div className="mt-6 rounded-xl border bg-card">
        <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-4">
          <div>
            <div className="text-sm font-semibold">Operations snapshot</div>
            <div className="mt-1 text-xs text-muted-foreground">
              A quick read on live work, source availability, and the next surface to open.
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button size="sm" onClick={() => navigate('/research')}>
              Open Research
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
        <Separator />
        <div className="grid grid-cols-1 gap-4 p-5 md:grid-cols-4">
          <div className="rounded-lg border bg-background p-4">
            <div className="text-xs text-muted-foreground">Source libraries</div>
            <div className="mt-1 text-xl font-semibold">{notebooksCount}</div>
            <div className="mt-2 text-xs text-muted-foreground">
              Versioned evidence bundles ready for document Q&A and analysis.
            </div>
          </div>
          <div className="rounded-lg border bg-background p-4">
            <div className="text-xs text-muted-foreground">Live runs</div>
            <div className="mt-1 text-xl font-semibold">
              {opsSummaryQuery.isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                opsSummaryQuery.data?.running_count ?? 0
              )}
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              Active work surfaced straight from the shared run ledger.
            </div>
          </div>
          <div className="rounded-lg border bg-background p-4">
            <div className="text-xs text-muted-foreground">Needs attention</div>
            <div className="mt-1 text-xl font-semibold">{opsSummaryQuery.data?.failed_count ?? 0}</div>
            <div className="mt-2 text-xs text-muted-foreground">
              Failed or interrupted runs that need a follow-up before the next demo.
            </div>
          </div>
          <div className="rounded-lg border bg-background p-4">
            <div className="text-xs text-muted-foreground">Testing cost</div>
            <div className="mt-1 text-xl font-semibold">
              {formatCost(opsSummaryQuery.data?.total_cost_micros ?? 0)}
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              {(opsSummaryQuery.data?.total_input_tokens ?? 0).toLocaleString()} input ·{' '}
              {(opsSummaryQuery.data?.total_output_tokens ?? 0).toLocaleString()} output
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-[1.3fr_0.7fr]">
        <div className="rounded-xl border bg-card p-5">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <Activity className="h-4 w-4" />
            Recent operational activity
          </div>
          <div className="mt-4 space-y-3">
            {(opsSummaryQuery.data?.recent_activity ?? []).slice(0, 5).map((item) => (
              <button
                key={item.id}
                className="flex w-full items-start justify-between gap-3 rounded-2xl border bg-background/80 px-4 py-3 text-left hover:bg-accent"
                onClick={() => navigate(item.href || '/research')}
              >
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium">{item.label}</div>
                  <div className="mt-1 text-xs text-muted-foreground">{item.detail}</div>
                </div>
                {item.status ? (
                  <span className="rounded-full border px-2 py-0.5 text-[11px] text-muted-foreground">
                    {item.status}
                  </span>
                ) : null}
              </button>
            ))}
            {!opsSummaryQuery.isLoading && (opsSummaryQuery.data?.recent_activity.length ?? 0) === 0 ? (
              <div className="rounded-2xl border border-dashed border-border/70 bg-background/60 px-4 py-4 text-sm text-muted-foreground">
                Activity will appear here as the workspace runs research and document tasks.
              </div>
            ) : null}
          </div>
        </div>

        <div className="rounded-xl border bg-card p-5">
          <div className="text-sm font-semibold">Open next</div>
          <div className="mt-4 space-y-3">
            <Button className="w-full justify-between" onClick={() => navigate('/research')}>
              Research workspace
              <ArrowRight className="h-4 w-4" />
            </Button>
            <Button variant="outline" className="w-full justify-between" onClick={() => navigate('/docs')}>
              Source library
              <ArrowRight className="h-4 w-4" />
            </Button>
            <Button variant="outline" className="w-full justify-between" onClick={() => navigate('/analysis')}>
              Workflow studio
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      <div className="mt-8">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold">Product surfaces</h2>
          <span className="text-xs text-muted-foreground">Each route stays wired to the live application runtime</span>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {CARDS.map((c) => (
            <button
              key={c.to}
              className="group rounded-2xl border bg-card p-5 text-left shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
              onClick={() => navigate(c.to)}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="grid h-10 w-10 place-items-center rounded-xl bg-muted text-foreground">
                  {c.icon}
                </div>
                <StatusPill status={c.status} />
              </div>
              <div className="mt-4">
                <div className="text-sm font-semibold">{c.title}</div>
                <div className="mt-1 text-sm text-muted-foreground">{c.description}</div>
              </div>
              <div className="mt-4 text-xs text-muted-foreground">
                Open <span className="text-foreground/80 group-hover:text-foreground">→</span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
