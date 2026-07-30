import type { Route } from "./+types/signin"
import { Link, useNavigate } from "react-router"
import { useForm } from "@tanstack/react-form"
import { useMutation } from "@tanstack/react-query"
import { ArrowRight, Loader2, AlertCircle } from "lucide-react"
import { signInSchema, type SignInValues } from "~/schemas/auth"
import { signInApi } from "~/api/auth"
import { useSessionStore } from "~/hooks/useSessionStore"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "~/components/ui/card"
import { Input } from "~/components/ui/input"
import { Label } from "~/components/ui/label"
import { Button } from "~/components/ui/button"
import AuthLayout from "~/layouts/AuthLayout"

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Sign In - NetToHost" },
    { name: "description", content: "Sign in to your NetToHost workspace" },
  ]
}

export default function SignIn() {
  const navigate = useNavigate()
  const { setSession } = useSessionStore()

  const signInMutation = useMutation({
    mutationFn: (values: SignInValues) => signInApi(values),
    onSuccess: (data) => {
      setSession(data)
      navigate("/dashboard")
    },
  })

  const form = useForm({
    defaultValues: {
      email: "",
      password: "",
    },
    onSubmit: async ({ value }) => {
      signInMutation.mutate(value)
    },
  })

  return (
    <AuthLayout>
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>Login</CardTitle>
          <CardDescription>
            Login to your acoount to access your NetToHost workspace.
          </CardDescription>
          <CardAction>
            <Link
              to="/signup"
              className="text-xs font-semibold text-primary hover:text-primary/80 hover:underline transition-colors"
            >
              Sign Up
            </Link>
          </CardAction>
        </CardHeader>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            e.stopPropagation()
            form.handleSubmit()
          }}
        >
          <CardContent className="space-y-4 pb-4">
            {signInMutation.isError && (
              <div className="p-3 rounded-lg border border-rose-500/30 bg-rose-950/30 text-rose-300 text-xs flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>{signInMutation.error.message}</span>
              </div>
            )}

            {/* Email Field */}
            <form.Field
              name="email"
              validators={{
                onChange: ({ value }) => {
                  const res = signInSchema.shape.email.safeParse(value)
                  return res.success ? undefined : res.error.issues[0]?.message
                },
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor={field.name}>Email</Label>
                  <Input
                    id={field.name}
                    name={field.name}
                    type="email"
                    placeholder="email@example.com"
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                  />
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-xs text-rose-400">
                      {field.state.meta.errors.join(", ")}
                    </p>
                  )}
                </div>
              )}
            </form.Field>

            {/* Password Field */}
            <form.Field
              name="password"
              validators={{
                onChange: ({ value }) => {
                  const res = signInSchema.shape.password.safeParse(value)
                  return res.success ? undefined : res.error.issues[0]?.message
                },
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor={field.name}>Password</Label>
                  <Input
                    id={field.name}
                    name={field.name}
                    type="password"
                    placeholder=""
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                  />
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-xs text-rose-400">
                      {field.state.meta.errors.join(", ")}
                    </p>
                  )}
                </div>
              )}
            </form.Field>
          </CardContent>

          <CardFooter>
            <Button
              type="submit"
              disabled={signInMutation.isPending}
              className="w-full"
            >
              {signInMutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <ArrowRight className="mr-2 h-4 w-4" />
              )}
              Login
            </Button>
          </CardFooter>
        </form>
      </Card>
    </AuthLayout>
  )
}
