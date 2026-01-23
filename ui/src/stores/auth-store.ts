/**
 * Auth store for managing authentication state
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  // Auth tokens
  accessToken: string | null
  apiKey: string | null

  // User info
  userId: string | null
  tenantId: string | null
  tenantName: string | null
  role: string | null
  scopes: string[]

  // State
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Actions
  setAccessToken: (token: string, userInfo: {
    userId: string
    tenantId: string
    tenantName?: string
    role?: string
  }) => void
  setApiKey: (key: string) => void
  logout: () => void
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      apiKey: null,
      userId: null,
      tenantId: null,
      tenantName: null,
      role: null,
      scopes: [],
      isAuthenticated: false,
      isLoading: false,
      error: null,

      setAccessToken: (token, userInfo) =>
        set({
          accessToken: token,
          userId: userInfo.userId,
          tenantId: userInfo.tenantId,
          tenantName: userInfo.tenantName || null,
          role: userInfo.role || null,
          isAuthenticated: true,
          error: null,
        }),

      setApiKey: (key) =>
        set({
          apiKey: key,
          isAuthenticated: true,
          error: null,
        }),

      logout: () =>
        set({
          accessToken: null,
          apiKey: null,
          userId: null,
          tenantId: null,
          tenantName: null,
          role: null,
          scopes: [],
          isAuthenticated: false,
          error: null,
        }),

      clearError: () => set({ error: null }),
    }),
    {
      name: 'intelli-auth',
      partialize: (state) => ({
        accessToken: state.accessToken,
        apiKey: state.apiKey,
        userId: state.userId,
        tenantId: state.tenantId,
        tenantName: state.tenantName,
        role: state.role,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

/**
 * Get authorization headers for API requests
 */
export function getAuthHeaders(): Record<string, string> {
  const { accessToken, apiKey } = useAuthStore.getState()

  if (apiKey) {
    return { 'X-API-Key': apiKey }
  }

  if (accessToken) {
    return { Authorization: `Bearer ${accessToken}` }
  }

  return {}
}
