import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  ArrowRight,
  BarChart3,
  BookOpen,
  BriefcaseBusiness,
  ClipboardCheck,
  FileSearch,
  Users,
} from 'lucide-react'

import { pointersApi } from '@/api/client'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

type Card = {
  title: string
  description: string
  to: string
  icon: React.ReactNode
  status: 'now' | 'next' | 'later'
}

const CARDS: Card[] = [
  {
    title: 'Research Intelligence',
    description: 'Gather sources, synthesize findings, keep traceability.',
    to: '/research',
    icon: <FileSearch className="h-5 w-5" />,
    status: 'next',
  },
  {
    title: 'Doc Intelligence',
    description: 'Notebooks: upload, index, ask, and cite sources.',
    to: '/docs',
    icon: <BookOpen className="h-5 w-5" />,
    status: 'now',
  },
  {
    title: 'Analysis Intelligence',
    description: 'Repeatable workflows that emit artifacts and claims.',
    to: '/analysis',
    icon: <BarChart3 className="h-5 w-5" />,
    status: 'next',
  },
  {
    title: 'Decision Intelligence',
    description: 'Confidence, recommendations, approvals, and audit.',
    to: '/decisions',
    icon: <ClipboardCheck className="h-5 w-5" />,
    status: 'later',
  },
  {
    title: 'Client Intelligence',
    description: 'CRM primitives linked to evidence and outputs.',
    to: '/clients',
    icon: <Users className="h-5 w-5" />,
    status: 'later',
  },
  {
    title: 'Project Intelligence',
    description: 'Objectives, tasks, deliverables, and timelines.',
    to: '/projects',
    icon: <BriefcaseBusiness className="h-5 w-5" />,
    status: 'later',
  },
]

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

  const notebooksQuery = useQuery({
    queryKey: ['pointers', 'notebooks'],
    queryFn: () => pointersApi.list('notebooks'),
  })

  const notebooksCount = useMemo(() => (notebooksQuery.data ?? []).length, [notebooksQuery.data])

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold tracking-tight">Overview</h1>
        <p className="text-sm text-muted-foreground max-w-2xl">
          You’re building a trusted commercial analysis platform. Start with notebooks and
          progressively add research, workflows, and decision governance—without losing provenance.
        </p>
      </div>

      <div className="mt-6 rounded-xl border bg-card">
        <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-4">
          <div>
            <div className="text-sm font-semibold">Right now</div>
            <div className="mt-1 text-xs text-muted-foreground">
              Doc Intelligence is live. Indexing runs automatically as sources change.
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button size="sm" onClick={() => navigate('/docs')}>
              Open Doc Intelligence
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
        <Separator />
        <div className="grid grid-cols-1 gap-4 p-5 md:grid-cols-3">
          <div className="rounded-lg border bg-background p-4">
            <div className="text-xs text-muted-foreground">Notebooks</div>
            <div className="mt-1 text-xl font-semibold">{notebooksCount}</div>
            <div className="mt-2 text-xs text-muted-foreground">
              Versioned sources (pointer → manifest → artifacts).
            </div>
          </div>
          <div className="rounded-lg border bg-background p-4">
            <div className="text-xs text-muted-foreground">Trust surface</div>
            <div className="mt-1 text-xl font-semibold">Runs + history</div>
            <div className="mt-2 text-xs text-muted-foreground">
              Audit trail exists; advanced view shows details.
            </div>
          </div>
          <div className="rounded-lg border bg-background p-4">
            <div className="text-xs text-muted-foreground">Next</div>
            <div className="mt-1 text-xl font-semibold">Research module</div>
            <div className="mt-2 text-xs text-muted-foreground">
              Orchestrator → agent framework → outputs back to notebook.
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold">Modules</h2>
          <span className="text-xs text-muted-foreground">Build iteratively on the backbone</span>
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
