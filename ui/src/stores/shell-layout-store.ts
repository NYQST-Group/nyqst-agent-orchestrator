import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ShellLayoutState {
  commandPaletteOpen: boolean
  opsOverlayOpen: boolean
  settingsOpen: boolean
  leftRailMobileOpen: boolean
  rightRailMobileOpen: boolean
  preferredModelId: string | null
  setCommandPaletteOpen: (open: boolean) => void
  setOpsOverlayOpen: (open: boolean) => void
  setSettingsOpen: (open: boolean) => void
  setLeftRailMobileOpen: (open: boolean) => void
  setRightRailMobileOpen: (open: boolean) => void
  setPreferredModelId: (modelId: string) => void
}

export const useShellLayoutStore = create<ShellLayoutState>()(
  persist(
    (set) => ({
      commandPaletteOpen: false,
      opsOverlayOpen: false,
      settingsOpen: false,
      leftRailMobileOpen: false,
      rightRailMobileOpen: false,
      preferredModelId: null,
      setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
      setOpsOverlayOpen: (open) => set({ opsOverlayOpen: open }),
      setSettingsOpen: (open) => set({ settingsOpen: open }),
      setLeftRailMobileOpen: (open) => set({ leftRailMobileOpen: open }),
      setRightRailMobileOpen: (open) => set({ rightRailMobileOpen: open }),
      setPreferredModelId: (preferredModelId) => set({ preferredModelId }),
    }),
    {
      name: 'intelli-shell-layout',
      partialize: (state) => ({
        preferredModelId: state.preferredModelId,
      }),
    }
  )
)
