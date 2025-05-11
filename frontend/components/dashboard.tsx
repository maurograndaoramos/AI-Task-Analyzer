"use client"

import { useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts"
import { useTaskContext } from "@/lib/task-context"

export function Dashboard() {
  const { tasks, loading, error, refreshTasks } = useTaskContext()

  useEffect(() => {
    refreshTasks()
  }, [refreshTasks])

  // Calculate statistics
  const totalTasks = tasks.length
  const categoryCounts = tasks.reduce((acc: Record<string, number>, task) => {
    const category = task.category || "Uncategorized"
    acc[category] = (acc[category] || 0) + 1
    return acc
  }, {})

  const priorityCounts = tasks.reduce((acc: Record<string, number>, task) => {
    const priority = task.priority || "Unassigned"
    acc[priority] = (acc[priority] || 0) + 1
    return acc
  }, {})

  const statusCounts = tasks.reduce((acc: Record<string, number>, task) => {
    const status = task.status || "Unknown"
    acc[status] = (acc[status] || 0) + 1
    return acc
  }, {})

  // Prepare chart data
  const categoryData = Object.entries(categoryCounts).map(([name, value]) => ({ name, value }))
  const priorityData = Object.entries(priorityCounts).map(([name, value]) => ({ name, value }))
  const statusData = Object.entries(statusCounts).map(([name, value]) => ({ name, value }))

  // Colors for charts
  const CATEGORY_COLORS = ["#8884d8", "#83a6ed", "#8dd1e1", "#82ca9d", "#a4de6c", "#d0ed57", "#ffc658"]
  const PRIORITY_COLORS = {
    High: "#ef4444",
    Medium: "#f59e0b",
    Low: "#10b981",
    Unassigned: "#6b7280",
  }
  const STATUS_COLORS = {
    Open: "#3b82f6",
    "In Progress": "#8b5cf6",
    Done: "#10b981",
    Unknown: "#6b7280",
  }

  // Recent tasks
  const recentTasks = [...tasks]
    .sort((a, b) => {
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    })
    .slice(0, 5)

  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardHeader className="pb-2">
              <Skeleton className="h-5 w-1/2" />
              <Skeleton className="h-4 w-1/3" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-[150px] w-full" />
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
          <p className="text-slate-600 dark:text-slate-400">
            No tasks found. Create your first task to see statistics!
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Tasks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalTasks}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">By Priority</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-1">
            {Object.entries(priorityCounts).map(([priority, count]) => {
              const color =
                priority === "High"
                  ? "bg-red-500"
                  : priority === "Medium"
                    ? "bg-yellow-500"
                    : priority === "Low"
                      ? "bg-green-500"
                      : "bg-gray-500"

              return (
                <Badge key={priority} className={`${color} text-white`}>
                  {priority}: {count}
                </Badge>
              )
            })}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">By Category</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-1">
            {Object.entries(categoryCounts)
              .slice(0, 3)
              .map(([category, count]) => (
                <Badge key={category} variant="outline">
                  {category}: {count}
                </Badge>
              ))}
            {Object.keys(categoryCounts).length > 3 && (
              <Badge variant="outline">+{Object.keys(categoryCounts).length - 3} more</Badge>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">By Status</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-1">
            {Object.entries(statusCounts).map(([status, count]) => (
              <Badge key={status} variant="secondary">
                {status}: {count}
              </Badge>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card className="col-span-1 md:col-span-2 lg:col-span-1">
          <CardHeader>
            <CardTitle>Tasks by Priority</CardTitle>
            <CardDescription>Distribution of tasks by priority level</CardDescription>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={priorityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  {priorityData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={
                        PRIORITY_COLORS[entry.name as keyof typeof PRIORITY_COLORS] ||
                        CATEGORY_COLORS[index % CATEGORY_COLORS.length]
                      }
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="col-span-1 md:col-span-2 lg:col-span-1">
          <CardHeader>
            <CardTitle>Tasks by Category</CardTitle>
            <CardDescription>Distribution of tasks by category</CardDescription>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="col-span-1 md:col-span-2 lg:col-span-1">
          <CardHeader>
            <CardTitle>Tasks by Status</CardTitle>
            <CardDescription>Distribution of tasks by status</CardDescription>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={statusData}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value">
                  {statusData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={
                        STATUS_COLORS[entry.name as keyof typeof STATUS_COLORS] ||
                        CATEGORY_COLORS[index % CATEGORY_COLORS.length]
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Tasks</CardTitle>
          <CardDescription>Latest tasks added to the system</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentTasks.map((task) => (
              <div key={task.id} className="flex items-start justify-between border-b pb-4 last:border-0 last:pb-0">
                <div>
                  <h3 className="font-medium">Task #{task.id}</h3>
                  <p className="line-clamp-1 text-sm text-slate-600 dark:text-slate-400">{task.description}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-500">
                    Created: {new Date(task.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex gap-2">
                  {task.category && (
                    <Badge variant="outline" className="font-normal">
                      {task.category}
                    </Badge>
                  )}
                  {task.priority && (
                    <Badge
                      className={`
                        ${
                          task.priority === "High"
                            ? "bg-red-500"
                            : task.priority === "Medium"
                              ? "bg-yellow-500"
                              : task.priority === "Low"
                                ? "bg-green-500"
                                : "bg-gray-500"
                        } 
                        text-white font-normal
                      `}
                    >
                      {task.priority}
                    </Badge>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
