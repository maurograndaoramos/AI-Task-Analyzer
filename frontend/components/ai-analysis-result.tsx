import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { Task } from "@/lib/types"

interface AIAnalysisResultProps {
  task: Task
}

export function AIAnalysisResult({ task }: AIAnalysisResultProps) {
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
        <CardTitle className="text-lg">AI Analysis Results</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h3 className="text-sm font-medium text-slate-500 mb-2">Category</h3>
            <Badge variant="outline" className="text-base font-normal">
              {task.category || "Not assigned"}
            </Badge>
          </div>
          <div>
            <h3 className="text-sm font-medium text-slate-500 mb-2">Priority</h3>
            <Badge className={`${getPriorityColor(task.priority)} text-white text-base font-normal`}>
              {task.priority || "Not assigned"}
            </Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
