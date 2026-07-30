export interface OrganizationResponse {
  id: string
  name: string
  created_at: string
  updated_at: string
}

export interface CreateOrganizationResponse {
  id: string
  name: string
  message: string
}

export interface UpdateOrganizationResponse {
  id: string
  name: string
  message: string
}

export interface DeleteOrganizationResponse {
  message: string
}

export interface Organization {
  id: string
  name: string
  createdAt: string
  updatedAt: string
}
