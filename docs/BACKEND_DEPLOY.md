# Backend deployment preparation

FinLightAI currently deploys the React/Vite frontend separately from the FastAPI backend. This document prepares the backend deployment step without starting Kakao OAuth implementation.

## FastAPI entrypoint

| Item | Value |
| --- | --- |
| ASGI app | `src.dashboard.app:app` |
| Source file | `src/dashboard/app.py` |
| Local command | `uvicorn src.dashboard.app:app --reload --port 8000` |
| Production command | `uvicorn src.dashboard.app:app --host 0.0.0.0 --port $PORT` |
| Health check | `GET /health` |
| API prefix | `/api` |

Do not add Vercel's FastAPI `[tool.vercel]` entrypoint configuration yet. The current Vercel task is frontend-only.

## Dependency management

The backend dependencies are managed with `requirements.txt`.

Important deployment packages:

- `fastapi`
- `uvicorn[standard]`
- `pydantic-settings`
- `SQLAlchemy`
- `psycopg[binary]`
- `httpx`
- `pandas`
- `numpy`
- `yfinance`

## Required environment variables

Commit only names and placeholders. Real values must live in the deployment platform's environment variable settings.

```env
APP_ENV=production
FRONTEND_URL=https://your-vercel-frontend.example
BACKEND_URL=https://your-backend-api.example
CORS_ORIGINS=https://your-vercel-frontend.example
DATABASE_URL=postgresql+psycopg://...
KAKAO_REST_API_KEY=
KAKAO_CLIENT_SECRET=
KAKAO_REDIRECT_URI=https://your-backend-api.example/api/auth/kakao/callback
JWT_SECRET_KEY=
JWT_EXPIRE_MINUTES=1440
GEMINI_API_KEY=
NEWS_API_KEY=
GDELT_BASE_URL=https://api.gdeltproject.org/api/v2/doc/doc
EXTERNAL_API_TIMEOUT_SECONDS=10
EXTERNAL_API_CACHE_SECONDS=300
```

Optional collector/provider variables can remain empty until each provider is enabled:

- `GUARDIAN_API_KEY`
- `FINNHUB_API_KEY`
- `ALPHA_VANTAGE_API_KEY`
- `OPENDART_API_KEY`
- `KIS_APP_KEY`
- `KIS_APP_SECRET`
- `KIS_ACCOUNT_NO`

## CORS configuration

The backend reads allowed origins from `CORS_ORIGINS` and also includes `FRONTEND_URL` when present.

Recommended production setting:

```env
FRONTEND_URL=https://your-vercel-frontend.example
CORS_ORIGINS=https://your-vercel-frontend.example
```

Keep local development origins in local `.env` only if needed:

```env
CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

Avoid `*` for production because OAuth/session flows may require credentials.

## Database usage

Local development defaults to SQLite:

```env
DATABASE_URL=sqlite:///./data/finlightai.db
```

For external deployment, PostgreSQL is recommended:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME
```

Reasons:

- SQLite files on many hosted runtimes are ephemeral unless persistent disks are explicitly configured.
- The data pipeline depends on persisted stock/news/signal tables.
- PostgreSQL makes later user/auth/onboarding data safer to operate.

After setting `DATABASE_URL`, initialize tables:

```bash
python scripts/setup_db.py
```

Then refresh pipeline data when the deployed database is ready:

```bash
python scripts/refresh_pipeline_data.py
```

## Backend deployment platform comparison

| Platform | Strengths | Weaknesses | Fit for current project |
| --- | --- | --- | --- |
| Render | Simple Python web service flow, direct start command, health check support, managed PostgreSQL option, easy environment variable UI | Free/low-cost instances may sleep depending on plan; data refresh jobs need a separate cron/background strategy | Best first choice for MVP backend API |
| Railway | Fast setup, convenient environment variables, PostgreSQL integration, good logs | Usage-based billing can be less predictable; project service boundaries should be watched | Good alternative if the team already uses Railway |
| Fly.io | Strong runtime control, regions, volumes, Docker-friendly deployment | More operational concepts: `fly.toml`, machines, volumes, networking | Powerful, but heavier than needed for first backend URL |

### Recommendation

Use Render first for the backend API.

Reasons:

- The current app can run with a plain `uvicorn` start command.
- Environment variables and managed PostgreSQL are straightforward.
- Logs and health checks are easy to inspect during smoke testing.
- It keeps frontend Vercel deployment separate from backend API deployment.

## Render setup checklist

Create a Render Web Service from the GitHub repository and use the backend branch selected for deployment.

Recommended values:

| Setting | Value |
| --- | --- |
| Runtime | Python |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn src.dashboard.app:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/health` |
| Environment | `Python 3` runtime |

Add environment variables in the Render dashboard. Do not commit `.env`.

## Vercel frontend connection

After the backend URL is created, set this in the Vercel frontend project:

```env
VITE_API_BASE_URL=https://your-backend-api.example
VITE_USER_ID=demo-user
```

The frontend API client already reads `VITE_API_BASE_URL`. If this value is empty, it falls back to relative `/api` paths, which only work when the backend/proxy is available on the same origin.

Only put browser-safe values in Vercel `VITE_` variables. Vite exposes `VITE_` variables to client-side JavaScript, so never place Kakao client secrets, JWT secrets, database URLs, or private API keys in Vercel frontend environment variables.

## URL consistency before OAuth implementation

Confirm these four values before starting Kakao OAuth:

```env
FRONTEND_URL=https://your-vercel-frontend.example
BACKEND_URL=https://your-render-backend.example
CORS_ORIGINS=https://your-vercel-frontend.example
KAKAO_REDIRECT_URI=https://your-render-backend.example/api/auth/kakao/callback
```

Then set the Vercel frontend variables:

```env
VITE_API_BASE_URL=https://your-render-backend.example
VITE_USER_ID=demo-user
```

The `KAKAO_REDIRECT_URI` value in Render must exactly match the Kakao Developers Redirect URI registration.

## Backend smoke test checklist

Run these after backend deployment and database initialization:

```bash
curl https://your-backend-api.example/health
curl https://your-backend-api.example/api/briefing
curl https://your-backend-api.example/api/news-guard
curl https://your-backend-api.example/api/industry-impact
curl https://your-backend-api.example/api/signals
```

Check:

- HTTP 200 for each endpoint.
- Response metadata includes provider/source/fallback fields where applicable.
- No browser CORS error from the Vercel frontend URL.
- `/api/signals` contains verified evidence when pipeline data exists.
- The deployed database has expected `stock_prices`, `news_raw`, `news_filtered`, and `signals` rows after refresh.

Future auth smoke checks:

- `GET /api/auth/me`
- Kakao callback URL after OAuth implementation.

## Deployment risks

- A fresh hosted PostgreSQL database will be empty until setup and pipeline refresh run.
- `GDELT` can return `429` or timeout and should remain non-blocking.
- `GEMINI_API_KEY` can stay empty for static briefing fallback until Gemini integration is explicitly enabled.
- Hosted schedulers or cron jobs are not configured yet; data refresh may need a separate job after the API is live.
