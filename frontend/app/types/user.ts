export interface User {
  id: string
  email: string
  displayName: string
  avatarUrl: string | null
}

export interface SignInResponse {
  status: string
  access_token: string
  user_id: string
  email: string
  display_name: string
  avatar_url?: string | null
}