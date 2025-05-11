# Project Report: AI-Powered Task Assistant (Full-Stack)

## 1. Introduction

This report details the development of the AI-Powered Task Assistant, a full-stack application featuring a FastAPI backend and a Next.js (React) frontend. The backend is designed to automatically categorize and prioritize tasks using AI, leveraging Crew AI for orchestrating AI agents and OpenAI's language models for analysis. The frontend provides a user interface for creating and viewing these tasks.

The primary goal was to create a cohesive system where users can submit task descriptions through a web interface, have the backend intelligently assign a relevant category and priority level, store this information, and display it back to the user.

## 2. Project Setup and Structure

### 2.1. Initial Setup

*   **Backend:**
    *   Language/Framework: Python 3.11 with FastAPI.
    *   Virtual Environment: Managed using `venv`.
    *   Dependencies: Listed in `backend/requirements.txt`, including `fastapi`, `uvicorn`, `crewai`, `openai`, `databases[sqlite]`, `pytest`, `ruff`.
*   **Frontend:**
    *   Framework/Library: Next.js with React.
    *   Language: TypeScript.
    *   Package Manager: `pnpm`.
    *   Dependencies: Listed in `frontend/package.json`, including `next`, `react`, `tailwindcss`, `lucide-react`, and UI components from `shadcn/ui`.
*   **Environment Configuration:**
    *   Backend: Using `.env` files (via `python-dotenv`) for managing `OPENAI_API_KEY` and `DATABASE_URL`. An `.env.example` is provided in the root.
    *   Frontend: Can use `frontend/.env.local` for `NEXT_PUBLIC_API_URL` if the backend API URL needs to be overridden from the default.

### 2.2. Directory Structure

The project follows a modular structure separating backend and frontend concerns:

```
.
├── backend/                # Backend FastAPI application
│   ├── app/                # Main application code
│   │   ├── main.py         # FastAPI app initialization, DB connection events
│   │   ├── agents/         # Definitions for Crew AI agents
│   │   ├── api/            # API related modules (schemas, endpoints)
│   │   ├── core/           # Core application logic (DB, config)
│   │   └── services/       # Business logic layer (TaskAnalysisService)
│   ├── tests/              # Automated tests for backend
│   ├── .dockerignore
│   ├── requirements.txt
│   └── ...                 # (Dockerfile for backend is at root for Docker Compose context)
├── frontend/               # Frontend Next.js application
│   ├── app/                # Next.js app router (pages, layouts)
│   ├── components/         # React components (UI, forms)
│   ├── lib/                # Frontend libraries (api calls, context)
│   ├── public/             # Static assets
│   ├── .gitignore
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── tsconfig.json
│   └── ...
├── .github/workflows/      # GitHub Actions CI configuration
│   └── ci.yml
├── .env.example            # Example environment variables for backend
├── .gitignore              # Root .gitignore
├── Dockerfile              # Dockerfile for the backend API service
├── docker-compose.yml      # Docker Compose for running all services
├── Makefile                # (Optional) For common development commands
├── README.md               # Project overview and setup instructions
└── REPORT.md               # This report
```

## 3. Core Components

### 3.1. Backend (FastAPI)

#### 3.1.1. FastAPI Application (`backend/app/main.py`)
*   Initializes the FastAPI application.
*   Includes the API router for task endpoints.
*   Manages database connection lifecycle.
*   Configures CORS middleware to allow requests from the frontend.

#### 3.1.2. Database (`backend/app/core/db.py`)
*   Uses SQLAlchemy core for defining the `tasks` table schema.
*   Employs the `databases` library for asynchronous database interactions with SQLite.
*   `DATABASE_URL` is configurable, defaulting to a local SQLite file (e.g., `sql_app.db`).

#### 3.1.3. Pydantic Schemas (`backend/app/api/v1/schemas.py`)
*   Defines schemas (`TaskBase`, `TaskCreate`, `Task`) for request validation and response serialization.

#### 3.1.4. AI Agent (`backend/app/agents/task_analyzer_agent.py`)
*   Defines the `TaskAnalyzerAgent` using Crew AI.
*   Goal: Analyze task details to determine 'category' and 'priority', outputting a JSON string.

#### 3.1.5. Task Service (`backend/app/services/task_service.py`)
*   `TaskAnalysisService` encapsulates interaction with the Crew AI agent.
*   Handles constructing the AI task, invoking the crew, and parsing the JSON response.

#### 3.1.6. API Endpoints (`backend/app/api/v1/endpoints/tasks.py`)
*   Provides CRUD operations for tasks (`POST /`, `GET /`, `GET /{task_id}`).
*   Integrates with `TaskAnalysisService` for AI processing during task creation.

### 3.2. Frontend (Next.js)

#### 3.2.1. Application Structure (`frontend/app/`)
*   Uses Next.js App Router for defining pages (e.g., home, create task, task list).
*   Global layout (`layout.tsx`) and styling (`globals.css`).

