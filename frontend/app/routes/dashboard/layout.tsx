import type { Route } from "./+types/layout"
import { useState, useEffect } from "react"
import {
  Link,
  NavLink,
  Outlet,
  useNavigate,
  useSearchParams,
  useLocation,
} from "react-router"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useForm } from "@tanstack/react-form"
import {
  Cpu,
  Building2,
  Server,
  KeyRound,
  Users,
  Plus,
  LogOut,
  ChevronDown,
  LayoutDashboard,
  Loader2,
  AlertCircle,
  MessageSquare,
} from "lucide-react"
import {
  getOrganizationsApi,
  createOrganizationApi,
  type Organization,
} from "~/api/dashboard"
import { createOrgSchema } from "~/schemas/dashboard"
import { Button } from "~/components/ui/button"
import { Input } from "~/components/ui/input"
import { Label } from "~/components/ui/label"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "~/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu"
import {
  SidebarProvider,
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarFooter,
  SidebarTrigger,
  SidebarInset,
} from "~/components/ui/sidebar"
import DashboardHeader from "~/routes/dashboard/header"

export function meta({}: Route.MetaArgs) {
  return [{ title: "Dashboard - NetToHost" }]
}

export default function DashboardLayout() {
  // const navigate = useNavigate()
  // const location = useLocation()
  // const queryClient = useQueryClient()
  // const [searchParams, setSearchParams] = useSearchParams()
  // const [isCreateOrgOpen, setIsCreateOrgOpen] = useState(false)
  // const [userDisplayName, setUserDisplayName] = useState("User")

  // useEffect(() => {
  //   const token = localStorage.getItem("nettohost_token")
  //   if (token) {
  //     navigate("/signin")
  //   }
  //   const name = localStorage.getItem("nettohost_display_name")
  //   if (name) {
  //     setUserDisplayName(name)
  //   }
  // }, [navigate])

  // // Fetch user organizations using TanStack Query
  // const { data: orgs = [], isLoading: isLoadingOrgs } = useQuery({
  //   queryKey: ["organizations"],
  //   queryFn: getOrganizationsApi,
  // })

  // const selectedOrgId = searchParams.get("orgId") || orgs[0]?.id || ""
  // const selectedOrg = orgs.find((o) => o.id === selectedOrgId) || orgs[0]

  // // Create Org Mutation
  // const createOrgMutation = useMutation({
  //   mutationFn: createOrganizationApi,
  //   onSuccess: (newOrg) => {
  //     queryClient.invalidateQueries({ queryKey: ["organizations"] })
  //     setIsCreateOrgOpen(false)
  //     setSearchParams({ orgId: newOrg.id })
  //   },
  // })

  // // Create Org Form
  // const createOrgForm = useForm({
  //   defaultValues: { name: "" },
  //   onSubmit: ({ value }) => {
  //     createOrgMutation.mutate(value)
  //   },
  // })

  // const handleLogout = () => {
  //   localStorage.removeItem("nettohost_token")
  //   localStorage.removeItem("nettohost_user_id")
  //   localStorage.removeItem("nettohost_display_name")
  //   navigate("/signin")
  // }

  // const selectOrganization = (orgId: string) => {
  //   setSearchParams({ orgId })
  // }

  return (
    <div className="flex flex-col min-h-screen">
      <DashboardHeader />
      <div className="flex-1 p-4">
        <Outlet />
      </div>
    </div>
  )
}
