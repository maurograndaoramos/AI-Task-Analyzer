from typing import Optional, Dict, Any, List, Union # Added Union
from crewai import Agent, Task, Crew
import json
import logging
from ..agent_base import AgentBase
from ....utils.json_parser import robust_json_parser # Import the new parser
from ....api.v1.schemas import ErrorSchema # Import ErrorSchema for typing and structure

logger = logging.getLogger(__name__)

class OperationsAgents(AgentBase):
    """Operations agents for project planning and DevOps tasks."""

    def make_project_manager(self) -> Agent:
        """
        Create a project manager agent focused on time estimation and planning.
        
        Returns:
            Agent: Configured project manager agent instance
        """
        return self.create_agent(
            role="Project Manager",
            goal="Estimate time for tasks and create project timelines considering team velocity. "
                 "Focus on realistic scheduling and resource allocation.",
            backstory="You are a skilled project manager with expertise in Agile methodologies. "
                     "You excel at estimating task complexity and duration based on team capabilities. "
                     "Your focus is on creating realistic timelines while identifying potential risks "
                     "and dependencies early in the planning process."
        )

    def make_devops_specialist(self) -> Agent:
        """
        Create a DevOps specialist agent focused on infrastructure and deployment.
        
        Returns:
            Agent: Configured DevOps specialist agent instance
        """
        return self.create_agent(
            role="DevOps Specialist",
            goal="Evaluate infrastructure requirements and design CI/CD pipelines. "
                 "Focus on automation, scalability, and operational efficiency.",
            backstory="You are an experienced DevOps engineer with expertise in cloud infrastructure "
                     "and deployment automation. You excel at designing scalable infrastructure and "
                     "implementing efficient CI/CD pipelines. You always consider security, "
                     "monitoring, and maintainability in your solutions."
        )

    async def estimate_timeline(self, tasks: List[Dict], team_velocity: Dict = None,
                            context: str = "") -> dict:
        """
        Estimate project timeline based on tasks using the project manager agent.
        
        Args:
            tasks (List[Dict]): Technical tasks to estimate
            team_velocity (Dict, optional): Information about team's velocity and capacity
            context (str, optional): Additional context about the project
            
        Returns:
            dict: Timeline estimates and scheduling recommendations
        """
        if not self.has_valid_llm():
            logger.warning("Project manager agent has no valid LLM configuration")
            return ErrorSchema(
                error="LLM Error",
                message="LLM not configured or initialization failed for Project Manager Agent.",
                agent_type="project_manager"
            ).model_dump(exclude_none=True)

        pm = self.make_project_manager()
        
        if team_velocity is None:
            team_velocity = {
                "sprint_length_weeks": 2,
                "avg_velocity_points": 30,
                "team_size": 5,
                "avg_hours_per_point": 4
            }
        
        estimation_task = Task(
            description=f"Estimate timeline for these tasks considering team velocity:\n"
                      f"Tasks: {json.dumps(tasks, indent=2)}\n"
                      f"Team Velocity: {json.dumps(team_velocity, indent=2)}\n"
                      f"Context: {context}\n"
                      f"Create a JSON object with timeline estimates and recommendations.",
            agent=pm,
            expected_output='A JSON object containing timeline estimates. Example:\n'
                          '{\n'
                          '  "timeline": {\n'
                          '    "total_weeks": 6,\n'
                          '    "total_story_points": 90,\n'
                          '    "sprints": [\n'
                          '      {\n'
                          '        "sprint": 1,\n'
                          '        "tasks": ["BE-1", "BE-2"],\n'
                          '        "story_points": 30\n'
                          '      }\n'
                          '    ]\n'
                          '  },\n'
                          '  "risks": ["Dependencies might delay delivery"],\n'
                          '  "recommendations": ["Consider parallel development"]\n'
                          '}'
        )

        crew = Crew(
            agents=[pm],
            tasks=[estimation_task],
            verbose=0
        )

        try:
            logger.info("Estimating project timeline...")
            result = crew.kickoff()
            
            parsed_json = robust_json_parser(str(result), context="Timeline Estimation")
            if parsed_json:
                # Basic validation: check if 'timeline' key exists (as per example output)
                if "timeline" in parsed_json and isinstance(parsed_json["timeline"], dict):
                    return parsed_json
                else:
                    logger.warning(f"Parsed JSON for timeline estimation is missing 'timeline' dict. Output: {str(result)[:500]}")
                    return ErrorSchema(
                        error="Invalid JSON Structure",
                        message="Parsed JSON for timeline estimation is missing 'timeline' dict or has incorrect type.",
                        agent_type="project_manager",
                        raw_output=str(result)
                    ).model_dump(exclude_none=True)
            else:
                logger.error(f"Failed to parse JSON from timeline estimation. Raw output: {str(result)[:500]}")
                return ErrorSchema(
                    error="JSON Parsing Error",
                    message="Failed to parse JSON output from Project Manager Agent.",
                    agent_type="project_manager",
                    raw_output=str(result)
                ).model_dump(exclude_none=True)
                
        except Exception as e:
            logger.error(f"Error during timeline estimation: {e}", exc_info=True)
            return ErrorSchema(
                error="Agent Execution Error",
                message=f"An unexpected error occurred during timeline estimation: {str(e)}",
                agent_type="project_manager"
            ).model_dump(exclude_none=True)

    async def plan_infrastructure(self, feature_description: str, technical_requirements: Dict,
                              scale_requirements: Dict = None, context: str = "") -> Union[dict, ErrorSchema]:
        """
        Plan infrastructure and CI/CD requirements using the DevOps specialist agent.
        
        Args:
            feature_description (str): Description of the feature to implement
            technical_requirements (Dict): Technical specifications and requirements
            scale_requirements (Dict, optional): Scaling and performance requirements
            context (str, optional): Additional context about the project
            
        Returns:
            dict: Infrastructure plan and CI/CD pipeline design
        """
        if not self.has_valid_llm():
            logger.warning("DevOps specialist agent has no valid LLM configuration")
            return ErrorSchema(
                error="LLM Error",
                message="LLM not configured or initialization failed for DevOps Specialist Agent.",
                agent_type="devops_specialist"
            ).model_dump(exclude_none=True)

        devops = self.make_devops_specialist()
        
        if scale_requirements is None:
            scale_requirements = {
                "expected_users": 1000,
                "peak_concurrent": 100,
                "data_storage_gb": 50,
                "availability_target": 0.99
            }
        
        planning_task = Task(
            description=f"Design infrastructure and CI/CD pipeline for this feature:\n"
                      f"Feature: {feature_description}\n"
                      f"Technical Requirements: {json.dumps(technical_requirements, indent=2)}\n"
                      f"Scale Requirements: {json.dumps(scale_requirements, indent=2)}\n"
                      f"Context: {context}\n"
                      f"Create a JSON object with infrastructure and pipeline design.",
            agent=devops,
            expected_output='A JSON object containing infrastructure plan. Example:\n'
                          '{\n'
                          '  "infrastructure": {\n'
                          '    "compute": {\n'
                          '      "type": "kubernetes",\n'
                          '      "sizing": {\n'
                          '        "initial_nodes": 2,\n'
                          '        "autoscaling": {"min": 2, "max": 5}\n'
                          '      }\n'
                          '    },\n'
                          '    "storage": {\n'
                          '      "type": "managed_sql",\n'
                          '      "backup_strategy": "daily"\n'
                          '    }\n'
                          '  },\n'
                          '  "ci_cd": {\n'
                          '    "pipeline_stages": ["build", "test", "deploy"],\n'
                          '    "deployment_strategy": "blue-green"\n'
                          '  },\n'
                          '  "monitoring": ["cpu_usage", "error_rates"],\n'
                          '  "security_measures": ["waf", "ssl_termination"]\n'
                          '}'
        )

        crew = Crew(
            agents=[devops],
            tasks=[planning_task],
            verbose=0
        )

        try:
            logger.info(f"Planning infrastructure for: {feature_description[:50]}...")
            result = crew.kickoff()
            
            parsed_json = robust_json_parser(str(result), context="Infrastructure Plan")
            if parsed_json:
                # Check for successful structure AND absence of an 'error' key from LLM
                # The original check was quite specific; let's simplify to ensure the main 'infrastructure' key is present
                # and it's a dictionary, and no 'error' key from LLM.
                # The Pydantic model `InfrastructureConfig` will do the finer-grained validation later.
                if ("infrastructure" in parsed_json and 
                    isinstance(parsed_json["infrastructure"], dict) and
                    "error" not in parsed_json): # Check for LLM-generated error field
                    # Further check for essential sub-keys based on InfrastructureConfig and example
                    if (all(k in parsed_json for k in ["ci_cd", "monitoring", "security_measures"]) and
                        all(k in parsed_json["infrastructure"] for k in ["compute", "storage"])):
                        return parsed_json # This is the successful data
                    else:
                        logger.warning(f"Parsed JSON for infrastructure plan is missing some expected sub-keys. Output: {str(result)[:500]}")
                        return ErrorSchema(
                            error="Invalid JSON Structure",
                            message="Parsed JSON for infrastructure plan is missing some expected sub-keys (e.g., infrastructure.compute, ci_cd).",
                            agent_type="devops_specialist",
                            raw_output=str(result)
                        ).model_dump(exclude_none=True)
                else:
                    logger.warning(f"Parsed JSON for infrastructure plan is invalid or contains an error field. Output: {str(result)[:500]}")
                    return ErrorSchema(
                        error="Invalid JSON Structure or LLM Error",
                        message="Parsed JSON for infrastructure plan is missing 'infrastructure' dict, has incorrect type, or contains an error indicator from the LLM.",
                        agent_type="devops_specialist",
                        raw_output=str(result)
                    ).model_dump(exclude_none=True)
            else:
                # robust_json_parser failed
                logger.error(f"Failed to parse JSON from infrastructure plan. Raw output: {str(result)[:500]}")
                return ErrorSchema(
                    error="JSON Parsing Error",
                    message="Failed to parse JSON output from DevOps Specialist Agent.",
                    agent_type="devops_specialist",
                    raw_output=str(result)
                ).model_dump(exclude_none=True)
                
        except Exception as e:
            logger.error(f"Error during infrastructure planning: {e}", exc_info=True)
            return ErrorSchema(
                error="Agent Execution Error",
                message=f"An unexpected error occurred during infrastructure planning: {str(e)}",
                agent_type="devops_specialist"
            ).model_dump(exclude_none=True)

if __name__ == "__main__":
    import asyncio
    
    async def test_operations_agents():
        agents = OperationsAgents()
        
        if not agents.has_valid_llm():
            print("Error: LLM not configured. Please set GEMINI_API_KEY in environment.")
            return
            
        # Test data for timeline estimation
        tasks = [
            {
                "id": "BE-1",
                "title": "Implement user preferences model",
                "type": "backend",
                "estimated_hours": 8
            },
            {
                "id": "BE-2",
                "title": "Create API endpoints",
                "type": "backend",
                "estimated_hours": 12
            }
        ]
        
        # Test timeline estimation
        timeline = await agents.estimate_timeline(tasks)
        print("\nTimeline Estimation Result:")
        print(json.dumps(timeline, indent=2))
        
        # Test infrastructure planning
        if not timeline.get("error"):
            tech_requirements = {
                "backend": "Python/FastAPI",
                "database": "PostgreSQL",
                "authentication": "JWT"
            }
            
            infra_plan = await agents.plan_infrastructure(
                feature_description="User preferences system with authentication",
                technical_requirements=tech_requirements
            )
            print("\nInfrastructure Planning Result:")
            print(json.dumps(infra_plan, indent=2))
            
    # Run the test
    asyncio.run(test_operations_agents())
