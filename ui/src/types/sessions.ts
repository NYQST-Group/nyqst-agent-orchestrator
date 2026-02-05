/**
 * TypeScript types for session API responses.
 */

export interface SessionResponse {
  id: string
  tenant_id: string
  user_id: string
  scope_type: string
  scope_id: string | null
  module: string | null
  objective: string | null
  status: string
  started_at: string
  last_active_at: string
  idle_timeout_minutes: number
  closed_at: string | null
  close_reason: string | null
  total_cost_micros: number
  created_at: string
  updated_at: string
}

export interface SessionListResponse {
  items: SessionResponse[]
  total: number
}

export interface SessionCostBreakdown {
  session_id: string
  total_cost_micros: number
  conversation_count: number
  total_input_tokens: number
  total_output_tokens: number
  conversations: Array<{
    id: string
    title: string | null
    cost_micros: number
    input_tokens: number
    output_tokens: number
  }>
}
