import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
import os
import json

from app.main import app
from app.core.db import database, metadata

# Test client setup
client = TestClient(app)

# Use in-memory SQLite for testing
DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(autouse=True)
async def setup_database():
    """Set up a new test database for each test."""
    # Create in-memory database
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create tables
    metadata.create_all(engine)
    
    # Override the database URL
    database.url = DATABASE_URL
    
    # Connect to test database
    await database.connect()
    
    yield
    
    # Cleanup
    await database.disconnect()
    metadata.drop_all(engine)

def test_create_task():
    """Test task creation and analysis."""
    task_data = {
        "description": "Add dark mode support to the application",
        "user_story": "As a user, I want to use dark mode for better nighttime viewing",
        "context": "Users have requested this feature frequently"
    }
    
    response = client.post("/api/v1/tasks/", json=task_data)
    assert response.status_code == 201
    
    result = response.json()
    assert "category" in result
    assert "priority" in result
    assert "user_stories" in result
    assert "technical_tasks" in result
    assert "test_strategy" in result
    assert "security_analysis" in result

def test_get_task():
    """Test retrieving a task."""
    # First create a task
    task_data = {
        "description": "Implement user authentication",
        "user_story": "As a user, I want to log in securely",
        "context": "Security is a top priority"
    }
    
    create_response = client.post("/api/v1/tasks/", json=task_data)
    assert create_response.status_code == 201
    task_id = create_response.json().get("id")
    
    # Then retrieve it
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    
    task = response.json()
    assert task["description"] == task_data["description"]
    assert task["user_story"] == task_data["user_story"]
    assert task["context"] == task_data["context"]

def test_task_analysis_components():
    """Test that all analysis components work correctly."""
    task_data = {
        "description": "Implement user preferences system",
        "user_story": "As a user, I want to save my preferences",
        "context": "Users need persistent settings"
    }
    
    response = client.post("/api/v1/tasks/", json=task_data)
    assert response.status_code == 201
    result = response.json()
    
    # Check Task Analyzer output
    assert result["category"] in ["Feature Request", "Bug Fix", "Documentation", "Research", "Testing", "Chore"]
    assert result["priority"] in ["High", "Medium", "Low"]
    
    # Check Product Analysis
    assert result["user_stories"]
    assert isinstance(result["user_stories"], list)
    assert result["ux_recommendations"]
    
    # Check Technical Analysis
    assert result["database_design"]
    assert isinstance(result["database_design"], list)
    assert result["technical_tasks"]
    assert isinstance(result["technical_tasks"], list)
    
    # Check Quality Analysis
    assert result["test_strategy"]
    assert result["security_analysis"]
    
    # Check Operations Analysis
    assert result["timeline_estimate"]
    assert result["infrastructure_plan"]

def test_error_handling():
    """Test error handling for invalid input."""
    # Empty description
    task_data = {
        "description": "",
        "user_story": "As a user, I want to save my preferences"
    }
    
    response = client.post("/api/v1/tasks/", json=task_data)
    assert response.status_code == 422  # Validation error
    
    # Invalid task ID
    response = client.get("/api/v1/tasks/999")
    assert response.status_code == 404
    
    # Invalid JSON
    response = client.post("/api/v1/tasks/", data="invalid json")
    assert response.status_code == 422

def test_task_filtering():
    """Test task filtering functionality."""
    # Create tasks with different categories and priorities
    tasks = [
        {
            "description": "Fix login bug",
            "context": "Users can't log in",
            "category": "Bug Fix",
            "priority": "High"
        },
        {
            "description": "Add dark mode",
            "context": "Feature request",
            "category": "Feature Request",
            "priority": "Medium"
        },
        {
            "description": "Update docs",
            "context": "Documentation needed",
            "category": "Documentation",
            "priority": "Low"
        }
    ]
    
    for task in tasks:
        client.post("/api/v1/tasks/", json=task)
    
    # Test category filter
    response = client.get("/api/v1/tasks/?category=Bug Fix")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 1
    assert result[0]["category"] == "Bug Fix"
    
    # Test priority filter
    response = client.get("/api/v1/tasks/?priority=High")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 1
    assert result[0]["priority"] == "High"
    
    # Test combined filters
    response = client.get("/api/v1/tasks/?category=Feature Request&priority=Medium")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 1
    assert result[0]["category"] == "Feature Request"
    assert result[0]["priority"] == "Medium"

def test_task_statistics():
    """Test task statistics endpoints."""
    # Create sample tasks
    tasks = [
        {"description": "Bug 1", "category": "Bug Fix", "priority": "High"},
        {"description": "Bug 2", "category": "Bug Fix", "priority": "Medium"},
        {"description": "Feature 1", "category": "Feature Request", "priority": "High"}
    ]
    
    for task in tasks:
        client.post("/api/v1/tasks/", json=task)
    
    # Test category stats
    response = client.get("/api/v1/tasks/stats/categories")
    assert response.status_code == 200
    categories = response.json()
    assert categories["Bug Fix"] == 2
    assert categories["Feature Request"] == 1
    
    # Test priority stats
    response = client.get("/api/v1/tasks/stats/priorities")
    assert response.status_code == 200
    priorities = response.json()
    assert priorities["High"] == 2
    assert priorities["Medium"] == 1

def test_agent_performance():
    """Test agent performance statistics."""
    # Create and analyze a task to generate agent execution data
    task_data = {
        "description": "Complex feature implementation",
        "user_story": "As a user, I want a complex feature",
        "context": "This is a complex task that requires all agents"
    }
    
    client.post("/api/v1/tasks/", json=task_data)
    
    # Get agent performance stats
    response = client.get("/api/v1/tasks/stats/agent-performance")
    assert response.status_code == 200
    
    stats = response.json()
    # Check that we have stats for all agent types
    assert "task_analyzer" in stats
    assert "avg_execution_time" in stats["task_analyzer"]
    assert "success_rate" in stats["task_analyzer"]
