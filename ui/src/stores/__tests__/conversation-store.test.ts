import { describe, it, expect, beforeEach } from 'vitest'
import { useConversationStore } from '../conversation-store'
import { makeConversation } from '@/test/factories'

describe('conversation-store', () => {
  beforeEach(() => {
    // Reset store to initial state
    useConversationStore.setState({
      conversations: [],
      activeConversationId: null,
      activeSessionId: null,
    })
  })

  it('test_initial_state_is_empty', () => {
    const state = useConversationStore.getState()
    expect(state.conversations).toEqual([])
    expect(state.activeConversationId).toBeNull()
    expect(state.activeSessionId).toBeNull()
  })

  it('test_set_conversations_replaces_list', () => {
    const convs = [
      makeConversation({ title: 'First' }),
      makeConversation({ title: 'Second' }),
    ]
    useConversationStore.getState().setConversations(convs)
    const state = useConversationStore.getState()
    expect(state.conversations).toEqual(convs)
  })

  it('test_add_conversation_prepends', () => {
    const existing = makeConversation({ title: 'Existing' })
    useConversationStore.setState({ conversations: [existing] })

    const newConv = makeConversation({ title: 'New' })
    useConversationStore.getState().addConversation(newConv)

    const state = useConversationStore.getState()
    expect(state.conversations).toHaveLength(2)
    expect(state.conversations[0]).toEqual(newConv)
    expect(state.conversations[1]).toEqual(existing)
  })

  it('test_add_conversation_deduplicates', () => {
    const conv = makeConversation({ title: 'Test' })
    useConversationStore.setState({ conversations: [conv] })

    // Try to add the same conversation again
    useConversationStore.getState().addConversation(conv)

    const state = useConversationStore.getState()
    expect(state.conversations).toHaveLength(1)
    expect(state.conversations[0]).toEqual(conv)
  })

  it('test_update_conversation_merges_fields', () => {
    const conv = makeConversation({ title: 'Original', message_count: 5 })
    useConversationStore.setState({ conversations: [conv] })

    useConversationStore.getState().updateConversation(conv.id, {
      title: 'Updated',
      message_count: 10,
    })

    const state = useConversationStore.getState()
    expect(state.conversations[0].title).toBe('Updated')
    expect(state.conversations[0].message_count).toBe(10)
    // Other fields should remain unchanged
    expect(state.conversations[0].id).toBe(conv.id)
    expect(state.conversations[0].tenant_id).toBe(conv.tenant_id)
  })

  it('test_remove_conversation_filters_out', () => {
    const conv1 = makeConversation({ title: 'First' })
    const conv2 = makeConversation({ title: 'Second' })
    const conv3 = makeConversation({ title: 'Third' })
    useConversationStore.setState({ conversations: [conv1, conv2, conv3] })

    useConversationStore.getState().removeConversation(conv2.id)

    const state = useConversationStore.getState()
    expect(state.conversations).toHaveLength(2)
    expect(state.conversations.find((c) => c.id === conv2.id)).toBeUndefined()
    expect(state.conversations.find((c) => c.id === conv1.id)).toBeDefined()
    expect(state.conversations.find((c) => c.id === conv3.id)).toBeDefined()
  })

  it('test_remove_active_conversation_clears_active_id', () => {
    const conv = makeConversation({ title: 'Active' })
    useConversationStore.setState({
      conversations: [conv],
      activeConversationId: conv.id,
    })

    useConversationStore.getState().removeConversation(conv.id)

    const state = useConversationStore.getState()
    expect(state.conversations).toHaveLength(0)
    expect(state.activeConversationId).toBeNull()
  })

  it('test_set_active_conversation_id', () => {
    useConversationStore.getState().setActiveConversationId('conv-123')
    const state = useConversationStore.getState()
    expect(state.activeConversationId).toBe('conv-123')
  })

  it('test_set_active_session_id', () => {
    useConversationStore.getState().setActiveSessionId('session-456')
    const state = useConversationStore.getState()
    expect(state.activeSessionId).toBe('session-456')
  })

  it('test_clear_resets_all_state', () => {
    const conv = makeConversation({ title: 'Test' })
    useConversationStore.setState({
      conversations: [conv],
      activeConversationId: 'conv-123',
      activeSessionId: 'session-456',
    })

    useConversationStore.getState().clear()

    const state = useConversationStore.getState()
    expect(state.conversations).toEqual([])
    expect(state.activeConversationId).toBeNull()
    expect(state.activeSessionId).toBeNull()
  })
})
