import { useState, useEffect } from "react"
import {
  Link,
  NavLink,
  Outlet,
  useNavigate,
  useSearchParams,
  useLocation,
} from "react-router"
import { Button } from "~/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu"
import { ChevronsUpDown, Check } from "lucide-react"
import { useOrganizationStore } from "~/hooks/useOrganizationStore"

export default function DashboardHeader() {
  const { selectedOrg } = useOrganizationStore()

  return (
    <div className="flex items-center justify-between p-3 border-b border-muted">
      <div className="flex items-center">
        <Link to="/dashboard" className="text-lg font-bold">
          NTH
        </Link>
        <p className="mx-3 text-xl text-muted">/</p>
        <p className="text-sm font-bold mr-2">
          {selectedOrg?.name ?? "Organization"}
        </p>
        <Dropdown />
      </div>
    </div>
  )
}

function Dropdown() {
  const { selectedOrg, setSelectedOrg, allOrganizations } =
    useOrganizationStore()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={
          <Button variant="ghost" size="sm" className="text-lg font-bold">
            <ChevronsUpDown />
          </Button>
        }
      />
      <DropdownMenuContent>
        {allOrganizations.map((org) => (
          <DropdownMenuItem
            key={org.id}
            onClick={() => setSelectedOrg(org)}
            className="flex items-center justify-between"
          >
            {org.name}
            {selectedOrg?.id === org.id && <Check />}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
