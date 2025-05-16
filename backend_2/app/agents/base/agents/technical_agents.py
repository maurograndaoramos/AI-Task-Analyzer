from typing import Optional, Dict, Any, List
from crewai import Agent, Task, Crew
import json
import logging
from ..agent_base import AgentBase

logger = logging.getLogger(__name__)

class TechnicalAgents(AgentBase):
    """Technical agents for architecture and implementation planning."""

    def make_db_architect(self) -> Agent:
        """
        Create a database architect agent for schema design.
        
        Returns:
            Agent: Configured database architect agent instance
        """
        return self.create_agent(
            role="Database Architect",
            goal="Design scalable and efficient database schemas based on user stories and requirements. "
                 "Focus on data relationships, indexing strategies, and performance considerations.",
            backstory="You are an expert database architect with extensive experience in designing "
                     "scalable database schemas for modern web applications. You excel at understanding "
                     "complex data relationships and optimizing for both performance and maintainability. "
                     "You consider factors like data integrity, scalability, and query optimization in "
                     "your designs."
        )

    def make_tech_lead(self) -> Agent:
        """
        Create a tech lead agent for technical planning and task breakdown.
        
        Returns:
            Agent: Configured tech lead agent instance
        """
        return self.create_agent(
            role="Tech Lead",
            goal="Break down features into detailed technical tasks and plan implementation approach. "
                 "Consider architecture implications, technical debt, and best practices.",
            backstory="You are a seasoned full-stack developer and software architect with years of "
                     "experience leading development teams. You excel at breaking down complex features "
                     "into manageable tasks while ensuring architectural consistency and code quality. "
                     "You always consider scalability, maintainability, and testing in your planning."
        )

    def make_code_reviewer(self) -> Agent:
        """
        Create a code reviewer agent for code quality analysis.
        
        Returns:
            Agent: Configured code reviewer agent instance
        """
        return self.create_agent(
            role="Code Reviewer",
            goal="Analyze code quality, suggest improvements, and ensure adherence to best practices. "
                 "Focus on code organization, patterns, and potential issues.",
            backstory="You are a senior developer with expertise in code quality and software design "
                     "patterns. You have extensive experience reviewing code across various languages "
                     "and frameworks. You focus on maintainability, readability, and adherence to "
                     "best practices while being pragmatic about real-world constraints."
        )

    async def design_database(self, user_stories: List[Dict], context: str = "") -> dict:
        """
        Design database schema based on user stories using the DB architect agent.
        
        Args:
            user_stories (List[Dict]): List of user stories to base the schema on
            context (str, optional): Additional context about the project
            
        Returns:
            dict: Database design recommendations and schema
        """
        if not self.has_valid_llm():
            logger.warning("DB architect agent has no valid LLM configuration")
            return {
                "tables": [],
                "error": "LLM not configured or initialization failed"
            }

        architect = self.make_db_architect()
        
        design_task = Task(
            description=f"Design a database schema based on these user stories:\n"
                      f"{json.dumps(user_stories, indent=2)}\n"
                      f"Context: {context}\n"
                      f"Create a JSON object defining the database schema, including tables, "
                      f"fields, relationships, and indexing recommendations.",
            agent=architect,
            expected_output='A JSON object containing database design. Example:\n'
                          '{\n'
                          '  "tables": [\n'
                          '    {\n'
                          '      "name": "users",\n'
                          '      "fields": [\n'
                          '        {"name": "id", "type": "uuid", "primary_key": true},\n'
                          '        {"name": "email", "type": "varchar", "indexed": true}\n'
                          '      ],\n'
                          '      "relationships": [\n'
                          '        {"table": "profiles", "type": "one_to_one"}\n'
                          '      ],\n'
                          '      "indexes": ["email"]\n'
                          '    }\n'
                          '  ],\n'
                          '  "recommendations": ["Add composite index for search performance"]\n'
                          '}'
        )

        crew = Crew(
            agents=[architect],
            tasks=[design_task],
            verbose=0
        )

        try:
            logger.info("Designing database schema...")
            result = crew.kickoff()
            
            result_str = str(result)
            json_start = result_str.find('{')
            json_end = result_str.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                try:
                    return json.loads(result_str[json_start:json_end])
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from schema design: {e}")
                    return {
                        "tables": [],
                        "error": f"JSON parsing error: {e}"
                    }
            else:
                return {
                    "tables": [],
                    "error": "No valid JSON found in design result"
                }
                
        except Exception as e:
            logger.error(f"Error during schema design: {e}")
            return {
                "tables": [],
                "error": f"Design error: {e}"
            }

    async def break_down_tasks(self, feature_description: str, user_stories: List[Dict], 
                             database_design: Dict, context: str = "") -> dict:
        """
        Break down implementation into technical tasks using the tech lead agent.
        
        Args:
            feature_description (str): Description of the feature
            user_stories (List[Dict]): User stories to implement
            database_design (Dict): Database schema design
            context (str, optional): Additional context
            
        Returns:
            dict: Technical tasks and implementation plan
        """
        if not self.has_valid_llm():
            logger.warning("Tech lead agent has no valid LLM configuration")
            return {
                "tasks": [],
                "error": "LLM not configured or initialization failed"
            }

        tech_lead = self.make_tech_lead()
        
        planning_task = Task(
            description=f"Break down this feature into technical tasks:\n"
                      f"Feature: {feature_description}\n"
                      f"User Stories: {json.dumps(user_stories, indent=2)}\n"
                      f"Database Design: {json.dumps(database_design, indent=2)}\n"
                      f"Context: {context}\n"
                      f"Create a JSON object with implementation tasks and technical considerations.",
            agent=tech_lead,
            expected_output='A JSON object containing tasks breakdown. Example:\n'
                          '{\n'
                          '  "tasks": [\n'
                          '    {\n'
                          '      "id": "BE-1",\n'
                          '      "title": "Implement user model",\n'
                          '      "description": "Create user model with fields...",\n'
                          '      "type": "backend",\n'
                          '      "dependencies": [],\n'
                          '      "estimated_hours": 4\n'
                          '    }\n'
                          '  ],\n'
                          '  "technical_considerations": ["API versioning needed"],\n'
                          '  "architectural_decisions": ["Use repository pattern"]\n'
                          '}'
        )

        crew = Crew(
            agents=[tech_lead],
            tasks=[planning_task],
            verbose=0
        )

        try:
            logger.info(f"Breaking down tasks for: {feature_description[:50]}...")
            result = crew.kickoff()
            
            result_str = str(result)
            json_start = result_str.find('{')
            json_end = result_str.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                try:
                    return json.loads(result_str[json_start:json_end])
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from task breakdown: {e}")
                    return {
                        "tasks": [],
                        "error": f"JSON parsing error: {e}"
                    }
            else:
                return {
                    "tasks": [],
                    "error": "No valid JSON found in breakdown result"
                }
                
        except Exception as e:
            logger.error(f"Error during task breakdown: {e}")
            return {
                "tasks": [],
                "error": f"Breakdown error: {e}"
            }

    async def review_implementation(self, tasks: List[Dict], code_snippets: List[Dict]) -> dict:
        """
        Review implementation plan and code snippets using the code reviewer agent.
        
        Args:
            tasks (List[Dict]): Technical tasks to review
            code_snippets (List[Dict]): Code snippets to analyze
            
        Returns:
            dict: Code review feedback and recommendations
        """
        if not self.has_valid_llm():
            logger.warning("Code reviewer agent has no valid LLM configuration")
            return {
                "feedback": [],
                "error": "LLM not configured or initialization failed"
            }

        reviewer = self.make_code_reviewer()
        
        review_task = Task(
            description=f"Review these implementation tasks and code snippets:\n"
                      f"Tasks: {json.dumps(tasks, indent=2)}\n"
                      f"Code Snippets: {json.dumps(code_snippets, indent=2)}\n"
                      f"Provide a JSON object with code review feedback and recommendations.",
            agent=reviewer,
            expected_output='A JSON object containing review feedback. Example:\n'
                          '{\n'
                          '  "feedback": [\n'
                          '    {\n'
                          '      "file": "user_model.py",\n'
                          '      "line": 23,\n'
                          '      "type": "suggestion",\n'
                          '      "message": "Consider adding input validation"\n'
                          '    }\n'
                          '  ],\n'
                          '  "best_practices": ["Add error handling"],\n'
                          '  "security_considerations": ["Sanitize user input"]\n'
                          '}'
        )

        crew = Crew(
            agents=[reviewer],
            tasks=[review_task],
            verbose=0
        )

        try:
            logger.info("Reviewing implementation plan...")
            result = crew.kickoff()
            
            result_str = str(result)
            json_start = result_str.find('{')
            json_end = result_str.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                try:
                    return json.loads(result_str[json_start:json_end])
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from code review: {e}")
                    return {
                        "feedback": [],
                        "error": f"JSON parsing error: {e}"
                    }
            else:
                return {
                    "feedback": [],
                    "error": "No valid JSON found in review result"
                }
                
        except Exception as e:
            logger.error(f"Error during code review: {e}")
            return {
                "feedback": [],
                "error": f"Review error: {e}"
            }

