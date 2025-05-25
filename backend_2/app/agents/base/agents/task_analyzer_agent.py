from typing import Optional, Dict, Union # Added Dict, Union
from crewai import Agent, Task, Crew
import json
import logging
from ..agent_base import AgentBase
from ....utils.json_parser import robust_json_parser # Import the new parser
from ....api.v1.schemas import ErrorSchema # Import ErrorSchema for typing and structure

logger = logging.getLogger(__name__)

class TaskAnalyzerAgent(AgentBase):
    """Agent responsible for analyzing tasks and determining their category and priority."""

    def make_agent(self) -> Agent:
        """
        Create a task analyzer agent with specific role configuration.
        
        Returns:
            Agent: Configured task analyzer agent instance
        """
        return self.create_agent(
            role="Task Analyzer Agent",
            goal="Analyze a given task description (and optional user story/context) to determine its category and priority. "
                 "You MUST ONLY output a single, valid JSON string with two keys: 'category' and 'priority'. "
                 "The 'category' MUST be one of: Bug Fix, Feature Request, Documentation, Research, Testing, Chore. "
                 "The 'priority' MUST be one of: High, Medium, Low.",
            backstory="You are an expert project management assistant. Your strength lies in quickly "
                     "understanding the nature of a software development task and assigning it an "
                     "appropriate category and priority based on its description, user story, and any "
                     "provided context. You aim for consistency and clarity. "
                     "Predefined categories are: Bug Fix, Feature Request, Documentation, Research, Testing, Chore. "
                     "Predefined priorities are: High, Medium, Low."
        )

    async def analyze_task(self, description: str, user_story: str = "", context: str = "") -> dict:
        """
        Analyze a task using the task analyzer agent.
        
        Args:
            description (str): The task description to analyze
            user_story (str, optional): Related user story for context
            context (str, optional): Additional context about the task
            
        Returns:
            dict: Analysis result with 'category' and 'priority' keys, plus optional 'error' key
        """
        if not self.has_valid_llm():
            logger.warning("Task analyzer agent has no valid LLM configuration")
            # For this agent, the return type in TaskService is directly Dict[str, Optional[str]]
            # So, we return a dict that includes an error key, rather than a full ErrorSchema object
            # to align with how its output is currently consumed.
            # Alternatively, TaskService could be updated to expect Union[Dict, ErrorSchema]
            return {
                "category": None,
                "priority": None,
                "error": "LLM Error: LLM not configured or initialization failed for Task Analyzer Agent."
            }

        analyzer = self.make_agent()
        
        analysis_task = Task(
            description=f"Analyze the following task details and determine its category and priority. "
                      f"Description: '{description}'. "
                      f"User Story: '{user_story}'. "
                      f"Context: '{context}'. "
                      f"Return the category and priority as a JSON string with 'category' and 'priority' keys.",
            agent=analyzer,
            expected_output="A JSON string containing the 'category' and 'priority'. For example: "
                          '"{ \\"category\\": \\"Bug Fix\\", \\"priority\\": \\"High\\" }"'
        )

        crew = Crew(
            agents=[analyzer],
            tasks=[analysis_task],
            verbose=0
        )

        try:
            logger.info(f"Analyzing task: {description[:50]}...")
            result = crew.kickoff()
            
            parsed_json = robust_json_parser(str(result), context="Task Analysis (Category/Priority)")
            
            if parsed_json:
                category = parsed_json.get("category")
                priority = parsed_json.get("priority")
                llm_error = parsed_json.get("error") # Check if LLM included an error field

                if llm_error: # If LLM itself reported an error in its JSON
                    logger.warning(f"LLM reported an error in its JSON for task analysis: {llm_error}. Output: {str(result)[:500]}")
                    return {
                        "category": None,
                        "priority": None,
                        "error": f"LLM Error in JSON: {llm_error}"
                    }
                
                # Basic validation for expected keys
                if category is not None and priority is not None:
                    return {
                        "category": category,
                        "priority": priority,
                        "error": None # Explicitly set error to None on success
                    }
                else: # Keys missing, structure is invalid
                    logger.warning(f"Parsed JSON for task analysis is missing 'category' or 'priority'. Output: {str(result)[:500]}")
                    return {
                        "category": None,
                        "priority": None,
                        "error": "Invalid JSON Structure: Parsed JSON for task analysis is missing 'category' or 'priority'."
                    }
            else: # robust_json_parser failed
                logger.error(f"Failed to parse JSON from task analysis. Raw output: {str(result)[:500]}")
                return {
                    "category": None,
                    "priority": None,
                    "error": "JSON Parsing Error: Failed to parse JSON output from Task Analyzer Agent."
                }
                
        except Exception as e:
            logger.error(f"Error during task analysis: {e}", exc_info=True)
            return {
                "category": None,
                "priority": None,
                "error": f"Agent Execution Error: An unexpected error occurred during task analysis: {str(e)}"
            }


if __name__ == "__main__":
    import asyncio
    
    async def test_analyzer():
        analyzer = TaskAnalyzerAgent()
        
        if not analyzer.has_valid_llm():
            print("Error: LLM not configured. Please set GEMINI_API_KEY in environment.")
            return
            
        test_task = {
            "description": "The login button is not responding on the main page after recent deployment",
            "user_story": "As a user, I want to be able to log in to access my account",
            "context": "This is affecting all users trying to access the platform"
        }
        
        result = await analyzer.analyze_task(
            description=test_task["description"],
            user_story=test_task["user_story"],
            context=test_task["context"]
        )
        
        print("\nAnalysis Result:")
        print(f"Category: {result.get('category')}")
        print(f"Priority: {result.get('priority')}")
        if result.get('error'):
            print(f"Error: {result.get('error')}")
            
    # Run the test
    asyncio.run(test_analyzer())
