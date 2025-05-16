from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from app.core.db import database
from app.services.task_service import TaskAnalysisService
from app.api.v1.schemas import (
    Task, TaskCreate, TaskUpdate, TaskAnalysisResult,
    AgentExecution, AgentConfig, ErrorResponse
)

router = APIRouter()
service = TaskAnalysisService()

@router.post("/", response_model=TaskAnalysisResult, status_code=201)
async def create_task(task: TaskCreate):
    """
    Create a new task and perform comprehensive AI analysis.
    
    The analysis includes:
    - Task categorization and prioritization
    - User story generation
    - UX recommendations
    - Database design
    - Technical task breakdown
    - Test strategy
    - Security analysis
    - Timeline estimation
    - Infrastructure planning
    """
    try:
        analysis_result = await service.analyze_task(task.dict())
        
        if "error" in analysis_result:
            raise HTTPException(
                status_code=500,
                detail=analysis_result["error"]
            )
            
        return analysis_result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Task analysis failed: {str(e)}"
        )

@router.get("/", response_model=List[Task])
async def get_tasks(
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=100)
):
    """
    Retrieve all tasks with optional filtering.
    
    Parameters:
    - status: Filter by task status
    - category: Filter by task category
    - priority: Filter by task priority
    - limit: Maximum number of tasks to return
    """
    try:
        tasks = await service.get_all_tasks()
        
        # Apply filters if provided
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        if category:
            tasks = [t for t in tasks if t["category"] == category]
        if priority:
            tasks = [t for t in tasks if t["priority"] == priority]
            
        # Apply limit
        return tasks[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve tasks: {str(e)}"
        )

@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: int):
    """Retrieve a specific task by ID."""
    task = await service.get_task(task_id)
    
    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
        
    return task

@router.patch("/{task_id}", response_model=Task)
async def update_task(task_id: int, task_update: TaskUpdate):
    """
    Update a task's information.
    
    Can update:
    - Description
    - User story
    - Context
    - Status
    - Category
    - Priority
    """
    updated_task = await service.update_task(
        task_id=task_id,
        updates=task_update.dict(exclude_unset=True)
    )
    
    if updated_task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
        
    return updated_task

@router.get("/{task_id}/executions", response_model=List[AgentExecution])
async def get_task_executions(task_id: int):
    """
    Retrieve the execution history for a task.
    Shows all agent operations performed on the task.
    """
    executions = await service.get_agent_executions(task_id)
    
    if not executions:
        raise HTTPException(
            status_code=404,
            detail="No executions found for this task"
        )
        
    return executions

@router.post("/{task_id}/reanalyze", response_model=TaskAnalysisResult)
async def reanalyze_task(task_id: int):
    """
    Perform a fresh analysis of an existing task.
    Useful when task details have been updated.
    """
    task = await service.get_task(task_id)
    
    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    
    try:
        analysis_result = await service.analyze_task({
            "description": task["description"],
            "user_story": task["user_story"],
            "context": task["context"]
        })
        
        if "error" in analysis_result:
            raise HTTPException(
                status_code=500,
                detail=analysis_result["error"]
            )
            
        # Update the task with new analysis results
        await service.update_task(task_id, analysis_result)
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Task reanalysis failed: {str(e)}"
        )

@router.get("/stats/categories", response_model=Dict[str, int])
async def get_category_stats():
    """Get task count by category."""
    try:
        tasks = await service.get_all_tasks()
        categories = {}
        
        for task in tasks:
            category = task["category"] or "Uncategorized"
            categories[category] = categories.get(category, 0) + 1
            
        return categories
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve category stats: {str(e)}"
        )

@router.get("/stats/priorities", response_model=Dict[str, int])
async def get_priority_stats():
    """Get task count by priority."""
    try:
        tasks = await service.get_all_tasks()
        priorities = {}
        
        for task in tasks:
            priority = task["priority"] or "Unset"
            priorities[priority] = priorities.get(priority, 0) + 1
            
        return priorities
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve priority stats: {str(e)}"
        )

@router.get("/stats/agent-performance", response_model=Dict[str, Dict[str, float]])
async def get_agent_performance_stats():
    """
    Get performance statistics for each agent type.
    Returns average execution time and success rate.
    """
    try:
        all_executions = []
        tasks = await service.get_all_tasks()
        
        for task in tasks:
            executions = await service.get_agent_executions(task["id"])
            all_executions.extend(executions)
            
        stats = {}
        
        for execution in all_executions:
            agent_type = execution["agent_type"]
            if agent_type not in stats:
                stats[agent_type] = {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "total_time": 0.0
                }
                
            stats[agent_type]["total_executions"] += 1
            stats[agent_type]["total_time"] += execution["execution_time"]
            if execution["success"]:
                stats[agent_type]["successful_executions"] += 1
                
        # Calculate averages and success rates
        result = {}
        for agent_type, data in stats.items():
            total = data["total_executions"]
            result[agent_type] = {
                "avg_execution_time": data["total_time"] / total if total > 0 else 0,
                "success_rate": data["successful_executions"] / total if total > 0 else 0
            }
            
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve agent performance stats: {str(e)}"
        )
