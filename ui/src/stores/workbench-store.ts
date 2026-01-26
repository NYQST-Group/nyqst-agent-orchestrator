/**
 * Zustand store for workbench state management
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type PanelId = 'explorer' | 'main' | 'details' | 'timeline'

export interface OpenTab {
  id: string
  type: 'artifact' | 'manifest' | 'pointer' | 'run' | 'settings'
  title: string
  resourceId: string
}

interface WorkbenchState {
  // Panel visibility and sizes
  leftPanelCollapsed: boolean
  rightPanelCollapsed: boolean
  bottomPanelCollapsed: boolean
  leftPanelSize: number
  rightPanelSize: number
  bottomPanelSize: number

  // Tabs
  tabs: OpenTab[]
  activeTabId: string | null

  // Selected resources
  selectedNamespace: string | null
  selectedPointerId: string | null
  selectedRunId: string | null

  // Actions
  toggleLeftPanel: () => void
  toggleRightPanel: () => void
  toggleBottomPanel: () => void
  setLeftPanelSize: (size: number) => void
  setRightPanelSize: (size: number) => void
  setBottomPanelSize: (size: number) => void

  // Tab actions
  openTab: (tab: Omit<OpenTab, 'id'>) => void
  closeTab: (tabId: string) => void
  setActiveTab: (tabId: string) => void

  // Selection actions
  selectNamespace: (namespace: string | null) => void
  selectPointer: (pointerId: string | null) => void
  selectRun: (runId: string | null) => void
}

export const useWorkbenchStore = create<WorkbenchState>()(
  persist(
    (set, get) => ({
      // Initial state
      leftPanelCollapsed: false,
      rightPanelCollapsed: false,
      bottomPanelCollapsed: true,
      leftPanelSize: 20,
      rightPanelSize: 25,
      bottomPanelSize: 30,

      tabs: [],
      activeTabId: null,

      selectedNamespace: null,
      selectedPointerId: null,
      selectedRunId: null,

      // Panel actions
      toggleLeftPanel: () =>
        set((state) => ({ leftPanelCollapsed: !state.leftPanelCollapsed })),
      toggleRightPanel: () =>
        set((state) => ({ rightPanelCollapsed: !state.rightPanelCollapsed })),
      toggleBottomPanel: () =>
        set((state) => ({ bottomPanelCollapsed: !state.bottomPanelCollapsed })),
      setLeftPanelSize: (size) => set({ leftPanelSize: size }),
      setRightPanelSize: (size) => set({ rightPanelSize: size }),
      setBottomPanelSize: (size) => set({ bottomPanelSize: size }),

      // Tab actions
      openTab: (tab) => {
        const id = `${tab.type}-${tab.resourceId}`
        const existingTab = get().tabs.find((t) => t.id === id)

        if (existingTab) {
          set({ activeTabId: id })
        } else {
          set((state) => ({
            tabs: [...state.tabs, { ...tab, id }],
            activeTabId: id,
          }))
        }
      },

      closeTab: (tabId) => {
        const { tabs, activeTabId } = get()
        const tabIndex = tabs.findIndex((t) => t.id === tabId)
        const newTabs = tabs.filter((t) => t.id !== tabId)

        let newActiveTabId = activeTabId
        if (activeTabId === tabId) {
          // Activate adjacent tab
          if (newTabs.length > 0) {
            const newIndex = Math.min(tabIndex, newTabs.length - 1)
            newActiveTabId = newTabs[newIndex].id
          } else {
            newActiveTabId = null
          }
        }

        set({ tabs: newTabs, activeTabId: newActiveTabId })
      },

      setActiveTab: (tabId) => set({ activeTabId: tabId }),

      // Selection actions
      selectNamespace: (namespace) => set({ selectedNamespace: namespace }),
      selectPointer: (pointerId) => set({ selectedPointerId: pointerId }),
      selectRun: (runId) => {
        set({ selectedRunId: runId })
        if (runId) {
          // Auto-open run tab
          get().openTab({
            type: 'run',
            title: `Run ${runId.slice(0, 8)}`,
            resourceId: runId,
          })
        }
      },
    }),
    {
      name: 'intelli-workbench',
      partialize: (state) => ({
        leftPanelCollapsed: state.leftPanelCollapsed,
        rightPanelCollapsed: state.rightPanelCollapsed,
        bottomPanelCollapsed: state.bottomPanelCollapsed,
        leftPanelSize: state.leftPanelSize,
        rightPanelSize: state.rightPanelSize,
        bottomPanelSize: state.bottomPanelSize,
      }),
    }
  )
)
