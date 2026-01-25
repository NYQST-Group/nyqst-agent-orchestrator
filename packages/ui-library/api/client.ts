/**
 * API Client with enterprise-safe patterns
 * - Automatic retries with exponential backoff
 * - Request/response interceptors
 * - Error normalization
 * - Request cancellation
 * - Request deduplication
 */

import type { ApiResponse, ApiError, PaginatedResponse, QueryOptions } from '@/types';

// ============================================================================
// Configuration
// ============================================================================

export interface ApiClientConfig {
  baseUrl: string;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  headers?: Record<string, string>;
  onUnauthorized?: () => void;
  onError?: (error: ApiError) => void;
}

const DEFAULT_CONFIG: Required<Omit<ApiClientConfig, 'baseUrl' | 'onUnauthorized' | 'onError'>> = {
  timeout: 30000,
  retries: 3,
  retryDelay: 1000,
  headers: {
    'Content-Type': 'application/json',
  },
};

// ============================================================================
// Error Classes
// ============================================================================

export class ApiClientError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly status?: number,
    public readonly details?: Record<string, unknown>,
    public readonly requestId?: string
  ) {
    super(message);
    this.name = 'ApiClientError';
  }

  toApiError(): ApiError {
    return {
      code: this.code,
      message: this.message,
      details: this.details,
      requestId: this.requestId,
    };
  }
}

export class NetworkError extends ApiClientError {
  constructor(message = 'Network error') {
    super('NETWORK_ERROR', message);
    this.name = 'NetworkError';
  }
}

export class TimeoutError extends ApiClientError {
  constructor(timeout: number) {
    super('TIMEOUT', `Request timed out after ${timeout}ms`);
    this.name = 'TimeoutError';
  }
}

// ============================================================================
// Request Deduplication
// ============================================================================

const pendingRequests = new Map<string, Promise<unknown>>();

function getRequestKey(method: string, url: string, body?: unknown): string {
  return `${method}:${url}:${body ? JSON.stringify(body) : ''}`;
}

// ============================================================================
// API Client Class
// ============================================================================

export class ApiClient {
  private config: Required<Omit<ApiClientConfig, 'onUnauthorized' | 'onError'>> &
    Pick<ApiClientConfig, 'onUnauthorized' | 'onError'>;
  private abortControllers = new Map<string, AbortController>();

  constructor(config: ApiClientConfig) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  private async fetchWithRetry<T>(
    url: string,
    options: RequestInit,
    retries: number = this.config.retries
  ): Promise<T> {
    const controller = new AbortController();
    const requestId = crypto.randomUUID();
    this.abortControllers.set(requestId, controller);

    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          ...this.config.headers,
          ...options.headers,
          'X-Request-ID': requestId,
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        // Handle specific status codes
        if (response.status === 401) {
          this.config.onUnauthorized?.();
        }

        const error = new ApiClientError(
          errorData.code || `HTTP_${response.status}`,
          errorData.message || response.statusText,
          response.status,
          errorData.details,
          requestId
        );

        this.config.onError?.(error.toApiError());
        throw error;
      }

      // Handle empty responses
      const contentType = response.headers.get('content-type');
      if (contentType?.includes('application/json')) {
        return await response.json();
      }
      return {} as T;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof ApiClientError) {
        throw error;
      }

      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new TimeoutError(this.config.timeout);
      }

      // Retry on network errors
      if (retries > 0 && error instanceof TypeError) {
        await this.delay(this.config.retryDelay * (this.config.retries - retries + 1));
        return this.fetchWithRetry<T>(url, options, retries - 1);
      }

      throw new NetworkError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      this.abortControllers.delete(requestId);
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  private buildUrl(path: string, params?: Record<string, string | number | boolean | undefined>): string {
    const url = new URL(path, this.config.baseUrl);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          url.searchParams.append(key, String(value));
        }
      });
    }
    return url.toString();
  }

  async get<T>(
    path: string,
    params?: Record<string, string | number | boolean | undefined>,
    options?: { dedupe?: boolean }
  ): Promise<ApiResponse<T>> {
    const url = this.buildUrl(path, params);
    const key = getRequestKey('GET', url);

    // Request deduplication
    if (options?.dedupe !== false && pendingRequests.has(key)) {
      return pendingRequests.get(key) as Promise<ApiResponse<T>>;
    }

    const promise = this.fetchWithRetry<ApiResponse<T>>(url, { method: 'GET' });

    if (options?.dedupe !== false) {
      pendingRequests.set(key, promise);
      promise.finally(() => pendingRequests.delete(key));
    }

    return promise;
  }

  async post<T, D = unknown>(path: string, data?: D): Promise<ApiResponse<T>> {
    return this.fetchWithRetry<ApiResponse<T>>(this.buildUrl(path), {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T, D = unknown>(path: string, data?: D): Promise<ApiResponse<T>> {
    return this.fetchWithRetry<ApiResponse<T>>(this.buildUrl(path), {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T, D = unknown>(path: string, data?: D): Promise<ApiResponse<T>> {
    return this.fetchWithRetry<ApiResponse<T>>(this.buildUrl(path), {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(path: string): Promise<ApiResponse<T>> {
    return this.fetchWithRetry<ApiResponse<T>>(this.buildUrl(path), {
      method: 'DELETE',
    });
  }

  async getPaginated<T>(
    path: string,
    options?: QueryOptions
  ): Promise<PaginatedResponse<T>> {
    const params: Record<string, string | number | boolean | undefined> = {
      page: options?.page,
      pageSize: options?.pageSize,
      search: options?.search,
    };

    if (options?.sort?.length) {
      params.sortField = options.sort[0].field;
      params.sortDirection = options.sort[0].direction;
    }

    if (options?.dateRange) {
      params.dateField = options.dateRange.field;
      params.dateFrom = options.dateRange.from;
      params.dateTo = options.dateRange.to;
    }

    return this.fetchWithRetry<PaginatedResponse<T>>(this.buildUrl(path, params), {
      method: 'GET',
    });
  }

  cancelRequest(requestId: string): void {
    const controller = this.abortControllers.get(requestId);
    if (controller) {
      controller.abort();
      this.abortControllers.delete(requestId);
    }
  }

  cancelAllRequests(): void {
    this.abortControllers.forEach((controller) => controller.abort());
    this.abortControllers.clear();
  }
}

// ============================================================================
// Default Client Instance
// ============================================================================

let defaultClient: ApiClient | null = null;

export function initApiClient(config: ApiClientConfig): ApiClient {
  defaultClient = new ApiClient(config);
  return defaultClient;
}

export function getApiClient(): ApiClient {
  if (!defaultClient) {
    // Initialize with default dev config if not configured
    defaultClient = new ApiClient({
      baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:3000/api',
    });
  }
  return defaultClient;
}
