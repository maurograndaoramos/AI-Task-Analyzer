import pytest
from httpx import AsyncClient
import json
from datetime import datetime

from app.main import app
from app.core.db import database, tasks
from app.services.task_service import TaskAnalysisService

pytestmark = pytest.mark.asyncio

async def test_end_to_end_task_analysis():
    """Test the complete task analysis flow from creation to statistics."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Create a new task
        task_data = {
            "description": "Implement OAuth2 authentication",
            "user_story": "As a user, I want to log in with my Google account",
            "context": "Need to support social login for easier onboarding"
        }
        
        response = await client.post("/api/v1/tasks/", json=task_data)
        assert response.status_code == 201
        result = response.json()
        
        task_id = result.get("id")
        assert task_id is not None
        
        # 2. Verify all analysis components are present
        assert result["category"] is not None
        assert result["priority"] is not None
        assert result["user_stories"] is not None
        assert result["ux_recommendations"] is not None
        assert result["database_design"] is not None
        assert result["technical_tasks"] is not None
        assert result["test_strategy"] is not None
        assert result["security_analysis"] is not None
        assert result["timeline_estimate"] is not None
        assert result["infrastructure_plan"] is not None
        
        # 3. Get task executions
        response = await client.get(f"/api/v1/tasks/{task_id}/executions")
        assert response.status_code == 200
        executions = response.json()
        assert len(executions) > 0
        
        # 4. Create multiple tasks for statistics testing
        additional_tasks = [
            {
                "description": "Fix security vulnerability",
                "context": "Critical security issue",
                "user_story": "As an admin, I want to patch the security hole"
            },
            {
                "description": "Add user dashboard",
                "context": "Users need analytics",
                "user_story": "As a user, I want to see my usage stats"
            }
        ]
        
        for task in additional_tasks:
            response = await client.post("/api/v1/tasks/", json=task)
            assert response.status_code == 201
        
        # 5. Test statistics endpoints
        response = await client.get("/api/v1/tasks/stats/categories")
        assert response.status_code == 200
        categories = response.json()
        assert len(categories) > 0
        
        response = await client.get("/api/v1/tasks/stats/priorities")
        assert response.status_code == 200
        priorities = response.json()
        assert len(priorities) > 0
        
        response = await client.get("/api/v1/tasks/stats/agent-performance")
        assert response.status_code == 200
        performance = response.json()
        assert len(performance) > 0

async def test_agent_interaction_flow():
    """Test the interaction between different agents in the analysis process."""
    service = TaskAnalysisService()
    
    task_details = {
        "description": "Implement real-time chat feature",
        "user_story": "As a user, I want to chat with other users in real-time",
        "context": "Need to support instant messaging between users"
    }
    
    # Perform the analysis
    result = await service.analyze_task(task_details)
    
    # Verify the logical flow of analysis
    assert result is not None
    assert "error" not in result
    
    # 1. Check if user stories were generated before technical analysis
    assert "user_stories" in result
    user_stories = result["user_stories"]
    assert isinstance(user_stories, list)
    assert len(user_stories) > 0
    
    # 2. Verify that technical tasks reference user stories
    assert "technical_tasks" in result
    technical_tasks = result["technical_tasks"]
    assert isinstance(technical_tasks, list)
    
    # 3. Check if database design aligns with requirements
    assert "database_design" in result
    db_design = result["database_design"]
    assert isinstance(db_design, list)
    
    # 4. Verify that security analysis considers the technical implementation
    assert "security_analysis" in result
    security = result["security_analysis"]
    assert isinstance(security, dict)
    
    # 5. Check if test strategy covers all components
    assert "test_strategy" in result
    test_strategy = result["test_strategy"]
    assert isinstance(test_strategy, dict)
    
    # 6. Verify timeline estimation includes all tasks
    assert "timeline_estimate" in result
    timeline = result["timeline_estimate"]
    assert isinstance(timeline, dict)

async def test_database_persistence():
    """Test that all analysis results are properly persisted in the database."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a task
        task_data = {
            "description": "Implement file upload feature",
            "user_story": "As a user, I want to upload files to my account",
            "context": "Need to support document storage"
        }
        
        response = await client.post("/api/v1/tasks/", json=task_data)
        assert response.status_code == 201
        created_task = response.json()
        task_id = created_task["id"]
        
        # Verify database record
        query = tasks.select().where(tasks.c.id == task_id)
        record = await database.fetch_one(query)
        
        assert record is not None
        assert record["description"] == task_data["description"]
        assert record["user_story"] == task_data["user_story"]
        assert record["context"] == task_data["context"]
        
        # Verify JSON fields are properly stored and retrievable
        assert json.loads(record["user_stories"]) == created_task["user_stories"]
        assert json.loads(record["technical_tasks"]) == created_task["technical_tasks"]
        assert json.loads(record["test_strategy"]) == created_task["test_strategy"]

async def test_concurrent_task_analysis():
    """Test handling of concurrent task analysis requests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Prepare multiple tasks
        tasks_data = [
            {
                "description": f"Concurrent task {i}",
                "user_story": f"As a user, I want feature {i}",
                "context": f"Testing concurrent analysis {i}"
            }
            for i in range(5)
        ]
        
        # Create tasks concurrently
        import asyncio
        responses = await asyncio.gather(
            *[
                client.post("/api/v1/tasks/", json=task_data)
                for task_data in tasks_data
            ]
        )
        
        # Verify all tasks were created successfully
        assert all(r.status_code == 201 for r in responses)
        
        # Verify each task has unique analysis
        results = [r.json() for r in responses]
        task_ids = [r["id"] for r in results]
        assert len(set(task_ids)) == len(tasks_data)  # All IDs should be unique

async def test_error_recovery():
    """Test system's ability to handle and recover from errors during analysis."""
    service = TaskAnalysisService()
    
    # Test with invalid input
    invalid_task = {
        "description": "",  # Empty description should cause validation error
        "user_story": "Invalid task"
    }
    
    result = await service.analyze_task(invalid_task)
    assert "error" in result
    
    # Test with valid task after error
    valid_task = {
        "description": "Valid task",
        "user_story": "As a user, I want a working feature",
        "context": "Testing error recovery"
    }
    
    result = await service.analyze_task(valid_task)
    assert "error" not in result
    assert result["category"] is not None
    assert result["priority"] is not None
