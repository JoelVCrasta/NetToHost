import { apiClient } from "./client"
import type { SignInValues, SignUpValues } from "~/schemas/auth"
import type { SignInResponse } from "~/types/user"

export interface SignUpResponse {
  status: string
  message: string
}

export async function signInApi(values: SignInValues): Promise<SignInResponse> {
  const response = await apiClient.post<SignInResponse>("/api/auth/signin", values)
  return response.data
}

export async function signUpApi(values: SignUpValues): Promise<SignUpResponse> {
  const response = await apiClient.post<SignUpResponse>("/api/auth/signup", values)
  return response.data
}

export async function getMeApi(accessToken: string): Promise<SignInResponse> {
  const response = await apiClient.get<SignInResponse>("/api/auth/me", {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  })
  return {
    ...response.data,
    access_token: accessToken,
  }
}

export async function signOutApi(): Promise<{ status: string; message: string }> {
  const response = await apiClient.post<{ status: string; message: string }>("/api/auth/signout")
  return response.data
}
