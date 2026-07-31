import type { Route } from "./+types/verify-email"
import { useEffect } from "react"
import { Link, useLocation, useNavigate } from "react-router"
import { MailCheck, ArrowRight } from "lucide-react"
import AuthLayout from "~/layouts/AuthLayout"
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "~/components/ui/card"
import { Button } from "~/components/ui/button"

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Verify Email - NetToHost" },
    {
      name: "description",
      content: "Check your email to confirm your NetToHost account",
    },
  ]
}

export default function VerifyEmail() {
  const navigate = useNavigate()
  const location = useLocation()

  const fromSignUp = location.state?.fromSignUp
  const email = location.state?.email || "your email address"

  useEffect(() => {
    if (!fromSignUp) {
      navigate("/signup", { replace: true })
    }
  }, [fromSignUp, navigate])

  if (!fromSignUp) {
    return null
  }

  return (
    <AuthLayout>
      <Card className="w-full max-w-sm text-center">
        <CardHeader className="space-y-3">
          <div className="mx-auto w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center text-primary border border-primary/20">
            <MailCheck className="w-6 h-6" />
          </div>
          <CardTitle className="text-xl">Check your inbox</CardTitle>
          <CardDescription className="">
            We sent a verification link to{" "}
            <span className="font-semibold text-foreground">{email}</span>.
          </CardDescription>
        </CardHeader>

        <CardContent className="text-muted-foreground space-y-2">
          <p>
            Click the link in the email to activate your NetToHost account and
            access your workspace.
          </p>
        </CardContent>

        <CardFooter className="">
          <Button
            variant="default"
            className="w-full"
            render={<Link to="/signin" />}
          >
            <ArrowRight className="ml-2 h-4 w-4" />
            <span>Back to Sign In</span>
          </Button>
        </CardFooter>
      </Card>
    </AuthLayout>
  )
}
