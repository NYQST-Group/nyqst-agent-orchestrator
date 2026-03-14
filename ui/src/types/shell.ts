export interface ShellContextEntity {
  id: string
  label: string
  href?: string | null
  subtitle?: string | null
}

export interface ShellModelOption {
  id: string
  label: string
  provider?: string | null
  is_default: boolean
}

export interface ShellSessionSummary {
  id: string
  module?: string | null
  objective?: string | null
  status: string
  last_active_at: string
  started_at: string
}

export interface ShellContext {
  workspace_name: string
  workspace_id: string
  initiative_name?: string | null
  active_project?: ShellContextEntity | null
  active_task?: ShellContextEntity | null
  active_session?: ShellSessionSummary | null
  current_user_role?: string | null
  available_models: ShellModelOption[]
  recent_entities: ShellContextEntity[]
}

export interface OpsActivityItem {
  id: string
  label: string
  detail: string
  href?: string | null
  timestamp: string
  kind: string
  status?: string | null
}

export interface UsageSummaryItem {
  model: string
  input_tokens: number
  output_tokens: number
  cost_micros: number
}

export interface OpsSummary {
  active_runs: OpsActivityItem[]
  recent_activity: OpsActivityItem[]
  queued_count: number
  running_count: number
  failed_count: number
  unread_operational_items: number
  price_table_version?: string | null
  total_input_tokens: number
  total_output_tokens: number
  total_cost_micros: number
  cost_by_model: UsageSummaryItem[]
}

export interface RightRailItem {
  id: string
  title: string
  subtitle?: string | null
  meta?: string | null
  href?: string | null
  badge?: string | null
}

export interface RightRailSection {
  kind: 'plans' | 'working_files' | 'sources' | 'activity' | 'usage' | 'empty_state' | string
  title: string
  description?: string | null
  items: RightRailItem[]
}

export interface RightRailPayload {
  module: string
  sections: RightRailSection[]
}
