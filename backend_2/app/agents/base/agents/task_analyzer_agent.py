from typing import Optional
from crewai import Agent, Task, Crew
import json
import logging
from ..agent_base import AgentBase

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
            return {
                "category": None,
                "priority": None,
                "error": "LLM not configured or initialization failed"
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
            
            # Handle result parsing
            result_str = str(result)
            logger.info(f"Raw analysis result: {result_str}")
            
            # Extract JSON from the result
            json_start = result_str.find('{')
            json_end = result_str.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = result_str[json_start:json_end]
                try:
                    parsed_result = json.loads(json_str)
                    category = parsed_result.get("category")
                    priority = parsed_result.get("priority")
                    
                    return {
                        "category": category,
                        "priority": priority
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from result: {e}")
                    return {
                        "category": None,
                        "priority": None,
                        "error": f"JSON parsing error: {e}"
                    }
            else:
                logger.warning("No JSON object found in analysis result")
                return {
                    "category": None,
                    "priority": None,
                    "error": "No valid JSON found in analysis result"
                }
                
        except Exception as e:
            logger.error(f"Error during task analysis: {e}")
            return {
                "category": None,
                "priority": None,
                "error": f"Analysis error: {e}"
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
