"use client"

import { useEffect } from "react"
import { TaskList } from "@/components/task-list"
import { CreateTaskForm } from "@/components/create-task-form"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { LayoutDashboard } from "lucide-react"
import Link from "next/link"
import { useTaskContext } from "@/lib/task-context"

export default function Home() {
  const { refreshTasks } = useTaskContext()

  useEffect(() => {
    refreshTasks()
  }, [refreshTasks])

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 dark:text-slate-50 sm:text-5xl">
            AI-Powered Task Assistant
          </h1>
          <p className="mt-3 text-lg text-slate-600 dark:text-slate-400">
            Automatically categorize and prioritize your tasks with AI
          </p>
          <Button variant="outline" className="mt-4" asChild>
            <Link href="/dashboard">
              <LayoutDashboard className="mr-2 h-4 w-4" />
              View Dashboard
            </Link>
          </Button>
        </header>

        <Tabs defaultValue="tasks" className="mx-auto max-w-4xl">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="tasks">View Tasks</TabsTrigger>
            <TabsTrigger value="create">Create Task</TabsTrigger>
          </TabsList>
          <TabsContent value="tasks" className="mt-6">
            <TaskList />
          </TabsContent>
          <TabsContent value="create" className="mt-6">
            <CreateTaskForm />
          </TabsContent>
        </Tabs>
      </div>
    </main>
  )
}
