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

export interface CreateTokenResponse {
  name: string
  token: string
  message: string
}

export interface AuthToken {
  id: string
  orgId: string
  name: string
  token?: string
  createdBy: string
  isActive: boolean
  expiresAt: string | null
  createdAt: string
  updatedAt: string
}
