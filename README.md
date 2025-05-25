# AI Task Analysis System (Backend)

A sophisticated multi-agent backend system built with FastAPI and Crew AI for comprehensive task analysis and project planning in software development. This system leverages a suite of specialized AI agents to process, analyze, and manage development tasks.

## Project Goal

To implement an integrated backend system that is:
- **Robust**: Reliably processes and responds to API requests.
- **Performant**: Optimized for low-latency, especially for real-time AI decision-making.
- **Extensible**: Modular design for easy addition of new AI functionalities or services.
- **User-Friendly**: Clear API documentation and straightforward setup.

## Features

- **AI-Powered Task Analysis**: Categorize, prioritize, and break down tasks using specialized AI agents.
- **User Story Generation**: Automatically create detailed user stories with acceptance criteria.
- **Technical Planning**: Decompose features into actionable technical tasks.
- **Database Schema Suggestions**: Assist in designing database structures based on requirements.
- **Security Insights**: Evaluate potential security implications.
- **QA Strategy Formulation**: Help design comprehensive testing approaches.
- **Project & Infrastructure Planning**: Support for timeline estimation and DevOps considerations.
- **Configurable Agents**: Agent behaviors and configurations can be managed via a database.

## Core Agents

The system utilizes a variety of agents, including but not limited to:

- **Task Analyzer**: Initial categorization and prioritization of tasks.
- **Product Manager**: Focuses on user stories, requirements, and UX aspects.
- **Tech Lead**: Handles technical breakdown, architecture, and code review perspectives.
- **Database Architect**: Assists with database design.
- **QA Strategist**: Develops testing strategies.
- **Security Analyst**: Identifies security requirements and concerns.
- **Project Manager**: Aids in timeline and resource estimation.
- **DevOps Specialist**: Considers deployment and infrastructure planning.

*(Refer to `app/agents/base/agents/` for specific implementations and `create_db.py` for default configurations.)*

## Getting Started

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (for containerized deployment)
- Access to an LLM API (e.g., Gemini) and an API key

### Local Development Setup

1.  **Clone the Repository (if you haven't already):**
    ```bash
    # git clone <repository-url>
    # cd <repository-folder>/backend_2
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python -m venv venv
    ```
    *   On macOS/Linux: `source venv/bin/activate`
    *   On Windows: `venv\Scripts\activate`

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    Copy the example environment file and customize it with your settings:
    ```bash
    cp .env.example .env
    ```
    Edit the `.env` file, ensuring you provide your `GEMINI_API_KEY` and other necessary configurations.
    ```dotenv
    # backend_2/.env
    API_V1_PREFIX=/api/v1
    PROJECT_NAME="AI Task Analysis System"
    DEBUG=true
    LOG_LEVEL=INFO

    BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"] # Adjust if you have a frontend on a different port

    # Database
    DATABASE_URL=sqlite:///./data/app.db # Ensures the DB is created within the 'data' directory

    # AI Settings
    GEMINI_API_KEY=your-gemini-api-key-here

    # Agent Settings
    AGENT_VERBOSE=true
    CREW_VERBOSE=0 # Set to 1 or 2 for more detailed Crew AI logs
    ```

5.  **Initialize the Database:**
    This script creates the necessary database tables (e.g., `app.db` in the `data/` directory) and populates default agent configurations.
    ```bash
    python create_db.py
    ```
    Ensure the `data/` directory exists or is created by the script if it doesn't. The `.gitignore` should allow the `data` directory but ignore its contents like `*.sqlite3`.

6.  **Run the Development Server:**
    The application will be served by Uvicorn.
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    Or using the Makefile:
    ```bash
    make run
    ```

### Dockerized Deployment

1.  **Ensure `.env` is Configured:**
    The `docker-compose.yml` file uses the `.env` file for environment variables. Make sure it's correctly set up as per step 4 above.

2.  **Build and Run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    Or using the Makefile:
    ```bash
    make docker-up
    ```
    This command will build the Docker image (if not already built or if changes are detected) and start the `api` service. The application will be accessible at `http://localhost:8000`.
    Data will be persisted in the `data/` volume, and logs in the `logs/` volume, as defined in `docker-compose.yml`.

## API Documentation

Once the application is running (either locally or via Docker), interactive API documentation will be available at:

-   **Swagger UI**: `http://localhost:8000/docs`
-   **ReDoc**: `http://localhost:8000/redoc`
-   **Health Check**: `http://localhost:8000/health`

## Usage Example (Conceptual Python Client)

```python
import httpx
import asyncio

BASE_URL = "http://localhost:8000/api/v1" # Adjust if your prefix or port differs

async def analyze_new_task():
    async with httpx.AsyncClient() as client:
        task_data = {
            "description": "Implement a new feature for user profile editing.",
            "user_story": "As a registered user, I want to be able to edit my profile information so that I can keep my details up to date.",
            "context": "This is a high-priority feature requested by several key stakeholders."
            # Add other relevant fields as defined in your API schemas
        }
        try:
            # Assuming you have an endpoint like /tasks/analyze
            response = await client.post(f"{BASE_URL}/tasks/analyze", json=task_data) # Replace with actual endpoint
            response.raise_for_status() # Raise an exception for HTTP errors
            
            analysis_result = response.json()
            print("Task Analysis Result:")
            print(analysis_result)
            
        except httpx.HTTPStatusError as e:
            print(f"Error analyzing task: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_new_task())
```
*(Note: The actual API endpoint for task submission and the exact request/response structure should be verified against `app/api/v1/endpoints/tasks.py` and `app/api/v1/schemas.py`.)*

## Project Structure Overview

```
backend_2/
├── app/                    # Main application source code
│   ├── main.py             # FastAPI application entry point
│   ├── agents/             # Crew AI agent definitions
│   ├── api/                # API endpoints and schemas
│   ├── core/               # Core logic (config, DB, logging)
│   ├── services/           # Business logic services
│   └── utils/              # Utility modules
├── data/                   # Data storage (e.g., SQLite DB) - gitignored content
├── logs/                   # Log files - gitignored content
├── tests/                  # Automated tests
│   ├── unit/
│   └── integration/
├── .dockerignore           # Specifies files to ignore for Docker builds
├── .env                    # Local environment variables (gitignored)
├── .env.example            # Example environment variables
├── create_db.py            # Database initialization script
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker image definition
├── Makefile                # Common development commands
├── README.md               # This file
├── requirements.prod.txt   # Production dependencies
└── requirements.txt        # Development and testing dependencies
```

## Development Practices

### Running Tests

Execute tests using Pytest:
```bash
pytest
```
Or via the Makefile:
```bash
make test
```

### Code Style and Linting

This project aims to follow standard Python coding conventions (PEP8).
-   **Formatting**: Consider using a tool like Black.
-   **Linting**: Consider using a tool like Ruff or Flake8.
-   **Type Checking**: Consider using MyPy.

Example commands (if tools are installed and configured):
```bash
# black .
# ruff check .
# mypy .
```

## Makefile Commands

The `Makefile` provides shortcuts for common operations:

-   `make setup`: Sets up the development environment (creates venv, installs deps, copies .env).
-   `make run`: Starts the development server with Uvicorn.
-   `make test`: Runs Pytest.
-   `make docker-build`: Builds the Docker image using Docker Compose.
-   `make docker-up`: Starts the Docker containers in detached mode.
-   `make docker-down`: Stops and removes the Docker containers.
-   `make clean`: Cleans up generated files like `__pycache__`, `.pytest_cache`, etc.