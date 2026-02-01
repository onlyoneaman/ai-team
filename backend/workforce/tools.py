"""
Generic tools for the AI Workforce.
Tools receive company data as a parameter and return closures.
"""

import json
from agents import function_tool


def create_tools(company_data: dict):
    """
    Factory function to create tools bound to specific company data.
    Returns a dict of tool functions.
    """

    market_research = company_data.get("market_research", {})
    seo_data = company_data.get("seo_data", {})
    brand_assets = company_data.get("brand_assets", {})
    content_templates = company_data.get("content_templates", {})
    analytics = company_data.get("analytics", {})
    company = company_data.get("company", {})

    @function_tool
    def get_market_research() -> str:
        """
        Get all market research data including trends, competitive analysis, and consumer insights.
        Returns the complete market research database as JSON.
        """
        if not market_research:
            return "No market research data available."
        return json.dumps(market_research, indent=2)

    @function_tool
    def get_seo_data() -> str:
        """
        Get all SEO and keyword data including keyword rankings, volumes, difficulty scores, and content gaps.
        Returns the complete SEO database as JSON.
        """
        if not seo_data:
            return "No SEO data available."
        return json.dumps(seo_data, indent=2)

    @function_tool
    def get_brand_assets() -> str:
        """
        Get brand voice examples, tone guidelines, and value propositions.
        Returns complete brand assets as JSON.
        """
        result = {
            "company_info": {
                "name": company.get("name"),
                "brand_voice": company.get("brand_voice"),
                "mission": company.get("mission"),
                "target_audience": company.get("target_audience"),
                "philosophy": company.get("philosophy"),
                "products": company.get("products", []),
            },
            "brand_assets": brand_assets,
        }
        return json.dumps(result, indent=2)

    @function_tool
    def get_content_templates() -> str:
        """
        Get content structure templates and social media best practices.
        Returns all content templates as JSON.
        """
        if not content_templates:
            return "No content templates available."
        return json.dumps(content_templates, indent=2)

    @function_tool
    def get_analytics() -> str:
        """
        Get internal analytics including sales metrics, customer data, marketing performance, and website analytics.
        Returns the complete analytics database as JSON.
        """
        if not analytics:
            return "No analytics data available."
        return json.dumps(analytics, indent=2)

    return {
        "get_market_research": get_market_research,
        "get_seo_data": get_seo_data,
        "get_brand_assets": get_brand_assets,
        "get_content_templates": get_content_templates,
        "get_analytics": get_analytics,
    }
