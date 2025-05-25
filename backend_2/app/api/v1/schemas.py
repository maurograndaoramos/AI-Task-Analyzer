from typing import Optional, List, Dict, Any, Union # Add Union
from pydantic import BaseModel, Field
from datetime import datetime

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None

ErrorSchema = ErrorResponse # Alias for use in other schemas and for import

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
    indexes: Optional[List[str]] = None # Reverted to list of strings

# class DatabaseIndex(BaseModel): # Removing this model
#     """Database index definition"""
#     name: str
#     columns: List[str]
#     unique: Optional[bool] = False
#     description: Optional[str] = None

# No need to re-declare DatabaseTable as the original declaration will now be correct.

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
    # These were the original fields, now likely nested or different
    # compute: Dict[str, Any]
    # storage: Dict[str, Any]
    # ci_cd: Dict[str, Any]
    # monitoring: List[str]
    # security_measures: List[str]

    # Based on LLM output, it seems to be a nested structure.
    # Let's define it to accept the common structure seen in logs.
    # The LLM output for infrastructure_plan was:
    # {
    #   "infrastructure": { "compute": ..., "storage": ..., "network": ... },
    #   "ci_cd": { ... },
    #   "monitoring": { "application": ..., "database": ... },
    #   "security_measures": { "web_application_firewall": ..., ... }
    # }
    # The Task schema expects InfrastructureConfig directly for infrastructure_plan.
    # So, InfrastructureConfig should model this entire structure.

    infrastructure: Optional[Dict[str, Any]] = None # For compute, storage, network
    ci_cd: Optional[Dict[str, Any]] = None
    monitoring: Optional[Dict[str, Any]] = None # Was List[str], now Dict
    security_measures: Optional[Dict[str, Any]] = None # Was List[str], now Dict


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
    user_stories: Optional[Union[List[UserStory], ErrorSchema]] = None
    ux_recommendations: Optional[Union[List[UXRecommendation], ErrorSchema]] = None
    
    # Technical analysis
    database_design: Optional[Union[List[DatabaseTable], ErrorSchema]] = None
    technical_tasks: Optional[Union[List[TechnicalTask], ErrorSchema]] = None
    
    # Quality analysis
    test_strategy: Optional[Union[Dict[str, Any], ErrorSchema]] = None
    security_analysis: Optional[Union[Dict[str, Any], ErrorSchema]] = None
    
    # Operations planning
    timeline_estimate: Optional[Union[Dict[str, Any], ErrorSchema]] = None
    infrastructure_plan: Optional[Union[InfrastructureConfig, ErrorSchema]] = None

    class Config:
        from_attributes = True

class TaskAnalysisResult(BaseModel):
    """Combined analysis results"""
    category: Optional[str] = None
    priority: Optional[str] = None
    user_stories: Optional[Union[List[UserStory], ErrorSchema]] = None
    ux_recommendations: Optional[Union[List[UXRecommendation], ErrorSchema]] = None
    database_design: Optional[Union[List[DatabaseTable], ErrorSchema]] = None
    technical_tasks: Optional[Union[List[TechnicalTask], ErrorSchema]] = None
    test_strategy: Optional[Union[Dict[str, Any], ErrorSchema]] = None
    security_analysis: Optional[Union[Dict[str, Any], ErrorSchema]] = None
    timeline_estimate: Optional[Union[Dict[str, Any], ErrorSchema]] = None
    infrastructure_plan: Optional[Union[InfrastructureConfig, ErrorSchema]] = None
    error: Optional[str] = None # This field might become redundant if errors are per-analysis-item

class AgentConfig(BaseModel):
    """Agent configuration"""
    id: int
    agent_type: str
    enabled: bool
    configuration: Dict[str, Any]
    updated_at: datetime

    class Config:
        from_attributes = True
