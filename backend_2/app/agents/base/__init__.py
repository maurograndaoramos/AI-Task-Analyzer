"""
Base package for the multi-agent task analysis system.
Provides the base agent class and specialized agent implementations.
"""

from .agent_base import AgentBase
from .agents import (
    TaskAnalyzerAgent,
    ProductAgents,
    TechnicalAgents,
    OperationsAgents,
    QualityAgents
)

__all__ = [
    'AgentBase',
    'TaskAnalyzerAgent',
    'ProductAgents',
    'TechnicalAgents',
    'OperationsAgents',
    'QualityAgents',
]
