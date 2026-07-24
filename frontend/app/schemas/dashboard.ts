import { z } from "zod";

export const createOrgSchema = z.object({
  name: z.string().min(1, "Organization name is required").min(2, "Name must be at least 2 characters"),
});
export type CreateOrgValues = z.infer<typeof createOrgSchema>;

export const updateOrgSchema = z.object({
  name: z.string().min(1, "Organization name is required").min(2, "Name must be at least 2 characters"),
});
export type UpdateOrgValues = z.infer<typeof updateOrgSchema>;

export const updateHostSchema = z.object({
  name: z.string().min(1, "Host device name is required"),
});
export type UpdateHostValues = z.infer<typeof updateHostSchema>;

export const createTokenSchema = z.object({
  name: z.string().optional(),
  expires_at: z.string().optional(),
});
export type CreateTokenValues = z.infer<typeof createTokenSchema>;

export const addMemberSchema = z.object({
  user_id: z.string().min(1, "User ID is required"),
  role: z.enum(["owner", "admin", "viewer"]),
});
export type AddMemberValues = z.infer<typeof addMemberSchema>;
