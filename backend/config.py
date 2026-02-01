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


def get_suggested_prompts(company_data: dict) -> list[dict]:
    """
    Generate suggested prompts based on company context.
    """
    company_name = company_data.get("company", {}).get("name", "the company")

    return [
        {
            "label": "Simple Research",
            "prompt": f"Research current industry trends for {company_name}.",
            "complexity": "simple",
            "expected_flow": ["Founder", "Market Researcher", "Founder"],
        },
        {
            "label": "SEO Analysis",
            "prompt": "What keywords should we target for our new product launch?",
            "complexity": "medium",
            "expected_flow": ["Founder", "Marketing Head", "SEO Analyst", "Marketing Head", "Founder"],
        },
        {
            "label": "Content Creation",
            "prompt": "Write a seo-optimized blog post about sustainable practices in our industry.",
            "complexity": "medium",
            "expected_flow": ["Founder", "Marketing Head", "SEO Analyst", "Content Creator", "Marketing Head", "Founder", "Evaluator", "Founder"],
        },
        {
            "label": "Full Marketing Strategy",
            "prompt": "I need a complete marketing strategy and blog post for our new product launch. Include SEO recommendations.",
            "complexity": "complex",
            "expected_flow": [
                "Founder", "Market Researcher", "Founder",
                "Marketing Head", "SEO Analyst", "Content Creator",
                "Marketing Head", "Founder"
            ],
        },
        {
            "label": "Competitive Analysis",
            "prompt": f"Analyze our competitors and identify opportunities for {company_name}.",
            "complexity": "medium",
            "expected_flow": ["Founder", "Market Researcher", "Founder"],
        },
    ]
