from typing import Optional, Dict, Any
from crewai import Agent, Task, Crew
import json
import logging
from ..agent_base import AgentBase

logger = logging.getLogger(__name__)

class ProductAgents(AgentBase):
    """Product-focused agents for user stories and design."""

    def make_product_manager(self) -> Agent:
        """
        Create a product manager agent focused on user story generation.
        
        Returns:
            Agent: Configured product manager agent instance
        """
        return self.create_agent(
            role="Product Manager",
            goal="Generate comprehensive user stories for the given app idea. "
                 "Break down features into clear, actionable user stories that capture "
                 "user needs, desired outcomes, and business value.",
            backstory="You are a detail-oriented product manager with years of experience in app development. "
                     "You excel at understanding user needs and translating them into clear, valuable features. "
                     "You focus on creating user stories that are specific, measurable, achievable, relevant, "
                     "and time-bound (SMART)."
        )

    def make_ux_designer(self) -> Agent:
        """
        Create a UX designer agent focused on user experience analysis.
        
        Returns:
            Agent: Configured UX designer agent instance
        """
        return self.create_agent(
            role="UX Designer",
            goal="Analyze user experience implications and suggest UI/UX improvements. "
                 "Evaluate proposed features from a user-centered design perspective "
                 "and provide specific recommendations for optimal user experience.",
            backstory="You are a creative designer with deep expertise in user-centered design principles. "
                     "You have a proven track record of creating intuitive, accessible, and engaging user "
                     "interfaces. You always consider user needs, accessibility requirements, and current "
                     "design trends in your recommendations."
        )

    async def generate_user_stories(self, feature_description: str, context: str = "") -> dict:
        """
        Generate user stories for a given feature using the product manager agent.
        
        Args:
            feature_description (str): Description of the feature to analyze
            context (str, optional): Additional context about the feature or project
            
        Returns:
            dict: User stories and acceptance criteria
        """
        if not self.has_valid_llm():
            logger.warning("Product manager agent has no valid LLM configuration")
            return {
                "user_stories": [],
                "error": "LLM not configured or initialization failed"
            }

        pm_agent = self.make_product_manager()
        
        story_task = Task(
            description=f"Generate user stories for the following feature: \n"
                      f"Feature: {feature_description}\n"
                      f"Context: {context}\n"
                      f"Create a JSON object containing an array of user stories, where each story has "
                      f"'role', 'goal', 'benefit', and 'acceptance_criteria' fields.",
            agent=pm_agent,
            expected_output='A JSON string containing an array of user stories. Example: \n'
                          '{"user_stories": [\n'
                          '  {\n'
                          '    "role": "registered user",\n'
                          '    "goal": "reset my password",\n'
                          '    "benefit": "regain access to my account",\n'
                          '    "acceptance_criteria": ["Can request reset via email", "..."]\n'
                          '  }\n'
                          ']}'
        )

        crew = Crew(
            agents=[pm_agent],
            tasks=[story_task],
            verbose=0
        )

        try:
            logger.info(f"Generating user stories for: {feature_description[:50]}...")
            result = crew.kickoff()
            
            # Parse the result
            result_str = str(result)
            json_start = result_str.find('{')
            json_end = result_str.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                try:
                    parsed_result = json.loads(result_str[json_start:json_end])
                    return parsed_result
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from result: {e}")
                    return {
                        "user_stories": [],
                        "error": f"JSON parsing error: {e}"
                    }
            else:
                return {
                    "user_stories": [],
                    "error": "No valid JSON found in result"
                }
                
        except Exception as e:
            logger.error(f"Error generating user stories: {e}")
            return {
                "user_stories": [],
                "error": f"Generation error: {e}"
            }

    async def analyze_ux(self, feature_description: str, user_stories: list, context: str = "") -> dict:
        """
        Analyze UX implications of a feature using the UX designer agent.
        
        Args:
            feature_description (str): Description of the feature to analyze
            user_stories (list): List of user stories to consider
            context (str, optional): Additional context about the feature or project
            
        Returns:
            dict: UX analysis and recommendations
        """
        if not self.has_valid_llm():
            logger.warning("UX designer agent has no valid LLM configuration")
            return {
                "recommendations": [],
                "error": "LLM not configured or initialization failed"
            }

        ux_agent = self.make_ux_designer()
        
        analysis_task = Task(
            description=f"Analyze the UX implications of this feature and provide recommendations:\n"
                      f"Feature: {feature_description}\n"
                      f"User Stories: {json.dumps(user_stories, indent=2)}\n"
                      f"Context: {context}\n"
                      f"Provide a JSON object with UX recommendations and potential issues.",
            agent=ux_agent,
            expected_output='A JSON string containing UX analysis. Example:\n'
                          '{\n'
                          '  "recommendations": [\n'
                          '    {\n'
                          '      "aspect": "Navigation",\n'
                          '      "suggestion": "Add breadcrumb navigation",\n'
                          '      "rationale": "Improves user orientation"\n'
                          '    }\n'
                          '  ],\n'
                          '  "potential_issues": ["..."],\n'
                          '  "accessibility_considerations": ["..."]\n'
                          '}'
        )

        crew = Crew(
            agents=[ux_agent],
            tasks=[analysis_task],
            verbose=0
        )

        try:
            logger.info(f"Analyzing UX for: {feature_description[:50]}...")
            result = crew.kickoff()
            
            # Parse the result
            result_str = str(result)
            json_start = result_str.find('{')
            json_end = result_str.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                try:
                    return json.loads(result_str[json_start:json_end])
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from UX analysis: {e}")
                    return {
                        "recommendations": [],
                        "error": f"JSON parsing error: {e}"
                    }
            else:
                return {
                    "recommendations": [],
                    "error": "No valid JSON found in analysis"
                }
                
        except Exception as e:
            logger.error(f"Error during UX analysis: {e}")
            return {
                "recommendations": [],
                "error": f"Analysis error: {e}"
            }

if __name__ == "__main__":
    import asyncio
    
    async def test_product_agents():
        agents = ProductAgents()
        
        if not agents.has_valid_llm():
            print("Error: LLM not configured. Please set GEMINI_API_KEY in environment.")
            return
            
        test_feature = {
            "description": "Add a dark mode feature to the application",
            "context": "Users have requested the ability to switch between light and dark themes"
        }
        
        # Generate user stories
        stories_result = await agents.generate_user_stories(
            feature_description=test_feature["description"],
            context=test_feature["context"]
        )
        
        print("\nUser Stories Result:")
        print(json.dumps(stories_result, indent=2))
        
        if "user_stories" in stories_result and not stories_result.get("error"):
            # Analyze UX implications
            ux_result = await agents.analyze_ux(
                feature_description=test_feature["description"],
                user_stories=stories_result["user_stories"],
                context=test_feature["context"]
            )
            
            print("\nUX Analysis Result:")
            print(json.dumps(ux_result, indent=2))
            
    # Run the test
    asyncio.run(test_product_agents())
