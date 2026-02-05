/**
 * Unit tests for useSessionLifecycle hook.
 *
 * Tests session creation on mount and transition to idle on unmount.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'

import { useSessionLifecycle } from '@/hooks/use-session-lifecycle'
import { useConversationStore } from '@/stores/conversation-store'

// Hoist mock functions with default implementations
const mockCreate = vi.hoisted(() =>
  vi.fn().mockResolvedValue({ id: 'default', status: 'active', module: 'research' })
)
const mockUpdateStatus = vi.hoisted(() => vi.fn().mockResolvedValue({}))

// Mock the sessions API
vi.mock('@/api/sessions', () => ({
  sessionsApi: {
    create: mockCreate,
    updateStatus: mockUpdateStatus,
  },
}))

describe('useSessionLifecycle', () => {
  beforeEach(() => {
    // Reset store state
    useConversationStore.getState().clear()
    useConversationStore.getState().setActiveSessionId(null)

    // Clear call history but keep implementations
    mockCreate.mockClear()
    mockUpdateStatus.mockClear()

    // Set default implementations
    mockCreate.mockResolvedValue({ id: 'default', status: 'active', module: 'research' })
    mockUpdateStatus.mockResolvedValue({})
  })

  afterEach(() => {
    // NOTE: Do NOT use vi.restoreAllMocks() here!
    // React's cleanup phase runs AFTER afterEach, and the hook's
    // cleanup function calls sessionsApi.updateStatus which needs
    // the mock to still be in place.
  })

  describe('session creation on mount', () => {
    it('creates a session with the specified module on mount', async () => {
      const mockSession = { id: 'sess-123', status: 'active', module: 'research' }
      mockCreate.mockResolvedValue(mockSession)

      renderHook(() => useSessionLifecycle('research'))

      await waitFor(() => {
        expect(mockCreate).toHaveBeenCalledWith({ module: 'research' })
      })
    })

    it('sets the active session ID in the store after creation', async () => {
      const mockSession = { id: 'sess-456', status: 'active', module: 'analysis' }
      mockCreate.mockResolvedValue(mockSession)

      renderHook(() => useSessionLifecycle('analysis'))

      await waitFor(() => {
        expect(useConversationStore.getState().activeSessionId).toBe('sess-456')
      })
    })

    it('does not create a new session if one already exists', async () => {
      // Pre-set an active session
      useConversationStore.getState().setActiveSessionId('existing-session')

      renderHook(() => useSessionLifecycle('research'))

      // Wait a tick to ensure effect ran
      await new Promise((r) => setTimeout(r, 10))

      // Should not call create since there's already an active session
      expect(mockCreate).not.toHaveBeenCalled()
    })

    it('handles session creation failure gracefully', async () => {
      const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {})
      mockCreate.mockRejectedValue(new Error('Network error'))

      renderHook(() => useSessionLifecycle('research'))

      await waitFor(() => {
        expect(consoleWarn).toHaveBeenCalledWith(
          'Failed to create session:',
          expect.any(Error)
        )
      })

      consoleWarn.mockRestore()
    })
  })

  describe('session transition on unmount', () => {
    it('transitions session to idle on unmount', async () => {
      const mockSession = { id: 'sess-unmount', status: 'active', module: 'research' }
      mockCreate.mockResolvedValue(mockSession)
      mockUpdateStatus.mockResolvedValue({ ...mockSession, status: 'idle' })

      const { unmount } = renderHook(() => useSessionLifecycle('research'))

      // Wait for session to be created
      await waitFor(() => {
        expect(mockCreate).toHaveBeenCalled()
      })

      // Unmount the hook
      unmount()

      // Should transition to idle
      await waitFor(() => {
        expect(mockUpdateStatus).toHaveBeenCalledWith('sess-unmount', { status: 'idle' })
      })
    })

    it('handles transition failure gracefully', async () => {
      const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const mockSession = { id: 'sess-fail', status: 'active', module: 'research' }
      mockCreate.mockResolvedValue(mockSession)
      mockUpdateStatus.mockRejectedValue(new Error('Network error'))

      const { unmount } = renderHook(() => useSessionLifecycle('research'))

      await waitFor(() => {
        expect(mockCreate).toHaveBeenCalled()
      })

      unmount()

      await waitFor(() => {
        expect(consoleWarn).toHaveBeenCalledWith(
          'Failed to update session status:',
          expect.any(Error)
        )
      })

      consoleWarn.mockRestore()
    })

    it('does not attempt transition if no session was created', async () => {
      // Pre-set an active session (so create won't be called and sessionRef never set)
      useConversationStore.getState().setActiveSessionId('existing')

      const { unmount } = renderHook(() => useSessionLifecycle('research'))

      // Wait a tick
      await new Promise((r) => setTimeout(r, 10))

      unmount()

      // Wait a tick for cleanup
      await new Promise((r) => setTimeout(r, 10))

      // updateStatus should not be called since sessionRef was never set
      expect(mockUpdateStatus).not.toHaveBeenCalled()
    })
  })

  describe('return value', () => {
    it('returns the active session ID', async () => {
      const mockSession = { id: 'sess-return', status: 'active', module: 'research' }
      mockCreate.mockResolvedValue(mockSession)

      const { result } = renderHook(() => useSessionLifecycle('research'))

      await waitFor(() => {
        expect(result.current).toBe('sess-return')
      })
    })

    it('returns existing session ID if already set', () => {
      useConversationStore.getState().setActiveSessionId('pre-existing')

      const { result } = renderHook(() => useSessionLifecycle('research'))

      expect(result.current).toBe('pre-existing')
    })
  })
})
