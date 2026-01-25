import { useCallback, useState, useEffect } from 'react';
import { Command } from 'cmdk';
import {
  Search,
  FileText,
  Play,
  MessageSquare,
  Package,
  Library,
  Database,
  Settings,
  Plus,
  Moon,
  Sun,
  Monitor,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTheme } from '@/components/providers/theme-provider';
import { useWorkspaceStore } from '@/stores/workspace-store';

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

interface CommandItem {
  id: string;
  label: string;
  description?: string;
  icon: React.ElementType;
  shortcut?: string[];
  action: () => void;
  group: string;
}

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  const [search, setSearch] = useState('');
  const { theme, setTheme } = useTheme();
  const { addPane } = useWorkspaceStore();

  // Reset search when closing
  useEffect(() => {
    if (!open) {
      setSearch('');
    }
  }, [open]);

  // Define commands
  const commands: CommandItem[] = [
    // Navigation
    {
      id: 'new-chat',
      label: 'New Chat',
      description: 'Start a new conversation thread',
      icon: MessageSquare,
      shortcut: ['Ctrl', 'N'],
      action: () => {
        addPane('main', {
          type: 'chat',
          title: 'New Chat',
          closable: true,
        });
        onOpenChange(false);
      },
      group: 'Create',
    },
    {
      id: 'new-run',
      label: 'Start New Run',
      description: 'Begin a new agent run',
      icon: Play,
      action: () => {
        console.log('Start new run');
        onOpenChange(false);
      },
      group: 'Create',
    },

    // Views
    {
      id: 'view-artifacts',
      label: 'View Artifacts',
      description: 'Browse all artifacts',
      icon: FileText,
      action: () => {
        addPane('sidebar', {
          type: 'artifact-browser',
          title: 'Artifacts',
          closable: true,
        });
        onOpenChange(false);
      },
      group: 'View',
    },
    {
      id: 'view-bundles',
      label: 'View Bundles',
      description: 'Browse bundles',
      icon: Package,
      action: () => {
        console.log('View bundles');
        onOpenChange(false);
      },
      group: 'View',
    },
    {
      id: 'view-corpora',
      label: 'View Corpora',
      description: 'Browse corpora',
      icon: Library,
      action: () => {
        console.log('View corpora');
        onOpenChange(false);
      },
      group: 'View',
    },
    {
      id: 'view-kbs',
      label: 'View Knowledge Bases',
      description: 'Browse knowledge bases',
      icon: Database,
      action: () => {
        console.log('View KBs');
        onOpenChange(false);
      },
      group: 'View',
    },
    {
      id: 'view-runs',
      label: 'View Runs',
      description: 'Browse all runs',
      icon: Play,
      action: () => {
        addPane('detail', {
          type: 'run-explorer',
          title: 'Run Explorer',
          closable: true,
        });
        onOpenChange(false);
      },
      group: 'View',
    },

    // Theme
    {
      id: 'theme-light',
      label: 'Light Theme',
      description: 'Switch to light mode',
      icon: Sun,
      action: () => {
        setTheme('light');
        onOpenChange(false);
      },
      group: 'Theme',
    },
    {
      id: 'theme-dark',
      label: 'Dark Theme',
      description: 'Switch to dark mode',
      icon: Moon,
      action: () => {
        setTheme('dark');
        onOpenChange(false);
      },
      group: 'Theme',
    },
    {
      id: 'theme-system',
      label: 'System Theme',
      description: 'Follow system preference',
      icon: Monitor,
      action: () => {
        setTheme('system');
        onOpenChange(false);
      },
      group: 'Theme',
    },

    // Settings
    {
      id: 'settings',
      label: 'Settings',
      description: 'Open settings',
      icon: Settings,
      shortcut: ['Ctrl', ','],
      action: () => {
        console.log('Open settings');
        onOpenChange(false);
      },
      group: 'Settings',
    },
  ];

  // Group commands
  const groups = commands.reduce(
    (acc, cmd) => {
      if (!acc[cmd.group]) {
        acc[cmd.group] = [];
      }
      acc[cmd.group].push(cmd);
      return acc;
    },
    {} as Record<string, CommandItem[]>
  );

  return (
    <Command.Dialog
      open={open}
      onOpenChange={onOpenChange}
      label="Command palette"
      className={cn(
        'fixed inset-0 z-50 bg-black/50',
        'data-[state=open]:animate-in data-[state=closed]:animate-out',
        'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0'
      )}
    >
      <div className="fixed left-[50%] top-[20%] translate-x-[-50%] w-full max-w-lg">
        <div className="rounded-lg border bg-popover text-popover-foreground shadow-lg overflow-hidden">
          <div className="flex items-center border-b px-3">
            <Search className="h-4 w-4 shrink-0 opacity-50" />
            <Command.Input
              value={search}
              onValueChange={setSearch}
              placeholder="Type a command or search..."
              className="flex h-11 w-full rounded-md bg-transparent py-3 px-2 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>

          <Command.List className="max-h-[300px] overflow-y-auto p-2">
            <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
              No results found.
            </Command.Empty>

            {Object.entries(groups).map(([groupName, items]) => (
              <Command.Group key={groupName} heading={groupName}>
                <div className="px-2 py-1.5 text-xs font-medium text-muted-foreground">
                  {groupName}
                </div>
                {items.map((item) => (
                  <Command.Item
                    key={item.id}
                    value={`${item.label} ${item.description || ''}`}
                    onSelect={item.action}
                    className={cn(
                      'relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none',
                      'hover:bg-accent hover:text-accent-foreground',
                      'data-[selected=true]:bg-accent data-[selected=true]:text-accent-foreground'
                    )}
                  >
                    <item.icon className="mr-2 h-4 w-4 shrink-0 opacity-70" />
                    <div className="flex-1">
                      <span>{item.label}</span>
                      {item.description && (
                        <p className="text-xs text-muted-foreground">
                          {item.description}
                        </p>
                      )}
                    </div>
                    {item.shortcut && (
                      <div className="ml-auto flex items-center gap-1">
                        {item.shortcut.map((key, i) => (
                          <kbd
                            key={i}
                            className="px-1.5 py-0.5 text-xs bg-muted rounded border"
                          >
                            {key}
                          </kbd>
                        ))}
                      </div>
                    )}
                  </Command.Item>
                ))}
              </Command.Group>
            ))}
          </Command.List>
        </div>
      </div>
    </Command.Dialog>
  );
}
