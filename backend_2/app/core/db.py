import os
from typing import Dict, Any
from sqlalchemy import (
    Table, Column, Integer, String, JSON, DateTime, MetaData,
    create_engine, Text, Float, Boolean
)
from databases import Database
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment or use default SQLite database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./test.db"
)

# SQLite specific configuration
if DATABASE_URL.startswith("sqlite"):
    DATABASE_URL = DATABASE_URL.replace(
        "sqlite:",
        "sqlite+aiosqlite:",
    )

# Initialize database
database = Database(DATABASE_URL)
metadata = MetaData()

# Tasks table with extended analysis fields
tasks = Table(
    "tasks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("description", String, nullable=False),
    Column("user_story", Text),
    Column("context", Text),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    Column("status", String, default="Open"),
    
    # Task Analyzer results
    Column("category", String),
    Column("priority", String),
    
    # Product Manager and UX results
    Column("user_stories", JSON),  # Detailed user stories
    Column("ux_recommendations", JSON),  # UX analysis
    
    # Technical analysis
    Column("database_design", JSON),  # DB schema design
    Column("technical_tasks", JSON),  # Broken down tasks
    Column("code_review", JSON),  # Code review feedback
    
    # Quality analysis
    Column("test_strategy", JSON),  # Test planning
    Column("security_analysis", JSON),  # Security considerations
    
    # Operations planning
    Column("timeline_estimate", JSON),  # Project timeline
    Column("infrastructure_plan", JSON),  # Infrastructure requirements
)

# Agents execution history for tracking and analysis
agent_executions = Table(
    "agent_executions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("task_id", Integer),
    Column("agent_type", String, nullable=False),
    Column("executed_at", DateTime, default=datetime.utcnow),
    Column("input_data", JSON),
    Column("output_data", JSON),
    Column("execution_time", Float),
    Column("success", Boolean, default=True),
    Column("error_message", Text),
)

# Agent configurations for dynamic agent management
agent_configs = Table(
    "agent_configs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("agent_type", String, unique=True, nullable=False),
    Column("enabled", Boolean, default=True),
    Column("configuration", JSON),  # Customizable agent parameters
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
)

async def connect_db():
    """Connect to the database."""
    try:
        await database.connect()
        print("Successfully connected to database")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

async def disconnect_db():
    """Disconnect from the database."""
    try:
        await database.disconnect()
        print("Successfully disconnected from database")
    except Exception as e:
        print(f"Error disconnecting from database: {e}")
        raise

def create_tables():
    """Create database tables if they don't exist."""
    engine = create_engine(DATABASE_URL)
    try:
        metadata.create_all(engine)
        print("Successfully created database tables")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

# Execute table creation when run directly
if __name__ == "__main__":
    create_tables()
