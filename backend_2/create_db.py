import asyncio
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from app.core.db import metadata, DATABASE_URL

# Load environment variables
load_dotenv()

def init_db():
    """Initialize the database with all tables."""
    print(f"Using database URL: {DATABASE_URL}")
    
    # Create an engine instance
    engine = create_engine(DATABASE_URL)
    
    try:
        # Create all tables
        metadata.create_all(bind=engine)
        print("Successfully created all database tables.")
        
        # List created tables
        table_names = metadata.tables.keys()
        print("\nCreated tables:")
        for table in table_names:
            print(f"  - {table}")
            
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

def setup_default_configs():
    """Set up default agent configurations in the database."""
    engine = create_engine(DATABASE_URL)
    
    default_configs = [
        {
            "agent_type": "task_analyzer",
            "enabled": True,
            "configuration": {
                "categories": ["Bug Fix", "Feature Request", "Documentation", "Research", "Testing", "Chore"],
                "priorities": ["High", "Medium", "Low"]
            }
        },
        {
            "agent_type": "product_manager",
            "enabled": True,
            "configuration": {
                "story_format": "As a {role}, I want to {goal} so that {benefit}",
                "require_acceptance_criteria": True
            }
        },
        {
            "agent_type": "tech_lead",
            "enabled": True,
            "configuration": {
                "task_types": ["backend", "frontend", "database", "testing", "devops"],
                "estimation_unit": "hours"
            }
        },
        {
            "agent_type": "db_architect",
            "enabled": True,
            "configuration": {
                "supported_databases": ["PostgreSQL", "MySQL", "SQLite"],
                "default_field_types": ["string", "integer", "boolean", "datetime", "json"]
            }
        },
        {
            "agent_type": "qa_strategist",
            "enabled": True,
            "configuration": {
                "test_types": ["unit", "integration", "e2e"],
                "coverage_threshold": 80
            }
        },
        {
            "agent_type": "security_analyst",
            "enabled": True,
            "configuration": {
                "security_checks": ["authentication", "authorization", "input_validation", "data_protection"],
                "compliance_standards": ["GDPR", "CCPA"]
            }
        },
        {
            "agent_type": "project_manager",
            "enabled": True,
            "configuration": {
                "sprint_length_weeks": 2,
                "estimation_style": "story_points"
            }
        },
        {
            "agent_type": "devops_specialist",
            "enabled": True,
            "configuration": {
                "deployment_strategies": ["blue-green", "canary", "rolling"],
                "supported_platforms": ["kubernetes", "aws", "gcp"]
            }
        }
    ]
    
    try:
        # Import here to avoid circular imports
        from app.core.db import database, agent_configs
        
        async def insert_configs():
            await database.connect()
            
            # Clear existing configs
            await database.execute(agent_configs.delete())
            
            # Insert default configurations
            for config in default_configs:
                await database.execute(
                    agent_configs.insert().values(
                        agent_type=config["agent_type"],
                        enabled=config["enabled"],
                        configuration=config["configuration"]
                    )
                )
            
            await database.disconnect()
        
        # Run the async function
        asyncio.run(insert_configs())
        print("\nSuccessfully set up default agent configurations.")
        
    except Exception as e:
        print(f"Error setting up default configurations: {e}")
        raise

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("\nSetting up default agent configurations...")
    setup_default_configs()
    print("\nDatabase setup complete!")
