"""
API Routes aggregation.
"""

from fastapi import APIRouter

from .health import router as health_router
from .chat import router as chat_router
from .company import router as company_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(chat_router)
api_router.include_router(company_router)

__all__ = ["api_router"]
