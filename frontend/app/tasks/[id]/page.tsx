"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { TaskDetails } from "@/components/task-details"
import { Skeleton } from "@/components/ui/skeleton"
import { ArrowLeft } from "lucide-react"
import type { Task } from "@/lib/types"
import { fetchTask } from "@/lib/api"

export default function TaskPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [task, setTask] = useState<Task | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadTask = async () => {
      try {
        setLoading(true)
        const data = await fetchTask(Number.parseInt(params.id))
        setTask(data)
        setError(null)
      } catch (err) {
        setError("Failed to load task. It may not exist or the server is unavailable.")
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    if (params.id) {
      loadTask()
    }
  }, [params.id])

  const handleBack = () => {
    router.push("/")
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Button variant="ghost" size="sm" className="mb-6" onClick={handleBack}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to list
        </Button>
        <div className="space-y-4">
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Button variant="ghost" size="sm" className="mb-6" onClick={handleBack}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to list
        </Button>
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 dark:border-red-900 dark:bg-red-950">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      </div>
    )
  }

  if (!task) {
    return null
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <TaskDetails task={task} onBack={handleBack} />
    </div>
  )
}
