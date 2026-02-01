# AI Workforce Orchestrator

Multi-agent system for marketing automation using OpenAI Agents SDK.

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │           Core Session              │
                    │  (Transport-agnostic orchestration) │
                    └──────────────┬──────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
        ┌──────────┐        ┌──────────┐        ┌──────────┐
        │   API    │        │   CLI    │        │  Future  │
        │ (FastAPI)│        │ (Terminal)│       │ (Slack?) │
        └──────────┘        └──────────┘        └──────────┘
```

### Agent Hierarchy

```
User Request
     │
     ▼
┌─────────┐
│ founder │ ◄── Orchestrator (only agent that responds to user)
└────┬────┘
     │
     ├──────────────┬────────────────┬─────────────────┐
     ▼              ▼                ▼                 ▼
┌───────────┐ ┌───────────┐ ┌─────────────┐ ┌───────────────┐
│ marketing │ │  market   │ │    data     │ │   evaluator   │
│   _head   │ │_researcher│ │  _analyst   │ │  (reviewer)   │
└─────┬─────┘ └─────┬─────┘ └──────┬──────┘ └───────┬───────┘
      │             │              │                │
      │             └──► founder ◄─┘ (bounce-back)  │
      │                    ▲                        │
      ├────────┐           │                        ▼
      ▼        ▼           │                    founder
┌─────────┐ ┌─────────┐    │
│   seo   │ │ content │    │
│_analyst │ │_creator │    │
└────┬────┘ └────┬────┘    │
     └──► marketing_head ◄─┘ (bounce-back)
```

**Agent IDs** (snake_case): `founder`, `marketing_head`, `market_researcher`, `data_analyst`, `seo_analyst`, `content_creator`, `evaluator`

## TaskMessage System

All inter-agent communication uses a unified message type:

```python
class TaskMessage(BaseModel):
    kind: str        # "task" | "result" | "evaluation" | "feedback"
    payload_json: str  # JSON-encoded free-form payload
```

### Why `payload_json` is a string

OpenAI Agents SDK enforces strict JSON schema for `input_type`. A `dict[str, Any]` generates `additionalProperties: true` which is rejected. Using a JSON string bypasses this constraint while preserving payload flexibility.

### Message Kinds

| Kind | Direction | Purpose |
|------|-----------|---------|
| `task` | Downward (founder→team) | Delegate work with context |
| `result` | Upward (worker→lead→founder) | Return completed work |
| `evaluation` | evaluator→founder | Judgment with verdict |
| `feedback` | founder→team | Revision instructions |

### Handoff Callback

```python
def on_task_handoff(ctx, message, from_agent, to_agent):
    # Parse payload
    payload = json.loads(message.payload_json)

    # Store artifact
    artifact_key = f"{from_agent}_v{iteration}"
    ctx.context.task.artifacts[artifact_key] = {
        "kind": message.kind,
        "payload": payload,
    }

    # Handle evaluation verdicts
    if message.kind == "evaluation":
        verdict = payload.get("verdict", "").upper()
        if verdict == "PASS":
            ctx.context.task.status = "done"
        elif verdict == "REVISE":
            ctx.context.task.status = "needs_revision"
```

## Core System

The `core/` module provides transport-agnostic orchestration:

```python
from core import Session

session = Session(company_data, entry_agent)

# Streaming
async for event in session.run_stream("Hello"):
    print(event)

# Non-streaming
result = await session.run("Hello")
```

### Session Features

- **Unique run ID** - `{YYYYMMDD}_{HHMMSS}_{microseconds}`
- **Event streaming** - Yields `SessionEvent` objects
- **Artifact logging** - Saves to `tmp/{run_id}/`
- **Duration tracking** - Measures execution time
- **Cost estimation** - USD pricing for token usage

### Artifacts (tmp/{run_id}/)

| File | Contents |
|------|----------|
| `input.txt` | Original user message |
| `events.jsonl` | All events (append-only log) |
| `response.md` | Final agent response |
| `trace.json` | Run summary + handoff trace + usage |
| `conversation.json` | Clean conversation summary |

## Running

### API Server

```bash
cd backend
source .venv/bin/activate
export OPENAI_API_KEY=sk-...
python main.py
```

Server: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

### CLI

```bash
# Interactive mode
python cli.py

# Single query
python cli.py "Research coffee trends"

# Different company
python cli.py --company promptsmint "What keywords should we target?"

# List companies
python cli.py --list-companies
```

## Agent Roles

| Agent ID | Role | Capabilities |
|----------|------|--------------|
| `founder` | Orchestrator | Receives all requests, delegates, manages evaluation cycles |
| `marketing_head` | Lead | Coordinates SEO + Content, reports to founder |
| `evaluator` | Reviewer | Reviews user-facing deliverables (brand voice, quality, task completion) |
| `market_researcher` | Worker | Web search, internal research DB |
| `data_analyst` | Worker | Internal analytics, KPIs, performance metrics |
| `seo_analyst` | Worker | Keyword research, web search |
| `content_creator` | Worker | Blog posts, social media, brand assets |

## Handoff Routes

All handoffs use `TaskMessage` with `input_type=TaskMessage`:

| From | To | Kind |
|------|-----|------|
| `founder` | `marketing_head`, `market_researcher`, `data_analyst`, `evaluator` | `task` or `feedback` |
| `marketing_head` | `seo_analyst`, `content_creator` | `task` |
| `marketing_head` | `founder` | `result` |
| `seo_analyst`, `content_creator` | `marketing_head` | `result` |
| `market_researcher`, `data_analyst` | `founder` | `result` |
| `evaluator` | `founder` | `evaluation` |

## Task State

`WorkforceContext.task` tracks state across handoffs:

| Field | Description |
|-------|-------------|
| `goal` | User's objective (set by founder) |
| `task_type` | content_creation, research, analysis, strategy |
| `iteration` | Current revision cycle (starts 0) |
| `max_iterations` | Max revision attempts (default 3) |
| `status` | in_progress, needs_revision, done |
| `artifacts` | Deliverables keyed by `{agent_id}_v{iteration}` |
| `feedback` | Revision notes from evaluator |

## Evaluation Flow

For user-facing deliverables (content, reports):

1. Team completes work → bounces to founder with `kind="result"`
2. founder → evaluator with `kind="task"`
3. evaluator returns `kind="evaluation"` with:
   - `verdict`: "PASS" or "REVISE"
   - `brand_voice_score`, `quality_score`, `completion_score` (1-5)
   - `feedback` (if REVISE)
4. founder: PASS → respond to user | REVISE → increment iteration, re-delegate with `kind="feedback"`

## Usage & Pricing

Token usage is tracked per run with cost estimation:

```python
from utils import estimate_cost

