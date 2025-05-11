import logging
from typing import List, Dict, Any
import os
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from app.api.v1.schemas import Task, TaskCreate, TaskUpdate
from app.core.db import database, tasks
from app.services.task_service import TaskAnalysisService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=Task, status_code=201)
async def create_task(task: TaskCreate):
    """Create a new task with optional AI analysis"""
    # Initialize task service to get AI analysis if available
    service = TaskAnalysisService()
    
    try:
        # Get AI analysis for category and priority if possible
        analysis_result = await service.analyze_task(task)
        if analysis_result.get("error"):
            logger.warning(
                f"AI Analysis for task description '{task.description[:50]}...' "
                f"resulted in an error/warning: {analysis_result['error']}. "
                f"Category/Priority will be null."
            )
        
        # Set the current time for created_at
        current_time = datetime.now(timezone.utc)
        
        # Prepare task data for database
        insert_query = tasks.insert().values(
            description=task.description,
            user_story=task.user_story,
            context=task.context,
            category=analysis_result.get("category"),
            priority=analysis_result.get("priority"),
            status="Open",
            created_at=current_time
        )
        
        last_record_id = await database.execute(insert_query)
        
        # Return created task
        return {
            "id": last_record_id,
            "description": task.description,
            "user_story": task.user_story,
            "context": task.context,
            "category": analysis_result.get("category"),
            "priority": analysis_result.get("priority"),
            "status": "Open",
            "created_at": current_time
        }
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Task])
async def read_tasks():
    """Get all tasks"""
    query = tasks.select()
    return await database.fetch_all(query)

@router.get("/{task_id}", response_model=Task)
async def read_task(task_id: int):
    """Get a specific task by ID"""
    query = tasks.select().where(tasks.c.id == task_id)
    task = await database.fetch_one(query)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=Task)
async def update_task(task_id: int, task_update: TaskUpdate):
    """Update an existing task"""
    select_query = tasks.select().where(tasks.c.id == task_id)
    existing_task = await database.fetch_one(select_query)

    if existing_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")

    update_query = (
        tasks.update()
        .where(tasks.c.id == task_id)
        .values(**update_data)
    )
    await database.execute(update_query)

    # Fetch the updated task to return
    updated_task = await database.fetch_one(select_query)
    if updated_task is None:
        # This should ideally not happen if the update was successful and task existed
        raise HTTPException(status_code=500, detail="Failed to retrieve updated task")
    return updated_task
