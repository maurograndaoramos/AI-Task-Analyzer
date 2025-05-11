import os
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

# Load .env file for OPENAI_API_KEY if present, for local testing convenience
load_dotenv()

from app.main import app
from app.core.db import (
    database,
    metadata,
    tasks,
    TEST_DATABASE_URL,
    set_db_url,
    reset_db_url
)

def setup_test_db():
    """Create a fresh test database with tables"""
    # Drop and recreate the test database
    if os.path.exists("test_integration.db"):
        try:
            os.remove("test_integration.db")
        except PermissionError:
            pass  # Ignore if file is locked

    # Create tables in the test database
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(bind=engine)
    return engine

@pytest.fixture(autouse=True)
async def setup_test_db_connection():
    """Set up test database and handle connections"""
    # Setup database
    engine = setup_test_db()
    set_db_url(TEST_DATABASE_URL)
    
    # Connect to test database
    if not database.is_connected:
        await database.connect()
    
    # Clear any existing data
    await database.execute(tasks.delete())
    
    yield
    
    # Cleanup
    if database.is_connected:
        await database.disconnect()
    
    # Reset database URL
    reset_db_url()
    
    # Clean up test database file
    engine.dispose()
    if os.path.exists("test_integration.db"):
        try:
            os.remove("test_integration.db")
        except PermissionError:
            pass  # Ignore if file is locked

@pytest.fixture
def client():
    """Test client fixture"""
    with TestClient(app) as test_client:
        yield test_client

def test_create_task_and_get_task(client: TestClient):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        pytest.skip("OPENAI_API_KEY not set, skipping integration test requiring AI.")

    task_data = {
        "description": "Integrate a new payment gateway for subscriptions.",
        "user_story": "As a finance manager, I want a new payment gateway to reduce transaction fees.",
        "context": "The current gateway has high fees for international transactions."
    }
    
    # Create a task
    response = client.post("/api/v1/tasks/", json=task_data)
    assert response.status_code == 201
    created_task_data = response.json()
    
    assert created_task_data["id"] is not None
    assert created_task_data["description"] == task_data["description"]
    assert created_task_data["user_story"] == task_data["user_story"]
    assert created_task_data["context"] == task_data["context"]
    assert created_task_data["status"] == "Open"
    
    # AI-populated fields should exist (might be None if AI fails, but keys should be there)
    assert "category" in created_task_data
    assert "priority" in created_task_data
    
    print(f"AI Analysis for created task: Category='{created_task_data['category']}', Priority='{created_task_data['priority']}'")
    assert isinstance(created_task_data["category"], (str, type(None)))
    assert isinstance(created_task_data["priority"], (str, type(None)))

    task_id = created_task_data["id"]
    
    # Get the specific task
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    retrieved_task_data = response.json()
    assert retrieved_task_data["id"] == task_id
    assert retrieved_task_data["description"] == task_data["description"]
    assert retrieved_task_data["category"] == created_task_data["category"]
    assert retrieved_task_data["priority"] == created_task_data["priority"]

def test_get_tasks_empty(client: TestClient):
    response = client.get("/api/v1/tasks/")
    assert response.status_code == 200
    assert response.json() == []

def test_get_tasks_with_data(client: TestClient):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        pytest.skip("OPENAI_API_KEY not set, skipping integration test requiring AI.")

    task_data1 = {"description": "Setup CI/CD pipeline"}
    task_data2 = {"description": "Write user documentation"}
    
    client.post("/api/v1/tasks/", json=task_data1)
    client.post("/api/v1/tasks/", json=task_data2)
    
    response = client.get("/api/v1/tasks/")
    assert response.status_code == 200
    tasks_list = response.json()
    assert len(tasks_list) == 2
    assert tasks_list[0]["description"] == task_data1["description"]
    assert tasks_list[1]["description"] == task_data2["description"]

def test_get_non_existent_task(client: TestClient):
    response = client.get("/api/v1/tasks/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_create_task_without_openai_key_if_service_allows(client: TestClient):
    # Temporarily unset OPENAI_API_KEY for this specific test's scope
    original_key = os.environ.pop("OPENAI_API_KEY", None)
    try:
        task_data = {
            "description": "Task created without AI key available.",
        }
        
        response = client.post("/api/v1/tasks/", json=task_data)
        assert response.status_code == 201  # Task creation should still succeed
        created_task_data = response.json()

        assert created_task_data["id"] is not None
        assert created_task_data["description"] == task_data["description"]
        assert created_task_data["category"] is None 
        assert created_task_data["priority"] is None
    finally:
        # Restore key if it was originally set
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key
