"""
Chat routes - main conversation endpoints.
"""

from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from config import get_suggested_prompts, load_company_data, list_companies
from workforce import create_workforce
from schemas import ChatRequest, ChatResponse
from core import Session

router = APIRouter(prefix="/api", tags=["chat"])

# Default company (first available)
DEFAULT_COMPANY = None


def _get_default_company() -> str:
    """Get default company ID."""
    global DEFAULT_COMPANY
    if DEFAULT_COMPANY is None:
        companies = list_companies()
        DEFAULT_COMPANY = companies[0] if companies else "solaris"
    return DEFAULT_COMPANY


def _load_for_request(company_id: str | None):
    """Load company data and create workforce for a request."""
    company_id = company_id or _get_default_company()

    try:
        company_data = load_company_data(company_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Company '{company_id}' not found"
        )

    workforce = create_workforce(company_data)
    return company_data, workforce["entry_agent"]


@router.post("/companies/{company_id}/chat")
async def chat_with_company(company_id: str, request: ChatRequest):
    """
    Chat with a specific company's workforce.
    Returns SSE stream if stream=True, otherwise returns complete response.
    """
    company_data, entry_agent = _load_for_request(company_id)

    if request.stream:
        return StreamingResponse(
            _stream_chat(request.message, company_data, entry_agent),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    return await _process_chat(request.message, company_data, entry_agent)


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat with default company's workforce.
    Use /api/companies/{company_id}/chat for specific company.
    """
    company_data, entry_agent = _load_for_request(request.company_id)

    if request.stream:
        return StreamingResponse(
            _stream_chat(request.message, company_data, entry_agent),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    return await _process_chat(request.message, company_data, entry_agent)


@router.get("/companies/{company_id}/suggested-prompts")
async def suggested_prompts_for_company(company_id: str):
    """Get suggested prompts for a specific company."""
    company_data, _ = _load_for_request(company_id)
    return {"prompts": get_suggested_prompts(company_data)}


@router.get("/suggested-prompts")
async def suggested_prompts():
    """Get suggested prompts for default company."""
    company_data, _ = _load_for_request(None)
    return {"prompts": get_suggested_prompts(company_data)}


async def _stream_chat(
    message: str,
    company_data: dict,
    entry_agent,
) -> AsyncGenerator[str, None]:
    """Stream agent execution with real-time updates via SSE."""
    session = Session(
        company_data=company_data,
        entry_agent=entry_agent,
        save_artifacts=True,
    )

    async for event in session.run_stream(message):
        yield event.to_sse()


async def _process_chat(
    message: str,
    company_data: dict,
    entry_agent,
) -> ChatResponse:
    """Non-streaming chat processing."""
    session = Session(
        company_data=company_data,
        entry_agent=entry_agent,
        save_artifacts=True,
    )

    try:
        result = await session.run(message)

        return ChatResponse(
            response=result.response,
            steps=[e.to_dict() for e in result.events],
            agents_involved=result.agents_involved,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
