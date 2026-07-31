import { Link } from "react-router"
import { useQuery } from "@tanstack/react-query"
import { Button } from "~/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu"
import { ChevronsUpDown, Check, Waypoints, Plus, Box } from "lucide-react"
import { getOrganizationsApi } from "~/api/organization"
import { useOrganizationStore } from "~/hooks/useOrganizationStore"

export default function DashboardHeader() {
  const { selectedOrg } = useOrganizationStore()

  return (
    <div className="flex items-center justify-between p-3 border-b border-muted">
      <div className="flex items-center">
        <Link to="/dashboard" className="text-lg font-bold">
          <Waypoints />
        </Link>
        <p className="mx-3 text-xl text-muted">/</p>
        <div className="flex items-center">
          <Box size="14" className="mr-2 text-muted-foreground" />
          <p className="text-sm font-bold mr-2">
            {selectedOrg?.name ?? "Organization"}
          </p>
        </div>
        <Dropdown />
      </div>
    </div>
  )
}

function Dropdown() {
  const { selectedOrg, setSelectedOrg } = useOrganizationStore()

  const { data: allOrganizations = [] } = useQuery({
    queryKey: ["organizations"],
    queryFn: getOrganizationsApi,
  })

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={
          <Button variant="ghost" size="sm" className="text-lg font-bold">
            <ChevronsUpDown className="text-muted-foreground" />
          </Button>
        }
      />
      <DropdownMenuContent className="w-60" align="start">
        {allOrganizations.map((org) => (
          <DropdownMenuItem
            key={org.id}
            onClick={() => setSelectedOrg(org)}
            className="flex items-center justify-between cursor-pointer"
          >
            {org.name}
            {selectedOrg?.id === org.id && <Check />}
          </DropdownMenuItem>
        ))}

        <DropdownMenuSeparator />

        <DropdownMenuItem render={<Link to="/dashboard/organizations" />}>
          All Organizations
        </DropdownMenuItem>

        <DropdownMenuSeparator />

        <DropdownMenuItem render={<Link to="/dashboard/organizations/new" />}>
          <Plus className="w-4 h-4 mr-2" />
          <span>Create Organization</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
