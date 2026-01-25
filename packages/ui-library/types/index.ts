/**
 * Central type exports for the Agent-First Document Intelligence Platform
 */

// Core backbone types
export * from './core';

// Knowledge system types
export * from './knowledge';

// Evidence, claims, decisions types
export * from './evidence';

// Run ledger event types
export * from './events';

// Document IR types
export * from './docir';

// Connector system types
export * from './connectors';

// ============================================================================
// Common type utilities
// ============================================================================

/**
 * Makes specific properties optional
 */
export type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

/**
 * Makes specific properties required
 */
export type RequiredBy<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;

/**
 * Extracts the type of array elements
 */
export type ArrayElement<T> = T extends readonly (infer U)[] ? U : never;

/**
 * Creates a type with all properties set to never
 */
export type Never<T> = { [K in keyof T]?: never };

/**
 * Union type that allows only one of the specified types
 */
export type OneOf<T, U> = (T & Never<U>) | (U & Never<T>);

/**
 * Deep partial type
 */
export type DeepPartial<T> = T extends object
  ? { [P in keyof T]?: DeepPartial<T[P]> }
  : T;

/**
 * Deep readonly type
 */
export type DeepReadonly<T> = T extends object
  ? { readonly [P in keyof T]: DeepReadonly<T[P]> }
  : T;

/**
 * Async function return type
 */
export type AsyncReturnType<T extends (...args: unknown[]) => Promise<unknown>> =
  T extends (...args: unknown[]) => Promise<infer R> ? R : never;

// ============================================================================
// API Response types
// ============================================================================

export interface ApiResponse<T> {
  data: T;
  meta?: ApiResponseMeta;
}

export interface ApiResponseMeta {
  requestId: string;
  timestamp: string;
  pagination?: PaginationMeta;
}

export interface PaginationMeta {
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  requestId?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  meta: ApiResponseMeta & {
    pagination: PaginationMeta;
  };
}

// ============================================================================
// Filter and Sort types
// ============================================================================

export interface FilterOptions {
  search?: string;
  filters?: FilterCondition[];
  dateRange?: {
    field: string;
    from?: string;
    to?: string;
  };
}

export interface FilterCondition {
  field: string;
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'nin' | 'contains' | 'startsWith';
  value: unknown;
}

export interface SortOptions {
  field: string;
  direction: 'asc' | 'desc';
}

export interface QueryOptions extends FilterOptions {
  sort?: SortOptions[];
  page?: number;
  pageSize?: number;
}
