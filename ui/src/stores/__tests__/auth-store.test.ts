import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore, getAuthHeaders } from '../auth-store'

describe('auth-store', () => {
  beforeEach(() => {
    // Reset store to initial state
    useAuthStore.setState({
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
    })
  })

  it('starts unauthenticated', () => {
    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(false)
    expect(state.accessToken).toBeNull()
  })

  it('setAccessToken sets auth state', () => {
    useAuthStore.getState().setAccessToken('tok-123', {
      userId: 'u1',
      tenantId: 't1',
      tenantName: 'Demo',
      role: 'owner',
    })
    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(true)
    expect(state.accessToken).toBe('tok-123')
    expect(state.userId).toBe('u1')
    expect(state.tenantId).toBe('t1')
    expect(state.tenantName).toBe('Demo')
    expect(state.role).toBe('owner')
  })

  it('setApiKey sets auth state', () => {
    useAuthStore.getState().setApiKey('int_abc123')
    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(true)
    expect(state.apiKey).toBe('int_abc123')
  })

  it('logout clears all state', () => {
    useAuthStore.getState().setAccessToken('tok', {
      userId: 'u', tenantId: 't',
    })
    useAuthStore.getState().logout()
    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(false)
    expect(state.accessToken).toBeNull()
    expect(state.userId).toBeNull()
  })

  it('clearError clears error', () => {
    useAuthStore.setState({ error: 'something broke' })
    useAuthStore.getState().clearError()
    expect(useAuthStore.getState().error).toBeNull()
  })

  it('setAccessToken clears previous error', () => {
    useAuthStore.setState({ error: 'old error' })
    useAuthStore.getState().setAccessToken('tok', { userId: 'u', tenantId: 't' })
    expect(useAuthStore.getState().error).toBeNull()
  })

  it('tenantName defaults to null when not provided', () => {
    useAuthStore.getState().setAccessToken('tok', {
      userId: 'u', tenantId: 't',
    })
    expect(useAuthStore.getState().tenantName).toBeNull()
  })

  it('role defaults to null when not provided', () => {
    useAuthStore.getState().setAccessToken('tok', {
      userId: 'u', tenantId: 't',
    })
    expect(useAuthStore.getState().role).toBeNull()
  })
})

describe('getAuthHeaders', () => {
  beforeEach(() => {
    useAuthStore.setState({
      accessToken: null,
      apiKey: null,
      isAuthenticated: false,
    })
  })

  it('returns empty object when no auth', () => {
    expect(getAuthHeaders()).toEqual({})
  })

  it('returns Bearer header with access token', () => {
    useAuthStore.setState({ accessToken: 'my-token' })
    expect(getAuthHeaders()).toEqual({ Authorization: 'Bearer my-token' })
  })

  it('prefers API key over access token', () => {
    useAuthStore.setState({ accessToken: 'tok', apiKey: 'int_key' })
    expect(getAuthHeaders()).toEqual({ 'X-API-Key': 'int_key' })
  })
})
