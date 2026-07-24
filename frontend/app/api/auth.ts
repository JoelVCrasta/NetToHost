import { apiClient } from "./client";
import type { SignInValues, SignUpValues } from "~/schemas/auth";

export interface SignInResponse {
  status: string;
  access_token: string;
  user_id: string;
  display_name: string;
}

export interface SignUpResponse {
  status: string;
  message: string;
}

export async function signInApi(values: SignInValues): Promise<SignInResponse> {
  const response = await apiClient.post<SignInResponse>("/api/auth/signin", values);
  return response.data;
}

export async function signUpApi(values: SignUpValues): Promise<SignUpResponse> {
  const response = await apiClient.post<SignUpResponse>("/api/auth/signup", values);
  return response.data;
}

export async function signOutApi(): Promise<{ status: string; message: string }> {
  const response = await apiClient.post<{ status: string; message: string }>("/api/auth/signout");
  return response.data;
}
