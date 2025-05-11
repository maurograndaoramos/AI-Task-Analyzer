"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { TaskDetails } from "@/components/task-details"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { useTaskContext } from "@/lib/task-context"
import type { Task } from "@/lib/types"

export function TaskList() {
  const { tasks, loading, error, refreshTasks } = useTaskContext()
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([])
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [categoryFilter, setCategoryFilter] = useState<string>("all")
  const [priorityFilter, setPriorityFilter] = useState<string>("all")
  const [searchQuery, setSearchQuery] = useState<string>("")

  useEffect(() => {
    refreshTasks()
  }, [refreshTasks])

  useEffect(() => {
    let result = [...tasks]

    // Apply category filter
    if (categoryFilter !== "all") {
      result = result.filter((task) => task.category === categoryFilter)
    }

    // Apply priority filter
    if (priorityFilter !== "all") {
      result = result.filter((task) => task.priority === priorityFilter)
    }

    // Apply search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      result = result.filter(
        (task) =>
          task.description.toLowerCase().includes(query) ||
          (task.user_story && task.user_story.toLowerCase().includes(query)) ||
          (task.context && task.context.toLowerCase().includes(query)),
      )
    }

    setFilteredTasks(result)
  }, [tasks, categoryFilter, priorityFilter, searchQuery])

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

  // Get unique categories and priorities for filters
  const categories = ["all", ...new Set(tasks.filter((task) => task.category).map((task) => task.category as string))]
  const priorities = ["all", ...new Set(tasks.filter((task) => task.priority).map((task) => task.priority as string))]

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="cursor-pointer hover:shadow-md transition-shadow">
            <CardHeader className="pb-2">
              <Skeleton className="h-6 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-4 w-full mb-2" />
              <Skeleton className="h-4 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950">
        <CardContent className="pt-6">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </CardContent>
      </Card>
    )
  }

  if (tasks.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6 text-center">
          <p className="text-slate-600 dark:text-slate-400">No tasks found. Create your first task!</p>
        </CardContent>
      </Card>
    )
  }

  if (selectedTask) {
    return <TaskDetails task={selectedTask} onBack={() => setSelectedTask(null)} />
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-4 sm:flex-row">
        <div className="flex-1">
          <Input
            placeholder="Search tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full"
          />
        </div>
        <div className="flex gap-2">
          <Select value={categoryFilter} onValueChange={setCategoryFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              {categories.map((category) => (
                <SelectItem key={category} value={category}>
                  {category === "all" ? "All Categories" : category}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={priorityFilter} onValueChange={setPriorityFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Priority" />
            </SelectTrigger>
            <SelectContent>
              {priorities.map((priority) => (
                <SelectItem key={priority} value={priority}>
                  {priority === "all" ? "All Priorities" : priority}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {filteredTasks.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-slate-600 dark:text-slate-400">
              No tasks match your filters. Try adjusting your search criteria.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredTasks.map((task) => (
            <Card
              key={task.id}
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => setSelectedTask(task)}
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xl">Task #{task.id}</CardTitle>
                  <div className="flex gap-2">
                    {task.category && (
                      <Badge variant="outline" className="font-normal">
                        {task.category}
                      </Badge>
                    )}
                    {task.priority && (
                      <Badge className={`${getPriorityColor(task.priority)} text-white font-normal`}>
                        {task.priority}
                      </Badge>
                    )}
                  </div>
                </div>
                <CardDescription>{new Date(task.created_at).toLocaleDateString()}</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="line-clamp-2 text-slate-700 dark:text-slate-300">{task.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
