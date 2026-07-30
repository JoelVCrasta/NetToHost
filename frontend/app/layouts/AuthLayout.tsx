import type { ReactNode } from "react"
import { Link, Outlet } from "react-router"
import { Cpu } from "lucide-react"

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex justify-center items-center p-2">
      {children}
    </div>
  )
}
