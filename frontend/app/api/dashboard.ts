import { apiClient } from "./client";
import type {
  CreateOrgValues,
  UpdateOrgValues,
  UpdateHostValues,
  CreateTokenValues,
} from "~/schemas/dashboard";

export interface Organization {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface HostDevice {
  id: number;
  host_id: string;
  org_id: string;
  name: string;
  is_online: boolean;
  last_seen: string;
}

export interface AuthToken {
  id: string;
  org_id: string;
  name: string;
  token?: string;
  created_by: string;
  is_active: boolean;
  expires_at?: string;
  created_at: string;
}

export interface OrgMember {
  id: string;
  org_id: string;
  user_id: string;
  role: "owner" | "admin" | "viewer";
  joined_at: string;
}

// Organization API
export async function getOrganizationsApi(): Promise<Organization[]> {
  const response = await apiClient.get<Organization[]>("/api/organizations/");
  return response.data;
}

export async function createOrganizationApi(values: CreateOrgValues): Promise<Organization> {
  const response = await apiClient.post<Organization>("/api/organizations/", values);
  return response.data;
}

export async function updateOrganizationApi(orgId: string, values: UpdateOrgValues): Promise<Organization> {
  const response = await apiClient.patch<Organization>(`/api/organizations/${orgId}`, values);
  return response.data;
}

export async function deleteOrganizationApi(orgId: string): Promise<{ message: string }> {
  const response = await apiClient.delete<{ message: string }>(`/api/organizations/${orgId}`);
  return response.data;
}

// Host Devices API
export async function getHostsApi(orgId: string): Promise<HostDevice[]> {
  const response = await apiClient.get<HostDevice[]>(`/api/organizations/${orgId}/hosts`);
  return response.data;
}

export async function updateHostNameApi(orgId: string, hostId: string, values: UpdateHostValues): Promise<HostDevice> {
  const response = await apiClient.patch<HostDevice>(`/api/organizations/${orgId}/hosts/${hostId}`, values);
  return response.data;
}

export async function removeHostApi(orgId: string, hostId: string): Promise<{ message: string }> {
  const response = await apiClient.delete<{ message: string }>(`/api/organizations/${orgId}/hosts/${hostId}`);
  return response.data;
}

// Auth Tokens API
export async function getAuthTokensApi(orgId: string): Promise<AuthToken[]> {
  const response = await apiClient.get<AuthToken[]>(`/api/organizations/${orgId}/tokens`);
  return response.data;
}

export async function createAuthTokenApi(
  orgId: string,
  values: CreateTokenValues
): Promise<{ name: string; token: string; message: string }> {
  const response = await apiClient.post<{ name: string; token: string; message: string }>(
    `/api/organizations/${orgId}/tokens`,
    values
  );
  return response.data;
}

export async function updateAuthTokenStatusApi(
  orgId: string,
  tokenId: string,
  isActive: boolean
): Promise<{ id: string; is_active: boolean; message: string }> {
  const response = await apiClient.patch<{ id: string; is_active: boolean; message: string }>(
    `/api/organizations/${orgId}/tokens/${tokenId}/status`,
    { is_active: isActive }
  );
  return response.data;
}

export async function deleteAuthTokenApi(orgId: string, tokenId: string): Promise<{ message: string }> {
  const response = await apiClient.delete<{ message: string }>(
    `/api/organizations/${orgId}/tokens/${tokenId}`
  );
  return response.data;
}

// Org Members API
export async function addOrgMembersApi(
  orgId: string,
  members: { id: string; role: string }[]
): Promise<{ message: string }> {
  const response = await apiClient.post<{ message: string }>(
    `/api/organizations/${orgId}/members`,
    { members }
  );
  return response.data;
}

export async function updateOrgMemberRoleApi(
  orgId: string,
  userId: string,
  newRole: string
): Promise<{ message: string }> {
  const response = await apiClient.patch<{ message: string }>(
    `/api/organizations/${orgId}/members`,
    { user_id: userId, new_role: newRole }
  );
  return response.data;
}

export async function removeOrgMemberApi(
  orgId: string,
  userId: string
): Promise<{ message: string }> {
  const response = await apiClient.delete<{ message: string }>(
    `/api/organizations/${orgId}/members`,
    { data: { user_ids: [userId] } }
  );
  return response.data;
}
