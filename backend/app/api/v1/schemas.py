from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class TaskBase(BaseModel):
    """Base Task schema with common attributes"""
    description: str
    user_story: Optional[str] = None
    context: Optional[str] = None

class TaskCreate(TaskBase):
    """Task schema for task creation - subset of fields needed for creation"""
    pass

class Task(TaskBase):
    """Task schema for task responses - includes all task fields"""
    id: int
    status: str = "Open"
    created_at: datetime
    category: Optional[str] = None
    priority: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class TaskUpdate(BaseModel):
    """Task schema for task updates - all fields are optional"""
    description: Optional[str] = None
    user_story: Optional[str] = None
    context: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
