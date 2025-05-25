from typing import Dict, Any, Optional, List, Union # Added Union
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
from app.api.v1.schemas import ErrorSchema # Import ErrorSchema

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
            # Initialize results with potential ErrorSchema placeholders
            analysis_result: Dict[str, Any] = {
                "category": None, "priority": None, "user_stories": None,
                "ux_recommendations": None, "database_design": None,
                "technical_tasks": None, "test_strategy": None,
                "security_analysis": None, "timeline_estimate": None,
                "infrastructure_plan": None
            }

            # Helper to check for error in agent output
            def is_error_output(output: Union[Dict, ErrorSchema]) -> bool:
                if isinstance(output, ErrorSchema):
                    return True
                if isinstance(output, dict) and "error" in output and output["error"] is not None:
                    return True
                return False

            # Step 1: Initial task analysis
            category_priority_raw = await self.task_analyzer.analyze_task(
                description=task_details["description"],
                user_story=task_details.get("user_story", ""),
                context=task_details.get("context", "")
            )
            if is_error_output(category_priority_raw):
                logger.warning(f"Task Analyzer Agent failed: {category_priority_raw.get('error')}")
                # Store the error message or a generic one if the structure is unexpected
                analysis_result["category"] = "Error"
                analysis_result["priority"] = "Error"
                # Optionally, store the detailed error in a separate field or log it
            else:
                analysis_result["category"] = category_priority_raw.get("category")
                analysis_result["priority"] = category_priority_raw.get("priority")

            # Step 2: User story generation and UX analysis
            stories_result_raw = await self.product_agents.generate_user_stories(
                feature_description=task_details["description"],
                context=task_details.get("context", "")
            )
            
            current_user_stories = None # For dependent agents
            if is_error_output(stories_result_raw):
                analysis_result["user_stories"] = stories_result_raw # Assign ErrorSchema dict
                analysis_result["ux_recommendations"] = ErrorSchema( # UX depends on stories
                    error="Dependency Error",
                    message="UX analysis skipped due to failure in user story generation.",
                    agent_type="ux_designer"
                ).model_dump(exclude_none=True)
            else:
                analysis_result["user_stories"] = stories_result_raw.get("user_stories") # Extract list for Task schema
                current_user_stories = stories_result_raw.get("user_stories", [])
                
                # Proceed with UX analysis only if user stories were successful
                ux_result_raw = await self.product_agents.analyze_ux(
                    feature_description=task_details["description"],
                    user_stories=current_user_stories, # Pass successful stories
                    context=task_details.get("context", "")
                )
                if is_error_output(ux_result_raw):
                    analysis_result["ux_recommendations"] = ux_result_raw # Assign ErrorSchema dict
                else:
                    analysis_result["ux_recommendations"] = ux_result_raw.get("recommendations") # Extract list for Task schema

            # Step 3: Technical analysis
            db_design_raw = await self.technical_agents.design_database(
                user_stories=current_user_stories if current_user_stories else [], 
                context=task_details.get("context", "")
            )
            
            current_db_design = None # For dependent agents
            if is_error_output(db_design_raw):
                analysis_result["database_design"] = db_design_raw # Assign ErrorSchema dict
            else:
                analysis_result["database_design"] = db_design_raw.get("tables") # Extract list for Task schema
                current_db_design = db_design_raw # Store full dict for dependent agents
            
            tech_tasks_raw = await self.technical_agents.break_down_tasks(
                feature_description=task_details["description"],
                user_stories=current_user_stories if current_user_stories else [],
                database_design=current_db_design if current_db_design else {}, 
                context=task_details.get("context", "")
            )

            current_tech_tasks_list = None # For dependent agents (e.g., timeline)
            current_tech_tasks_dict = None # For dependent agents (e.g., quality, ops)
            if is_error_output(tech_tasks_raw):
                analysis_result["technical_tasks"] = tech_tasks_raw # Assign ErrorSchema dict
            else:
                analysis_result["technical_tasks"] = tech_tasks_raw.get("tasks") # Extract list for Task schema
                current_tech_tasks_list = tech_tasks_raw.get("tasks", [])
                current_tech_tasks_dict = tech_tasks_raw # Store full dict for dependent agents


            # Step 4: Quality analysis
            test_strategy_raw = await self.quality_agents.design_test_strategy(
                feature_description=task_details["description"],
                user_stories=current_user_stories if current_user_stories else [],
                technical_specs=current_tech_tasks_dict if current_tech_tasks_dict else {},
                context=task_details.get("context", "")
            )
            analysis_result["test_strategy"] = test_strategy_raw
            
            security_analysis_raw = await self.quality_agents.analyze_security(
                feature_description=task_details["description"],
                technical_specs=current_tech_tasks_dict if current_tech_tasks_dict else {},
                context=task_details.get("context", "")
            )
            analysis_result["security_analysis"] = security_analysis_raw
            
            # Step 5: Operations planning
            timeline_raw = await self.operations_agents.estimate_timeline(
                tasks=current_tech_tasks_list if current_tech_tasks_list else []
            )
            analysis_result["timeline_estimate"] = timeline_raw
            
            infrastructure_raw = await self.operations_agents.plan_infrastructure(
                feature_description=task_details["description"],
                technical_requirements=current_tech_tasks_dict if current_tech_tasks_dict else {},
                context=task_details.get("context", "")
            )
            analysis_result["infrastructure_plan"] = infrastructure_raw
            
            # Create task record in database
            # The Pydantic model `Task` in schemas.py now uses Union for these fields,
            # so it can accept ErrorSchema dicts or the actual data.
            task_id = await database.execute(
                tasks.insert().values(
                    description=task_details["description"],
                    user_story=task_details.get("user_story"),
                    context=task_details.get("context"),
                    status="Analyzed", # Or some other status indicating completion/partial completion
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    # Assign from analysis_result which now holds either data or ErrorSchema dicts
                    category=analysis_result["category"],
                    priority=analysis_result["priority"],
                    user_stories=analysis_result["user_stories"],
                    ux_recommendations=analysis_result["ux_recommendations"],
                    database_design=analysis_result["database_design"],
                    technical_tasks=analysis_result["technical_tasks"],
                    test_strategy=analysis_result["test_strategy"],
                    security_analysis=analysis_result["security_analysis"],
                    timeline_estimate=analysis_result["timeline_estimate"],
                    infrastructure_plan=analysis_result["infrastructure_plan"],
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
