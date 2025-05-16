from typing import List, Union, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings
import os
import json
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AI Task Analysis System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"]
    )
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [i.strip() for i in v.split(",")]
        return v
    
    # Database Settings
    DATABASE_URL: str = Field(
        default="sqlite:///./test.db",
        description="Database connection string"
    )
    
    # Security Settings
    SECRET_KEY: str = Field(
        default="your-super-secret-key-here",
        description="Secret key for JWT token generation"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # LLM Settings
    GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description="Google Gemini API key for LLM services"
    )
    GOOGLE_API_KEY: Optional[str] = Field(
        default=None,
        description="Alternative Google API key"
    )
    
    # Agent Settings
    AGENT_VERBOSE: bool = True
    CREW_VERBOSE: int = Field(
        default=0,
        description="Crew verbosity level (0=minimal, 1=basic, 2=detailed)"
    )
    
    # Logging Settings
    LOG_LEVEL: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # File Storage
    UPLOAD_DIR: Path = Field(
        default=Path("uploads"),
        description="Directory for file uploads"
    )
    MAX_UPLOAD_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum file upload size in bytes"
    )
    
    # Cache Settings
    CACHE_TTL: int = Field(
        default=3600,
        description="Cache time-to-live in seconds"
    )
    
    # Task Analysis Settings
    DEFAULT_TASK_PRIORITY: str = "Medium"
    DEFAULT_TASK_CATEGORY: str = "Feature Request"
    VALID_PRIORITIES: List[str] = ["High", "Medium", "Low"]
    VALID_CATEGORIES: List[str] = [
        "Feature Request",
        "Bug Fix",
        "Documentation",
        "Research",
        "Testing",
        "Chore"
    ]
    
    # Performance Settings
    PERFORMANCE_LOG_INTERVAL: int = Field(
        default=300,
        description="Interval in seconds for performance metric logging"
    )
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        
    @validator("UPLOAD_DIR", pre=True)
    def create_upload_dir(cls, v: Union[str, Path]) -> Path:
        """Ensure upload directory exists."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path
        
    def get_llm_api_key(self) -> Optional[str]:
        """Get the appropriate LLM API key."""
        return self.GEMINI_API_KEY or self.GOOGLE_API_KEY
        
    def validate_priority(self, priority: str) -> str:
        """Validate task priority."""
        if priority not in self.VALID_PRIORITIES:
            return self.DEFAULT_TASK_PRIORITY
        return priority
        
    def validate_category(self, category: str) -> str:
        """Validate task category."""
        if category not in self.VALID_CATEGORIES:
            return self.DEFAULT_TASK_CATEGORY
        return category

# Create global settings instance
settings = Settings()

# Ensure required directories exist
os.makedirs("logs", exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

__all__ = ['settings']
