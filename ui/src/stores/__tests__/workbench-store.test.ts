import { describe, it, expect, beforeEach } from 'vitest'
import { useWorkbenchStore } from '../workbench-store'

describe('workbench-store', () => {
  beforeEach(() => {
    useWorkbenchStore.setState({
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
    })
  })

  it('opens a new tab and activates it', () => {
    useWorkbenchStore.getState().openTab({
      type: 'artifact',
      title: 'Test',
      resourceId: 'abc',
    })
    const state = useWorkbenchStore.getState()
    expect(state.tabs).toHaveLength(1)
    expect(state.activeTabId).toBe('artifact-abc')
  })

  it('does not duplicate existing tab', () => {
    const tab = { type: 'artifact' as const, title: 'Test', resourceId: 'abc' }
    useWorkbenchStore.getState().openTab(tab)
    useWorkbenchStore.getState().openTab(tab)
    expect(useWorkbenchStore.getState().tabs).toHaveLength(1)
  })

  it('closes tab and activates adjacent', () => {
    useWorkbenchStore.getState().openTab({ type: 'artifact', title: 'A', resourceId: '1' })
    useWorkbenchStore.getState().openTab({ type: 'artifact', title: 'B', resourceId: '2' })
    // Active is artifact-2
    useWorkbenchStore.getState().closeTab('artifact-2')
    const state = useWorkbenchStore.getState()
    expect(state.tabs).toHaveLength(1)
    expect(state.activeTabId).toBe('artifact-1')
  })

  it('selectRun auto-opens run tab', () => {
    useWorkbenchStore.getState().selectRun('run-id-12345678')
    const state = useWorkbenchStore.getState()
    expect(state.selectedRunId).toBe('run-id-12345678')
    expect(state.tabs).toHaveLength(1)
    expect(state.tabs[0].type).toBe('run')
  })

  it('selectNamespace updates state', () => {
    useWorkbenchStore.getState().selectNamespace('notebooks')
    expect(useWorkbenchStore.getState().selectedNamespace).toBe('notebooks')
  })
})
