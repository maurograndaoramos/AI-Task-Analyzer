from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class UserStory(BaseModel):
    """User story details"""
    role: str
    goal: str
    benefit: str
    acceptance_criteria: List[str]

class UXRecommendation(BaseModel):
    """UX analysis recommendation"""
    aspect: str
    suggestion: str
    rationale: str

class DatabaseField(BaseModel):
    """Database field definition"""
    name: str
    type: str
    primary_key: Optional[bool] = False
    indexed: Optional[bool] = False
    nullable: Optional[bool] = True

class DatabaseTable(BaseModel):
    """Database table definition"""
    name: str
    fields: List[DatabaseField]
    relationships: Optional[List[Dict[str, str]]] = None
    indexes: Optional[List[str]] = None

class SecurityVulnerability(BaseModel):
    """Security vulnerability details"""
    type: str
    severity: str
    mitigation: str

class TestScenario(BaseModel):
    """Test scenario definition"""
    component: str
    scenarios: List[str]
    coverage_targets: Optional[List[str]] = None

class TechnicalTask(BaseModel):
    """Technical task breakdown"""
    id: str
    title: str
    description: str
    type: str
    dependencies: Optional[List[str]] = None
    estimated_hours: float

class SprintPlan(BaseModel):
    """Sprint planning details"""
    sprint: int
    tasks: List[str]
    story_points: int

class InfrastructureConfig(BaseModel):
    """Infrastructure configuration"""
    compute: Dict[str, Any]
    storage: Dict[str, Any]
    ci_cd: Dict[str, Any]
    monitoring: List[str]
    security_measures: List[str]

class AgentExecution(BaseModel):
    """Agent execution record"""
    id: int
    task_id: int
    agent_type: str
    executed_at: datetime
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    execution_time: float
    success: bool
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    """Base task fields"""
    description: str
    user_story: Optional[str] = None
    context: Optional[str] = None

class TaskCreate(TaskBase):
    """Task creation fields"""
    pass

class TaskUpdate(BaseModel):
    """Task update fields"""
    description: Optional[str] = None
    user_story: Optional[str] = None
    context: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None

class Task(TaskBase):
    """Complete task model with analysis results"""
    id: int
    created_at: datetime
    updated_at: datetime
    status: str = "Open"
    
    # Task Analyzer results
    category: Optional[str] = None
    priority: Optional[str] = None
    
    # Product and UX analysis
    user_stories: Optional[List[UserStory]] = None
    ux_recommendations: Optional[List[UXRecommendation]] = None
    
    # Technical analysis
    database_design: Optional[List[DatabaseTable]] = None
    technical_tasks: Optional[List[TechnicalTask]] = None
    
    # Quality analysis
    test_strategy: Optional[Dict[str, Any]] = None
    security_analysis: Optional[Dict[str, Any]] = None
    
    # Operations planning
    timeline_estimate: Optional[Dict[str, Any]] = None
    infrastructure_plan: Optional[InfrastructureConfig] = None

    class Config:
        from_attributes = True

class TaskAnalysisResult(BaseModel):
    """Combined analysis results"""
    category: Optional[str] = None
    priority: Optional[str] = None
    user_stories: Optional[List[UserStory]] = None
    ux_recommendations: Optional[List[UXRecommendation]] = None
    database_design: Optional[List[DatabaseTable]] = None
    technical_tasks: Optional[List[TechnicalTask]] = None
    test_strategy: Optional[Dict[str, Any]] = None
    security_analysis: Optional[Dict[str, Any]] = None
    timeline_estimate: Optional[Dict[str, Any]] = None
    infrastructure_plan: Optional[InfrastructureConfig] = None
    error: Optional[str] = None

class AgentConfig(BaseModel):
    """Agent configuration"""
    id: int
    agent_type: str
    enabled: bool
    configuration: Dict[str, Any]
    updated_at: datetime

    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
