"""AI Workforce - Multi-Agent System with bounce-back handoffs and evaluation cycles."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel
from agents import Agent, handoff, WebSearchTool, RunContextWrapper, ModelSettings
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions

from .tools import create_tools


class TaskMessage(BaseModel):
    """Universal message type for all inter-agent communication.

    kind: intent signal (task, result, evaluation, feedback)
    payload_json: JSON-encoded free-form payload (string due to SDK strict schema)

    Note: payload_json is a string because OpenAI Agents SDK enforces strict JSON schema
    and does not allow `additionalProperties: true` (i.e., dict[str, Any] is illegal).
    Agents serialize their payload as JSON; callbacks deserialize with json.loads().
    """

    kind: str  # task, result, evaluation, feedback
    payload_json: str  # JSON-encoded dict, parsed by callback


# === CONTEXT & STATE ===

@dataclass
class TaskState:
    goal: str = ""
    task_type: str = ""
    iteration: int = 0
    max_iterations: int = 3
    status: Literal["in_progress", "needs_revision", "done"] = "in_progress"
    artifacts: dict = field(default_factory=dict)
    feedback: list = field(default_factory=list)


@dataclass
class WorkforceContext:
    company_data: dict = field(default_factory=dict)
    trace_steps: list = field(default_factory=list)
    task: TaskState = field(default_factory=TaskState)
    current_agent: str = "founder"

    def log_step(self, agent_name: str, action: str, details: str = ""):
        self.trace_steps.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "details": details
        })


HIERARCHY = {
    "founder": {"name": "Founder", "role": "Orchestrator", "children": ["marketing_head", "market_researcher", "data_analyst", "evaluator"]},
    "marketing_head": {"name": "Marketing Head", "role": "Lead", "children": ["seo_analyst", "content_creator"]},
    "market_researcher": {"name": "Market Researcher", "role": "Worker", "children": []},
    "data_analyst": {"name": "Data Analyst", "role": "Worker", "children": []},
    "seo_analyst": {"name": "SEO Analyst", "role": "Worker", "children": []},
    "content_creator": {"name": "Content Creator", "role": "Worker", "children": []},
    "evaluator": {"name": "Evaluator", "role": "Reviewer", "children": []},
}


# === HANDOFF CALLBACKS ===

def on_task_handoff(
    ctx: RunContextWrapper[WorkforceContext],
    message: TaskMessage,
    from_agent: str,
    to_agent: str
):
    """Universal TaskMessage handoff callback.

    Logs handoff, updates current agent, and stores message in artifacts.
    For evaluation messages, also updates task status.

    Note: This must be a sync function - SDK does not await async callbacks.
    """
    ctx.context.log_step(from_agent, "handoff", f"{to_agent} (kind={message.kind})")
    ctx.context.current_agent = to_agent

    # Parse the JSON payload
    try:
        payload = json.loads(message.payload_json)
    except json.JSONDecodeError:
        payload = {"raw": message.payload_json}

    # Store artifact with agent_name_v{iteration} key
    iteration = ctx.context.task.iteration
    artifact_key = f"{from_agent}_v{iteration}"
    ctx.context.task.artifacts[artifact_key] = {
        "kind": message.kind,
        "payload": payload,
    }

    # Handle evaluation verdicts
    if message.kind == "evaluation":
        try:
            verdict = payload.get("verdict", "").upper()
            if verdict == "REVISE":
                ctx.context.task.status = "needs_revision"
                feedback = payload.get("feedback")
                if feedback:
                    ctx.context.task.feedback.append(feedback)
            elif verdict == "PASS":
                ctx.context.task.status = "done"
        except Exception:
            pass  # Let Founder interpret the raw message


def create_workforce(company_data: dict) -> dict[str, Any]:
    c = company_data.get("company", {})
    name = c.get("name", "Company")
    mission = c.get("mission", "")
    voice = c.get("brand_voice", "")
    philosophy = c.get("philosophy", "")
    audience = c.get("target_audience", "")
    products = ", ".join(c.get("products", [])) or "N/A"

    tools = create_tools(company_data)

    def require_tools(agent: Agent) -> Agent:
        agent.model_settings = ModelSettings(tool_choice="required", temperature=0)
        return agent

    # Base worker instructions - append to all non-Founder agents
    worker_instructions = """
