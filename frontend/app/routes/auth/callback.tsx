import { useEffect, useState } from "react"
import { useNavigate, useLocation } from "react-router"
import { Loader2, AlertCircle } from "lucide-react"
import { getMeApi } from "~/api/auth"
import { useSessionStore } from "~/hooks/useSessionStore"
import AuthLayout from "~/layouts/AuthLayout"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "~/components/ui/card"

export default function AuthCallback() {
  const navigate = useNavigate()
  const location = useLocation()
  const { setSession } = useSessionStore()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function handleAuthCallback() {
      try {
        const hash = location.hash || window.location.hash
        const params = new URLSearchParams(hash.replace(/^#/, ""))
        const accessToken = params.get("access_token")

        if (accessToken) {
          const userSession = await getMeApi(accessToken)
          setSession(userSession)
          navigate("/dashboard")
          return
        }

        const searchParams = new URLSearchParams(location.search)
        const code = searchParams.get("code")
        if (code) {
          navigate("/signin")
          return
        }

        setError("Confirmation token not found or expired. Please sign in.")
      } catch (err: any) {
        setError(err.message || "Failed to confirm email session.")
      }
    }

    handleAuthCallback()
  }, [location, navigate, setSession])

  return (
    <AuthLayout>
      <Card className="w-full max-w-sm text-center">
        <CardHeader>
          <CardTitle>Confirming Account</CardTitle>
          <CardDescription>
            Authenticating your email confirmation link...
          </CardDescription>
        </CardHeader>
        <CardContent className="py-6 flex flex-col items-center justify-center space-y-3">
          {error ? (
            <div className="p-3 rounded-lg border border-rose-500/30 bg-rose-950/30 text-rose-300 text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{error}</span>
            </div>
          ) : (
            <>
              <Loader2 className="w-8 h-8 text-primary animate-spin" />
              <p className="text-xs text-muted-foreground">
                Setting up your workspace session...
              </p>
            </>
          )}
        </CardContent>
      </Card>
    </AuthLayout>
  )
}
