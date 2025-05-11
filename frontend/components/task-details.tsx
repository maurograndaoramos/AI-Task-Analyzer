"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowLeft } from "lucide-react"
import { useTaskContext } from "@/lib/task-context"
import { updateTaskStatus } from "@/lib/api"
import type { Task } from "@/lib/types"

interface TaskDetailsProps {
  task: Task
  onBack: () => void
}

export function TaskDetails({ task, onBack }: TaskDetailsProps) {
  const [currentTask, setCurrentTask] = useState<Task>(task)
  const [updating, setUpdating] = useState(false)
  const [updateError, setUpdateError] = useState<string | null>(null)
  const { refreshTasks } = useTaskContext()

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

  const handleStatusChange = async (newStatus: string) => {
    try {
      setUpdating(true)
      setUpdateError(null)

      try {
        // Try to call the API if it's implemented
        const updatedTask = await updateTaskStatus(currentTask.id, newStatus)
        setCurrentTask(updatedTask)
      } catch (error) {
        console.log("API not implemented yet, using local state update")
        // Fallback to local state update if API is not implemented
        const updatedTask = {
          ...currentTask,
          status: newStatus,
          updated_at: new Date().toISOString(),
        }
        setCurrentTask(updatedTask)
      }

      // Refresh the task list to reflect the changes
      await refreshTasks()
    } catch (error) {
      console.error("Error updating task status:", error)
      setUpdateError("Failed to update task status. Please try again.")
    } finally {
      setUpdating(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <Button variant="ghost" size="sm" className="mb-2 w-fit -ml-2" onClick={onBack}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to list
        </Button>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <CardTitle className="text-2xl">Task #{currentTask.id}</CardTitle>
          <div className="flex flex-wrap gap-2">
            {currentTask.status && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-slate-500">Status:</span>
                <Select value={currentTask.status} onValueChange={handleStatusChange} disabled={updating}>
                  <SelectTrigger className="h-7 w-[130px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Open">Open</SelectItem>
                    <SelectItem value="In Progress">In Progress</SelectItem>
                    <SelectItem value="Done">Done</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}
            {currentTask.category && (
              <Badge variant="outline" className="font-normal">
                {currentTask.category}
              </Badge>
            )}
            {currentTask.priority && (
              <Badge className={`${getPriorityColor(currentTask.priority)} text-white font-normal`}>
                {currentTask.priority}
              </Badge>
            )}
          </div>
        </div>
        <CardDescription>
          Created: {new Date(currentTask.created_at).toLocaleString()}
          {currentTask.updated_at !== currentTask.created_at && (
            <> | Updated: {new Date(currentTask.updated_at).toLocaleString()}</>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {updateError && (
          <div className="rounded-md bg-red-50 p-3 text-sm text-red-600 dark:bg-red-950 dark:text-red-400">
            {updateError}
          </div>
        )}

        <div>
          <h3 className="text-lg font-semibold mb-1">Description</h3>
          <p className="text-slate-700 dark:text-slate-300 whitespace-pre-wrap">{currentTask.description}</p>
        </div>

        {currentTask.user_story && (
          <div>
            <h3 className="text-lg font-semibold mb-1">User Story</h3>
            <p className="text-slate-700 dark:text-slate-300 whitespace-pre-wrap">{currentTask.user_story}</p>
          </div>
        )}

        {currentTask.context && (
          <div>
            <h3 className="text-lg font-semibold mb-1">Context</h3>
            <p className="text-slate-700 dark:text-slate-300 whitespace-pre-wrap">{currentTask.context}</p>
          </div>
        )}
      </CardContent>
      <CardFooter className="flex justify-end">
        <Button variant="outline" onClick={onBack}>
          Close
        </Button>
      </CardFooter>
    </Card>
  )
}
