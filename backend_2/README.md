# AI Task Analysis System

A sophisticated multi-agent system for comprehensive task analysis and project planning in software development.

## Features

- **Task Analysis**: Categorize and prioritize tasks using AI
- **User Story Generation**: Create detailed user stories with acceptance criteria
- **Technical Planning**: Break down features into technical tasks
- **Database Design**: Generate database schemas based on requirements
- **Security Analysis**: Evaluate security implications and requirements
- **QA Strategy**: Design comprehensive testing approaches
- **Project Planning**: Estimate timelines and resource requirements
- **Infrastructure Planning**: Plan deployment and DevOps requirements

## Agents

- **Task Analyzer**: Categorizes and prioritizes tasks
- **Product Manager**: Generates user stories and requirements
- **UX Designer**: Analyzes user experience implications
- **Database Architect**: Designs database schemas
- **Tech Lead**: Breaks down features into tasks
- **Code Reviewer**: Analyzes code quality
- **QA Strategist**: Designs test strategies
- **Security Analyst**: Evaluates security requirements
- **Project Manager**: Estimates timelines
- **DevOps Specialist**: Plans infrastructure

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Configure the database:
   ```bash
   python create_db.py
   ```

5. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Usage Example

```python
from app.agents import TaskAnalyzerAgent, ProductAgents, TechnicalAgents

# Initialize agents
task_analyzer = TaskAnalyzerAgent()
product_agents = ProductAgents()
tech_agents = TechnicalAgents()

# Analyze a task
task_details = {
    "description": "Add dark mode support",
    "user_story": "As a user, I want dark mode for better nighttime viewing",
    "context": "Users have requested this feature frequently"
}

# Get task analysis
analysis = await task_analyzer.analyze_task(
    description=task_details["description"],
    user_story=task_details["user_story"],
    context=task_details["context"]
)

# Generate user stories
stories = await product_agents.generate_user_stories(
    feature_description=task_details["description"],
    context=task_details["context"]
)

# Break down into technical tasks
tasks = await tech_agents.break_down_tasks(
    feature_description=task_details["description"],
    user_stories=stories["user_stories"],
    database_design={}
)
```

## Project Structure

```
backend_2/
├── app/
│   ├── agents/
│   │   ├── base/
│   │   │   ├── agent_base.py
│   │   │   └── agents/
│   │   │       ├── task_analyzer_agent.py
│   │   │       ├── product_agents.py
│   │   │       ├── technical_agents.py
│   │   │       ├── operations_agents.py
│   │   │       └── quality_agents.py
│   ├── api/
│   ├── core/
│   └── services/
├── tests/
├── requirements.txt
└── README.md
```

## Development

### Running Tests

```bash
pytest
```

### Code Style

The project uses:
- Black for code formatting
- Ruff for linting
- MyPy for type checking

```bash
# Format code
black .

# Lint code
ruff check .

# Type check
mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[MIT License](LICENSE)
