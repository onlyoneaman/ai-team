"""
Health check routes.
"""

from fastapi import APIRouter

from config import list_companies

router = APIRouter(tags=["health"])


@router.get("/")
async def root():
    """Health check."""
    return {
        "status": "online",
        "service": "AI Workforce Orchestrator",
        "companies": list_companies(),
    }


@router.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "companies_available": list_companies(),
    }
