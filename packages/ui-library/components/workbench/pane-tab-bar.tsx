import { useRef } from 'react';
import {
  X,
  MessageSquare,
  Play,
  FileBox,
  FileText,
  Table,
  GitBranch,
  Diff,
  Pin,
  CheckCircle,
  Link2,
  Shield,
  Settings,
  ListTodo,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import type { Pane, PaneType } from '@/stores/workspace-store';

interface PaneTabBarProps {
  groupId: string;
  panes: Pane[];
  activePane: string | null;
  onTabSelect: (paneId: string) => void;
  onTabClose: (paneId: string) => void;
}

const PANE_ICONS: Record<PaneType, React.ElementType> = {
  'chat': MessageSquare,
  'planner': ListTodo,
  'run-explorer': Play,
  'artifact-browser': FileBox,
  'document-viewer': FileText,
  'table-viewer': Table,
  'graph-viewer': GitBranch,
  'diff-viewer': Diff,
  'context-pinboard': Pin,
  'evaluations': CheckCircle,
  'provenance': Link2,
  'governance': Shield,
  'admin': Settings,
};

export function PaneTabBar({
  groupId,
  panes,
  activePane,
  onTabSelect,
  onTabClose,
}: PaneTabBarProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  if (panes.length === 0) {
    return null;
  }

  return (
    <div className="h-9 border-b bg-muted/30 flex items-center">
      <ScrollArea className="flex-1">
        <div ref={scrollRef} className="flex items-center gap-0.5 px-1">
          {panes.map((pane) => {
            const Icon = PANE_ICONS[pane.type] || FileText;
            const isActive = pane.id === activePane;

            return (
              <Tooltip key={pane.id}>
                <TooltipTrigger asChild>
                  <div
                    className={cn(
                      'group flex items-center gap-1.5 px-3 py-1.5 rounded-t-md cursor-pointer transition-colors',
                      'hover:bg-background/50',
                      isActive
                        ? 'bg-background border-b-2 border-primary text-foreground'
                        : 'text-muted-foreground'
                    )}
                    onClick={() => onTabSelect(pane.id)}
                    role="tab"
                    aria-selected={isActive}
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        onTabSelect(pane.id);
                      }
                    }}
                  >
                    <Icon className="h-3.5 w-3.5 shrink-0" />
                    <span className="text-xs font-medium truncate max-w-[120px]">
                      {pane.title}
                    </span>
                    {pane.dirty && (
                      <span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
                    )}
                    {pane.closable && (
                      <Button
                        variant="ghost"
                        size="icon-xs"
                        className={cn(
                          'h-4 w-4 p-0 opacity-0 group-hover:opacity-100 transition-opacity',
                          'hover:bg-muted'
                        )}
                        onClick={(e) => {
                          e.stopPropagation();
                          onTabClose(pane.id);
                        }}
                        aria-label={`Close ${pane.title}`}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    )}
                  </div>
                </TooltipTrigger>
                <TooltipContent side="bottom">
                  <p>{pane.title}</p>
                  {pane.resourceUri && (
                    <p className="text-xs text-muted-foreground">{pane.resourceUri}</p>
                  )}
                </TooltipContent>
              </Tooltip>
            );
          })}
        </div>
        <ScrollBar orientation="horizontal" className="h-1.5" />
      </ScrollArea>
    </div>
  );
}
