"""
Core orchestration module.
Provides a transport-agnostic interface for running agent workflows.
"""

from .session import Session, SessionEvent, EventType

__all__ = ["Session", "SessionEvent", "EventType"]
