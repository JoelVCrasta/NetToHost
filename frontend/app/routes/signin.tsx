import type { Route } from "./+types/signin"
import { Link, useNavigate } from "react-router"
import { useForm } from "@tanstack/react-form"
import { useMutation } from "@tanstack/react-query"
import { Cpu, Mail, Lock, ArrowRight, Loader2, AlertCircle } from "lucide-react"
import { signInSchema, type SignInValues } from "~/schemas/auth"
import { signInApi } from "~/api/auth"
import { Card, CardContent } from "~/components/ui/card"
import { Input } from "~/components/ui/input"
import { Label } from "~/components/ui/label"
import { Button } from "~/components/ui/button"

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Sign In - NetToHost" },
    { name: "description", content: "Sign in to your NetToHost workspace" },
  ]
}

export default function SignIn() {
  const navigate = useNavigate()

  const signInMutation = useMutation({
    mutationFn: (values: SignInValues) => signInApi(values),
    onSuccess: (data) => {
      localStorage.setItem("nettohost_token", data.access_token)
      localStorage.setItem("nettohost_user_id", data.user_id)
      localStorage.setItem("nettohost_display_name", data.display_name)
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
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-center items-center py-12 px-4 sm:px-6 lg:px-8 selection:bg-indigo-500 selection:text-white relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] bg-indigo-600/15 rounded-full blur-[140px] pointer-events-none" />

      <div className="w-full max-w-md relative z-10 space-y-6">
        <div className="text-center space-y-2">
          <Link
            to="/"
            className="inline-flex items-center space-x-3 group mb-2"
          >
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/25 group-hover:scale-105 transition-transform">
              <Cpu className="w-7 h-7 text-white" />
            </div>
            <span className="font-bold text-2xl tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              NetToHost
            </span>
          </Link>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100">
            Sign in to your account
          </h2>
          <p className="text-sm text-slate-400">
            Or{" "}
            <Link
              to="/signup"
              className="font-medium text-indigo-400 hover:text-indigo-300 transition-colors"
            >
              create a new account
            </Link>
          </p>
        </div>

        <Card className="bg-slate-900/80 border-slate-800 backdrop-blur-xl shadow-2xl">
          <CardContent className="pt-6">
            {signInMutation.isError && (
              <div className="mb-6 p-3.5 rounded-xl border border-rose-500/30 bg-rose-950/30 text-rose-300 text-sm flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                <span>{signInMutation.error.message}</span>
              </div>
            )}

            <form
              onSubmit={(e) => {
                e.preventDefault()
                e.stopPropagation()
                form.handleSubmit()
              }}
              className="space-y-5"
            >
              {/* Email Field */}
              <form.Field
                name="email"
                validators={{
                  onChange: ({ value }) => {
                    const result = signInSchema.shape.email.safeParse(value)
                    return result.success
                      ? undefined
                      : result.error.issues[0]?.message || "Invalid input"
                  },
                }}
              >
                {(field) => (
                  <div className="space-y-2">
                    <Label
                      htmlFor={field.name}
                      className="text-xs font-semibold uppercase tracking-wider text-slate-300"
                    >
                      Email Address
                    </Label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                        <Mail className="w-4 h-4" />
                      </div>
                      <Input
                        id={field.name}
                        name={field.name}
                        type="email"
                        placeholder="name@company.com"
                        value={field.state.value}
                        onBlur={field.handleBlur}
                        onChange={(e) => field.handleChange(e.target.value)}
                        className="pl-10 bg-slate-950/80 border-slate-800 text-slate-100 placeholder:text-slate-500 focus-visible:ring-indigo-500"
                      />
                    </div>
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
                    const result = signInSchema.shape.password.safeParse(value)
                    return result.success
                      ? undefined
                      : result.error.issues[0]?.message || "Invalid input"
                  },
                }}
              >
                {(field) => (
                  <div className="space-y-2">
                    <Label
                      htmlFor={field.name}
                      className="text-xs font-semibold uppercase tracking-wider text-slate-300"
                    >
                      Password
                    </Label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                        <Lock className="w-4 h-4" />
                      </div>
                      <Input
                        id={field.name}
                        name={field.name}
                        type="password"
                        placeholder="••••••••"
                        value={field.state.value}
                        onBlur={field.handleBlur}
                        onChange={(e) => field.handleChange(e.target.value)}
                        className="pl-10 bg-slate-950/80 border-slate-800 text-slate-100 placeholder:text-slate-500 focus-visible:ring-indigo-500"
                      />
                    </div>
                    {field.state.meta.errors.length > 0 && (
                      <p className="text-xs text-rose-400">
                        {field.state.meta.errors.join(", ")}
                      </p>
                    )}
                  </div>
                )}
              </form.Field>

              <Button
                type="submit"
                disabled={signInMutation.isPending}
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold shadow-lg shadow-indigo-600/25"
              >
                {signInMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  <>
                    Sign In
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
