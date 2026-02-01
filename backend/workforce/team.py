"""
Generic AI Workforce - Multi-Agent System
Creates agents dynamically based on company context.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agents import Agent, handoff, WebSearchTool, RunContextWrapper

from .tools import create_tools


@dataclass
class WorkforceContext:
    """Shared context for workforce agents during a run."""
    company_data: dict = field(default_factory=dict)
    trace_steps: list = field(default_factory=list)

    def log_step(self, agent_name: str, action: str, details: str = ""):
        step = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "details": details
        }
        self.trace_steps.append(step)
        return step


@dataclass
class AgentHierarchy:
    """Describes the agent hierarchy for UI visualization."""
    agents: dict = field(default_factory=dict)

    @staticmethod
    def default():
        return {
            "founder": {
                "name": "Founder",
                "role": "Orchestrator",
                "children": ["marketing_head", "market_researcher", "data_analyst"]
            },
            "marketing_head": {
                "name": "Marketing Head",
                "role": "Lead",
                "children": ["seo_analyst", "content_creator"]
            },
            "market_researcher": {
                "name": "Market Researcher",
                "role": "Worker",
                "children": []
            },
            "data_analyst": {
                "name": "Data Analyst",
                "role": "Worker",
                "children": []
            },
            "seo_analyst": {
                "name": "SEO Analyst",
                "role": "Worker",
                "children": []
            },
            "content_creator": {
                "name": "Content Creator",
                "role": "Worker",
                "children": []
            }
        }


def _create_handoff_callback(from_agent: str, to_agent: str):
    """Factory to create handoff callbacks for tracing."""
    def on_handoff(ctx: RunContextWrapper[WorkforceContext]):
        if ctx.context:
            ctx.context.log_step(from_agent, "handoff", f"Delegating to {to_agent}")
    return on_handoff


def create_workforce(company_data: dict) -> dict[str, Any]:
    """
    Factory function to create a workforce of agents for a specific company.

    Args:
        company_data: Company-specific data including company info, market research, etc.

    Returns:
        Dict with 'entry_agent', 'all_agents', and 'hierarchy'
    """
    company = company_data.get("company", {})
    company_name = company.get("name", "Company")
    mission = company.get("mission", "")
    brand_voice = company.get("brand_voice", "")
    philosophy = company.get("philosophy", "")
    target_audience = company.get("target_audience", "")
    products = company.get("products", [])

    # Create tools bound to this company's data
    tools = create_tools(company_data)

    # =========================================================================
    # WORKER AGENTS
    # =========================================================================

    content_creator = Agent(
        name="Content Creator",
        handoff_description="Creates blog posts, social media content, and marketing copy",
        instructions=f"""
You are the Content Creator for {company_name}.

## Your Role
You create compelling blog posts, social media content, and marketing copy that embodies our brand voice.

## Brand Context
- Company: {company_name}
- Mission: {mission}
- Brand Voice: {brand_voice}
- Target Audience: {target_audience}

## Your Responsibilities
1. Write blog posts, articles, and long-form content
2. Create social media copy (Instagram, LinkedIn, Twitter)
3. Develop email marketing content
4. Craft product descriptions and landing page copy

## Guidelines
- Always maintain our brand voice: {brand_voice}
- Use get_content_templates for structure guidance
- Use get_brand_assets for tone examples and company info
- Create content that resonates with our target audience

## Important
You are a WORKER agent. Once you complete your content creation task, you MUST report your deliverable back so it can be reviewed. Do not attempt to contact the user directly.
""",
        tools=[tools["get_content_templates"], tools["get_brand_assets"]],
    )

    seo_analyst = Agent(
        name="SEO Analyst",
        handoff_description="Researches keywords, analyzes search trends, provides SEO recommendations",
        instructions=f"""You are the SEO Analyst for {company_name}.

## Your Role
You analyze search trends, identify keyword opportunities, and provide SEO recommendations to improve our content's discoverability.

## Your Responsibilities
1. Research relevant keywords and search volumes
2. Analyze keyword difficulty and competition
3. Identify content gaps and opportunities
4. Provide SEO recommendations for content optimization
5. Use web search to find current trending topics

## Tools Available
- get_seo_data: Access our internal keyword database (returns full JSON)
- WebSearchTool: Search the web for current trends and competitor analysis

## Guidelines
- Focus on keywords relevant to our industry and target audience
- Prioritize long-tail keywords with lower difficulty for quick wins
- Always consider search intent (informational, commercial, transactional)

## Important
You are a WORKER agent. Once you complete your SEO analysis, you MUST report your findings back so they can be used by other team members. Do not attempt to contact the user directly.
""",
        tools=[tools["get_seo_data"], WebSearchTool()],
    )

    data_analyst = Agent(
        name="Data Analyst",
        handoff_description="Analyzes internal metrics, performance data, and provides data-driven insights",
        instructions=f"""
You are the Data Analyst for {company_name}.

## Your Role
You analyze internal business data, track KPIs, and provide actionable insights based on performance metrics.

## Your Responsibilities
1. Analyze sales and revenue metrics
2. Track customer behavior and segmentation
3. Evaluate marketing campaign performance
4. Monitor website analytics and conversion funnels
5. Identify trends and anomalies in data

## Tools Available
- get_analytics: Access internal analytics database (returns full JSON with sales, customers, marketing, website data)

## Guidelines
- Focus on actionable insights, not just raw numbers
- Compare metrics against benchmarks when available
- Identify opportunities for improvement
- Highlight both wins and areas of concern