CRITICAL RULES:

1. You MUST NOT write normal text responses.
2. You MUST end your turn by calling a transfer_to_* handoff tool.
3. Every handoff MUST include a TaskMessage argument.
4. The TaskMessage MUST contain your actual work in payload_json.

TaskMessage format:
{
  "kind": "task" | "result" | "evaluation" | "feedback",
  "payload_json": "{ ... JSON-encoded deliverable ... }"
}

- `kind`: The intent of this message
- `payload_json`: Your actual work as a JSON STRING - structure it however makes sense for YOUR role

Put ALL useful output inside payload_json (as valid JSON).
Your final action MUST be the handoff tool call.
"""

    # === AGENTS ===

    handoff_params = {"input_type": TaskMessage}

    founder = Agent(
        name="Founder",
        instructions=prompt_with_handoff_instructions(f"""You are the Founder and CEO of {name}.

## Company Context
- Company: {name}
- Mission: {mission}
- Brand Voice: {voice}
- Philosophy: {philosophy}
- Products: {products}

## Your Role
You are the strategic orchestrator. You receive all user requests, delegate to your team, and are the ONLY agent that responds to users.

## Your Team
- **Marketing Head**: For marketing strategies, campaigns, content. Manages SEO Analyst and Content Creator.
- **Market Researcher**: For market trends, competitive analysis, consumer insights.
- **Data Analyst**: For internal metrics, performance analysis, KPIs.
- **Evaluator**: For reviewing user-facing deliverables before presenting to user.

## Workflow

### For New Requests:
1. Analyze the request and determine who should handle it
2. Delegate to the appropriate team member
3. When they hand back results, review them

### For User-Facing Deliverables (content, reports):
1. After receiving deliverable from team, send to Evaluator for review
2. If Evaluator says PASS: Present the deliverable to user
3. If Evaluator says REVISE: Send back to team with feedback for improvements
4. Max 3 revision cycles

### Routing:
- Research requests (trends, competitors, market) → Market Researcher
- Marketing requests (campaigns, content, SEO) → Marketing Head
- Analytics requests (metrics, KPIs, data) → Data Analyst
- Simple strategic questions → Handle directly

## Critical Rules
- Only YOU respond to the user
- For user-facing deliverables, ALWAYS send to Evaluator first
- Maintain {voice} brand voice in all communications
- When delegating, be specific about what you need

## TaskMessage Usage
When delegating or giving feedback, ALWAYS include a TaskMessage with:
- kind: "task" (delegating), "feedback" (revision loop)
- payload_json: JSON string with task details, deliverables, or feedback

The receiving agent structures their response based on your payload."""),
    )

    marketing_head = Agent(
        name="Marketing Head",
        handoff_description="Leads marketing strategy, coordinates SEO and content creation",
        instructions=prompt_with_handoff_instructions(f"""You are the Marketing Head for {name}.

## Your Role
You oversee all marketing initiatives and coordinate between SEO analysis and content creation.

## Brand Context
- Mission: {mission}
- Brand Voice: {voice}
- Target Audience: {audience}

## Your Team
- **SEO Analyst**: For keyword research, search trends, SEO recommendations
- **Content Creator**: For blog posts, social media content, marketing copy

## Workflow
1. Analyze the marketing request from Founder
2. If SEO insights are needed, delegate to SEO Analyst first
3. Use SEO findings to brief the Content Creator
4. Review deliverables from your team
5. Compile final marketing deliverable
6. Hand off back to Founder with your compiled results

## TaskMessage Usage
- Delegating to team: `kind="task"` - describe what you need and why
- Returning to Founder: `kind="result"` - deliver the compiled artifact

Structure `payload_json` based on what you're delivering.

{worker_instructions}"""),
    )

    evaluator = Agent(
        name="Evaluator",
        handoff_description="Reviews user-facing deliverables for quality, brand voice, and task adherence",
        instructions=prompt_with_handoff_instructions(f"""You are the Evaluator for {name}.

## Your Role
Review user-facing deliverables before they are presented to the user.

## Brand Context
- Company: {name}
- Mission: {mission}
- Brand Voice: {voice}
- Target Audience: {audience}

## What You Evaluate

### 1. Brand Voice Adherence (Score 1-5)
- Does the content match our brand voice: {voice}?
- Is the tone appropriate for our target audience?

