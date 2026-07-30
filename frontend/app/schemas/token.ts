import { z } from "zod"

export const createTokenSchema = z.object({
  name: z.string().optional(),
  expires_at: z.string().optional(),
})
export type CreateTokenValues = z.infer<typeof createTokenSchema>
