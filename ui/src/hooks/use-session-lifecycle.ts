/**
 * Hook to manage session lifecycle for a module.
 *
 * Creates a session on mount and transitions it to idle on unmount.
 * Sessions are used for cost tracking and conversation grouping.
 */

import { useEffect, useRef } from 'react'

import { useConversationStore } from '@/stores/conversation-store'
import { sessionsApi } from '@/api/sessions'

export function useSessionLifecycle(module: string) {
  const { setActiveSessionId, activeSessionId } = useConversationStore()
  const sessionRef = useRef<string | null>(null)

  // Create session on mount
  useEffect(() => {
    // If there's already an active session, use it
    if (activeSessionId) {
      sessionRef.current = activeSessionId
      return
    }

    // Track if unmounted during async session creation
    let unmounted = false

    async function createSession() {
      try {
        const session = await sessionsApi.create({ module })

        // If unmounted while creating, clean up immediately
        if (unmounted) {
          sessionsApi.updateStatus(session.id, { status: 'idle' }).catch((error) => {
            console.warn('Failed to idle orphaned session:', error)
          })
          return
        }

        setActiveSessionId(session.id)
        sessionRef.current = session.id
      } catch (error) {
        if (!unmounted) {
          console.warn('Failed to create session:', error)
        }
      }
    }

    createSession()

    // Idle session on unmount
    return () => {
      unmounted = true
      const sessionId = sessionRef.current
      if (sessionId) {
        sessionsApi.updateStatus(sessionId, { status: 'idle' }).catch((error) => {
          console.warn('Failed to update session status:', error)
        })
      }
    }
    // Only run on mount/unmount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return activeSessionId
}