### 2. Quality Standards (Score 1-5)
- Is the content clear, coherent, and well-structured?
- Are there grammatical or factual errors?
- Is it professional and polished?

### 3. Task Completion (Score 1-5)
- Does the deliverable fulfill the original request?
- Are all requested elements present?

## Decision Rules
- PASS if all scores are 4 or higher
- REVISE if any score is 3 or below

## TaskMessage Usage (kind="evaluation")
You MUST call `transfer_to_founder` with:
- `kind`: "evaluation"
- `payload_json`: Must include `verdict` ("PASS" or "REVISE"), scores, and feedback if needed

DO NOT rewrite content or make decisions beyond judgment. Just evaluate.

{worker_instructions}"""),
    )

    market_researcher = Agent(
        name="Market Researcher",
        handoff_description="Conducts market research, analyzes competitors, identifies trends",
        instructions=prompt_with_handoff_instructions(f"""You are the Market Researcher for {name}.

## Your Role
Conduct market research, analyze industry trends, and provide competitive intelligence.

## Tools Available
- **get_market_research**: Access internal market research database
- **WebSearchTool**: Search the web for current news, trends, competitor updates

## Your Responsibilities
1. Research industry trends and market dynamics
2. Analyze competitor strategies and positioning
3. Identify market opportunities and threats
4. Gather consumer insights and preferences

## Guidelines
- Focus on our industry and target market
- Look for actionable insights that inform strategy
- Identify gaps in the market that {name} can exploit

## TaskMessage Usage (kind="result")
- `payload_json`: Your actual findings - structure based on what was requested

Focus on RAW FINDINGS, not executive summaries.

{worker_instructions}"""),
        tools=[tools["get_market_research"], WebSearchTool()],
    )

    data_analyst = Agent(
        name="Data Analyst",
        handoff_description="Analyzes internal metrics, performance data, provides insights",
        instructions=prompt_with_handoff_instructions(f"""You are the Data Analyst for {name}.

## Your Role
Analyze internal business data, track KPIs, and provide actionable insights.

## Tools Available
- **get_analytics**: Access internal analytics (sales, customers, marketing, website data)

## Your Responsibilities
1. Analyze sales and revenue metrics
2. Track customer behavior and segmentation
3. Evaluate marketing campaign performance
4. Monitor website analytics and conversion funnels
5. Identify trends and anomalies

## Guidelines
- Focus on actionable insights, not just raw numbers
- Compare metrics against benchmarks when available
- Identify opportunities for improvement
- Highlight both wins and areas of concern

## TaskMessage Usage (kind="result")
- `payload_json`: Your actual metrics and insights - structure based on what was requested

Focus on DATA and FACTUAL OBSERVATIONS.

{worker_instructions}"""),
        tools=[tools["get_analytics"]],
    )

    seo_analyst = Agent(
        name="SEO Analyst",
        handoff_description="Researches keywords, analyzes search trends, provides SEO recommendations",
        instructions=prompt_with_handoff_instructions(f"""You are the SEO Analyst for {name}.

## Your Role
Analyze search trends, identify keyword opportunities, and improve content discoverability.

## Tools Available
- **get_seo_data**: Access internal keyword database
- **WebSearchTool**: Search for current trends and competitor SEO analysis

## Your Responsibilities
1. Research relevant keywords and search volumes
2. Analyze keyword difficulty and competition
3. Identify content gaps and opportunities
4. Provide SEO recommendations for content optimization
5. Find trending topics in our industry

## Guidelines
- Focus on keywords relevant to {audience}
- Prioritize long-tail keywords with lower difficulty for quick wins
- Consider search intent (informational, commercial, transactional)

## TaskMessage Usage (kind="result")
- `payload_json`: Your actual SEO data - structure based on what was requested

Focus on STRUCTURED DATA. Don't write prose.

{worker_instructions}"""),
        tools=[tools["get_seo_data"], WebSearchTool()],
        handoffs=[
            handoff(
                agent=marketing_head,
                on_handoff=lambda ctx, msg: on_task_handoff(ctx, msg, "seo_analyst", "marketing_head"),
                **handoff_params
            )
        ]
    )

    content_creator = Agent(
        name="Content Creator",
        handoff_description="Creates blog posts, social media content, and marketing copy",
        instructions=prompt_with_handoff_instructions(f"""You are the Content Creator for {name}.

