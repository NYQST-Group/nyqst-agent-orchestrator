/**
 * Workspace Store - Manages UI state for the workbench
 * Uses Zustand for client-side state management
 */

import { create } from 'zustand';
import { persist, devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import type { UUID, ResourceURI, PinnedContextItem } from '@/types';

// ============================================================================
// Types
// ============================================================================

export type PaneType =
  | 'chat'
  | 'planner'
  | 'run-explorer'
  | 'artifact-browser'
  | 'document-viewer'
  | 'table-viewer'
  | 'graph-viewer'
  | 'diff-viewer'
  | 'context-pinboard'
  | 'evaluations'
  | 'provenance'
  | 'governance'
  | 'admin';

export interface Pane {
  id: string;
  type: PaneType;
  title: string;
  resourceUri?: ResourceURI;
  closable: boolean;
  dirty?: boolean;
  metadata?: Record<string, unknown>;
}

export interface PaneGroup {
  id: string;
  panes: Pane[];
  activePane: string | null;
  size?: number;
}

export interface WorkspaceLayout {
  id: string;
  name: string;
  groups: PaneGroup[];
  orientation: 'horizontal' | 'vertical';
}

export interface WorkspaceState {
  // Current layout
  layout: WorkspaceLayout;

  // Pinned context items
  pinnedItems: PinnedContextItem[];

  // Recently accessed resources
  recentResources: ResourceURI[];

  // Active project/session context
  activeProjectId: UUID | null;
  activeSessionId: UUID | null;
  activeThreadId: UUID | null;

  // UI preferences
  sidebarCollapsed: boolean;
  commandPaletteOpen: boolean;
}

export interface WorkspaceActions {
  // Pane management
  addPane: (groupId: string, pane: Omit<Pane, 'id'>) => string;
  removePane: (groupId: string, paneId: string) => void;
  setActivePane: (groupId: string, paneId: string) => void;
  updatePane: (groupId: string, paneId: string, updates: Partial<Pane>) => void;
  movePane: (fromGroupId: string, toGroupId: string, paneId: string, index?: number) => void;

  // Group management
  addGroup: (group: Omit<PaneGroup, 'id'>) => string;
  removeGroup: (groupId: string) => void;
  resizeGroup: (groupId: string, size: number) => void;

  // Layout management
  saveLayout: (name: string) => WorkspaceLayout;
  loadLayout: (layout: WorkspaceLayout) => void;
  resetLayout: () => void;

  // Context management
  pinItem: (item: Omit<PinnedContextItem, 'pinnedAt'>) => void;
  unpinItem: (itemId: UUID) => void;
  clearPinnedItems: () => void;

  // Resource tracking
  addRecentResource: (uri: ResourceURI) => void;
  clearRecentResources: () => void;

  // Active context
  setActiveProject: (projectId: UUID | null) => void;
  setActiveSession: (sessionId: UUID | null) => void;
  setActiveThread: (threadId: UUID | null) => void;

  // UI state
  toggleSidebar: () => void;
  setCommandPaletteOpen: (open: boolean) => void;
}

// ============================================================================
// Default Layout
// ============================================================================

const DEFAULT_LAYOUT: WorkspaceLayout = {
  id: 'default',
  name: 'Default Layout',
  orientation: 'horizontal',
  groups: [
    {
      id: 'sidebar',
      panes: [
        {
          id: 'artifact-browser',
          type: 'artifact-browser',
          title: 'Artifacts',
          closable: false,
        },
      ],
      activePane: 'artifact-browser',
      size: 25,
    },
    {
      id: 'main',
      panes: [
        {
          id: 'chat',
          type: 'chat',
          title: 'Chat',
          closable: false,
        },
      ],
      activePane: 'chat',
      size: 50,
    },
    {
      id: 'detail',
      panes: [
        {
          id: 'run-explorer',
          type: 'run-explorer',
          title: 'Run Explorer',
          closable: true,
        },
      ],
      activePane: 'run-explorer',
      size: 25,
    },
  ],
};

// ============================================================================
// Store
// ============================================================================

export const useWorkspaceStore = create<WorkspaceState & WorkspaceActions>()(
  devtools(
    persist(
      immer((set, get) => ({
        // Initial state
        layout: DEFAULT_LAYOUT,
        pinnedItems: [],
        recentResources: [],
        activeProjectId: null,
        activeSessionId: null,
        activeThreadId: null,
        sidebarCollapsed: false,
        commandPaletteOpen: false,

        // Pane management
        addPane: (groupId, pane) => {
          const paneId = `pane-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
          set((state) => {
            const group = state.layout.groups.find((g) => g.id === groupId);
            if (group) {
              group.panes.push({ ...pane, id: paneId });
              group.activePane = paneId;
            }
          });
          return paneId;
        },

        removePane: (groupId, paneId) => {
          set((state) => {
            const group = state.layout.groups.find((g) => g.id === groupId);
            if (group) {
              const index = group.panes.findIndex((p) => p.id === paneId);
              if (index !== -1) {
                group.panes.splice(index, 1);
                if (group.activePane === paneId) {
                  group.activePane = group.panes[Math.max(0, index - 1)]?.id ?? null;
                }
              }
            }
          });
        },

        setActivePane: (groupId, paneId) => {
          set((state) => {
            const group = state.layout.groups.find((g) => g.id === groupId);
            if (group && group.panes.some((p) => p.id === paneId)) {
              group.activePane = paneId;
            }
          });
        },

        updatePane: (groupId, paneId, updates) => {
          set((state) => {
            const group = state.layout.groups.find((g) => g.id === groupId);
            if (group) {
              const pane = group.panes.find((p) => p.id === paneId);
              if (pane) {
                Object.assign(pane, updates);
              }
            }
          });
        },

        movePane: (fromGroupId, toGroupId, paneId, index) => {
          set((state) => {
            const fromGroup = state.layout.groups.find((g) => g.id === fromGroupId);
            const toGroup = state.layout.groups.find((g) => g.id === toGroupId);
            if (fromGroup && toGroup) {
              const paneIndex = fromGroup.panes.findIndex((p) => p.id === paneId);
              if (paneIndex !== -1) {
                const [pane] = fromGroup.panes.splice(paneIndex, 1);
                const insertIndex = index ?? toGroup.panes.length;
                toGroup.panes.splice(insertIndex, 0, pane);
                toGroup.activePane = paneId;
                if (fromGroup.activePane === paneId) {
                  fromGroup.activePane = fromGroup.panes[0]?.id ?? null;
                }
              }
            }
          });
        },

        // Group management
        addGroup: (group) => {
          const groupId = `group-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
          set((state) => {
            state.layout.groups.push({ ...group, id: groupId });
          });
          return groupId;
        },

        removeGroup: (groupId) => {
          set((state) => {
            const index = state.layout.groups.findIndex((g) => g.id === groupId);
            if (index !== -1) {
              state.layout.groups.splice(index, 1);
            }
          });
        },

        resizeGroup: (groupId, size) => {
          set((state) => {
            const group = state.layout.groups.find((g) => g.id === groupId);
            if (group) {
              group.size = size;
            }
          });
        },

        // Layout management
        saveLayout: (name) => {
          const { layout } = get();
          return { ...layout, id: `layout-${Date.now()}`, name };
        },

        loadLayout: (layout) => {
          set((state) => {
            state.layout = layout;
          });
        },

        resetLayout: () => {
          set((state) => {
            state.layout = DEFAULT_LAYOUT;
          });
        },

        // Context management
        pinItem: (item) => {
          set((state) => {
            const exists = state.pinnedItems.some((p) => p.id === item.id);
            if (!exists) {
              state.pinnedItems.push({
                ...item,
                pinnedAt: new Date().toISOString(),
              });
            }
          });
        },

        unpinItem: (itemId) => {
          set((state) => {
            const index = state.pinnedItems.findIndex((p) => p.id === itemId);
            if (index !== -1) {
              state.pinnedItems.splice(index, 1);
            }
          });
        },

        clearPinnedItems: () => {
          set((state) => {
            state.pinnedItems = [];
          });
        },

        // Resource tracking
        addRecentResource: (uri) => {
          set((state) => {
            // Remove if exists, then add to front
            state.recentResources = state.recentResources.filter((r) => r !== uri);
            state.recentResources.unshift(uri);
            // Keep only last 20
            if (state.recentResources.length > 20) {
              state.recentResources = state.recentResources.slice(0, 20);
            }
          });
        },

        clearRecentResources: () => {
          set((state) => {
            state.recentResources = [];
          });
        },

        // Active context
        setActiveProject: (projectId) => {
          set((state) => {
            state.activeProjectId = projectId;
          });
        },

        setActiveSession: (sessionId) => {
          set((state) => {
            state.activeSessionId = sessionId;
          });
        },

        setActiveThread: (threadId) => {
          set((state) => {
            state.activeThreadId = threadId;
          });
        },

        // UI state
        toggleSidebar: () => {
          set((state) => {
            state.sidebarCollapsed = !state.sidebarCollapsed;
          });
        },

        setCommandPaletteOpen: (open) => {
          set((state) => {
            state.commandPaletteOpen = open;
          });
        },
      })),
      {
        name: 'nyqst-workspace',
        partialize: (state) => ({
          layout: state.layout,
          pinnedItems: state.pinnedItems,
          recentResources: state.recentResources,
          sidebarCollapsed: state.sidebarCollapsed,
        }),
      }
    ),
    { name: 'workspace' }
  )
);

// ============================================================================
// Selectors
// ============================================================================

export const selectActivePane = (groupId: string) => (state: WorkspaceState) => {
  const group = state.layout.groups.find((g) => g.id === groupId);
  return group?.panes.find((p) => p.id === group.activePane);
};

export const selectPanesByType = (type: PaneType) => (state: WorkspaceState) => {
  return state.layout.groups.flatMap((g) => g.panes.filter((p) => p.type === type));
};

export const selectPinnedItemsByType = (type: PinnedContextItem['type']) => (state: WorkspaceState) => {
  return state.pinnedItems.filter((item) => item.type === type);
};