if __name__ == "__main__":
    import asyncio
    
    async def test_technical_agents():
        agents = TechnicalAgents()
        
        if not agents.has_valid_llm():
            print("Error: LLM not configured. Please set GEMINI_API_KEY in environment.")
            return
            
        # Test data
        user_stories = [
            {
                "role": "user",
                "goal": "store my preferences",
                "benefit": "customize my experience",
                "acceptance_criteria": [
                    "Save theme preference",
                    "Persist settings across sessions"
                ]
            }
        ]
        
        # Test database design
        db_design = await agents.design_database(user_stories)
        print("\nDatabase Design Result:")
        print(json.dumps(db_design, indent=2))
        
        if "tables" in db_design and not db_design.get("error"):
            # Test task breakdown
            tasks = await agents.break_down_tasks(
                feature_description="Implement user preferences storage",
                user_stories=user_stories,
                database_design=db_design
            )
            print("\nTask Breakdown Result:")
            print(json.dumps(tasks, indent=2))
            
            if "tasks" in tasks and not tasks.get("error"):
                # Test code review
                code_snippets = [
                    {
                        "file": "models/user_preferences.py",
                        "code": "class UserPreferences:\n    def __init__(self, theme='light'):\n        self.theme = theme"
                    }
                ]
                review = await agents.review_implementation(tasks["tasks"], code_snippets)
                print("\nCode Review Result:")
                print(json.dumps(review, indent=2))
            
    # Run the test
    asyncio.run(test_technical_agents())
