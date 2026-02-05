/**
 * TypeScript types for tag API responses.
 */

export interface TagResponse {
  id: string
  tenant_id: string
  entity_type: string
  entity_id: string
  namespace: string
  key: string
  value: string
  source: string
  confidence: number | null
  verified_by: string | null
  verified_at: string | null
  created_at: string
}

export interface TagListResponse {
  items: TagResponse[]
  total: number
}
