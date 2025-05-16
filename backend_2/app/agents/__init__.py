"""
Multi-agent task analysis system with specialized agents for different aspects
of software development and project management.
"""

from .base import (
    AgentBase,
    TaskAnalyzerAgent,
    ProductAgents,
    TechnicalAgents,
    OperationsAgents,
    QualityAgents
)

__version__ = '1.0.0'

__all__ = [
    'AgentBase',
    'TaskAnalyzerAgent',
    'ProductAgents',
    'TechnicalAgents',
    'OperationsAgents',
    'QualityAgents',
]

# Version information
VERSION_INFO = {
    'version': __version__,
    'requires': [
        'crewai',
        'langchain-community',
        'python-dotenv'
    ]
}
