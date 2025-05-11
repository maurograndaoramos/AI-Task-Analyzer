"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { ThemeToggle } from "@/components/theme-toggle"
import { Button } from "@/components/ui/button"
import { PlusCircle, ListTodo, LayoutDashboard } from "lucide-react"

export function Navbar() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="flex items-center space-x-2">
            <ListTodo className="h-6 w-6" />
            <span className="font-bold">Task Assistant</span>
          </Link>
        </div>
        <div className="flex flex-1 items-center justify-end space-x-2">
          <nav className="flex items-center space-x-2">
            <Button variant={pathname === "/dashboard" ? "default" : "ghost"} size="sm" asChild>
              <Link href="/dashboard">
                <LayoutDashboard className="mr-2 h-4 w-4" />
                Dashboard
              </Link>
            </Button>
            <Button variant={pathname === "/tasks" ? "default" : "ghost"} size="sm" asChild>
              <Link href="/tasks">
                <ListTodo className="mr-2 h-4 w-4" />
                Tasks
              </Link>
            </Button>
            <Button variant={pathname === "/tasks/create" ? "default" : "ghost"} size="sm" asChild>
              <Link href="/tasks/create">
                <PlusCircle className="mr-2 h-4 w-4" />
                New Task
              </Link>
            </Button>
            <ThemeToggle />
          </nav>
        </div>
      </div>
    </header>
  )
}
