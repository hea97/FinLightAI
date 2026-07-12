# FinLightAI

AI, policy, and semiconductor news are filtered for reliability, combined with market reaction data, and shown as RED/YELLOW/GREEN market-state signals.

This project is an analysis and alerting platform, not an investment recommendation system.

## Exhibition authentication status

- Exhibition authentication: environment-gated demo login with `POST /api/auth/demo`.
- Google OAuth: implemented in code, but the production Google Cloud Console is not connected yet.
- Full self-service signup, password storage, password reset, and email/password account creation are outside the exhibition scope.
- The exhibition notification channel is email only.
- RED/YELLOW/GREEN are informational market-state signals, not buy/sell instructions or profit guarantees.

The exhibition demo login flow is:

```text
Login page
-> 전시용 데모 시작하기
-> POST /api/auth/demo
-> Find or create the fixed demo provider user
-> Issue the existing signed finlight_session cookie
-> Reuse the same portfolio, preferences, settings, onboarding, and email subscription APIs
```

Demo login security rules:

- `EXHIBITION_DEMO_LOGIN_ENABLED` defaults to `false`.
- Enable demo login explicitly in Render only for the exhibition.
- Set `EXHIBITION_DEMO_ACCESS_CODE` for the exhibition whenever possible.
- Pass the access code in the JSON body or `X-Demo-Access-Code` header, never in a URL query string.
- Do not enter sensitive personal information or real asset information into the demo account.
- Demo account data can be shared by multiple demonstration users.
- Disable demo login after the exhibition by setting `EXHIBITION_DEMO_LOGIN_ENABLED=false`.

## Exhibition deployment configuration

Render environment variables:

```dotenv
EXHIBITION_DEMO_LOGIN_ENABLED=true
EXHIBITION_DEMO_ACCESS_CODE=
EXHIBITION_DEMO_EMAIL=demo@finlightai.local
EXHIBITION_DEMO_NAME=FinLightAI Demo
FRONTEND_URL=https://your-project.vercel.app
BACKEND_URL=https://your-service.onrender.com
CORS_ORIGINS=https://your-project.vercel.app
JWT_SECRET_KEY=replace-with-a-long-random-secret
DATABASE_URL=provided-by-render
```

Optional or post-exhibition Google OAuth variables:

```dotenv
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=
```

Do not commit actual Google client secrets, JWT secrets, database URLs, email provider keys, or demo access codes.

Vercel environment variables:

```dotenv
VITE_API_BASE_URL=https://your-service.onrender.com
VITE_EXHIBITION_DEMO_LOGIN_ENABLED=true
```

Do not append `/api` to `VITE_API_BASE_URL`; the frontend already sends requests such as `/api/auth/demo`.

Post-merge exhibition smoke sequence:

1. Configure Render environment variables.
2. Configure Vercel environment variables.
3. Merge this branch into `main`.
4. Confirm the latest Render deployment.
5. Confirm the latest Vercel Production deployment.
6. Open the login page and start the exhibition demo.
7. Confirm `/api/auth/me` returns the demo user.
8. Confirm portfolio, preferences, settings, onboarding, and email subscription persistence.
9. Confirm logout clears the session.

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

## Email Provider

The MVP email provider is Resend. SMTP remains the fallback option for local
or customer-managed mail infrastructure.

Required Resend settings:

```dotenv
EMAIL_PROVIDER=resend
SMTP_FROM=FinLightAI <alerts@your-verified-domain.example>
RESEND_API_KEY=re_xxx
EMAIL_WEBHOOK_SECRET=whsec_xxx
```

`SMTP_FROM` must use a sender address on a domain or single sender identity
verified in Resend before production smoke testing. Register the Resend webhook
URL as `POST /api/notifications/email-events` and store its signing secret in
`EMAIL_WEBHOOK_SECRET`.

SMTP alternative:

```dotenv
EMAIL_PROVIDER=smtp
SMTP_FROM=FinLightAI <alerts@your-domain.example>
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
```

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

- `GET /api/auth/google/login`
- `GET /api/auth/google/callback`
- `POST /api/auth/demo`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `GET /api/briefing`
- `GET /api/news-guard`
- `GET /api/industry-impact`
- `GET|POST /api/portfolio`
- `PATCH|DELETE /api/portfolio/{asset_id}`
- `GET/PUT /api/email-subscription`
- `GET /api/email-subscription/confirm`
- `GET /api/email-subscription/unsubscribe`
- `POST /api/notifications/dispatch`
- `POST /api/notifications/email-events`
- `GET|PATCH /api/mypage`
- `GET|PUT /api/settings`

Portfolio, email alert, profile, and settings data are scoped by the signed session cookie in production. The `X-User-ID` header remains a local development bridge and must be disabled for production traffic. For the exhibition, demo login is the fallback authentication path and is controlled by backend environment variables. Google OAuth is implemented, but the production Google Cloud Console, Render, and Vercel settings must be completed before post-exhibition OAuth smoke testing.

## Project Layout

```text
config/                 App settings and ticker universe
database/               PostgreSQL schema and migrations
docs/                   Requirements, agent guide, and project plan
scripts/                Setup and pipeline entrypoints
src/collector/          News, stock, and reliability collection
src/processor/          Filtering, sentiment, market reaction, event scoring
src/signal/             RED/YELLOW/GREEN signal generation
src/notifier/           Email notifications
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
