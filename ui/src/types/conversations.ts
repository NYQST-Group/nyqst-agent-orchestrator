/**
 * TypeScript types for conversation API responses.
 */

// Type aliases matching backend Literal types
export type ConversationStatus = 'active' | 'archived' | 'deleted'
export type MessageRole = 'user' | 'assistant' | 'system' | 'tool'
export type MessageStatus = 'pending' | 'streaming' | 'complete' | 'failed'
export type FeedbackRating = 'positive' | 'negative'

export interface ConversationResponse {
  id: string
  tenant_id: string
  user_id: string
  scope_type: string
  scope_id: string | null
  module: string | null
  title: string | null
  status: ConversationStatus
  message_count: number
  total_input_tokens: number
  total_output_tokens: number
  total_cost_micros: number
  session_id: string | null
  run_id: string | null
  created_at: string
  updated_at: string
  last_message_at: string | null
}

export interface ConversationListResponse {
  items: ConversationResponse[]
  total: number
}

export interface MessageResponse {
  id: string
  conversation_id: string
  role: MessageRole
  content: string | null
  parts: Record<string, unknown> | null
  input_tokens: number | null
  output_tokens: number | null
  cost_micros: number | null
  latency_ms: number | null
  model_id: string | null
  status: MessageStatus
  parent_message_id: string | null
  sequence_number: number
  created_at: string
}

export interface MessageListResponse {
  items: MessageResponse[]
  total: number
}

export interface FeedbackResponse {
  id: string
  message_id: string
  user_id: string
  rating: FeedbackRating
  content: string | null
  created_at: string
}

export interface BranchResponse {
  conversation_id: string
  branch_point_message_id: string
  new_sequence_number: number
}

export interface SiblingResponse {
  items: MessageResponse[]
  total: number
  current_index: number
}
