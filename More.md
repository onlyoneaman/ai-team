# TeamAI - Detailed Documentation

## What It Does

TeamAI simulates an AI-powered marketing agency with a hierarchical workforce. When you submit a task, a **Founder** agent receives it and delegates to specialized workers:

- **Marketing Head** - Coordinates content and SEO teams
- **Market Researcher** - Web search and market analysis
- **Data Analyst** - Internal analytics and KPIs
- **SEO Analyst** - Keyword research
- **Content Creator** - Blog posts, social media content
- **Evaluator** - Reviews deliverables for quality and brand voice

Agents communicate using a structured TaskMessage protocol with bounce-back handoffs. User-facing deliverables go through an evaluation cycle (up to 3 revision attempts) before being returned.

## Project Structure

```
teamai/
├── backend/               # Python backend (FastAPI + CLI)
│   ├── cli.py            # Interactive terminal interface
│   ├── main.py           # API server entry point
│   ├── core/             # Transport-agnostic session management
│   ├── workforce/        # Agent definitions and tools
│   └── data/             # Company contexts (solaris.json, promptsmint.json)
└── teams-web/            # Next.js frontend
    ├── app/              # Next.js app router pages
    ├── components/       # React components (agents, chat, sidebar)
    └── lib/              # Zustand stores and API utilities
```

## Running the Project

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key

### Backend Setup
```bash
cd backend
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-...

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### CLI Mode (Easiest)
```bash
python cli.py                              # Interactive mode
python cli.py chat "Research coffee trends"  # Single query
python cli.py companies                     # List companies
python cli.py runs                          # Show recent runs
```

### API Mode
```bash
python main.py
# Server: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Frontend
```bash
cd teams-web
npm install
npm run dev      # http://localhost:3000
```

## Demo Walkthrough

1. **Start the backend API:**
   ```bash
   cd backend
   source .venv/bin/activate
   python main.py
   ```
   Server runs at http://localhost:8000

2. **Start the frontend:**
   ```bash
   cd teams-web
   npm run dev
   ```
   Dev server runs at http://localhost:3000

3. **Open the app:** Navigate to http://localhost:3000

4. **Select a company:** Choose "Solaris Coffee" from the dropdown in the header

5. **Run a task:** Click "Sustainability Blog" or "New Espresso Blend" from the suggested prompts

6. **Watch the agents work:** The agent visualization moves to center stage, showing:
   - Active agent highlighted with pulsing animation
   - Activity feed in the sidebar with real-time updates
   - Agent handoffs as work is delegated

7. **View the result:** Final response appears as formatted markdown with copy/download options

## Key Features

- **Hierarchical agent structure** with delegation and bounce-back
- **Evaluation cycles** ensure quality before user delivery
- **Real-time SSE streaming** for live agent status updates
- **Per-company context** with brand voice, products, research data
- **Artifact logging** saves all runs to `tmp/{run_id}/`
- **Cost tracking** with token usage and USD estimates
- **Static frontend** deployable to Cloudflare Pages

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/companies` | List all companies |
| `GET /api/companies/{id}` | Get company details |
| `GET /api/companies/{id}/agents` | Get agent hierarchy |
| `POST /api/companies/{id}/chat` | Send task to agents (SSE) |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for agent models |
| `COMPANY_ID` | No | Default company (uses first available if omitted) |
