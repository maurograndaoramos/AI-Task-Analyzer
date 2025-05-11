"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { AlertCircle, CheckCircle2 } from "lucide-react"
import { createTask } from "@/lib/api"
import { useTaskContext } from "@/lib/task-context"
import { useRouter } from "next/navigation"

const formSchema = z.object({
  description: z.string().min(5, {
    message: "Description must be at least 5 characters.",
  }),
  user_story: z.string().optional(),
  context: z.string().optional(),
})

type FormValues = z.infer<typeof formSchema>

export function CreateTaskForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<{
    type: "success" | "error"
    message: string
  } | null>(null)
  const { refreshTasks, setLastCreatedTask, lastCreatedTask } = useTaskContext() // Correctly added lastCreatedTask here
  const router = useRouter()

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      description: "",
      user_story: "",
      context: "",
    },
  })

  async function onSubmit(values: FormValues) {
    setIsSubmitting(true)
    setSubmitStatus(null)

    try {
      const createdTask = await createTask(values)
      setLastCreatedTask(createdTask)
      await refreshTasks()

      setSubmitStatus({
        type: "success",
        message: "Task created successfully! The AI has analyzed and categorized your task.",
      })
      form.reset()
    } catch (error) {
      console.error("Error creating task:", error)
      setSubmitStatus({
        type: "error",
        message: "Failed to create task. Please try again later.",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const getPriorityColor = (priority: string | null) => {
    if (!priority) return "bg-gray-500"

    switch (priority.toLowerCase()) {
      case "high":
        return "bg-red-500"
      case "medium":
        return "bg-yellow-500"
      case "low":
        return "bg-green-500"
      default:
        return "bg-gray-500"
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Create New Task</CardTitle>
        <CardDescription>Add a new task to be analyzed and categorized by AI</CardDescription>
      </CardHeader>
      <CardContent>
        {submitStatus && (
          <Alert
            variant={submitStatus.type === "error" ? "destructive" : "default"}
            className={`mb-6 ${submitStatus.type === "success" ? "border-green-500 text-green-700 dark:text-green-300" : ""}`}
          >
            {submitStatus.type === "success" ? (
              <CheckCircle2 className="h-4 w-4" />
            ) : (
              <AlertCircle className="h-4 w-4" />
            )}
            <AlertTitle>{submitStatus.type === "success" ? "Success" : "Error"}</AlertTitle>
            <AlertDescription>{submitStatus.message}</AlertDescription>
          </Alert>
        )}

        {submitStatus?.type === "success" && (
          <div className="mb-6 rounded-lg border border-slate-200 p-4 dark:border-slate-800">
            <h3 className="mb-2 text-sm font-medium">AI Analysis Results:</h3>
            <div className="flex flex-wrap gap-2">
              {lastCreatedTask && ( // Use lastCreatedTask for the condition
                <>
                  <div className="flex items-center gap-1">
                    <span className="text-sm text-slate-500">Category:</span>
                    <Badge variant="outline" className="font-normal">
                      {lastCreatedTask.category || "Not assigned"} {/* Use lastCreatedTask */}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="text-sm text-slate-500">Priority:</span>
                    <Badge className={`${getPriorityColor(lastCreatedTask.priority)} text-white font-normal`}> {/* Use lastCreatedTask */}
                      {lastCreatedTask.priority || "Not assigned"} {/* Use lastCreatedTask */}
                    </Badge>
                  </div>
                </>
              )}
            </div>
            <div className="mt-3 flex gap-2">
              <Button variant="outline" size="sm" onClick={() => router.push("/tasks")}>
                View All Tasks
              </Button>
              <Button variant="outline" size="sm" onClick={() => router.push("/dashboard")}>
                Go to Dashboard
              </Button>
            </div>
          </div>
        )}

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description *</FormLabel>
                  <FormControl>
                    <Textarea placeholder="Describe the task in detail" className="min-h-[100px]" {...field} />
                  </FormControl>
                  <FormDescription>Provide a clear description of the task to be analyzed.</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="user_story"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>User Story (Optional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="As a [user], I want to [action] so that [benefit]"
                      className="min-h-[100px]"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    Adding a user story helps the AI better understand the task's purpose.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="context"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Additional Context (Optional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Any additional context or information about the task"
                      className="min-h-[100px]"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>Provide any additional context that might help with categorization.</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? "Creating..." : "Create Task"}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}
