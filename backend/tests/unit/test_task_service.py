__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import pytest
from unittest.mock import patch, Mock
import os
from crewai import Agent

from app.services.task_service import TaskAnalysisService
from app.api.v1.schemas import TaskCreate

def create_mock_agent():
    """Creates a properly structured mock agent for CrewAI"""
    agent = Agent(
        role="Mock Task Analyzer",
        goal="Mock analysis",
        backstory="Mock backstory",
    )
    return agent

@pytest.fixture
def mock_agent():
    # Create a properly structured mock agent
    agent = create_mock_agent()
    with patch("app.services.task_service.TaskAnalyzerAgents") as mock_agents_class:
        mock_agents_class.return_value.make_task_analyzer_agent.return_value = agent
        yield agent

@pytest.fixture
def service_with_key(mock_agent):
    """Create a service instance with OPENAI_API_KEY set"""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}, clear=True):
        return TaskAnalysisService()

@pytest.mark.asyncio
async def test_analyze_task_success(service_with_key):
    task_details = TaskCreate(
        description="Test task description",
        user_story="Test user story",
        context="Test context",
    )

    mock_ai_response = '{ "category": "Feature Request", "priority": "Medium" }'

    with patch("crewai.Crew.kickoff", return_value=mock_ai_response):
        result = await service_with_key.analyze_task(task_details)

        assert result["category"] == "Feature Request"
        assert result["priority"] == "Medium"
        assert result.get("error") is None

@pytest.mark.asyncio
async def test_analyze_task_json_decode_error(service_with_key):
    task_details = TaskCreate(description="Another test task")
    mock_ai_response = "This is not valid JSON"  # Invalid JSON

    with patch("crewai.Crew.kickoff", return_value=mock_ai_response):
        result = await service_with_key.analyze_task(task_details)

        assert result["category"] is None
        assert result["priority"] is None
        assert "AI result not in expected JSON format" in result.get(
            "error", ""
        ) or "JSONDecodeError" in result.get("error", "")

@pytest.mark.asyncio
async def test_analyze_task_crew_kickoff_exception(service_with_key):
    task_details = TaskCreate(description="Task that causes kickoff error")

    with patch("crewai.Crew.kickoff", side_effect=Exception("Crew AI exploded")):
        result = await service_with_key.analyze_task(task_details)

        assert result["category"] is None
        assert result["priority"] is None
        assert "Crew AI execution failed: Crew AI exploded" in result.get("error", "")

@pytest.mark.asyncio
async def test_analyze_task_no_openai_key():
    # Test service instantiation and call when OPENAI_API_KEY is NOT set
    with patch.dict(os.environ, {}, clear=True):  # Temporarily remove all env vars
        service_no_key = TaskAnalysisService()
        task_details = TaskCreate(description="Test without API key")

        result = await service_no_key.analyze_task(task_details)

        assert result["category"] is None
        assert result["priority"] is None
        assert result.get("error") == "OPENAI_API_KEY not set"

@pytest.mark.asyncio
async def test_analyze_task_ai_output_malformed_json_still_parses(service_with_key):
    task_details = TaskCreate(description="Task with slightly malformed AI output")

    # Example of AI output that might have extra text but contains valid JSON
    mock_ai_response = 'Some introductory text from AI. Here is the JSON: { "category": "Research", "priority": "Low" }. And some concluding remarks.'

    with patch("crewai.Crew.kickoff", return_value=mock_ai_response):
        result = await service_with_key.analyze_task(task_details)

        assert result["category"] == "Research"
        assert result["priority"] == "Low"
        assert result.get("error") is None
