export interface AuthTokenResponse {
  id: string
  org_id: string
  name: string
  created_by: string
  is_active: boolean
  expires_at: string | null
  created_at: string
  updated_at: string
}
