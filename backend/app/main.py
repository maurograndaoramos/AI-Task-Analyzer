from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from app.api.v1.endpoints import tasks as tasks_router
from app.core.db import database, metadata, engine

# Load environment variables from .env file
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Database connection lifecycle management"""
    if not database.is_connected:
        await database.connect()
    
    yield
    
    if database.is_connected:
        await database.disconnect()

app = FastAPI(
    title="AI-Powered Task Assistant",
    lifespan=lifespan,
    description="An intelligent task manager that uses AI to categorize and prioritize tasks.",
    version="1.0.0"
)

# CORS Middleware configuration
origins = [
    "http://localhost:3000",  # Allow your Next.js frontend
    # You can add other origins here if needed, e.g., your deployed frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create tables at startup if they don't exist
metadata.create_all(bind=engine)

app.include_router(tasks_router.router, prefix="/api/v1/tasks", tags=["tasks"])

@app.get("/")
async def read_root():
    return {
        "message": "Welcome to the AI-Powered Task Assistant API",
        "docs": "/docs",
        "redoc": "/redoc"
    }
