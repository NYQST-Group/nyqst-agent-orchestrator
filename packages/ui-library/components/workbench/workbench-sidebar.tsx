import {
  FolderKanban,
  Package,
  Library,
  Database,
  Play,
  FileText,
  MessageSquare,
  Settings,
  HelpCircle,
  Shield,
  Link,
  Users,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { useWorkspaceStore } from '@/stores/workspace-store';

interface WorkbenchSidebarProps {
  collapsed: boolean;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ElementType;
  paneType?: string;
  badge?: string | number;
}

const NAV_SECTIONS: { title: string; items: NavItem[] }[] = [
  {
    title: 'Work',
    items: [
      { id: 'projects', label: 'Projects', icon: FolderKanban },
      { id: 'threads', label: 'Threads', icon: MessageSquare },
      { id: 'runs', label: 'Runs', icon: Play },
    ],
  },
  {
    title: 'Substrate',
    items: [
      { id: 'bundles', label: 'Bundles', icon: Package },
      { id: 'corpora', label: 'Corpora', icon: Library },
      { id: 'artifacts', label: 'Artifacts', icon: FileText },
      { id: 'kbs', label: 'Knowledge Bases', icon: Database },
    ],
  },
  {
    title: 'Governance',
    items: [
      { id: 'claims', label: 'Claims', icon: Shield },
      { id: 'connectors', label: 'Connectors', icon: Link },
    ],
  },
];

const BOTTOM_NAV: NavItem[] = [
  { id: 'team', label: 'Team', icon: Users },
  { id: 'settings', label: 'Settings', icon: Settings },
  { id: 'help', label: 'Help', icon: HelpCircle },
];

export function WorkbenchSidebar({ collapsed }: WorkbenchSidebarProps) {
  const { addPane } = useWorkspaceStore();

  const handleNavClick = (item: NavItem) => {
    // For now, just log - in full implementation, this would open panes or navigate
    console.log('Nav clicked:', item.id);
  };

  if (collapsed) {
    return (
      <div className="h-full flex flex-col items-center py-2 gap-1">
        {NAV_SECTIONS.flatMap((section) =>
          section.items.map((item) => (
            <Tooltip key={item.id}>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon-sm"
                  className="w-8 h-8"
                  onClick={() => handleNavClick(item)}
                >
                  <item.icon className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">
                {item.label}
              </TooltipContent>
            </Tooltip>
          ))
        )}
        <div className="flex-1" />
        <Separator className="w-8 my-2" />
        {BOTTOM_NAV.map((item) => (
          <Tooltip key={item.id}>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon-sm"
                className="w-8 h-8"
                onClick={() => handleNavClick(item)}
              >
                <item.icon className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              {item.label}
            </TooltipContent>
          </Tooltip>
        ))}
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <ScrollArea className="flex-1">
        <div className="py-2 px-2">
          {NAV_SECTIONS.map((section, sectionIndex) => (
            <div key={section.title}>
              {sectionIndex > 0 && <Separator className="my-3" />}
              <div className="px-2 mb-1">
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  {section.title}
                </span>
              </div>
              <nav className="space-y-0.5">
                {section.items.map((item) => (
                  <Button
                    key={item.id}
                    variant="ghost"
                    className={cn(
                      'w-full justify-start gap-2 h-8 px-2',
                      'text-muted-foreground hover:text-foreground'
                    )}
                    onClick={() => handleNavClick(item)}
                  >
                    <item.icon className="h-4 w-4 shrink-0" />
                    <span className="truncate">{item.label}</span>
                    {item.badge && (
                      <span className="ml-auto text-xs bg-muted rounded-full px-1.5">
                        {item.badge}
                      </span>
                    )}
                  </Button>
                ))}
              </nav>
            </div>
          ))}
        </div>
      </ScrollArea>

      <Separator />
      <div className="p-2 space-y-0.5">
        {BOTTOM_NAV.map((item) => (
          <Button
            key={item.id}
            variant="ghost"
            className="w-full justify-start gap-2 h-8 px-2 text-muted-foreground hover:text-foreground"
            onClick={() => handleNavClick(item)}
          >
            <item.icon className="h-4 w-4 shrink-0" />
            <span className="truncate">{item.label}</span>
          </Button>
        ))}
      </div>
    </div>
  );
}
