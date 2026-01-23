import { Suspense, ReactNode, ComponentType } from 'react';
import { ErrorBoundary, FallbackProps } from 'react-error-boundary';
import { PanelLoader, Skeleton } from './loading-states';
import { ComponentErrorFallback } from './error-fallback';

interface AsyncBoundaryProps {
  children: ReactNode;
  /** Loading fallback - can be a component or ReactNode */
  loadingFallback?: ReactNode;
  /** Error fallback component */
  errorFallback?: ComponentType<FallbackProps>;
  /** Called when error boundary resets */
  onReset?: () => void;
  /** Called when an error is caught */
  onError?: (error: Error, info: { componentStack: string }) => void;
  /** Keys that trigger error boundary reset when changed */
  resetKeys?: unknown[];
}

/**
 * Combines Suspense and ErrorBoundary for async components.
 * Enterprise-safe pattern for handling loading and error states.
 */
export function AsyncBoundary({
  children,
  loadingFallback,
  errorFallback: ErrorFallback = ComponentErrorFallback,
  onReset,
  onError,
  resetKeys,
}: AsyncBoundaryProps) {
  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onReset={onReset}
      onError={onError}
      resetKeys={resetKeys}
    >
      <Suspense fallback={loadingFallback ?? <PanelLoader />}>
        {children}
      </Suspense>
    </ErrorBoundary>
  );
}

interface WithSuspenseOptions<T> {
  /** Loading fallback component or element */
  fallback?: ReactNode;
  /** Display name for the wrapped component */
  displayName?: string;
}

/**
 * HOC to wrap a component with Suspense boundary.
 * Use for lazy-loaded components or components using `use()` hook.
 */
export function withSuspense<P extends object>(
  Component: ComponentType<P>,
  options: WithSuspenseOptions<P> = {}
): ComponentType<P> {
  const { fallback, displayName } = options;

  function Wrapped(props: P) {
    return (
      <Suspense fallback={fallback ?? <PanelLoader />}>
        <Component {...props} />
      </Suspense>
    );
  }

  Wrapped.displayName = displayName ?? `withSuspense(${Component.displayName ?? Component.name ?? 'Component'})`;

  return Wrapped;
}

interface WithAsyncBoundaryOptions<P> extends WithSuspenseOptions<P> {
  /** Custom error fallback component */
  errorFallback?: ComponentType<FallbackProps>;
  /** Called on error boundary reset */
  onReset?: () => void;
}

/**
 * HOC to wrap a component with both Suspense and ErrorBoundary.
 * Use for components that need both loading and error handling.
 */
export function withAsyncBoundary<P extends object>(
  Component: ComponentType<P>,
  options: WithAsyncBoundaryOptions<P> = {}
): ComponentType<P> {
  const { fallback, displayName, errorFallback, onReset } = options;

  function Wrapped(props: P) {
    return (
      <AsyncBoundary
        loadingFallback={fallback}
        errorFallback={errorFallback}
        onReset={onReset}
      >
        <Component {...props} />
      </AsyncBoundary>
    );
  }

  Wrapped.displayName = displayName ?? `withAsyncBoundary(${Component.displayName ?? Component.name ?? 'Component'})`;

  return Wrapped;
}

/**
 * Deferred loading component - delays rendering until after hydration.
 * Useful for components that might cause hydration mismatches.
 */
export function DeferredRender({
  children,
  fallback = null,
}: {
  children: ReactNode;
  fallback?: ReactNode;
}) {
  // In SSR/initial render, show fallback
  // After hydration, show children
  // This is handled by Suspense + the component's own loading state
  return (
    <Suspense fallback={fallback}>
      {children}
    </Suspense>
  );
}

/**
 * Retry boundary - allows manual retry of failed async operations
 */
export function RetryBoundary({
  children,
  fallback,
  maxRetries = 3,
}: {
  children: ReactNode;
  fallback?: ReactNode;
  maxRetries?: number;
}) {
  return (
    <ErrorBoundary
      FallbackComponent={({ error, resetErrorBoundary }) => (
        <ComponentErrorFallback
          error={error}
          resetErrorBoundary={resetErrorBoundary}
          title="Failed to load"
          description={`Error: ${error.message}`}
        />
      )}
    >
      <Suspense fallback={fallback ?? <PanelLoader />}>
        {children}
      </Suspense>
    </ErrorBoundary>
  );
}

/**
 * Creates a loading skeleton that matches a component's expected shape
 */
export function createLoadingSkeleton(
  structure: 'card' | 'list' | 'table' | 'timeline' | 'document' | 'chat'
): ReactNode {
  switch (structure) {
    case 'card':
      return <Skeleton className="h-32 w-full rounded-lg" />;
    case 'list':
      return (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-12 w-full rounded-md" />
          ))}
        </div>
      );
    case 'table':
      return (
        <div className="space-y-2">
          <Skeleton className="h-10 w-full rounded-md" />
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-12 w-full rounded-md" />
          ))}
        </div>
      );
    case 'timeline':
      return (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex gap-3">
              <Skeleton className="h-8 w-8 rounded-full shrink-0" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-1/3" />
                <Skeleton className="h-20 w-full rounded-md" />
              </div>
            </div>
          ))}
        </div>
      );
    case 'document':
      return (
        <div className="space-y-4 p-4">
          <Skeleton className="h-8 w-1/2" />
          <Skeleton className="h-4 w-1/3" />
          <div className="space-y-2 mt-6">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-4 w-full" />
            ))}
          </div>
        </div>
      );
    case 'chat':
      return (
        <div className="space-y-4 p-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className={`flex gap-3 ${i % 2 === 0 ? 'flex-row-reverse' : ''}`}>
              <Skeleton className="h-8 w-8 rounded-full shrink-0" />
              <Skeleton className="h-16 w-48 rounded-lg" />
            </div>
          ))}
        </div>
      );
    default:
      return <Skeleton className="h-32 w-full rounded-lg" />;
  }
}
