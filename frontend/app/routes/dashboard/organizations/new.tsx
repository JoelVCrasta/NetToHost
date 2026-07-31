import type { Route } from "./+types/new"
import { useNavigate } from "react-router"
import { useForm } from "@tanstack/react-form"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Building2, ArrowRight } from "lucide-react"
import { createOrgSchema, type CreateOrgValues } from "~/schemas/organization"
import { createOrganizationApi } from "~/api/organization"
import { useOrganizationStore } from "~/hooks/useOrganizationStore"
import { toast } from "~/components/ui/toast"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "~/components/ui/card"
import { Input } from "~/components/ui/input"
import { Label } from "~/components/ui/label"
import { Button } from "~/components/ui/button"
import { Spinner } from "~/components/ui/spinner"

export function meta({}: Route.MetaArgs) {
  return [
    { title: "New Organization - NetToHost" },
    { name: "description", content: "Create a new organization in NetToHost" },
  ]
}

export default function CreateOrganizationPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { setSelectedOrg } = useOrganizationStore()

  const createOrgMutation = useMutation({
    mutationFn: (values: CreateOrgValues) => createOrganizationApi(values),
    onSuccess: (newOrg) => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] })
      setSelectedOrg(newOrg)
      toast.add({
        title: "Organization created!",
        description: `${newOrg.name} is now your active workspace.`,
        type: "success",
      })
      navigate("/dashboard")
    },
    onError: (error: Error) => {
      toast.add({
        title: "Failed to create organization",
        description: error.message || "An error occurred.",
        type: "error",
      })
    },
  })

  const form = useForm({
    defaultValues: {
      name: "",
    },
    onSubmit: async ({ value }) => {
      createOrgMutation.mutate(value)
    },
  })

  return (
    <div className="w-full max-w-md mx-auto mt-10">
      <Card>
        <CardHeader>
          {/* <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary mb-2 border border-primary/20">
            <Building2 className="w-5 h-5" />
          </div> */}
          <CardTitle>Create Organization</CardTitle>
          <CardDescription>
            Organizations are a way to group your things. Each organization can
            be configured with different team members and host devices.
          </CardDescription>
        </CardHeader>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            e.stopPropagation()
            form.handleSubmit()
          }}
        >
          <CardContent className="space-y-4 pb-4">
            <form.Field
              name="name"
              validators={{
                onChange: ({ value }) => {
                  const res = createOrgSchema.shape.name.safeParse(value)
                  return res.success ? undefined : res.error.issues[0]?.message
                },
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor={field.name}>Name</Label>
                  <Input
                    id={field.name}
                    name={field.name}
                    type="text"
                    placeholder="Organization name"
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                  />
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-xs text-rose-400">
                      {field.state.meta.errors.join(", ")}
                    </p>
                  )}
                </div>
              )}
            </form.Field>
          </CardContent>

          <CardFooter>
            <Button
              type="submit"
              disabled={createOrgMutation.isPending}
              className="w-full"
            >
              {createOrgMutation.isPending ? (
                <Spinner />
              ) : (
                <ArrowRight className="mr-2 h-4 w-4" />
              )}
              Create Organization
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
