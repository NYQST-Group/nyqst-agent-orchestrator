import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore, getAuthHeaders } from '@/stores/auth-store'
import { ApiError } from '@/api/client'

describe('ApiError', () => {
  it('creates error with status and statusText', () => {
    const err = new ApiError(404, 'Not Found')
    expect(err.status).toBe(404)
    expect(err.statusText).toBe('Not Found')
    expect(err.message).toContain('404')
  })

  it('includes body when provided', () => {
    const err = new ApiError(400, 'Bad Request', { detail: 'invalid' })
    expect(err.body).toEqual({ detail: 'invalid' })
  })

  it('is an instance of Error', () => {
    const err = new ApiError(500, 'Server Error')
    expect(err).toBeInstanceOf(Error)
    expect(err.name).toBe('ApiError')
  })
})

describe('getAuthHeaders integration', () => {
  beforeEach(() => {
    useAuthStore.setState({
      accessToken: null,
      apiKey: null,
    })
  })

  it('withAuth uses token from store', () => {
    useAuthStore.setState({ accessToken: 'test-jwt' })
    const headers = getAuthHeaders()
    expect(headers).toEqual({ Authorization: 'Bearer test-jwt' })
  })
})
