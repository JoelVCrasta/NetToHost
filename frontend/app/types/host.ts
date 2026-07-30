export interface HostDeviceResponse {
  id: number
  host_id: string
  org_id: string
  name: string
  is_online: boolean
  last_seen: string
}

export interface HostDevice {
  id: number
  hostId: string
  orgId: string
  name: string
  isOnline: boolean
  lastSeen: string
}
