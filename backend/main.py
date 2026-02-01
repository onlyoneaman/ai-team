"""
AI Workforce Orchestrator - FastAPI Application
Stateless design: each request specifies its company.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import list_companies
from routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    companies = list_companies()
    print(f"AI Workforce Orchestrator started")
    print(f"Available companies: {', '.join(companies)}")
    yield
    print("Shutting down...")


app = FastAPI(
    title="AI Workforce Orchestrator",
    description="Multi-agent system for marketing automation",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
