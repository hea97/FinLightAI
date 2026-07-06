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

`python scripts/setup_db.py` upgrades the configured database to the latest Alembic revision. Application startup does not create or mutate tables. Create new revisions with:

```powershell
python -m alembic revision --autogenerate -m "describe change"
python -m alembic upgrade head
python -m alembic check
```

The migration history in `database/migrations/` is the schema source of truth. A legacy database without an `alembic_version` table is stamped at the baseline revision before operational migrations are applied.

## Docker

Run the application and PostgreSQL together:

```powershell
docker compose up --build
```

The container applies Alembic migrations before Uvicorn starts. Liveness and database readiness endpoints are available at `/health/live` and `/health/ready`.

## Operational monitoring

Every data refresh records its trigger, status, timestamps, row counts, and error. Provider checks retain an event history plus the current failure streak and recovery timestamp.

- `GET /api/operations/status` — latest refresh, recent refreshes, provider state, and recent provider events
- `python scripts/refresh_pipeline_data.py` — scheduled/manual refresh entrypoint

Signal generation maps each article to the next session from the NYSE or KRX exchange calendar and records the expected session and match quality in signal evidence.

## Verification

```powershell
python -m pytest -q
cd frontend
npm ci
npm run build
npx playwright install chromium
npm run test:e2e
```

Playwright covers cross-origin credentialed cookies and error, empty, and fallback UI states. GitHub Actions runs backend, frontend, E2E, migration-drift, and Docker build jobs.

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
