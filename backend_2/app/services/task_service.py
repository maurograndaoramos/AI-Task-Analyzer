from typing import Dict, Any, Optional, List
import logging
import time
from datetime import datetime

from app.core.db import database, tasks, agent_executions
from app.agents import (
    TaskAnalyzerAgent,
    ProductAgents,
    TechnicalAgents,
    OperationsAgents,
    QualityAgents
)

logger = logging.getLogger(__name__)

class TaskAnalysisService:
    """
    Service for coordinating multi-agent task analysis and management.
    Orchestrates different specialized agents and manages their results.
    """
    
    def __init__(self):
        # Initialize all agents
        self.task_analyzer = TaskAnalyzerAgent()
        self.product_agents = ProductAgents()
        self.technical_agents = TechnicalAgents()
        self.operations_agents = OperationsAgents()
        self.quality_agents = QualityAgents()
        
        # Track agent availability
        self.ai_enabled = all([
            self.task_analyzer.has_valid_llm(),
            self.product_agents.has_valid_llm(),
            self.technical_agents.has_valid_llm(),
            self.operations_agents.has_valid_llm(),
            self.quality_agents.has_valid_llm()
        ])
        
        if not self.ai_enabled:
            logger.warning("One or more agents do not have valid LLM configuration")

    async def _log_agent_execution(
        self,
        task_id: int,
        agent_type: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        execution_time: float,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log agent execution details for tracking and analysis."""
        try:
            await database.execute(
                agent_executions.insert().values(
                    task_id=task_id,
                    agent_type=agent_type,
                    input_data=input_data,
                    output_data=output_data,
                    execution_time=execution_time,
                    success=success,
                    error_message=error_message
                )
            )
        except Exception as e:
            logger.error(f"Error logging agent execution: {e}")

    async def analyze_task(self, task_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive task analysis using all available agents.
        
        Args:
            task_details: Dictionary containing task information including:
                - description: Task description
                - user_story: Optional user story
                - context: Optional additional context
                
        Returns:
            Dictionary containing analysis results from all agents
        """
        if not self.ai_enabled:
            return {
                "error": "AI analysis not available - LLM configuration missing"
            }

        start_time = time.time()
        
        try:
            # Step 1: Initial task analysis
            category_priority = await self.task_analyzer.analyze_task(
                description=task_details["description"],
                user_story=task_details.get("user_story", ""),
                context=task_details.get("context", "")
            )
            
            # Step 2: User story generation and UX analysis
            stories_result = await self.product_agents.generate_user_stories(
                feature_description=task_details["description"],
                context=task_details.get("context", "")
            )
            
            if stories_result.get("user_stories"):
                ux_result = await self.product_agents.analyze_ux(
                    feature_description=task_details["description"],
                    user_stories=stories_result["user_stories"],
                    context=task_details.get("context", "")
                )
            else:
                ux_result = {"error": "Failed to generate user stories"}
            
            # Step 3: Technical analysis
            db_design = await self.technical_agents.design_database(
                user_stories=stories_result.get("user_stories", []),
                context=task_details.get("context", "")
            )
            
            tech_tasks = await self.technical_agents.break_down_tasks(
                feature_description=task_details["description"],
                user_stories=stories_result.get("user_stories", []),
                database_design=db_design,
                context=task_details.get("context", "")
            )
            
            # Step 4: Quality analysis
            test_strategy = await self.quality_agents.design_test_strategy(
                feature_description=task_details["description"],
                user_stories=stories_result.get("user_stories", []),
                technical_specs=tech_tasks,
                context=task_details.get("context", "")
            )
            
            security_analysis = await self.quality_agents.analyze_security(
                feature_description=task_details["description"],
                technical_specs=tech_tasks,
                context=task_details.get("context", "")
            )
            
            # Step 5: Operations planning
            timeline = await self.operations_agents.estimate_timeline(
                tasks=tech_tasks.get("tasks", [])
            )
            
            infrastructure = await self.operations_agents.plan_infrastructure(
                feature_description=task_details["description"],
                technical_requirements=tech_tasks,
                context=task_details.get("context", "")
            )
            
            # Prepare the complete analysis result
            analysis_result = {
                "category": category_priority.get("category"),
                "priority": category_priority.get("priority"),
                "user_stories": stories_result.get("user_stories"),
                "ux_recommendations": ux_result,
                "database_design": db_design,
                "technical_tasks": tech_tasks,
                "test_strategy": test_strategy,
                "security_analysis": security_analysis,
                "timeline_estimate": timeline,
                "infrastructure_plan": infrastructure
            }
            
            # Create task record in database
            task_id = await database.execute(
                tasks.insert().values(
                    description=task_details["description"],
                    user_story=task_details.get("user_story"),
                    context=task_details.get("context"),
                    category=category_priority.get("category"),
                    priority=category_priority.get("priority"),
                    user_stories=stories_result.get("user_stories"),
                    ux_recommendations=ux_result,
                    database_design=db_design,
                    technical_tasks=tech_tasks,
                    test_strategy=test_strategy,
                    security_analysis=security_analysis,
                    timeline_estimate=timeline,
                    infrastructure_plan=infrastructure,
                    created_at=datetime.utcnow()
                )
            )
            
            # Log agent executions
            execution_time = time.time() - start_time
            await self._log_agent_execution(
                task_id=task_id,
                agent_type="comprehensive_analysis",
                input_data=task_details,
                output_data=analysis_result,
                execution_time=execution_time
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error during comprehensive task analysis: {e}")
            return {
                "error": f"Analysis failed: {str(e)}"
            }

    async def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a task and its analysis results by ID."""
        try:
            query = tasks.select().where(tasks.c.id == task_id)
            return await database.fetch_one(query)
        except Exception as e:
            logger.error(f"Error retrieving task {task_id}: {e}")
            return None

    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Retrieve all tasks and their analysis results."""
        try:
            query = tasks.select()
            return await database.fetch_all(query)
        except Exception as e:
            logger.error(f"Error retrieving tasks: {e}")
            return []

    async def update_task(self, task_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a task with new information or analysis results."""
        try:
            query = (
                tasks.update()
                .where(tasks.c.id == task_id)
                .values(**updates)
            )
            await database.execute(query)
            return await self.get_task(task_id)
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            return None

    async def get_agent_executions(self, task_id: int) -> List[Dict[str, Any]]:
        """Retrieve execution history for a specific task."""
        try:
            query = agent_executions.select().where(agent_executions.c.task_id == task_id)
            return await database.fetch_all(query)
        except Exception as e:
            logger.error(f"Error retrieving agent executions for task {task_id}: {e}")
            return []
