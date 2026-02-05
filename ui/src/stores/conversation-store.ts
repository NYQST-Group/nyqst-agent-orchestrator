/**
 * Conversation state management with Zustand.
 *
 * Tracks conversations, active conversation, and active session.
 * Persisted to localStorage for cross-tab continuity.
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ConversationResponse } from '@/types/conversations'

interface ConversationState {
  conversations: ConversationResponse[]
  activeConversationId: string | null
  activeSessionId: string | null

  // Actions
  setConversations: (conversations: ConversationResponse[]) => void
  addConversation: (conversation: ConversationResponse) => void
  updateConversation: (id: string, updates: Partial<ConversationResponse>) => void
  removeConversation: (id: string) => void
  setActiveConversationId: (id: string | null) => void
  setActiveSessionId: (id: string | null) => void
  clear: () => void
}

export const useConversationStore = create<ConversationState>()(
  persist(
    (set) => ({
      conversations: [],
      activeConversationId: null,
      activeSessionId: null,

      setConversations: (conversations) => set({ conversations }),

      addConversation: (conversation) =>
        set((state) => {
          if (state.conversations.some((c) => c.id === conversation.id)) return state
          return { conversations: [conversation, ...state.conversations] }
        }),

      updateConversation: (id, updates) =>
        set((state) => ({
          conversations: state.conversations.map((c) =>
            c.id === id ? { ...c, ...updates } : c
          ),
        })),

      removeConversation: (id) =>
        set((state) => ({
          conversations: state.conversations.filter((c) => c.id !== id),
          activeConversationId:
            state.activeConversationId === id ? null : state.activeConversationId,
        })),

      setActiveConversationId: (id) => set({ activeConversationId: id }),
      setActiveSessionId: (id) => set({ activeSessionId: id }),
      clear: () =>
        set({ conversations: [], activeConversationId: null, activeSessionId: null }),
    }),
    {
      name: 'intelli-conversations',
      partialize: (state) => ({
        activeConversationId: state.activeConversationId,
        activeSessionId: state.activeSessionId,
      }),
    }
  )
)
