import { useEffect } from "react"
import { Outlet, useNavigate } from "react-router"
import { Loader2 } from "lucide-react"
import { useSessionStore } from "~/hooks/useSessionStore"
import { Spinner } from "~/components/ui/spinner"

export default function ProtectedRouteLayout() {
  const navigate = useNavigate()
  const { accessToken, hasHydrated } = useSessionStore()

  useEffect(() => {
    if (hasHydrated && !accessToken) {
      navigate("/signin", { replace: true })
    }
  }, [hasHydrated, accessToken, navigate])

  if (!hasHydrated) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spinner className="size-8 text-muted-foreground" />
      </div>
    )
  }

  if (!accessToken) {
    return null
  }

  return <Outlet />
}
