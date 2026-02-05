/**
 * Run state management with Zustand.
 *
 * Tracks the active run ID for timeline display.
 */

import { create } from 'zustand'

interface RunState {
  activeRunId: string | null
  setActiveRunId: (id: string | null) => void
  clear: () => void
}

export const useRunStore = create<RunState>()((set) => ({
  activeRunId: null,
  setActiveRunId: (id) => set({ activeRunId: id }),
  clear: () => set({ activeRunId: null }),
}))
