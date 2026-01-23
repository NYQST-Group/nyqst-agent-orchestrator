import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { Suspense } from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import { Toaster } from '@/components/ui/toaster';
import { ThemeProvider } from '@/components/providers/theme-provider';
import { WorkbenchShell } from '@/components/workbench/workbench-shell';
import { GlobalErrorFallback } from '@/components/async/error-fallback';
import { FullPageLoader } from '@/components/async/loading-states';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      suspense: false, // We handle suspense explicitly per-component
    },
    mutations: {
      retry: 1,
    },
  },
});

export function App() {
  return (
    <ErrorBoundary FallbackComponent={GlobalErrorFallback}>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider defaultTheme="system" storageKey="nyqst-ui-theme">
          <BrowserRouter>
            <Suspense fallback={<FullPageLoader />}>
              <WorkbenchShell />
              <Toaster />
            </Suspense>
          </BrowserRouter>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
