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
│ Founder │ ◄── Orchestrator (entry point)
└────┬────┘
     │
     ├─────────────────────┬────────────────────┐
     ▼                     ▼                    ▼
┌─────────────┐   ┌──────────────┐   ┌──────────────┐
│ Marketing   │   │   Market     │   │    Data      │
│    Head     │   │  Researcher  │   │   Analyst    │ ◄── Workers
└──────┬──────┘   └──────────────┘   └──────────────┘
       │
       ├────────────────┐
       ▼                ▼
┌─────────────┐   ┌─────────────┐
│ SEO Analyst │   │  Content    │
│             │   │  Creator    │ ◄── Workers
└─────────────┘   └─────────────┘
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

### Artifacts (tmp/{run_id}/)

| File | Contents |
|------|----------|
| `input.txt` | Original user message |
| `events.jsonl` | All events (append-only log) |
| `response.md` | Final agent response |
| `trace.json` | Run summary + handoff trace |
| `handoff_trace.json` | Detailed handoff context |

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

| Agent | Role | Capabilities |
|-------|------|--------------|
| **Founder** | Orchestrator | Receives all requests, delegates to leads/workers |
| **Marketing Head** | Lead | Coordinates SEO + Content, reports to Founder |
| **Market Researcher** | Worker | Web search, internal research DB |
| **Data Analyst** | Worker | Internal analytics, KPIs, performance metrics |
| **SEO Analyst** | Worker | Keyword research, web search |
| **Content Creator** | Worker | Blog posts, social media, brand assets |

## Tools

| Tool | Used By | Source |
|------|---------|--------|
| `get_market_research` | Market Researcher | Company JSON (full data) |
| `get_seo_data` | SEO Analyst | Company JSON (full data) |
| `get_brand_assets` | Content Creator | Company JSON (full data) |
| `get_content_templates` | Content Creator | Company JSON (full data) |
| `get_analytics` | Data Analyst | Company JSON (full data) |
| `WebSearchTool` | Researcher, SEO | OpenAI hosted |

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

### Parallel Requests

Since the API is stateless, you can run multiple companies simultaneously:

```bash
# Terminal 1: Solaris Coffee
curl -X POST http://localhost:8000/api/companies/solaris/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Research trends", "stream": false}'

# Terminal 2: PromptsMint (at the same time)
curl -X POST http://localhost:8000/api/companies/promptsmint/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "SEO keywords", "stream": false}'
```

## File Structure

```
backend/
├── main.py                 # App setup, lifespan, middleware (stateless)
├── cli.py                  # Terminal app (same core as API)
├── config.py               # Company loading utilities
├── schemas.py              # Pydantic request/response models
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
│   ├── team.py             # Agent factory: create_workforce()
│   └── tools.py            # Tool factory: create_tools()
└── tmp/                    # Run artifacts (gitignored)
    └── {run_id}/
        ├── input.txt
        ├── events.jsonl
        ├── response.md
        └── trace.json
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `COMPANY_ID` | No | Default company to load (default: first in data/) |

## Key Design Decisions

1. **Stateless API** - Each request specifies company_id, no global state
2. **Parallel-safe** - Multiple companies can run simultaneously
3. **Transport-agnostic core** - Same Session works for API, CLI, or any future integration
4. **Artifact logging** - Every run saves debug info to `tmp/{run_id}/`
5. **Agents are company-agnostic** - Same agent code works for any company
6. **Company data is injected** - Tools receive data at creation time
7. **No model hardcoded** - Uses SDK default, configurable via environment
8. **SSE for real-time** - Stream agent traces to frontend
