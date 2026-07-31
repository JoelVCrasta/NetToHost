import { useEffect } from "react"
import { Outlet, useNavigate } from "react-router"
import { useSessionStore } from "~/hooks/useSessionStore"

export default function ProtectedRouteLayout() {
  const navigate = useNavigate()
  const { accessToken } = useSessionStore()

  useEffect(() => {
    if (!accessToken) {
      navigate("/signin", { replace: true })
    }
  }, [accessToken, navigate])

  if (!accessToken) {
    return null
  }

  return <Outlet />
}
