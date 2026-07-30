import { z } from "zod"

export const signInSchema = z.object({
  email: z
    .email({ error: "Please enter a valid email address" })
    .min(1, "Email address is required"),
  password: z.string().min(6, "Password must be at least 6 characters"),
})

export const signUpSchema = z.object({
  display_name: z
    .string()
    .min(1, "Display name is required")
    .min(2, "Name must be at least 2 characters"),
  email: z
    .email({ error: "Please enter a valid email address" })
    .min(1, "Email address is required"),
  password: z
    .string()
    .min(1, "Password is required")
    .min(6, "Password must be at least 6 characters"),
})

export type SignInValues = z.infer<typeof signInSchema>
export type SignUpValues = z.infer<typeof signUpSchema>
