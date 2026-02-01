"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    company_id: str | None = None  # If None, uses default company
    stream: bool = True


class ChatResponse(BaseModel):
    response: str
    steps: list[dict]
    agents_involved: list[str]
    company_id: str | None = None
    run_id: str | None = None


class CompanyInfo(BaseModel):
    id: str
    name: str
    mission: str | None = None
    brand_voice: str | None = None
    target_audience: str | None = None
