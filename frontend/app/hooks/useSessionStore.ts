import { create } from "zustand"
import { persist } from "zustand/middleware"
import type { User, SignInResponse } from "~/types/user"

interface SessionState {
  user: User | null
  accessToken: string | null
  setSession: (payload: SignInResponse) => void
  setAccessToken: (token: string) => void
  clearSession: () => void
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      setSession: (payload: SignInResponse) => {
        const { user_id, email, display_name, avatar_url, access_token } =
          payload
        set({
          user: {
            id: user_id,
            email,
            displayName: display_name,
            avatarUrl: avatar_url ?? null,
          },
          accessToken: access_token,
        })
      },
      setAccessToken: (token: string) => {
        set({ accessToken: token })
      },
      clearSession: () => {
        set({ user: null, accessToken: null })
      },
    }),
    {
      name: "session-storage",
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
      }),
    },
  ),
)
