from crewai import Task, Crew
from app.agents.task_analyzer_agent import TaskAnalyzerAgents
from app.api.v1.schemas import TaskCreate
import json
import os
import logging

logger = logging.getLogger(__name__)

class TaskAnalysisService:
    def __init__(self):
        # Check for GEMINI_API_KEY or GOOGLE_API_KEY as CrewAI might use either
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.ai_enabled = bool(self.gemini_api_key)
        if not self.ai_enabled:
            logger.warning("GEMINI_API_KEY (or GOOGLE_API_KEY) is not set. AI features will not work.")
            self.analyzer_agent = None
        else:
            logger.info("GEMINI_API_KEY (or GOOGLE_API_KEY) is set. Initializing TaskAnalyzerAgent.")
            self.analyzer_agent = TaskAnalyzerAgents().make_task_analyzer_agent()
            if self.analyzer_agent.llm is None:
                logger.error("Failed to initialize LLM for TaskAnalyzerAgent. AI features may not work.")
                self.ai_enabled = False # Disable AI if LLM failed to init

    async def analyze_task(self, task_details: TaskCreate) -> dict:
        if not self.ai_enabled or not self.analyzer_agent or not self.analyzer_agent.llm:
            logger.warning("AI features are disabled or agent/LLM not initialized. Skipping AI analysis.")
            return {"category": None, "priority": None, "error": "GEMINI_API_KEY not set or LLM initialization failed"}

        task_description = task_details.description
        user_story = task_details.user_story or ""
        context = task_details.context or ""

        analysis_task_definition = Task(
            description=f"Analyze the following task details and determine its category and priority. "
                        f"Description: '{task_description}'. "
                        f"User Story: '{user_story}'. "
                        f"Context: '{context}'. "
                        f"Return the category and priority as a JSON string with 'category' and 'priority' keys.",
            agent=self.analyzer_agent,
            expected_output="A JSON string containing the 'category' and 'priority'. For example: "
                            '"{ \\"category\\": \\"Bug Fix\\", \\"priority\\": \\"High\\" }"'
        )

        crew = Crew(
            agents=[self.analyzer_agent],
            tasks=[analysis_task_definition],
            verbose=0
        )

        try:
            logger.info(f"Analyzing task: {task_description[:50]}...")
            crew_output_obj = crew.kickoff() # This is a CrewOutput object
            logger.info(f"AI Analysis raw CrewOutput object: {crew_output_obj}")

            # Convert CrewOutput object to string for parsing.
            # The string representation of CrewOutput is expected to be the agent's final text answer.
            ai_result_str = str(crew_output_obj)
            logger.info(f"AI Analysis string to parse: {ai_result_str}")

            try:
                # Try to find JSON within the string if it's not a pure JSON string
                json_start_index = ai_result_str.find('{')
                json_end_index = ai_result_str.rfind('}') + 1
                if json_start_index != -1 and json_end_index != 0:
                    json_str_candidate = ai_result_str[json_start_index:json_end_index]
                    parsed_result = json.loads(json_str_candidate)
                    category = parsed_result.get("category")
                    priority = parsed_result.get("priority")
                    return {"category": category, "priority": priority}
                else:
                    logger.warning(f"Could not find JSON object in AI output: {ai_result_str}")
                    return {
                        "category": None,
                        "priority": None,
                        "error": "AI result not in expected JSON format"
                    }

            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from AI result: {ai_result_str}. Error: {e}")
                return {
                    "category": None,
                    "priority": None,
                    "error": f"JSONDecodeError: {e}"
                }
            except Exception as e:
                logger.error(f"Unexpected error parsing AI result: {ai_result_str}. Error: {e}")
                return {
                    "category": None,
                    "priority": None,
                    "error": f"Parsing error: {e}"
                }

        except Exception as e:
            logger.error(f"Error during Crew AI kickoff: {e}")
            return {
                "category": None,
                "priority": None,
                "error": f"Crew AI execution failed: {e}"
            }

if __name__ == '__main__':
    import asyncio

    async def main():
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not gemini_key:
            print("Error: GEMINI_API_KEY (or GOOGLE_API_KEY) environment variable not set for service test.")
            print("Please set it before running this script.")
            return

        print("Testing TaskAnalysisService with Gemini...")
        # Ensure the .env is loaded if running standalone for testing
        # from dotenv import load_dotenv
        # load_dotenv()
        service = TaskAnalysisService()

        if not service.ai_enabled or not service.analyzer_agent or not service.analyzer_agent.llm:
            print("Service AI features not enabled or agent/LLM failed to initialize. Aborting test.")
            return
        
        # Example task
        sample_task_data = TaskCreate(
            description="The payment gateway integration is failing for new user signups.",
            user_story="As a new user, I want to be able to complete payment so I can subscribe to the service.",
            context="This is blocking all new subscriptions and causing revenue loss."
        )
        
        logger.info(f"\nAnalyzing task: {sample_task_data.description}")
        analysis_result = await service.analyze_task(sample_task_data)
        
        logger.info("\nService Analysis Result:")
        logger.info(f"  Category: {analysis_result.get('category')}")
        logger.info(f"  Priority: {analysis_result.get('priority')}")
        if analysis_result.get('error'):
            logger.error(f"  Error: {analysis_result.get('error')}")

    asyncio.run(main())
