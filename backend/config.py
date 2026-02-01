"""
Configuration and company data loading.
"""

import json
import os
from pathlib import Path
from functools import lru_cache

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Default company to load (can be overridden via environment)
DEFAULT_COMPANY = os.getenv("COMPANY_ID", "solaris")


@lru_cache
def load_company_data(company_id: str | None = None) -> dict:
    """
    Load company data from JSON file.

    Args:
        company_id: ID of the company (filename without .json)

    Returns:
        Company data dict
    """
    company_id = company_id or DEFAULT_COMPANY
    data_file = DATA_DIR / f"{company_id}.json"

    if not data_file.exists():
        raise FileNotFoundError(f"Company data not found: {data_file}")

    return json.loads(data_file.read_text())


def list_companies() -> list[str]:
    """List all available company IDs."""
    return [f.stem for f in DATA_DIR.glob("*.json")]


from utils.prompts import GENERIC_PROMPTS, COMPANY_PROMPTS


def get_suggested_prompts(company_data: dict) -> list[dict]:
    """
    Generate suggested prompts based on company context.
    Returns a mix of company-specific and generic prompts (max 5).
    """
    company_id = company_data.get("id")
    
    # Get company specific prompts
    specific_prompts = COMPANY_PROMPTS.get(company_id, [])
    
    # Start with company specific prompts
    suggested = list(specific_prompts)
    
    # Fill remaining slots with generic prompts
    remaining_slots = 5 - len(suggested)
    if remaining_slots > 0:
        suggested.extend(GENERIC_PROMPTS[:remaining_slots])
        
    return suggested[:5]