## Important
You are a WORKER agent. Once you complete your analysis, you MUST report your findings back so they can inform strategic decisions. Do not attempt to contact the user directly.
""",
        tools=[tools["get_analytics"]],
    )

    market_researcher = Agent(
        name="Market Researcher",
        handoff_description="Conducts market research, analyzes competitors, identifies trends and opportunities",
        instructions=f"""
You are the Market Researcher for {company_name}.

## Your Role
You conduct market research, analyze industry trends, and provide competitive intelligence to inform strategic decisions.

## Your Responsibilities
1. Research industry trends and market dynamics
2. Analyze competitor strategies and positioning
3. Identify market opportunities and threats
4. Gather consumer insights and preferences
5. Use web search for real-time market intelligence

## Tools Available
- get_market_research: Access our internal market research database (returns full JSON)
- WebSearchTool: Search the web for current news, trends, and competitor updates

## Guidelines
- Focus on our industry and target market
- Look for actionable insights that can inform marketing strategy
- Identify gaps in the market that {company_name} can exploit

## Important
You are a WORKER agent. Once you complete your research, you MUST report your findings back so they can inform strategic decisions. Do not attempt to contact the user directly.
""",
        tools=[tools["get_market_research"], WebSearchTool()],
    )

    # =========================================================================
    # LEAD AGENTS
    # =========================================================================

    marketing_head = Agent(
        name="Marketing Head",
        handoff_description="Leads marketing strategy, coordinates SEO and content creation efforts",
        instructions=f"""
You are the Marketing Head for {company_name}.

## Your Role
You oversee all marketing initiatives and coordinate between SEO analysis and content creation to deliver cohesive marketing strategies.

## Your Team
You can delegate to:
- **SEO Analyst**: For keyword research, search trends, and SEO recommendations
- **Content Creator**: For blog posts, social media content, and marketing copy

## Your Responsibilities
1. Develop marketing strategies aligned with company goals
2. Coordinate SEO and content efforts for maximum impact
3. Review and approve marketing deliverables
4. Report marketing outcomes back to the Founder

## Workflow
1. Analyze the marketing request
2. If SEO insights are needed, delegate to SEO Analyst first
3. Use SEO findings to brief the Content Creator
4. Review deliverables and compile final output
5. Report back to the Founder with completed work

## Brand Context
- Mission: {mission}
- Brand Voice: {brand_voice}
- Target Audience: {target_audience}

## Important
You are a LEAD agent. You coordinate your team but must report final deliverables back to the Founder. Ensure all content aligns with our brand voice.
""",
        handoffs=[
            handoff(
                agent=seo_analyst,
                on_handoff=_create_handoff_callback("Marketing Head", "SEO Analyst"),
            ),
            handoff(
                agent=content_creator,
                on_handoff=_create_handoff_callback("Marketing Head", "Content Creator"),
            ),
        ],
    )

    # =========================================================================
    # ORCHESTRATOR AGENT
    # =========================================================================

    founder = Agent(
        name="Founder",
        instructions=f"""
You are the Founder and CEO of {company_name}.

## Company Context
- **Company**: {company_name}
- **Mission**: {mission}
- **Brand Voice**: {brand_voice}
- **Philosophy**: {philosophy}
- **Products**: {', '.join(products) if products else 'N/A'}

## Your Role
You are the strategic orchestrator of the AI workforce. You receive all user requests and delegate to the appropriate team members based on the nature of the task.

## Your Team
You can delegate to:
- **Marketing Head**: For marketing strategies, campaigns, content planning, and coordinated marketing efforts. The Marketing Head manages SEO Analyst and Content Creator.
- **Market Researcher**: For market trends, competitive analysis, consumer insights, and industry research.
- **Data Analyst**: For internal metrics, performance analysis, KPIs, and data-driven insights.

## Decision Framework
1. **Research requests** (trends, competitors, market analysis) → Delegate to Market Researcher
2. **Marketing requests** (campaigns, content, SEO, social media) → Delegate to Marketing Head
3. **Analytics requests** (metrics, performance, KPIs, data) → Delegate to Data Analyst
4. **Complex requests** requiring multiple perspectives → Coordinate between relevant team members
5. **Strategic questions** about company direction → Handle directly with your expertise

## Workflow
1. Analyze the incoming request
2. Determine which team member(s) are best suited
3. Delegate with clear instructions
4. Synthesize results from your team
5. Provide a cohesive response to the user

## Guidelines
- Always maintain {brand_voice} voice in communications
- Ensure all outputs align with our mission: {mission}
- When in doubt about a request, ask clarifying questions before delegating
""",
        handoffs=[
            handoff(
                agent=marketing_head,
                on_handoff=_create_handoff_callback("Founder", "Marketing Head"),
            ),
            handoff(
                agent=market_researcher,
                on_handoff=_create_handoff_callback("Founder", "Market Researcher"),
            ),
            handoff(
                agent=data_analyst,
                on_handoff=_create_handoff_callback("Founder", "Data Analyst"),
            ),
        ],
    )

    return {
        "entry_agent": founder,
        "all_agents": {
            "founder": founder,
            "marketing_head": marketing_head,
            "market_researcher": market_researcher,
            "data_analyst": data_analyst,
            "seo_analyst": seo_analyst,
            "content_creator": content_creator,
        },
        "hierarchy": AgentHierarchy.default(),
    }
