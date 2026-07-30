export enum MemberRole {
  Owner = "owner",
  Admin = "admin",
  Viewer = "viewer",
}

export interface OrgMemberResponse {
  id: string
  org_id: string
  user_id: string
  role: MemberRole
  joined_at: string
}

export interface CreateOrgMemberResponse {
  members: OrgMemberResponse[]
  message: string
}

export interface UpdateOrgMemberRoleResponse {
  message: string
}

export interface RemoveOrgMembersResponse {
  message: string
}

export interface OrgMember {
  id: string
  orgId: string
  userId: string
  role: MemberRole
  joinedAt: string
}
