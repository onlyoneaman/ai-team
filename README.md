# TeamAI

AI employees for solopreneurs and small teams. A multi-agent system that simulates a company workforce—agents with specialized roles, hierarchical delegation, and quality verification—so you can scale without hiring.

## How to Run

### Backend (Python)
```bash
cd backend
cp .env.example .env          # Add your OPENAI_API_KEY
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py                 # API server at http://localhost:8023
```

### Frontend (Next.js)
```bash
cd teams-web
npm install
npm run dev                    # Dev server at http://localhost:3000
```

## Demo Steps

1. Start the backend: `cd backend && source .venv/bin/activate && python main.py`
2. Start the frontend: `cd teams-web && npm run dev`
3. Open http://localhost:3000
4. Select "Solaris Coffee" from the company dropdown
5. Click a suggested prompt (e.g., "Sustainability Blog" or "New Espresso Blend")
6. Watch the agent visualization in the center as the AI workforce collaborates
7. See the final response rendered as formatted markdown
