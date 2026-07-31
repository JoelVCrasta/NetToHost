import { create } from "zustand"
import { persist } from "zustand/middleware"
import type { Organization } from "~/types/organization"

interface OrganizationState {
  selectedOrg: Organization | null
  setSelectedOrg: (org: Organization | null) => void
  clearOrganizationStore: () => void
}

export const useOrganizationStore = create<OrganizationState>()(
  persist(
    (set) => ({
      selectedOrg: null,
      setSelectedOrg: (org: Organization | null) => {
        set({ selectedOrg: org })
      },
      clearOrganizationStore: () => {
        set({ selectedOrg: null })
      },
    }),
    {
      name: "organization-storage",
    },
  ),
)
