# FinLightAI

AI, policy, and semiconductor news are filtered for reliability, combined with market reaction data, and shown as RED/YELLOW/GREEN market-state signals.

This project is an analysis and alerting platform, not an investment recommendation system.

## Quick Start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python scripts/setup_db.py
python -m pytest
cd frontend
npm install
npm run build
cd ..
uvicorn src.dashboard.app:app --reload --port 8000
```

Open http://localhost:8000 after starting the dashboard.

For frontend development, run FastAPI on port `8000` and Vite in a second terminal:

```powershell
cd frontend
npm run dev
```

Vite proxies `/api` to FastAPI. `VITE_API_BASE_URL` can point to a different API origin when needed.

## Database

Local development uses `sqlite:///./data/finlightai.db` by default. To use PostgreSQL, set:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/finlightai
```

`python scripts/setup_db.py` creates the SQLAlchemy tables for the configured database. The PostgreSQL reference schema is in `database/schema.sql`.

## Dashboard API

The React dashboard uses these FastAPI endpoints:

- `GET /api/briefing`
- `GET /api/news-guard`
- `GET /api/industry-impact`
- `GET|POST /api/portfolio`
- `PATCH|DELETE /api/portfolio/{asset_id}`
- `GET /api/kakao-alert`
- `PATCH /api/kakao-alert/rules/{rule_id}`
- `GET|PATCH /api/mypage`
- `GET|PUT /api/settings`

Portfolio, alert, profile, and settings data are scoped by the `X-User-ID` header. This is a local integration bridge, not production authentication. Replace it with verified Kakao OAuth/session identity before deployment.

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
