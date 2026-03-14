import {
  BarChart3,
  BookOpen,
  BriefcaseBusiness,
  ClipboardCheck,
  FileSearch,
  LayoutGrid,
  Users,
  type LucideIcon,
} from 'lucide-react'

export type ShellModule =
  | 'overview'
  | 'research'
  | 'docs'
  | 'analysis'
  | 'projects'
  | 'clients'
  | 'decisions'

export interface ShellNavItem {
  to: `/${ShellModule}`
  module: ShellModule
  label: string
  description: string
  icon: LucideIcon
}

export const SHELL_NAV_ITEMS: ShellNavItem[] = [
  {
    to: '/overview',
    module: 'overview',
    label: 'Overview',
    description: 'Control centre',
    icon: LayoutGrid,
  },
  {
    to: '/research',
    module: 'research',
    label: 'Research',
    description: 'Investigate and synthesize',
    icon: FileSearch,
  },
  {
    to: '/docs',
    module: 'docs',
    label: 'Source Library',
    description: 'Files, bundles, versions',
    icon: BookOpen,
  },
  {
    to: '/analysis',
    module: 'analysis',
    label: 'Workflow Studio',
    description: 'Build and run flows',
    icon: BarChart3,
  },
  {
    to: '/projects',
    module: 'projects',
    label: 'Projects',
    description: 'Track work and outputs',
    icon: BriefcaseBusiness,
  },
  {
    to: '/clients',
    module: 'clients',
    label: 'Clients',
    description: 'Accounts and deliverables',
    icon: Users,
  },
  {
    to: '/decisions',
    module: 'decisions',
    label: 'Decisions',
    description: 'Recommendations and audit',
    icon: ClipboardCheck,
  },
]

export function getShellModuleFromPath(pathname: string): ShellModule {
  const firstSegment = pathname.split('/').filter(Boolean)[0]
  switch (firstSegment) {
    case 'research':
      return 'research'
    case 'docs':
      return 'docs'
    case 'analysis':
      return 'analysis'
    case 'projects':
      return 'projects'
    case 'clients':
      return 'clients'
    case 'decisions':
      return 'decisions'
    default:
      return 'overview'
  }
}

export function getShellModuleLabel(module: ShellModule): string {
  return SHELL_NAV_ITEMS.find((item) => item.module === module)?.label ?? 'Overview'
}
