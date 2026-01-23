/**
 * NYQST Intelli UI - Agent-First Document Intelligence Platform
 * Enterprise-safe, async-first React component library
 */

// Types
export * from './types';

// Utilities
export { cn, formatDate, formatRelativeTime, formatBytes, truncate, stringToColor, debounce, throttle, createId, groupBy } from './lib/utils';

// Async Primitives
export {
  GlobalErrorFallback,
  ComponentErrorFallback,
  InlineError,
  FullPageLoader,
  PanelLoader,
  InlineLoader,
  Spinner,
  Skeleton,
  TextSkeleton,
  CardSkeleton,
  ListSkeleton,
  TableSkeleton,
  GridSkeleton,
  TimelineSkeleton,
  DocumentSkeleton,
  ChatMessageSkeleton,
  ChatThreadSkeleton,
  AsyncBoundary,
  withSuspense,
  withAsyncBoundary,
  DeferredRender,
  RetryBoundary,
  createLoadingSkeleton,
} from './components/async';

// UI Components
export { Button, buttonVariants } from './components/ui/button';
export { Badge, badgeVariants } from './components/ui/badge';
export { Input } from './components/ui/input';
export { Tabs, TabsList, TabsTrigger, TabsContent } from './components/ui/tabs';
export { ScrollArea, ScrollBar } from './components/ui/scroll-area';
export { Separator } from './components/ui/separator';
export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from './components/ui/tooltip';
export { Toaster, useToast, toast } from './components/ui/toaster';

// Workbench Components
export { WorkbenchShell, PaneTabBar, WorkbenchSidebar, CommandPalette } from './components/workbench';

// Pane Components
export { ChatPane, RunExplorerPane, ArtifactBrowserPane, DocumentViewerPane, GovernancePane, ProvenancePane } from './components/panes';

// Providers
export { ThemeProvider, useTheme } from './components/providers/theme-provider';

// Hooks
export {
  useAsync,
  useDebouncedAsync,
  useApiQuery,
  useApiPaginatedQuery,
  useApiInfiniteQuery,
  useApiMutation,
  useOptimisticMutation,
  usePolling,
  useSSE,
} from './hooks/use-async';

// Stores
export { useWorkspaceStore, selectActivePane, selectPanesByType, selectPinnedItemsByType } from './stores/workspace-store';
export type { PaneType, Pane, PaneGroup, WorkspaceLayout, WorkspaceState, WorkspaceActions } from './stores/workspace-store';

// API Client
export { ApiClient, ApiClientError, NetworkError, TimeoutError, initApiClient, getApiClient } from './api/client';
export type { ApiClientConfig } from './api/client';
