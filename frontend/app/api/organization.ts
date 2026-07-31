import { apiClient } from "./client"
import type { CreateOrgValues, UpdateOrgValues } from "~/schemas/organization"
import type { OrganizationResponse, Organization } from "~/types/organization"

export async function getOrganizationsApi(): Promise<Organization[]> {
  const response = await apiClient.get<OrganizationResponse[]>(
    "/api/organizations/",
  )
  return response.data.map((o) => ({
    id: o.id,
    name: o.name,
    createdAt: o.created_at,
    updatedAt: o.updated_at,
  }))
}

export async function createOrganizationApi(
  values: CreateOrgValues,
): Promise<Organization> {
  const response = await apiClient.post<OrganizationResponse>(
    "/api/organizations/",
    values,
  )
  return {
    id: response.data.id,
    name: response.data.name,
    createdAt: response.data.created_at,
    updatedAt: response.data.updated_at,
  }
}

export async function updateOrganizationApi(
  orgId: string,
  values: UpdateOrgValues,
): Promise<Organization> {
  const response = await apiClient.patch<OrganizationResponse>(
    `/api/organizations/${orgId}`,
    values,
  )
  return {
    id: response.data.id,
    name: response.data.name,
    createdAt: response.data.created_at,
    updatedAt: response.data.updated_at,
  }
}

export async function deleteOrganizationApi(
  orgId: string,
): Promise<{ message: string }> {
  const response = await apiClient.delete<{ message: string }>(
    `/api/organizations/${orgId}`,
  )
  return response.data
}
