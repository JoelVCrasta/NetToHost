import { create } from "zustand"
import { persist } from "zustand/middleware"
import type { Organization } from "~/types/organization"

interface OrganizationState {
  selectedOrg: Organization | null
  allOrganizations: Organization[]
  setSelectedOrg: (org: Organization | null) => void
  setAllOrganizations: (orgs: Organization[]) => void
  clearOrganizationStore: () => void
}

export const useOrganizationStore = create<OrganizationState>()(
  persist(
    (set) => ({
      selectedOrg: null,
      allOrganizations: [],
      setSelectedOrg: (org: Organization | null) => {
        set({ selectedOrg: org })
      },
      clearOrganizationStore: () => {
        set({ selectedOrg: null })
      },
      setAllOrganizations: (orgs: Organization[]) => {
        set({ allOrganizations: orgs })
      },
    }),
    {
      name: "organization-storage",
    },
  ),
)
