import type { Route } from "./+types/signup"
import { Link, useNavigate } from "react-router"
import { useForm } from "@tanstack/react-form"
import { useMutation } from "@tanstack/react-query"
import { ArrowRight, Loader2 } from "lucide-react"
import { signUpSchema, type SignUpValues } from "~/schemas/auth"
import { signUpApi } from "~/api/auth"
import { toast } from "~/components/ui/toast"
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
import { useSessionStore } from "~/hooks/useSessionStore"
import { useEffect } from "react"

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Sign Up - NetToHost" },
    { name: "description", content: "Create a new NetToHost account" },
  ]
}

export default function SignUp() {
  const navigate = useNavigate()

  const signUpMutation = useMutation({
    mutationFn: (values: SignUpValues) => signUpApi(values),
    onSuccess: (_, variables) => {
      navigate("/verify-email", {
        state: { fromSignUp: true, email: variables.email },
        replace: true,
      })
    },
    onError: (error: Error) => {
      toast.add({
        title: "Sign up failed",
        description: error.message || "An error occurred during sign up.",
        type: "error",
      })
    },
  })

  const form = useForm({
    defaultValues: {
      display_name: "",
      email: "",
      password: "",
    },
    onSubmit: async ({ value }) => {
      signUpMutation.mutate(value)
    },
  })

  return (
    <AuthLayout>
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>Sign Up</CardTitle>
          <CardDescription>
            Create your account to manage your NetToHost workspace.
          </CardDescription>
          <CardAction>
            <Link
              to="/signin"
              className="text-xs font-semibold text-primary hover:text-primary/80 hover:underline transition-colors"
            >
              Sign In
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
            {/* Display Name Field */}
            <form.Field
              name="display_name"
              validators={{
                onChange: ({ value }) => {
                  const res = signUpSchema.shape.display_name.safeParse(value)
                  return res.success ? undefined : res.error.issues[0]?.message
                },
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor={field.name}>Display Name</Label>
                  <Input
                    id={field.name}
                    name={field.name}
                    type="text"
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

            {/* Email Field */}
            <form.Field
              name="email"
              validators={{
                onChange: ({ value }) => {
                  const res = signUpSchema.shape.email.safeParse(value)
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
                  const res = signUpSchema.shape.password.safeParse(value)
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

          <CardFooter className="pt-2">
            <Button
              type="submit"
              disabled={signUpMutation.isPending}
              className="w-full"
            >
              {signUpMutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <ArrowRight className="mr-2 h-4 w-4" />
              )}
              Create Account
            </Button>
          </CardFooter>
        </form>
      </Card>
    </AuthLayout>
  )
}
