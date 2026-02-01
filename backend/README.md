# AI Workforce Orchestrator

Multi-agent system for marketing automation using OpenAI Agents SDK.

## Overview

This backend system orchestrates a team of AI agents to handle marketing tasks. It uses a transport-agnostic core design that supports both CLI and API interactions.

### Agent Hierarchy

The system simulates a company structure with the following roles:

| Agent | Role | Capabilities |
|-------|------|--------------|
| **Founder** | Orchestrator | Receives all requests, delegates, manages evaluation cycles |
| **Marketing Head** | Lead | Coordinates SEO + Content, reports to Founder |
| **Evaluator** | Reviewer | Reviews user-facing deliverables (brand voice, quality) |
| **Market Researcher** | Worker | Web search, internal research DB |
| **Data Analyst** | Worker | Internal analytics, KPIs, performance metrics |
| **SEO Analyst** | Worker | Keyword research, web search |
| **Content Creator** | Worker | Blog posts, social media, brand assets |

## How to Run

### 1. Setup

Navigate to the backend directory and set up your environment:

```bash
cd backend
cp .env.example .env
# Open .env and add your OPENAI_API_KEY
```

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. CLI Usage

The CLI is the easiest way to interact with the agents.

**Interactive Mode:**
```bash
python cli.py
```

**Single Query:**
```bash
python cli.py chat "Research coffee trends"
```

**Common Commands:**
- `python cli.py companies` - List available simulated companies
- `python cli.py messages` - Show message history
- `python cli.py runs` - List recent agent execution runs

### 3. API Server

The backend also provides a FastAPI server.

```bash
python main.py
```
- Server: `http://localhost:8023`
- Docs: `http://localhost:8023/docs`

## Project Structure

- `core/` - Transport-agnostic session management
- `workforce/` - Agent and tool definitions
- `data/` - Company context (brand voice, products, etc.)
- `cli.py` - Command-line interface
- `main.py` - API Entry point
