import axios from "axios"
import { useSessionStore } from "~/hooks/useSessionStore"

export const apiClient = axios.create({
  baseURL: "",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
})

apiClient.interceptors.request.use((config) => {
  const token = useSessionStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true
      try {
        const refreshResponse = await axios.post<{ access_token: string }>(
          "/api/auth/refresh",
          {},
          { withCredentials: true },
        )
        const newAccessToken = refreshResponse.data.access_token
        useSessionStore.getState().setAccessToken(newAccessToken)
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
        return apiClient(originalRequest)
      } catch (refreshError) {
        useSessionStore.getState().clearSession()
        return Promise.reject(refreshError)
      }
    }

    const detail = error.response?.data?.detail
    if (detail) {
      return Promise.reject(
        new Error(typeof detail === "string" ? detail : JSON.stringify(detail)),
      )
    }
    return Promise.reject(error)
  },
)