# In trace.json usage block:
{
  "requests": 4,
  "input_tokens": 6308,
  "output_tokens": 1136,
  "total_tokens": 7444,
  "model": "gpt-4.1",
  "total_estimated_usd_cost": 0.021704
}
```

### Model Pricing (per 1M tokens)

| Model | Input | Output |
|-------|-------|--------|
| `gpt-4.1` (default) | $2.00 | $8.00 |
| `gpt-4.1-mini` | $0.40 | $1.60 |
| `gpt-4.1-nano` | $0.10 | $0.40 |
| `gpt-4o` | $2.50 | $10.00 |
| `gpt-4o-mini` | $0.15 | $0.60 |

## Tools

| Tool | Used By | Source |
|------|---------|--------|
| `get_market_research` | market_researcher | Company JSON |
| `get_seo_data` | seo_analyst | Company JSON |
| `get_brand_assets` | content_creator | Company JSON |
| `get_content_templates` | content_creator | Company JSON |
| `get_analytics` | data_analyst | Company JSON |
| `WebSearchTool` | market_researcher, seo_analyst | OpenAI hosted |

## Adding a New Company

1. Create `data/{company_id}.json`:

```json
{
  "id": "mycompany",
  "company": {
    "name": "My Company",
    "mission": "...",
    "brand_voice": "...",
    "philosophy": "...",
    "target_audience": "...",
    "products": ["..."]
  },
  "market_research": { ... },
  "seo_data": { ... },
  "brand_assets": { ... },
  "content_templates": { ... }
}
```

2. Use it immediately - no server restart needed

## API Reference

### Health

```
GET  /                      # Health check
GET  /health                # Detailed health check
```

### Companies

```
GET  /api/companies                     # List all companies
GET  /api/companies/{id}                # Get company details
GET  /api/companies/{id}/agents         # Get agent hierarchy
GET  /api/companies/{id}/suggested-prompts  # Get demo prompts
```

### Chat (Stateless)

**Per-company endpoint:**
```
POST /api/companies/{company_id}/chat
Content-Type: application/json

{
  "message": "Research coffee trends",
  "stream": true
}
```

**Default company endpoint:**
```
POST /api/chat
Content-Type: application/json

{
  "message": "Research coffee trends",
  "company_id": "solaris",   // optional, uses first available if omitted
  "stream": true
}
```

**SSE Events** (when `stream: true`):
- `start` - Workflow started
- `agent_change` - New agent activated
- `tool_call` - Agent using a tool
- `tool_result` - Tool completed
- `delta` - Streaming text chunk
- `complete` - Final response + all steps
- `artifacts_saved` - Run artifacts saved to tmp/ (includes path)
- `error` - Error occurred

## File Structure

```
backend/
├── main.py                 # App setup, lifespan, middleware (stateless)
├── cli.py                  # Terminal app (same core as API)
├── config.py               # Company loading utilities
├── schemas.py              # Pydantic request/response models
├── utils.py                # Utilities (pricing, etc.)
├── requirements.txt
├── core/
│   ├── __init__.py
│   └── session.py          # Session management, artifact logging
├── routes/
│   ├── __init__.py         # Router aggregation
│   ├── health.py           # Health check endpoints
│   ├── chat.py             # Chat endpoints (per-company)
│   └── company.py          # Company info endpoints
├── data/
│   ├── solaris.json        # Solaris Coffee context
│   └── promptsmint.json    # PromptsMint context
├── workforce/
│   ├── __init__.py
│   ├── team.py             # Agent factory: create_workforce(), TaskMessage
│   └── tools.py            # Tool factory: create_tools()
└── tmp/                    # Run artifacts (gitignored)
    └── {run_id}/
        ├── input.txt
        ├── events.jsonl
        ├── response.md
        ├── trace.json
        └── conversation.json
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `COMPANY_ID` | No | Default company to load (default: first in data/) |

## Key Design Decisions

1. **Unified TaskMessage** - Single message type for all handoffs (`kind` + `payload_json`)
2. **JSON string payload** - Bypasses SDK strict schema while preserving flexibility
3. **Snake_case agent IDs** - Consistent identifiers: `founder`, `data_analyst`, etc.
4. **Stateless API** - Each request specifies company_id, no global state
5. **Parallel-safe** - Multiple companies can run simultaneously
6. **Transport-agnostic core** - Same Session works for API, CLI, or any future integration
7. **Artifact logging** - Every run saves debug info to `tmp/{run_id}/`
8. **Cost tracking** - Token usage with USD cost estimation
9. **Bounce-back handoffs** - Workers always return to their owner with `kind="result"`
10. **Evaluation cycles** - User-facing content goes through evaluator before response

---

*Keep this doc updated when modifying `workforce/team.py` - agent roles, handoffs, or task state.*
