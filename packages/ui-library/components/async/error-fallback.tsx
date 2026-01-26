import { FallbackProps } from 'react-error-boundary';
import { AlertTriangle, RefreshCw, Home, Bug, ChevronDown, ChevronUp } from 'lucide-react';
import { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface ErrorFallbackProps extends Partial<FallbackProps> {
  title?: string;
  description?: string;
  showHomeButton?: boolean;
  showReportButton?: boolean;
  className?: string;
  compact?: boolean;
}

/**
 * Global error fallback for top-level error boundary
 */
export function GlobalErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="max-w-lg w-full space-y-6 text-center">
        <div className="flex justify-center">
          <div className="rounded-full bg-destructive/10 p-4">
            <AlertTriangle className="h-12 w-12 text-destructive" />
          </div>
        </div>

        <div className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight">Something went wrong</h1>
          <p className="text-muted-foreground">
            An unexpected error occurred. Please try refreshing the page or contact support if the
            problem persists.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={resetErrorBoundary}
            className="inline-flex items-center justify-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 focus-ring"
          >
            <RefreshCw className="h-4 w-4" />
            Try again
          </button>
          <button
            onClick={() => (window.location.href = '/')}
            className="inline-flex items-center justify-center gap-2 rounded-md border border-input bg-background px-4 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground focus-ring"
          >
            <Home className="h-4 w-4" />
            Go home
          </button>
        </div>

        {error && (
          <div className="mt-6">
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
            >
              {showDetails ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              {showDetails ? 'Hide' : 'Show'} error details
            </button>

            {showDetails && (
              <div className="mt-3 rounded-lg bg-muted p-4 text-left">
                <p className="text-sm font-medium text-destructive">{error.name}</p>
                <p className="text-sm text-muted-foreground mt-1">{error.message}</p>
                {error.stack && (
                  <pre className="mt-2 text-xs text-muted-foreground overflow-auto max-h-48 scrollbar-thin">
                    {error.stack}
                  </pre>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Component-level error fallback for localized error boundaries
 */
export function ComponentErrorFallback({
  error,
  resetErrorBoundary,
  title = 'Failed to load',
  description,
  showHomeButton = false,
  showReportButton = false,
  className,
  compact = false,
}: ErrorFallbackProps) {
  const [showDetails, setShowDetails] = useState(false);

  const handleReport = useCallback(() => {
    // In production, this would send to an error reporting service
    console.error('Error report:', error);
    alert('Error has been reported. Thank you!');
  }, [error]);

  if (compact) {
    return (
      <div
        className={cn(
          'flex items-center gap-3 rounded-md border border-destructive/20 bg-destructive/5 p-3',
          className
        )}
      >
        <AlertTriangle className="h-4 w-4 text-destructive shrink-0" />
        <span className="text-sm text-destructive">{title}</span>
        {resetErrorBoundary && (
          <button
            onClick={resetErrorBoundary}
            className="ml-auto text-sm text-destructive hover:underline"
          >
            Retry
          </button>
        )}
      </div>
    );
  }

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-6 rounded-lg border border-destructive/20 bg-destructive/5',
        className
      )}
      role="alert"
    >
      <AlertTriangle className="h-8 w-8 text-destructive mb-3" />
      <h3 className="text-lg font-medium text-destructive">{title}</h3>
      {description && <p className="text-sm text-muted-foreground mt-1 text-center">{description}</p>}
      {error?.message && !description && (
        <p className="text-sm text-muted-foreground mt-1 text-center">{error.message}</p>
      )}

      <div className="flex flex-wrap gap-2 mt-4 justify-center">
        {resetErrorBoundary && (
          <button
            onClick={resetErrorBoundary}
            className="inline-flex items-center gap-1.5 rounded-md bg-destructive px-3 py-1.5 text-sm font-medium text-destructive-foreground hover:bg-destructive/90 focus-ring"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Try again
          </button>
        )}
        {showHomeButton && (
          <button
            onClick={() => (window.location.href = '/')}
            className="inline-flex items-center gap-1.5 rounded-md border border-input bg-background px-3 py-1.5 text-sm font-medium hover:bg-accent focus-ring"
          >
            <Home className="h-3.5 w-3.5" />
            Home
          </button>
        )}
        {showReportButton && (
          <button
            onClick={handleReport}
            className="inline-flex items-center gap-1.5 rounded-md border border-input bg-background px-3 py-1.5 text-sm font-medium hover:bg-accent focus-ring"
          >
            <Bug className="h-3.5 w-3.5" />
            Report
          </button>
        )}
      </div>

      {error && (
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="mt-4 text-xs text-muted-foreground hover:text-foreground"
        >
          {showDetails ? 'Hide details' : 'Show details'}
        </button>
      )}

      {showDetails && error && (
        <pre className="mt-2 p-2 rounded bg-muted text-xs text-muted-foreground overflow-auto max-w-full max-h-32 scrollbar-thin">
          {error.stack || error.message}
        </pre>
      )}
    </div>
  );
}

/**
 * Inline error display for form fields, etc.
 */
export function InlineError({
  message,
  className,
}: {
  message: string;
  className?: string;
}) {
  return (
    <div className={cn('flex items-center gap-1.5 text-sm text-destructive', className)}>
      <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
      <span>{message}</span>
    </div>
  );
}
