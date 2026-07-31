import type { Route } from "./+types/layout"
import { Outlet } from "react-router"
import { SidebarProvider, SidebarInset } from "~/components/ui/sidebar"
import DashboardHeader from "./components/DashboardHeader"
import DashboardSidebar from "./components/DashboardSidebar"

export function meta({}: Route.MetaArgs) {
  return [{ title: "Dashboard - NetToHost" }]
}

export default function DashboardLayout() {
  return (
    <SidebarProvider defaultOpen={true}>
      <div className="flex flex-col min-h-screen w-full bg-background text-foreground selection:bg-primary selection:text-primary-foreground">
        <DashboardHeader />
        <div className="flex flex-1 overflow-hidden">
          {/* <DashboardSidebar /> */}
          <SidebarInset className="flex-1 p-6 overflow-y-auto bg-background">
            <Outlet />
          </SidebarInset>
        </div>
      </div>
    </SidebarProvider>
  )
}
