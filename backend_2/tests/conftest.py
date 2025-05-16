import pytest
import os
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
import asyncio
from databases import Database

from app.main import app
from app.core.db import database, metadata

# Test database URL
TEST_DATABASE_URL = "sqlite:///:memory:"

# Test API key
os.environ["GEMINI_API_KEY"] = "test_api_key"

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine

@pytest.fixture(autouse=True)
async def test_db(test_engine) -> AsyncGenerator:
    """
    Create test database tables before each test and drop them after.
    Also handles database connection and disconnection.
    """
    # Create tables
    metadata.create_all(test_engine)
    
    # Override the database URL for testing
    app.state.database = Database(TEST_DATABASE_URL)
    database.url = TEST_DATABASE_URL
    
    # Connect to test database
    await database.connect()
    
    yield
    
    # Cleanup
    await database.disconnect()
    metadata.drop_all(test_engine)

@pytest.fixture
def client() -> Generator:
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def example_task_data() -> dict:
    """Provide example task data for tests."""
    return {
        "description": "Implement user authentication system",
        "user_story": "As a user, I want to securely log in to the application",
        "context": "Security is a top priority for this feature"
    }

@pytest.fixture
def example_task_batch() -> list:
    """Provide a batch of example tasks for testing."""
    return [
        {
            "description": "Fix login bug",
            "user_story": "As a user, I want to log in without errors",
            "context": "Critical bug affecting all users",
            "category": "Bug Fix",
            "priority": "High"
        },
        {
            "description": "Add dark mode",
            "user_story": "As a user, I want a dark theme option",
            "context": "Frequently requested feature",
            "category": "Feature Request",
            "priority": "Medium"
        },
        {
            "description": "Update API documentation",
            "user_story": "As a developer, I want clear API docs",
            "context": "Documentation needs updating",
            "category": "Documentation",
            "priority": "Low"
        }
    ]

@pytest.fixture
def mock_llm_response() -> dict:
    """Provide mock LLM analysis response for testing."""
    return {
        "category": "Feature Request",
        "priority": "High",
        "user_stories": [
            {
                "role": "user",
                "goal": "authenticate securely",
                "benefit": "protect my account",
                "acceptance_criteria": [
                    "Support email/password login",
                    "Implement password reset",
                    "Add 2FA option"
                ]
            }
        ],
        "technical_tasks": [
            {
                "id": "AUTH-1",
                "title": "Implement user model",
                "description": "Create user database schema",
                "type": "backend",
                "estimated_hours": 4
            }
        ]
    }

@pytest.fixture
def headers() -> dict:
    """Provide common headers for API requests."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

# Mock the LLM for testing
@pytest.fixture(autouse=True)
def mock_llm(monkeypatch):
    """Mock the LLM to avoid actual API calls during testing."""
    def mock_init(*args, **kwargs):
        return None
        
    def mock_generate(*args, **kwargs):
        return '{"category": "Feature Request", "priority": "High"}'
        
    # Mock the LLM initialization
    monkeypatch.setattr(
        "langchain_community.chat_models.ChatLiteLLM.__init__",
        mock_init
    )
    
    # Mock the generation method
    monkeypatch.setattr(
        "langchain_community.chat_models.ChatLiteLLM.generate",
        mock_generate
    )
