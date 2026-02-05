import { describe, it, expect, vi, beforeEach, afterEach, afterAll } from 'vitest'
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { authApi, ApiError } from '@/api/auth'

// Mock the auth store
vi.mock('@/stores/auth-store', () => ({
  getAuthHeaders: vi.fn(() => ({ Authorization: 'Bearer test-token' })),
}))

const server = setupServer()

beforeEach(() => {
  server.listen({ onUnhandledRequest: 'error' })
})

afterEach(() => {
  server.resetHandlers()
})

afterAll(() => {
  server.close()
})

// Helper to capture request details - avoids TypeScript 'never' narrowing issue
interface RequestCapture {
  url?: URL
  path?: string
  headers?: Headers
  body?: unknown
}

describe('authApi', () => {
  describe('login', () => {
    it('test_login_sends_post_with_credentials', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.post('/api/v1/auth/login', async ({ request }) => {
          capture.body = await request.json()
          return HttpResponse.json({
            access_token: 'jwt-token-123',
            token_type: 'bearer',
            expires_in: 3600,
            tenant_id: 'tenant-1',
            user_id: 'user-1',
          })
        })
      )

      const credentials = {
        email: 'test@example.com',
        password: 'password123',
        tenant_slug: 'acme',
      }

      await authApi.login(credentials)

      expect(capture.body).toEqual(credentials)
    })

    it('test_login_returns_token_on_success', async () => {
      const mockResponse = {
        access_token: 'jwt-token-123',
        token_type: 'bearer',
        expires_in: 3600,
        tenant_id: 'tenant-1',
        user_id: 'user-1',
      }

      server.use(
        http.post('/api/v1/auth/login', () => {
          return HttpResponse.json(mockResponse)
        })
      )

      const result = await authApi.login({
        email: 'test@example.com',
        password: 'password123',
        tenant_slug: 'acme',
      })

      expect(result).toEqual(mockResponse)
      expect(result.access_token).toBe('jwt-token-123')
      expect(result.user_id).toBe('user-1')
    })

    it('test_login_throws_api_error_on_failure', async () => {
      server.use(
        http.post('/api/v1/auth/login', () => {
          return HttpResponse.json(
            { detail: 'Invalid credentials' },
            { status: 401, statusText: 'Unauthorized' }
          )
        })
      )

      await expect(
        authApi.login({
          email: 'test@example.com',
          password: 'wrong',
          tenant_slug: 'acme',
        })
      ).rejects.toThrow(ApiError)

      try {
        await authApi.login({
          email: 'test@example.com',
          password: 'wrong',
          tenant_slug: 'acme',
        })
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError)
        const apiError = error as ApiError
        expect(apiError.status).toBe(401)
        expect(apiError.statusText).toBe('Unauthorized')
        expect(apiError.body).toEqual({ detail: 'Invalid credentials' })
      }
    })
  })

  describe('devBootstrap', () => {
    it('test_dev_bootstrap_sends_post', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.post('/api/v1/auth/dev-bootstrap', async ({ request }) => {
          capture.body = await request.json()
          return HttpResponse.json({
            access_token: 'dev-token',
            token_type: 'bearer',
            expires_in: 3600,
            tenant_id: 'dev-tenant',
            user_id: 'dev-user',
          })
        })
      )

      const bootstrapData = {
        tenant_slug: 'dev-tenant',
        email: 'dev@example.com',
      }

      await authApi.devBootstrap(bootstrapData)

      expect(capture.body).toEqual(bootstrapData)
    })

    it('test_dev_bootstrap_works_with_empty_body', async () => {
      server.use(
        http.post('/api/v1/auth/dev-bootstrap', () => {
          return HttpResponse.json({
            access_token: 'dev-token',
            token_type: 'bearer',
            expires_in: 3600,
            tenant_id: 'dev-tenant',
            user_id: 'dev-user',
          })
        })
      )

      const result = await authApi.devBootstrap()
      expect(result.access_token).toBe('dev-token')
    })
  })

  describe('getCurrentUser', () => {
    it('test_get_current_user_includes_auth_headers', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.get('/api/v1/auth/me', ({ request }) => {
          capture.headers = request.headers
          return HttpResponse.json({
            user_id: 'user-1',
            tenant_id: 'tenant-1',
            tenant_name: 'ACME Corp',
            role: 'admin',
            scopes: ['read:all', 'write:all'],
            api_key_id: null,
          })
        })
      )

      await authApi.getCurrentUser()

      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
    })

    it('test_get_current_user_returns_user_data', async () => {
      const mockUser = {
        user_id: 'user-1',
        tenant_id: 'tenant-1',
        tenant_name: 'ACME Corp',
        role: 'admin',
        scopes: ['read:all', 'write:all'],
        api_key_id: null,
      }

      server.use(
        http.get('/api/v1/auth/me', () => {
          return HttpResponse.json(mockUser)
        })
      )

      const result = await authApi.getCurrentUser()
      expect(result).toEqual(mockUser)
    })
  })

  describe('listAPIKeys', () => {
    it('test_list_api_keys_includes_auth_headers', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.get('/api/v1/auth/keys', ({ request }) => {
          capture.headers = request.headers
          return HttpResponse.json([])
        })
      )

      await authApi.listAPIKeys()

      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
    })

    it('test_list_api_keys_returns_keys', async () => {
      const mockKeys = [
        {
          id: 'key-1',
          name: 'Production Key',
          key_prefix: 'sk_prod_',
          scopes: ['read:all'],
          expires_at: null,
          rate_limit_rpm: 60,
          is_active: true,
          last_used_at: null,
          use_count: 0,
          created_at: '2024-01-01T00:00:00Z',
        },
      ]

      server.use(
        http.get('/api/v1/auth/keys', () => {
          return HttpResponse.json(mockKeys)
        })
      )

      const result = await authApi.listAPIKeys()
      expect(result).toEqual(mockKeys)
    })
  })

  describe('createAPIKey', () => {
    it('test_create_api_key_sends_body', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.post('/api/v1/auth/keys', async ({ request }) => {
          capture.body = await request.json()
          capture.headers = request.headers
          return HttpResponse.json({
            id: 'key-1',
            name: 'Test Key',
            key_prefix: 'sk_test_',
            scopes: ['read:all'],
            expires_at: null,
            rate_limit_rpm: 60,
            is_active: true,
            last_used_at: null,
            use_count: 0,
            created_at: '2024-01-01T00:00:00Z',
            full_key: 'sk_test_1234567890abcdef',
          })
        })
      )

      const keyData = {
        name: 'Test Key',
        scopes: ['read:all'],
        expires_in_days: 30,
        rate_limit_rpm: 100,
      }

      await authApi.createAPIKey(keyData)

      expect(capture.body).toEqual(keyData)
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
      expect(capture.headers?.get('Content-Type')).toBe('application/json')
    })

    it('test_create_api_key_returns_full_key', async () => {
      const mockResponse = {
        id: 'key-1',
        name: 'Test Key',
        key_prefix: 'sk_test_',
        scopes: ['read:all'],
        expires_at: null,
        rate_limit_rpm: 60,
        is_active: true,
        last_used_at: null,
        use_count: 0,
        created_at: '2024-01-01T00:00:00Z',
        full_key: 'sk_test_1234567890abcdef',
      }

      server.use(
        http.post('/api/v1/auth/keys', () => {
          return HttpResponse.json(mockResponse)
        })
      )

      const result = await authApi.createAPIKey({
        name: 'Test Key',
        scopes: ['read:all'],
      })

      expect(result.full_key).toBe('sk_test_1234567890abcdef')
      expect(result.id).toBe('key-1')
    })
  })

  describe('revokeAPIKey', () => {
    it('test_revoke_api_key_sends_delete', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.delete('/api/v1/auth/keys/:keyId', ({ request, params }) => {
          capture.path = `/api/v1/auth/keys/${params.keyId}`
          capture.headers = request.headers
          return new HttpResponse(null, { status: 204 })
        })
      )

      await authApi.revokeAPIKey('key-123')

      expect(capture.path).toBe('/api/v1/auth/keys/key-123')
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
    })

    it('test_revoke_api_key_throws_on_error', async () => {
      server.use(
        http.delete('/api/v1/auth/keys/:keyId', () => {
          return HttpResponse.json(
            { detail: 'Key not found' },
            { status: 404, statusText: 'Not Found' }
          )
        })
      )

      await expect(authApi.revokeAPIKey('key-999')).rejects.toThrow(ApiError)
    })
  })
})
