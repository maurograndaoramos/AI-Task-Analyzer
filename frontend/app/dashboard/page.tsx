import { Dashboard } from "@/components/dashboard"

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50">Dashboard</h1>
          <p className="mt-2 text-slate-600 dark:text-slate-400">
            Overview of your tasks and their AI-assigned categories and priorities
          </p>
        </header>

        <div className="mx-auto">
          <Dashboard />
        </div>
      </div>
    </div>
  )
}
