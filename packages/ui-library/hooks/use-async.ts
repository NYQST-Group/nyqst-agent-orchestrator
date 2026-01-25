/**
 * Async operation hooks with enterprise-safe patterns
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { useQuery, useMutation, useInfiniteQuery, useQueryClient } from '@tanstack/react-query';
import type { UseQueryOptions, UseMutationOptions, UseInfiniteQueryOptions } from '@tanstack/react-query';
import { getApiClient, ApiClientError } from '@/api/client';
import type { ApiResponse, PaginatedResponse, QueryOptions, UUID } from '@/types';

// ============================================================================
// Types
// ============================================================================

export interface AsyncState<T> {
  data: T | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
}

export interface UseAsyncOptions {
  onSuccess?: (data: unknown) => void;
  onError?: (error: Error) => void;
  retry?: number;
}

// ============================================================================
// Core Async Hook
// ============================================================================

/**
 * Hook for managing async operations with loading/error states
 */
export function useAsync<T, Args extends unknown[]>(
  asyncFn: (...args: Args) => Promise<T>,
  options?: UseAsyncOptions
) {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    isLoading: false,
    isError: false,
    error: null,
  });

  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const execute = useCallback(
    async (...args: Args): Promise<T | null> => {
      setState((prev) => ({ ...prev, isLoading: true, isError: false, error: null }));

      try {
        const data = await asyncFn(...args);
        if (mountedRef.current) {
          setState({ data, isLoading: false, isError: false, error: null });
          options?.onSuccess?.(data);
        }
        return data;
      } catch (error) {
        if (mountedRef.current) {
          const err = error instanceof Error ? error : new Error(String(error));
          setState({ data: null, isLoading: false, isError: true, error: err });
          options?.onError?.(err);
        }
        return null;
      }
    },
    [asyncFn, options]
  );

  const reset = useCallback(() => {
    setState({ data: null, isLoading: false, isError: false, error: null });
  }, []);

  return { ...state, execute, reset };
}

// ============================================================================
// Debounced Async Hook
// ============================================================================

/**
 * Hook for debounced async operations (useful for search)
 */
export function useDebouncedAsync<T, Args extends unknown[]>(
  asyncFn: (...args: Args) => Promise<T>,
  delay: number = 300,
  options?: UseAsyncOptions
) {
  const { execute, ...state } = useAsync(asyncFn, options);
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const debouncedExecute = useCallback(
    (...args: Args) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = setTimeout(() => {
        execute(...args);
      }, delay);
    },
    [execute, delay]
  );

  const cancel = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
  }, []);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return { ...state, execute: debouncedExecute, cancel };
}

// ============================================================================
// API Query Hooks (React Query wrappers)
// ============================================================================

/**
 * Generic hook for fetching a single resource
 */
export function useApiQuery<T>(
  key: string[],
  path: string,
  params?: Record<string, string | number | boolean | undefined>,
  options?: Omit<UseQueryOptions<ApiResponse<T>, ApiClientError>, 'queryKey' | 'queryFn'>
) {
  const client = getApiClient();

  return useQuery<ApiResponse<T>, ApiClientError>({
    queryKey: key,
    queryFn: () => client.get<T>(path, params),
    ...options,
  });
}

/**
 * Generic hook for fetching a paginated list
 */
export function useApiPaginatedQuery<T>(
  key: string[],
  path: string,
  queryOptions?: QueryOptions,
  options?: Omit<UseQueryOptions<PaginatedResponse<T>, ApiClientError>, 'queryKey' | 'queryFn'>
) {
  const client = getApiClient();

  return useQuery<PaginatedResponse<T>, ApiClientError>({
    queryKey: [...key, queryOptions],
    queryFn: () => client.getPaginated<T>(path, queryOptions),
    ...options,
  });
}

/**
 * Generic hook for infinite scroll pagination
 */
export function useApiInfiniteQuery<T>(
  key: string[],
  path: string,
  queryOptions?: Omit<QueryOptions, 'page'>,
  options?: Omit<
    UseInfiniteQueryOptions<PaginatedResponse<T>, ApiClientError>,
    'queryKey' | 'queryFn' | 'getNextPageParam' | 'initialPageParam'
  >
) {
  const client = getApiClient();

  return useInfiniteQuery<PaginatedResponse<T>, ApiClientError>({
    queryKey: [...key, queryOptions],
    queryFn: ({ pageParam }) =>
      client.getPaginated<T>(path, { ...queryOptions, page: pageParam as number }),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (lastPage.meta.pagination.hasNext) {
        return lastPage.meta.pagination.page + 1;
      }
      return undefined;
    },
    ...options,
  });
}

/**
 * Generic mutation hook
 */
