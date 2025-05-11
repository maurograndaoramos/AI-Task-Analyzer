import { TaskList } from "@/components/task-list"
import { ThemeToggle } from "@/components/theme-toggle"

export default function TasksPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8 flex items-center justify-between">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50">All Tasks</h1>
        </header>

        <div className="mx-auto max-w-4xl">
          <TaskList />
        </div>
      </div>
    </div>
  )
}
