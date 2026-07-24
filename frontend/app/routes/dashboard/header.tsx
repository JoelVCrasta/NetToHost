import { useState, useEffect } from "react"
import {
  Link,
  NavLink,
  Outlet,
  useNavigate,
  useSearchParams,
  useLocation,
} from "react-router"

export default function DashboardHeader() {
  return (
    <div className="flex items-center justify-between p-3 border-b border-muted">
      <div className="flex items-center">
        <Link to="/dashboard" className="text-lg font-bold">
          NTH
        </Link>
        <p className="mx-3 text-xl text-muted">/</p>
        
      </div>
    </div>
  )
}