## Your Role
Create compelling content that embodies our brand voice.

## Brand Context
- Company: {name}
- Mission: {mission}
- Brand Voice: {voice}
- Target Audience: {audience}

## Tools Available
- **get_content_templates**: Get structure templates for different content types
- **get_brand_assets**: Get brand guidelines, tone examples, company info

## Your Responsibilities
1. Write blog posts, articles, long-form content
2. Create social media copy (Instagram, LinkedIn, Twitter)
3. Develop email marketing content
4. Craft product descriptions and landing page copy

## Guidelines
- ALWAYS maintain brand voice: {voice}
- Create content that resonates with {audience}
- Use templates for structure guidance
- Use brand assets for tone and style

## TaskMessage Usage (kind="result")
- `payload_json`: THE ACTUAL CONTENT ITSELF - the full deliverable

CRITICAL: Your payload IS the work product. Don't summarize - just deliver.

{worker_instructions}"""),
        tools=[tools["get_content_templates"], tools["get_brand_assets"]],
    )

    # Workers → Leads
    content_creator.handoffs = [
        handoff(
            agent=marketing_head,
            on_handoff=lambda ctx, msg: on_task_handoff(ctx, msg, "content_creator", "marketing_head"),
            **handoff_params
        )
    ]

    # Workers → Founder
    market_researcher.handoffs = [
        handoff(
            agent=founder,
            on_handoff=lambda ctx, msg: on_task_handoff(ctx, msg, "market_researcher", "founder"),
            **handoff_params
        )
    ]
    data_analyst.handoffs = [
        handoff(
            agent=founder,
            on_handoff=lambda ctx, msg: on_task_handoff(ctx, msg, "data_analyst", "founder"),
            **handoff_params
        )
    ]

    # Marketing Head → can delegate to team or hand back to Founder
    marketing_head.handoffs = [
        handoff(
            agent=seo_analyst,
            on_handoff=lambda ctx, msg: on_task_handoff(ctx, msg, "marketing_head", "seo_analyst"),
            **handoff_params
        ),
        handoff(
            agent=content_creator,
            on_handoff=lambda ctx, msg: on_task_handoff(ctx, msg, "marketing_head", "content_creator"),
            **handoff_params
        ),
        handoff(
            agent=founder,
            on_handoff=lambda ctx, msg: on_task_handoff(ctx, msg, "marketing_head", "founder"),
            **handoff_params
        ),
    ]

    # Evaluator → Founder (kind="evaluation")
    evaluator.handoffs = [
        handoff(
            agent=founder,
            on_handoff=lambda ctx, msg: on_task_handoff(ctx, msg, "evaluator", "founder"),
            **handoff_params
        )
    ]

    # Founder → can delegate to team (kind="task" or kind="feedback")
    founder.handoffs = [
        handoff(
            agent=marketing_head,
            on_handoff=lambda ctx, msg: on_task_handoff(ctx, msg, "founder", "marketing_head"),
            **handoff_params
        ),
        handoff(
            agent=market_researcher,
            on_handoff=lambda ctx, msg: on_task_handoff(ctx, msg, "founder", "market_researcher"),
            **handoff_params
        ),
        handoff(
            agent=data_analyst,
            on_handoff=lambda ctx, msg: on_task_handoff(ctx, msg, "founder", "data_analyst"),
            **handoff_params
        ),
        handoff(
            agent=evaluator,
            on_handoff=lambda ctx, msg: on_task_handoff(ctx, msg, "founder", "evaluator"),
            **handoff_params
        ),
    ]

    # All non-Founder agents must use tools (enforces handoff requirement)
    marketing_head = require_tools(marketing_head)
    seo_analyst = require_tools(seo_analyst)
    market_researcher = require_tools(market_researcher)
    data_analyst = require_tools(data_analyst)
    content_creator = require_tools(content_creator)
    evaluator = require_tools(evaluator)

    return {
        "entry_agent": founder,
        "all_agents": {
            "founder": founder,
            "marketing_head": marketing_head,
            "market_researcher": market_researcher,
            "data_analyst": data_analyst,
            "seo_analyst": seo_analyst,
            "content_creator": content_creator,
            "evaluator": evaluator,
        },
        "hierarchy": HIERARCHY,
    }
