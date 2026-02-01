"""
Company and agent routes.
"""

from fastapi import APIRouter, HTTPException

from config import list_companies, load_company_data
from workforce import create_workforce

router = APIRouter(prefix="/api", tags=["company"])


@router.get("/companies")
async def get_companies():
    """List available companies."""
    companies = []
    for company_id in list_companies():
        try:
            data = load_company_data(company_id)
            companies.append({
                "id": company_id,
                "name": data.get("company", {}).get("name", company_id),
            })
        except Exception:
            companies.append({"id": company_id, "name": company_id})

    return {"companies": companies}


@router.get("/companies/{company_id}")
async def get_company(company_id: str):
    """Get company details."""
    try:
        data = load_company_data(company_id)
        return data.get("company", {})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Company '{company_id}' not found")


@router.get("/companies/{company_id}/agents")
async def get_agents(company_id: str):
    """Get agent hierarchy for a company."""
    try:
        data = load_company_data(company_id)
        workforce = create_workforce(data)
        return {
            "company_id": company_id,
            "hierarchy": workforce["hierarchy"],
            "entry_point": "founder",
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Company '{company_id}' not found")
