from crewai import Agent
import os
# from langchain_google_genai import ChatGoogleGenerativeAI # No longer using this directly
from langchain_community.chat_models import ChatLiteLLM # Use ChatLiteLLM

# It's good practice to load API keys from environment variables
# Ensure GEMINI_API_KEY is set in your environment
# For local development, you might use a .env file and python-dotenv
from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '.env'))  # Explicitly load project root .env

class TaskAnalyzerAgents:
    def make_task_analyzer_agent(self) -> Agent:
        # Instantiate the LLM using ChatLiteLLM for Gemini
        # GEMINI_API_KEY should be set in the environment and LiteLLM will pick it up.
        llm = None
        try:
            # Ensure GEMINI_API_KEY is available for LiteLLM
            if not os.getenv("GEMINI_API_KEY"):
                print("GEMINI_API_KEY not found in environment variables. LLM will not be configured.")
            else:
                llm = ChatLiteLLM(
                    model="gemini/gemini-2.0-flash", # LiteLLM model string for Gemini
                    # temperature=0.7 # Optional: set temperature
                )
                print(f"ChatLiteLLM initialized with model: gemini/gemini-2.0-flash")
        except Exception as e:
            print(f"Error instantiating ChatLiteLLM with gemini/gemini-2.0-flash: {e}")
            print("Please ensure GEMINI_API_KEY is set and the langchain-google-genai package is installed.")
            # Depending on desired behavior, you might raise the error or return a non-LLM agent
            # For now, we'll let the Agent creation fail if llm is None or misconfigured.

        return Agent(
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
            "Predefined priorities are: High, Medium, Low.",
            verbose=True,
            allow_delegation=False,
            llm=llm # Pass the configured Gemini LLM
        )

if __name__ == "__main__":
    # This is a simple test script that can be run standalone
    # Ensure GEMINI_API_KEY is set in your environment before running
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set.")
        print(
            "Please set it before running this script, e.g., export GEMINI_API_KEY='your_key_here'"
        )
    else:
        print("GEMINI_API_KEY is set. Attempting to create and test agent with Gemini...")
        try:
            from crewai import Task, Crew

            analyzer_agent = TaskAnalyzerAgents().make_task_analyzer_agent()

            if analyzer_agent.llm is None:
                print("LLM not configured for the agent. Exiting test.")
            else:
                # Example task details
                task_description = "The user login button is not working on the main page after the last deployment."
                user_story = (
                    "As a user, I want to be able to log in so I can access my account."
                )
                context = "This is critical as it affects all users trying to access the platform."

                analysis_task_definition = Task(
                    description=f"Analyze the following task details and determine its category and priority. "
                    f"Description: '{task_description}'. "
                    f"User Story: '{user_story}'. "
                    f"Context: '{context}'. "
                    f"Return the category and priority as a JSON string with 'category' and 'priority' keys.",
                    agent=analyzer_agent,
                    expected_output="A JSON string containing the 'category' and 'priority'. For example: "
                    '"{ \\"category\\": \\"Bug Fix\\", \\"priority\\": \\"High\\" }"',
                )

                # Create a simple crew to run this one task
                crew = Crew(
                    agents=[analyzer_agent], tasks=[analysis_task_definition], verbose=2
                )

                print("\nRunning Crew to analyze task with Gemini...")
                result = crew.kickoff()

                print("\nTask Analysis Result (Gemini):")
                print(result)

                print("\nAttempting to parse the JSON result...")
                import json

                try:
                    # CrewAI results can sometimes have extra text, try to find JSON
                    json_start_index = result.find('{')
                    json_end_index = result.rfind('}') + 1
                    if json_start_index != -1 and json_end_index != 0:
                        json_str_candidate = result[json_start_index:json_end_index]
                        parsed_result = json.loads(json_str_candidate)
                        print("Parsed Category:", parsed_result.get("category"))
                        print("Parsed Priority:", parsed_result.get("priority"))
                    else:
                        print(f"Could not find JSON object in AI output: {result}")
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON from result: {result}")
                except AttributeError: # If result is not a string
                    print("Result might not be a string or does not have .get method.")
                except Exception as e:
                    print(f"An error occurred during JSON parsing: {e}")


        except ImportError as e:
            print(f"ImportError: {e}. Make sure all dependencies are installed (e.g., langchain-google-genai).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
