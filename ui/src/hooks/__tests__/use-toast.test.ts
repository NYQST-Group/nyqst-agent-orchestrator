import { describe, it, expect } from 'vitest'
import { reducer, toast } from '../use-toast'

describe('toast reducer', () => {
  const emptyState = { toasts: [] }

  it('ADD_TOAST adds a toast', () => {
    const result = reducer(emptyState, {
      type: 'ADD_TOAST',
      toast: { id: '1', open: true },
    })
    expect(result.toasts).toHaveLength(1)
    expect(result.toasts[0].id).toBe('1')
  })

  it('ADD_TOAST limits to TOAST_LIMIT (1)', () => {
    const state = reducer(emptyState, {
      type: 'ADD_TOAST',
      toast: { id: '1', open: true },
    })
    const result = reducer(state, {
      type: 'ADD_TOAST',
      toast: { id: '2', open: true },
    })
    // TOAST_LIMIT = 1, so only latest toast remains
    expect(result.toasts).toHaveLength(1)
    expect(result.toasts[0].id).toBe('2')
  })

  it('UPDATE_TOAST updates matching toast', () => {
    const state = {
      toasts: [{ id: '1', open: true, title: 'old' } as any],
    }
    const result = reducer(state, {
      type: 'UPDATE_TOAST',
      toast: { id: '1', title: 'new' },
    })
    expect(result.toasts[0].title).toBe('new')
  })

  it('DISMISS_TOAST sets open to false', () => {
    const state = {
      toasts: [{ id: '1', open: true } as any],
    }
    const result = reducer(state, {
      type: 'DISMISS_TOAST',
      toastId: '1',
    })
    expect(result.toasts[0].open).toBe(false)
  })

  it('REMOVE_TOAST removes specific toast', () => {
    const state = {
      toasts: [{ id: '1', open: true } as any],
    }
    const result = reducer(state, {
      type: 'REMOVE_TOAST',
      toastId: '1',
    })
    expect(result.toasts).toHaveLength(0)
  })
})

describe('toast function', () => {
  it('returns id and control functions', () => {
    const result = toast({ title: 'Test' } as any)
    expect(result.id).toBeDefined()
    expect(typeof result.dismiss).toBe('function')
    expect(typeof result.update).toBe('function')
  })
})
