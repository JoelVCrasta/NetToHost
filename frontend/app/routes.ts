import { type RouteConfig, index, route } from "@react-router/dev/routes"

export default [
  index("routes/home.tsx"),
  route("signin", "routes/signin.tsx"),
  route("signup", "routes/signup.tsx"),
  route("auth/callback", "routes/auth/callback.tsx"),
  route("dashboard", "routes/dashboard/layout.tsx"),
] satisfies RouteConfig