export function useApiMutation<TData, TVariables>(
  mutationFn: (variables: TVariables) => Promise<ApiResponse<TData>>,
  options?: UseMutationOptions<ApiResponse<TData>, ApiClientError, TVariables>
) {
  return useMutation<ApiResponse<TData>, ApiClientError, TVariables>({
    mutationFn,
    ...options,
  });
}

// ============================================================================
// Optimistic Update Helpers
// ============================================================================

/**
 * Hook for optimistic updates with rollback
 */
export function useOptimisticMutation<TData, TVariables extends { id: UUID }>(
  queryKey: string[],
  mutationFn: (variables: TVariables) => Promise<ApiResponse<TData>>,
  options?: {
    updateFn?: (old: TData | undefined, variables: TVariables) => TData;
    onSuccess?: (data: ApiResponse<TData>, variables: TVariables) => void;
    onError?: (error: ApiClientError, variables: TVariables) => void;
  }
) {
  const queryClient = useQueryClient();

  return useMutation<ApiResponse<TData>, ApiClientError, TVariables>({
    mutationFn,
    onMutate: async (variables) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey });

      // Snapshot previous value
      const previousData = queryClient.getQueryData<ApiResponse<TData>>(queryKey);

      // Optimistically update
      if (options?.updateFn && previousData) {
        queryClient.setQueryData<ApiResponse<TData>>(queryKey, {
          ...previousData,
          data: options.updateFn(previousData.data, variables),
        });
      }

      return { previousData };
    },
    onError: (error, variables, context) => {
      // Rollback on error
      if (context?.previousData) {
        queryClient.setQueryData(queryKey, context.previousData);
      }
      options?.onError?.(error, variables);
    },
    onSuccess: options?.onSuccess,
    onSettled: () => {
      // Invalidate to refetch
      queryClient.invalidateQueries({ queryKey });
    },
  });
}

// ============================================================================
// Polling Hook
// ============================================================================

/**
 * Hook for polling data at intervals
 */
export function usePolling<T>(
  key: string[],
  fetcher: () => Promise<T>,
  intervalMs: number,
  options?: {
    enabled?: boolean;
    onSuccess?: (data: T) => void;
    onError?: (error: Error) => void;
    stopCondition?: (data: T) => boolean;
  }
) {
  const { enabled = true, stopCondition, onSuccess, onError } = options ?? {};
  const [shouldPoll, setShouldPoll] = useState(enabled);

  const query = useQuery<T, Error>({
    queryKey: key,
    queryFn: fetcher,
    refetchInterval: shouldPoll ? intervalMs : false,
    enabled: shouldPoll,
  });

  useEffect(() => {
    if (query.data && stopCondition?.(query.data)) {
      setShouldPoll(false);
    }
  }, [query.data, stopCondition]);

  useEffect(() => {
    if (query.data) {
      onSuccess?.(query.data);
    }
  }, [query.data, onSuccess]);

  useEffect(() => {
    if (query.error) {
      onError?.(query.error);
    }
  }, [query.error, onError]);

  const startPolling = useCallback(() => setShouldPoll(true), []);
  const stopPolling = useCallback(() => setShouldPoll(false), []);

  return {
    ...query,
    isPolling: shouldPoll,
    startPolling,
    stopPolling,
  };
}

// ============================================================================
// Streaming Hook (for SSE/WebSocket)
// ============================================================================

export interface StreamingState<T> {
  data: T[];
  isConnected: boolean;
  error: Error | null;
}

/**
 * Hook for Server-Sent Events streaming
 */
export function useSSE<T>(
  url: string,
  options?: {
    enabled?: boolean;
    onMessage?: (data: T) => void;
    onError?: (error: Error) => void;
    transform?: (raw: string) => T;
  }
) {
  const { enabled = true, onMessage, onError, transform } = options ?? {};
  const [state, setState] = useState<StreamingState<T>>({
    data: [],
    isConnected: false,
    error: null,
  });
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!enabled) return;

    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setState((prev) => ({ ...prev, isConnected: true, error: null }));
    };

    eventSource.onmessage = (event) => {
      try {
        const data = transform ? transform(event.data) : JSON.parse(event.data);
        setState((prev) => ({ ...prev, data: [...prev.data, data] }));
        onMessage?.(data);
      } catch (error) {
        const err = error instanceof Error ? error : new Error('Parse error');
        setState((prev) => ({ ...prev, error: err }));
        onError?.(err);
      }
    };

    eventSource.onerror = () => {
      const error = new Error('SSE connection error');
      setState((prev) => ({ ...prev, isConnected: false, error }));
      onError?.(error);
    };

    return () => {
      eventSource.close();
      eventSourceRef.current = null;
    };
  }, [url, enabled, onMessage, onError, transform]);

  const disconnect = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
    setState((prev) => ({ ...prev, isConnected: false }));
  }, []);

  const clear = useCallback(() => {
    setState((prev) => ({ ...prev, data: [] }));
  }, []);

  return { ...state, disconnect, clear };
}
