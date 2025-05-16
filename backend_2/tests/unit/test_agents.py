import pytest
from datetime import datetime
from unittest.mock import MagicMock
import json

from app.agents.base.agents.task_analyzer_agent import TaskAnalyzerAgent
from app.agents.base.agents.product_agents import ProductAgents
from app.agents.base.agents.technical_agents import TechnicalAgents
from app.agents.base.agents.operations_agents import OperationsAgents
from app.agents.base.agents.quality_agents import QualityAgents

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing."""
    mock = MagicMock()
    mock.generate.return_value = '{"category": "Feature Request", "priority": "High"}'
    return mock

class TestTaskAnalyzerAgent:
    async def test_analyze_task(self):
        """Test task analyzer agent's basic functionality."""
        agent = TaskAnalyzerAgent()
        
        result = await agent.analyze_task(
            description="Add dark mode support",
            user_story="As a user, I want dark mode",
            context="Users need dark mode for nighttime use"
        )
        
        assert isinstance(result, dict)
        assert "category" in result
        assert "priority" in result
        assert result.get("error") is None
        
    async def test_invalid_input_handling(self):
        """Test how task analyzer handles invalid input."""
        agent = TaskAnalyzerAgent()
        
        result = await agent.analyze_task(
            description="",  # Empty description
            user_story="",
            context=""
        )
        
        assert isinstance(result, dict)
        assert "error" in result

class TestProductAgents:
    async def test_generate_user_stories(self):
        """Test user story generation."""
        agents = ProductAgents()
        
        result = await agents.generate_user_stories(
            feature_description="Implement user authentication",
            context="Security is important"
        )
        
        assert isinstance(result, dict)
        assert "user_stories" in result
        assert isinstance(result["user_stories"], list)
        
    async def test_analyze_ux(self):
        """Test UX analysis."""
        agents = ProductAgents()
        
        user_stories = [{
            "role": "user",
            "goal": "authenticate securely",
            "benefit": "protect my account"
        }]
        
        result = await agents.analyze_ux(
            feature_description="Implement authentication",
            user_stories=user_stories,
            context="Security focused"
        )
        
        assert isinstance(result, dict)
        assert "recommendations" in result

class TestTechnicalAgents:
    async def test_design_database(self):
        """Test database design generation."""
        agents = TechnicalAgents()
        
        user_stories = [{
            "role": "user",
            "goal": "store preferences",
            "benefit": "customize experience"
        }]
        
        result = await agents.design_database(
            user_stories=user_stories,
            context="Need to persist user preferences"
        )
        
        assert isinstance(result, dict)
        assert "tables" in result
        
    async def test_break_down_tasks(self):
        """Test technical task breakdown."""
        agents = TechnicalAgents()
        
        result = await agents.break_down_tasks(
            feature_description="Add user preferences",
            user_stories=[],
            database_design={"tables": []},
            context="Storage feature"
        )
        
        assert isinstance(result, dict)
        assert "tasks" in result
        
    async def test_review_implementation(self):
        """Test code review functionality."""
        agents = TechnicalAgents()
        
        tasks = [{
            "id": "TASK-1",
            "title": "Implement user model"
        }]
        
        code_snippets = [{
            "file": "user.py",
            "code": "class User: pass"
        }]
        
        result = await agents.review_implementation(
            tasks=tasks,
            code_snippets=code_snippets
        )
        
        assert isinstance(result, dict)
        assert "feedback" in result

class TestOperationsAgents:
    async def test_estimate_timeline(self):
        """Test timeline estimation."""
        agents = OperationsAgents()
        
        tasks = [{
            "id": "TASK-1",
            "estimated_hours": 8
        }]
        
        result = await agents.estimate_timeline(
            tasks=tasks,
            context="Sprint planning"
        )
        
        assert isinstance(result, dict)
        assert "timeline" in result
        
    async def test_plan_infrastructure(self):
        """Test infrastructure planning."""
        agents = OperationsAgents()
        
        result = await agents.plan_infrastructure(
            feature_description="Add file upload",
            technical_requirements={
                "storage": "S3",
                "processing": "async"
            }
        )
        
        assert isinstance(result, dict)
        assert "infrastructure" in result

class TestQualityAgents:
    async def test_design_test_strategy(self):
        """Test test strategy design."""
        agents = QualityAgents()
        
        result = await agents.design_test_strategy(
            feature_description="User authentication",
            user_stories=[],
            technical_specs={},
            context="Security critical"
        )
        
        assert isinstance(result, dict)
        assert "test_strategy" in result
        
    async def test_analyze_security(self):
        """Test security analysis."""
        agents = QualityAgents()
        
        result = await agents.analyze_security(
            feature_description="Payment processing",
            technical_specs={
                "processing": "stripe",
                "storage": "encrypted"
            }
        )
        
        assert isinstance(result, dict)
        assert "security_analysis" in result

class TestAgentInteroperability:
    """Test how different agents work together."""
    
    async def test_analysis_chain(self):
        """Test the full chain of analysis from different agents."""
        # Initialize all agents
        task_analyzer = TaskAnalyzerAgent()
        product_agents = ProductAgents()
        technical_agents = TechnicalAgents()
        quality_agents = QualityAgents()
        operations_agents = OperationsAgents()
        
        # 1. Initial task analysis
        task_result = await task_analyzer.analyze_task(
            description="Add payment processing",
            user_story="As a user, I want to make payments",
            context="E-commerce feature"
        )
        
        assert task_result["category"] is not None
        assert task_result["priority"] is not None
        
        # 2. Generate user stories
        stories_result = await product_agents.generate_user_stories(
            feature_description="Add payment processing",
            context="E-commerce feature"
        )
        
        assert stories_result.get("user_stories") is not None
        
        # 3. Technical planning
        tech_result = await technical_agents.break_down_tasks(
            feature_description="Add payment processing",
            user_stories=stories_result["user_stories"],
            database_design={},
            context="E-commerce feature"
        )
        
        assert tech_result.get("tasks") is not None
        
        # 4. Quality planning
        quality_result = await quality_agents.design_test_strategy(
            feature_description="Add payment processing",
            user_stories=stories_result["user_stories"],
            technical_specs=tech_result,
            context="E-commerce feature"
        )
        
        assert quality_result.get("test_strategy") is not None
        
        # 5. Operations planning
        ops_result = await operations_agents.estimate_timeline(
            tasks=tech_result["tasks"]
        )
        
        assert ops_result.get("timeline") is not None
        
        # Verify all results can be combined
        combined_result = {
            "category": task_result["category"],
            "priority": task_result["priority"],
            "user_stories": stories_result["user_stories"],
            "technical_tasks": tech_result["tasks"],
            "test_strategy": quality_result["test_strategy"],
            "timeline": ops_result["timeline"]
        }
        
        assert all(v is not None for v in combined_result.values())
