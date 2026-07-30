import { z } from "zod"

export const updateHostSchema = z.object({
  name: z.string().min(1, "Host device name is required"),
})
export type UpdateHostValues = z.infer<typeof updateHostSchema>
