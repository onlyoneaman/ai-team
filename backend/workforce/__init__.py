"""
AI Workforce - Generic Multi-Agent System
Agents are company-agnostic and receive context at runtime.
"""

from .team import create_workforce, AgentHierarchy, WorkforceContext
from .tools import create_tools

__all__ = ["create_workforce", "create_tools", "AgentHierarchy", "WorkforceContext"]
