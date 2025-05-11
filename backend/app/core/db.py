import os
from sqlalchemy import (
    Column,
    Integer,
    String,
    MetaData,
    Table,
    create_engine,
    DateTime,
)
from sqlalchemy.sql import func
from databases import Database

# Use environment variable for database URL or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
TEST_DATABASE_URL = "sqlite:///./test_integration.db"

# Create database engines
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Only needed for SQLite
)

# Create metadata object
metadata = MetaData()

# Define tasks table
tasks = Table(
    "tasks",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("description", String),
    Column("user_story", String, nullable=True),
    Column("context", String, nullable=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("status", String, default="Open"),
    Column("category", String, nullable=True),
    Column("priority", String, nullable=True),
)

# Create database connection object
database = Database(DATABASE_URL)

async def get_database() -> Database:
    """Return database instance, connecting if necessary"""
    if not database.is_connected:
        await database.connect()
    return database

async def close_database():
    """Close database connection if connected"""
    if database.is_connected:
        await database.disconnect()

def get_db_url() -> str:
    """Get the current database URL"""
    return str(database.url)

def set_db_url(url: str):
    """Set the database URL (mainly for testing)"""
    global engine
    database._url = url
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False},
    )

def reset_db_url():
    """Reset database URL to default"""
    global engine
    database._url = DATABASE_URL
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )

# Create tables at import time - this is fine for a small app
metadata.create_all(bind=engine)
