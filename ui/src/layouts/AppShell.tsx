import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import {
  BarChart3,
  BookOpen,
  Brain,
  BriefcaseBusiness,
  ClipboardCheck,
  FileSearch,
  LayoutGrid,
  LogOut,
  Settings,
  Users,
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/auth-store'

type NavItem = {
  to: string
  label: string
  description: string
  icon: React.ReactNode
}

const NAV: NavItem[] = [
  {
    to: '/overview',
    label: 'Overview',
    description: 'What’s happening',
    icon: <LayoutGrid className="h-4 w-4" />,
  },
  {
    to: '/research',
    label: 'Research Intelligence',
    description: 'Gather + synthesize',
    icon: <FileSearch className="h-4 w-4" />,
  },
  {
    to: '/docs',
    label: 'Doc Intelligence',
    description: 'Notebooks + sources',
    icon: <BookOpen className="h-4 w-4" />,
  },
  {
    to: '/analysis',
    label: 'Analysis Intelligence',
    description: 'Workflows + outputs',
    icon: <BarChart3 className="h-4 w-4" />,
  },
  {
    to: '/decisions',
    label: 'Decision Intelligence',
    description: 'Claims + confidence',
    icon: <ClipboardCheck className="h-4 w-4" />,
  },
  {
    to: '/clients',
    label: 'Client Intelligence',
    description: 'CRM + context',
    icon: <Users className="h-4 w-4" />,
  },
  {
    to: '/projects',
    label: 'Project Intelligence',
    description: 'Workstreams + trace',
    icon: <BriefcaseBusiness className="h-4 w-4" />,
  },
]

function NavRow({ item }: { item: NavItem }) {
  return (
    <NavLink
      to={item.to}
      className={({ isActive }) =>
        cn(
          'group flex items-start gap-3 rounded-xl px-3 py-2 transition-colors',
          isActive
            ? 'bg-accent text-foreground'
            : 'text-muted-foreground hover:bg-muted/60 hover:text-foreground'
        )
      }
    >
      <div className="mt-0.5 text-muted-foreground group-hover:text-foreground">
        {item.icon}
      </div>
      <div className="min-w-0">
        <div className="truncate text-sm font-medium">{item.label}</div>
        <div className="truncate text-xs opacity-80">{item.description}</div>
      </div>
    </NavLink>
  )
}

export function AppShell() {
  const navigate = useNavigate()
  const location = useLocation()
  const { tenantName, role, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const showAdvanced = !location.pathname.startsWith('/workbench')

  return (
    <div className="h-screen w-screen overflow-hidden bg-background">
      <div className="flex h-full">
        {/* Sidebar */}
        <aside className="hidden h-full w-[300px] shrink-0 border-r bg-gradient-to-b from-background to-muted/30 md:flex">
          <div className="flex h-full w-full flex-col p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="grid h-9 w-9 place-items-center rounded-xl bg-primary text-primary-foreground shadow-sm">
                  <Brain className="h-5 w-5" />
                </div>
                <div className="min-w-0">
                  <div className="truncate text-sm font-semibold leading-tight">
                    Intelli
                  </div>
                  <div className="truncate text-xs text-muted-foreground">
                    Trusted analysis workspace
                  </div>
                </div>
              </div>
              <Button variant="ghost" size="icon" aria-label="Settings (coming soon)">
                <Settings className="h-4 w-4" />
              </Button>
            </div>

            <div className="mt-4 rounded-xl border bg-card px-3 py-2">
              <div className="text-xs text-muted-foreground">Tenant</div>
              <div className="truncate text-sm font-medium">{tenantName || 'Demo'}</div>
              <div className="mt-1 text-xs text-muted-foreground">
                Role: {role ? role : '—'}
              </div>
            </div>

            <Separator className="my-4" />

            <nav className="space-y-1">
              {NAV.map((item) => (
                <NavRow key={item.to} item={item} />
              ))}
            </nav>

            <div className="mt-auto pt-4">
              <Separator className="mb-3" />
              <div className="flex items-center justify-between">
                {showAdvanced ? (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => window.open('/workbench', '_blank', 'noopener,noreferrer')}
                  >
                    Open Dev Workbench
                  </Button>
                ) : (
                  <div />
                )}
                <Button variant="ghost" size="icon" onClick={handleLogout} aria-label="Sign out">
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
              <div className="mt-2 text-[11px] text-muted-foreground">
                Keep the backbone. Iterate the product.
              </div>
            </div>
          </div>
        </aside>

        {/* Main */}
        <main className="flex h-full min-w-0 flex-1 flex-col">
          {/* Mobile top bar */}
          <div className="flex items-center justify-between border-b bg-background px-4 py-3 md:hidden">
            <div className="flex items-center gap-2">
              <div className="grid h-9 w-9 place-items-center rounded-xl bg-primary text-primary-foreground shadow-sm">
                <Brain className="h-5 w-5" />
              </div>
              <div>
                <div className="text-sm font-semibold leading-tight">Intelli</div>
                <div className="text-xs text-muted-foreground truncate max-w-[220px]">
                  {tenantName || 'Demo'}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.open('/workbench', '_blank', 'noopener,noreferrer')}
              >
                Dev
              </Button>
              <Button variant="ghost" size="icon" onClick={handleLogout} aria-label="Sign out">
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="min-w-0 flex-1 overflow-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

