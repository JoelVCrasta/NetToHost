import { useEffect } from "react"
import { Link, Outlet, useLocation, useNavigate } from "react-router"
import {
  Cpu,
  Building2,
  Server,
  KeyRound,
  Users,
  LogOut,
  ChevronDown,
  LayoutDashboard,
  MessageSquare,
} from "lucide-react"
import { useSessionStore } from "~/hooks/useSessionStore"
import { useOrganizationStore } from "~/hooks/useOrganizationStore"
import { Button } from "~/components/ui/button"
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

export default function DashboardLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, clearSession } = useSessionStore()
  const { selectedOrg, setSelectedOrg } = useOrganizationStore()

  const handleLogout = () => {
    clearSession()
    navigate("/signin")
  }

  return <></>
}