#### 3.2.2. UI Components (`frontend/components/`)
*   Reusable React components built with TypeScript, Tailwind CSS, and Shadcn/ui.
*   Includes `CreateTaskForm.tsx`, `TaskList.tsx`, `TaskDetails.tsx`, `Navbar.tsx`, etc.

#### 3.2.3. State Management (`frontend/lib/task-context.tsx`)
*   React Context (`TaskContext`) for managing global task state (tasks list, loading status, errors, last created task).
*   Provides `useTaskContext` hook for easy access to task data and operations like `refreshTasks`.

#### 3.2.4. API Interaction (`frontend/lib/api.ts`)
*   Functions for making HTTP requests to the backend API (e.g., `fetchTasks`, `createTask`).
*   Handles base URL configuration (defaulting to `http://localhost:8000/api/v1`).

## 4. Backend Testing Strategy

*   **Unit Tests (`backend/tests/unit/`)**:
    *   `test_task_service.py`: Tests `TaskAnalysisService`, mocking `crew.kickoff()` to isolate service logic. Covers success, JSON parsing issues, AI errors, and missing API key scenarios.
*   **Integration Tests (`backend/tests/integration/`)**:
    *   `test_task_api.py`: Tests API endpoints with a separate test database. Makes real OpenAI calls if `OPENAI_API_KEY` is available. Covers task creation (with AI analysis), retrieval, and error handling.
*   **Test Runner:** `pytest` with `pytest-asyncio`.

*(Frontend testing was not implemented within the scope of this phase but is a key area for future enhancement.)*

## 5. Dockerization and CI/CD

### 5.1. Docker

*   **`Dockerfile` (root):** Defines the image for the backend FastAPI application.
*   **`docker-compose.yml`:**
    *   Defines two services: `api` (backend) and `web` (frontend).
    *   The `api` service builds from the root `Dockerfile`.
    *   The `web` service builds from a Dockerfile typically located within `frontend/` (or uses a pre-built Node image and mounts code).
    *   Manages networking between services.
    *   Handles environment variables and volume mounts for data persistence and live reloading.
*   **`.dockerignore` files:** In root (for backend) and `frontend/` to optimize build contexts.

### 5.2. CI (GitHub Actions)

*   Workflow in `.github/workflows/ci.yml` focusing on the backend.
*   Triggers on pushes/pulls to main branches.
*   Jobs: Python setup, dependency installation, linting (Ruff), and Pytest execution.
*   Requires `OPENAI_API_KEY` as a GitHub secret for integration tests.

## 6. Challenges and Solutions

*   **Backend - LLM Output Consistency:** LLMs can produce non-JSON or verbose output.
    *   **Solution:** Specific agent prompting for JSON. Robust JSON parsing in `TaskAnalysisService` to extract JSON from potentially larger strings.
*   **Backend - Managing API Keys:** Securely handling `OPENAI_API_KEY`.
    *   **Solution:** `.env` files (gitignored) for local development; GitHub Secrets for CI.
*   **Backend - Synchronous Crew AI in Async FastAPI:** Crew AI's `kickoff()` is synchronous.
    *   **Solution (Project Scope):** Called directly. Noted that for production, `run_in_executor` would be needed.
*   **Backend - Test Database Management:** Ensuring isolated test environments.
    *   **Solution:** Separate test database file for integration tests, managed by pytest fixtures.
*   **Frontend - CORS:** Frontend (on port 3000) making requests to backend (on port 8000).
    *   **Solution:** Implemented `CORSMiddleware` in the FastAPI backend to allow requests from the frontend's origin.
*   **Frontend - State Management & Re-rendering Loops:**
    *   **Challenge:** Initial "Maximum update depth exceeded" error due to `useEffect` dependencies and function re-creation in context.
    *   **Solution:** Stabilized the `refreshTasks` function in `TaskContext` using `useCallback` to prevent unnecessary re-renders and infinite loops.
    *   **Challenge:** AI analysis results not showing immediately after task creation.
    *   **Solution:** Ensured `CreateTaskForm` correctly used the `lastCreatedTask` state from `TaskContext` (which is updated *after* the `await createTask()` API call resolves) rather than misusing the setter function or an outdated state. The `await` on the API call was key to ensuring data was available before attempting to display it.

## 7. Conclusion

The AI-Powered Task Assistant project successfully integrates a FastAPI backend with Crew AI and a Next.js frontend to deliver a functional full-stack application. It demonstrates intelligent task processing, persistent storage, and a user-friendly interface. The system is containerized using Docker for ease of deployment and includes a CI pipeline for backend validation.

Key learnings include managing AI output variability, handling asynchronous operations across the stack, and addressing React-specific rendering and state management challenges. While the current version provides a solid foundation, future enhancements like frontend testing, user authentication, and more advanced AI capabilities could further improve the application.
