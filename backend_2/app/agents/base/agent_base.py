from crewai import Agent
from langchain_community.chat_models import ChatLiteLLM
from typing import Optional
from dotenv import load_dotenv
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AgentBase:
    """Base class for all agents with common initialization and LLM setup."""
    
    def __init__(self):
        self._load_environment()
        self.llm = self._initialize_llm()
    
    def _load_environment(self) -> None:
        """Load environment variables."""
        # Get the project root directory (backend_2)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        env_path = os.path.join(project_root, '.env')
        
        # Load environment variables from .env file
        load_dotenv(env_path)
        
        # Try both GEMINI_API_KEY and GOOGLE_API_KEY
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("Neither GEMINI_API_KEY nor GOOGLE_API_KEY found in environment variables.")
    
    def _initialize_llm(self) -> Optional[ChatLiteLLM]:
        """Initialize the LLM with error handling."""
        if not self.api_key:
            logger.error("No API key available. LLM initialization skipped.")
            return None
            
        try:
            llm = ChatLiteLLM(
                model="gemini/gemini-2.0-flash",
                max_tokens=8000  # Increase output token limit
            )
            logger.info("LLM initialized successfully with model: gemini/gemini-2.0-flash and max_tokens=8000")
            return llm
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            logger.error("Please ensure required packages are installed and API key is valid.")
            return None
    
    def create_agent(self, role: str, goal: str, backstory: str) -> Agent:
        """
        Create a CrewAI agent with common configuration.
        
        Args:
            role (str): The role of the agent (e.g., "Product Manager", "Tech Lead")
            goal (str): The specific goal or objective of the agent
            backstory (str): The agent's background and expertise
            
        Returns:
            Agent: Configured CrewAI agent instance
            
        Note:
            If LLM initialization failed, the agent will be created but may not be functional
            for AI operations. Check agent.llm before using for AI tasks.
        """
        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def has_valid_llm(self) -> bool:
        """Check if the agent has a valid LLM configuration."""
        return self.llm is not None

if __name__ == "__main__":
    # Simple test to verify the base agent functionality
    base = AgentBase()
    if base.has_valid_llm():
        print("Base agent initialized successfully with LLM")
        test_agent = base.create_agent(
            role="Test Agent",
            goal="Verify agent creation functionality",
            backstory="A test agent for verification purposes"
        )
        print(f"Test agent created with role: {test_agent.role}")
    else:
        print("Base agent initialized but LLM is not available")
        print("Please check your environment variables and API key")
