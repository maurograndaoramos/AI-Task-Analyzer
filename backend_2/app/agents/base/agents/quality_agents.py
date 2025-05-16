from typing import Optional, Dict, Any, List
from crewai import Agent, Task, Crew
import json
import logging
from ..agent_base import AgentBase

logger = logging.getLogger(__name__)

class QualityAgents(AgentBase):
    """Quality assurance and security-focused agents."""

    def make_qa_strategist(self) -> Agent:
        """
        Create a QA strategist agent focused on testing strategies.
        
        Returns:
            Agent: Configured QA strategist agent instance
        """
        return self.create_agent(
            role="QA Strategist",
            goal="Design comprehensive testing strategies including unit, integration, and e2e tests. "
                 "Focus on test coverage, automation, and quality assurance processes.",
            backstory="You are an expert in quality assurance with deep knowledge of testing "
                     "methodologies and automation frameworks. You excel at designing comprehensive "
                     "test strategies that ensure robust and reliable software. You always consider "
                     "edge cases, error scenarios, and user workflows in your test plans."
        )

    def make_security_analyst(self) -> Agent:
        """
        Create a security analyst agent focused on security implications.
        
        Returns:
            Agent: Configured security analyst agent instance
        """
        return self.create_agent(
            role="Security Analyst",
            goal="Analyze security implications and requirements for proposed features. "
                 "Focus on identifying potential vulnerabilities and recommending security measures.",
            backstory="You are an experienced cybersecurity expert specializing in web application "
                     "security. You have a strong background in identifying security risks and "
                     "implementing protective measures. You always consider the latest security "
                     "threats and best practices in your analysis."
        )

    async def design_test_strategy(self, feature_description: str, user_stories: List[Dict],
                               technical_specs: Dict, context: str = "") -> dict:
        """
        Design a comprehensive test strategy using the QA strategist agent.
        
        Args:
            feature_description (str): Description of the feature to test
            user_stories (List[Dict]): User stories to cover in testing
            technical_specs (Dict): Technical specifications and implementation details
            context (str, optional): Additional context about the project
            
        Returns:
            dict: Test strategy and coverage plans
        """
        if not self.has_valid_llm():
            logger.warning("QA strategist agent has no valid LLM configuration")
            return {
                "test_strategy": {},
                "error": "LLM not configured or initialization failed"
            }

        qa = self.make_qa_strategist()
        
        strategy_task = Task(
            description=f"Design a comprehensive test strategy for this feature:\n"
                      f"Feature: {feature_description}\n"
                      f"User Stories: {json.dumps(user_stories, indent=2)}\n"
                      f"Technical Specs: {json.dumps(technical_specs, indent=2)}\n"
                      f"Context: {context}\n"
                      f"Create a JSON object detailing the test strategy and coverage plans.",
            agent=qa,
            expected_output='A JSON object containing test strategy. Example:\n'
                          '{\n'
                          '  "test_levels": {\n'
                          '    "unit_tests": [\n'
                          '      {\n'
                          '        "component": "UserPreferences",\n'
                          '        "scenarios": ["Valid input", "Invalid input"],\n'
                          '        "coverage_targets": ["Methods", "Edge cases"]\n'
                          '      }\n'
                          '    ],\n'
                          '    "integration_tests": [\n'
                          '      {\n'
                          '        "flow": "Save preferences",\n'
                          '        "components": ["API", "Database"],\n'
                          '        "scenarios": ["Success", "Failure"]\n'
                          '      }\n'
                          '    ],\n'
                          '    "e2e_tests": ["Complete user workflow"]\n'
                          '  },\n'
                          '  "automation_approach": ["Jest", "Cypress"],\n'
                          '  "test_data_strategy": "Mock external services",\n'
                          '  "quality_gates": ["80% coverage", "Zero high-severity bugs"]\n'
                          '}'
        )

        crew = Crew(
            agents=[qa],
            tasks=[strategy_task],
            verbose=0
        )

        try:
            logger.info(f"Designing test strategy for: {feature_description[:50]}...")
            result = crew.kickoff()
            
            result_str = str(result)
            json_start = result_str.find('{')
            json_end = result_str.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                try:
                    return json.loads(result_str[json_start:json_end])
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from test strategy: {e}")
                    return {
                        "test_strategy": {},
                        "error": f"JSON parsing error: {e}"
                    }
            else:
                return {
                    "test_strategy": {},
                    "error": "No valid JSON found in strategy result"
                }
                
        except Exception as e:
            logger.error(f"Error during test strategy design: {e}")
            return {
                "test_strategy": {},
                "error": f"Strategy design error: {e}"
            }

    async def analyze_security(self, feature_description: str, technical_specs: Dict,
                           data_handling: Dict = None, context: str = "") -> dict:
        """
        Analyze security implications using the security analyst agent.
        
        Args:
            feature_description (str): Description of the feature to analyze
            technical_specs (Dict): Technical specifications and implementation details
            data_handling (Dict, optional): Information about data processing and storage
            context (str, optional): Additional context about the project
            
        Returns:
            dict: Security analysis and recommendations
        """
        if not self.has_valid_llm():
            logger.warning("Security analyst agent has no valid LLM configuration")
            return {
                "security_analysis": {},
                "error": "LLM not configured or initialization failed"
            }

        analyst = self.make_security_analyst()
        
        if data_handling is None:
            data_handling = {
                "data_types": ["personal_info", "preferences"],
                "storage": "encrypted_database",
                "retention": "user_lifetime"
            }
        
        analysis_task = Task(
            description=f"Analyze security implications for this feature:\n"
                      f"Feature: {feature_description}\n"
                      f"Technical Specs: {json.dumps(technical_specs, indent=2)}\n"
                      f"Data Handling: {json.dumps(data_handling, indent=2)}\n"
                      f"Context: {context}\n"
                      f"Create a JSON object with security analysis and recommendations.",
            agent=analyst,
            expected_output='A JSON object containing security analysis. Example:\n'
                          '{\n'
                          '  "risk_assessment": {\n'
                          '    "vulnerabilities": [\n'
                          '      {\n'
                          '        "type": "Injection",\n'
                          '        "severity": "High",\n'
                          '        "mitigation": "Input validation"\n'
                          '      }\n'
                          '    ],\n'
                          '    "data_protection": [\n'
                          '      {\n'
                          '        "data_type": "personal_info",\n'
                          '        "measures": ["encryption", "access_control"]\n'
                          '      }\n'
                          '    ]\n'
                          '  },\n'
                          '  "security_requirements": ["Authentication", "Authorization"],\n'
                          '  "compliance_considerations": ["GDPR", "CCPA"],\n'
                          '  "recommendations": ["Implement rate limiting"]\n'
                          '}'
        )

        crew = Crew(
            agents=[analyst],
            tasks=[analysis_task],
            verbose=0
        )

        try:
            logger.info(f"Analyzing security for: {feature_description[:50]}...")
            result = crew.kickoff()
            
            result_str = str(result)
            json_start = result_str.find('{')
            json_end = result_str.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                try:
                    return json.loads(result_str[json_start:json_end])
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from security analysis: {e}")
                    return {
                        "security_analysis": {},
                        "error": f"JSON parsing error: {e}"
                    }
            else:
                return {
                    "security_analysis": {},
                    "error": "No valid JSON found in analysis result"
                }
                
        except Exception as e:
            logger.error(f"Error during security analysis: {e}")
            return {
                "security_analysis": {},
                "error": f"Analysis error: {e}"
            }

if __name__ == "__main__":
    import asyncio
    
    async def test_quality_agents():
        agents = QualityAgents()
        
        if not agents.has_valid_llm():
            print("Error: LLM not configured. Please set GEMINI_API_KEY in environment.")
            return
            
        # Test data
        feature = {
            "description": "User authentication system with OAuth",
            "user_stories": [
                {
                    "role": "user",
                    "goal": "log in with Google account",
                    "benefit": "quick and secure access"
                }
            ],
            "technical_specs": {
                "auth_provider": "OAuth2",
                "user_data": ["email", "profile"],
                "session_management": "JWT"
            }
        }
        
        # Test test strategy design
        test_strategy = await agents.design_test_strategy(
            feature_description=feature["description"],
            user_stories=feature["user_stories"],
            technical_specs=feature["technical_specs"]
        )
        print("\nTest Strategy Result:")
        print(json.dumps(test_strategy, indent=2))
        
        # Test security analysis
        if not test_strategy.get("error"):
            security_analysis = await agents.analyze_security(
                feature_description=feature["description"],
                technical_specs=feature["technical_specs"]
            )
            print("\nSecurity Analysis Result:")
            print(json.dumps(security_analysis, indent=2))
            
    # Run the test
    asyncio.run(test_quality_agents())
