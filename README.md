# FinLightAI

AI, policy, and semiconductor news are filtered for reliability, combined with market reaction data, and shown as RED/YELLOW/GREEN market-state signals.

This project is an analysis and alerting platform, not an investment recommendation system.

## Quick Start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m pytest
uvicorn src.dashboard.app:app --reload --port 8000
```

Open http://localhost:8000 after starting the dashboard.

## Project Layout

```text
config/                 App settings and ticker universe
database/               PostgreSQL schema and migrations
docs/                   Requirements, agent guide, and project plan
scripts/                Setup and pipeline entrypoints
src/collector/          News, stock, and reliability collection
src/processor/          Filtering, sentiment, market reaction, event scoring
src/signal/             RED/YELLOW/GREEN signal generation
src/notifier/           Discord and email notifications
src/dashboard/          FastAPI dashboard and API routes
src/ml/                 Training, prediction, and backtesting placeholders
tests/                  Focused unit tests
```

## Core Flow

1. Collect relevant news from GDELT/NewsAPI-style sources.
2. Block low-reliability articles with source, date, sensationalism, consistency, and coverage checks.
3. Filter duplicates and short or keyword-poor articles.
4. Analyze sentiment and combine it with market reaction metrics.
5. Generate RED/YELLOW/GREEN signals.
6. Show signals on the dashboard and send alerts for RED/YELLOW events.

## Safety Notes

- API keys and credentials must live in `.env`, never in source code.
- A single unverified article should not produce a RED signal.
- Outputs are informational market-state signals only.
