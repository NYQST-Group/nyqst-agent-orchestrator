/**
 * Tests for run-store.
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useRunStore } from './run-store'

describe('run-store', () => {
  beforeEach(() => {
    // Reset store to initial state
    useRunStore.setState({
      activeRunId: null,
    })
  })

  it('initial state has null activeRunId', () => {
    const state = useRunStore.getState()
    expect(state.activeRunId).toBeNull()
  })

  it('setActiveRunId updates state', () => {
    useRunStore.getState().setActiveRunId('run-123')
    const state = useRunStore.getState()
    expect(state.activeRunId).toBe('run-123')
  })

  it('setActiveRunId can set to null', () => {
    // First set to a value
    useRunStore.getState().setActiveRunId('run-123')
    expect(useRunStore.getState().activeRunId).toBe('run-123')

    // Then set back to null
    useRunStore.getState().setActiveRunId(null)
    expect(useRunStore.getState().activeRunId).toBeNull()
  })

  it('clear resets to null', () => {
    // Set to a value
    useRunStore.getState().setActiveRunId('run-456')
    expect(useRunStore.getState().activeRunId).toBe('run-456')

    // Clear should reset to null
    useRunStore.getState().clear()
    const state = useRunStore.getState()
    expect(state.activeRunId).toBeNull()
  })

  it('supports multiple updates', () => {
    useRunStore.getState().setActiveRunId('run-1')
    expect(useRunStore.getState().activeRunId).toBe('run-1')

    useRunStore.getState().setActiveRunId('run-2')
    expect(useRunStore.getState().activeRunId).toBe('run-2')

    useRunStore.getState().setActiveRunId('run-3')
    expect(useRunStore.getState().activeRunId).toBe('run-3')
  })
})
