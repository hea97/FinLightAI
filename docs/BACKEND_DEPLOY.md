# Backend deployment preparation

FinLightAI deploys the React/Vite frontend separately from the FastAPI backend. This document prepares the Google OAuth and email-notification MVP backend deployment while keeping Kakao/n8n as a future expansion.

## FastAPI entrypoint

| Item | Value |
| --- | --- |
| ASGI app | `src.dashboard.app:app` |
| Source file | `src/dashboard/app.py` |
| Local command | `uvicorn src.dashboard.app:app --reload --port 8000` |
| Production command | `uvicorn src.dashboard.app:app --host 0.0.0.0 --port $PORT` |
| Health check | `GET /health/live`, `GET /health/ready` |
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
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=https://your-backend-api.example/api/auth/google/callback
JWT_SECRET_KEY=
JWT_EXPIRE_MINUTES=1440
AUTH_COOKIE_SAMESITE=none
AUTH_COOKIE_SECURE=true
# AUTH_COOKIE_DOMAIN=  # Leave empty for the default Render host.

EMAIL_PROVIDER=resend
RESEND_API_KEY=
SMTP_FROM=FinLightAI <alerts@your-verified-domain.example>
EMAIL_WEBHOOK_SECRET=
NOTIFICATION_SECRET=
NOTIFICATION_TOKEN_SECRET=

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
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `KAKAO_CHANNEL_ID`
- `KAKAO_CHANNEL_APPROVED`
- `N8N_KAKAO_WEBHOOK_URL`
- `N8N_WEBHOOK_TOKEN`

Kakao/n8n variables are for future expansion. The MVP login path is Google
OAuth, and the MVP notification channel is email.

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

## HTTPS session cookie behavior

The frontend sends API requests with `credentials: "include"` and the backend
enables credentialed CORS. In production the backend defaults the session
cookie to `Secure; HttpOnly; SameSite=None`; local development defaults to
`SameSite=Lax` without `Secure`.

This is the minimum required configuration for a Vercel frontend to send the
Render cookie on cross-site API requests:

```env
APP_ENV=production
FRONTEND_URL=https://your-vercel-frontend.example
CORS_ORIGINS=https://your-vercel-frontend.example
AUTH_COOKIE_SAMESITE=none
AUTH_COOKIE_SECURE=true
```

However, `*.vercel.app` and `*.onrender.com` are different sites. Browsers that
block third-party cookies can still reject this session even with
`SameSite=None`. For reliable production auth, use owned sibling subdomains
such as `app.example.com` and `api.example.com`, or place the API behind a
same-origin reverse proxy/BFF. Do not set `AUTH_COOKIE_DOMAIN` to
`.vercel.app` or `.onrender.com`.

## Database usage

Local development defaults to SQLite:

```env
DATABASE_URL=sqlite:///./data/finlightai.db
```

For external deployment, PostgreSQL is recommended. Both Render-style
`postgresql://` URLs and explicit SQLAlchemy `postgresql+psycopg://` URLs are
accepted; the application normalizes the former to the installed psycopg v3
driver.

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
| Health Check Path | `/health/ready` |
| Environment | `Python 3` runtime |

Add environment variables in the Render dashboard. Do not commit `.env`.

## Vercel frontend connection

After the backend URL is created, set this in the Vercel frontend project:

```env
VITE_API_BASE_URL=https://your-backend-api.example
```

The frontend API client already reads `VITE_API_BASE_URL`. If this value is empty, it falls back to relative `/api` paths, which only work when the backend/proxy is available on the same origin.

Only put browser-safe values in Vercel `VITE_` variables. Vite exposes `VITE_` variables to client-side JavaScript, so never place Kakao client secrets, JWT secrets, database URLs, or private API keys in Vercel frontend environment variables.

## URL consistency before Google OAuth production

Confirm these values before production Google OAuth smoke testing:

```env
FRONTEND_URL=https://your-vercel-frontend.example
BACKEND_URL=https://your-render-backend.example
CORS_ORIGINS=https://your-vercel-frontend.example
GOOGLE_REDIRECT_URI=https://your-render-backend.example/api/auth/google/callback
```

Then set the Vercel frontend variables:

```env
VITE_API_BASE_URL=https://your-render-backend.example
```

Do not set `VITE_ENABLE_DEV_USER_HEADER=true` in Vercel production.
`VITE_USER_ID` is only a local-development fallback and is not an
authentication credential. In `APP_ENV=production`, authenticated user APIs
must use the Google session cookie; `X-User-ID` is rejected as a production
identity substitute.

The `GOOGLE_REDIRECT_URI` value in Render must exactly match the Google Cloud
OAuth Client's Authorized redirect URI.

## Email notification variables

Email is the MVP notification channel. With the recommended Resend provider,
set:

```env
EMAIL_PROVIDER=resend
RESEND_API_KEY=re_...
SMTP_FROM=FinLightAI <alerts@your-verified-domain.example>
EMAIL_WEBHOOK_SECRET=...
NOTIFICATION_SECRET=...
NOTIFICATION_TOKEN_SECRET=...
```

`SMTP_FROM` is still required with Resend because it is the visible sender
address. Verify the sender domain or single sender in the provider dashboard
before running production smoke tests.

If using SMTP instead of Resend:

```env
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
SMTP_FROM=FinLightAI <alerts@your-verified-domain.example>
NOTIFICATION_SECRET=...
NOTIFICATION_TOKEN_SECRET=...
```

`NOTIFICATION_SECRET` protects manual/cron dispatch requests.
`NOTIFICATION_TOKEN_SECRET` signs confirmation and unsubscribe tokens.
`EMAIL_WEBHOOK_SECRET` protects provider event webhook verification when
bounce/complaint events are enabled.

## Backend smoke test checklist

Run these after backend deployment and database initialization:

```bash
curl https://your-backend-api.example/health/live
curl https://your-backend-api.example/health/ready
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

Auth and browser checks:

1. Open the Vercel production URL in a private browser window.
2. Confirm `GET /api/auth/me` returns `authenticated: false` before login.
3. Start `GET /api/auth/google/login` and complete Google login.
4. Confirm the callback returns to `FRONTEND_URL` with
   `?auth=google_connected`.
5. In browser developer tools, confirm `finlight_session` belongs to the API
   host and has `HttpOnly`, `Secure`, `SameSite=None`, and `Path=/`.
6. Confirm the Vercel page can call `GET /api/auth/me` with HTTP 200 and an
   authenticated user. A 200 anonymous response here usually means the browser
   blocked the cross-site cookie.
7. Save and reload onboarding preferences to verify PostgreSQL persistence.
8. Call `POST /api/auth/logout`, then confirm `/api/auth/me` is anonymous and
   the session cookie is removed.
9. Check that API responses include exactly the configured
   `Access-Control-Allow-Origin` value and
   `Access-Control-Allow-Credentials: true`.
10. Repeat the login check in Safari. If it fails only there, move to owned
    sibling domains or a same-origin API proxy instead of weakening cookie
    security.

Email checks:

1. After Google login, save an email subscription from the Vercel UI.
2. Confirm the API request uses the Google `finlight_session` cookie, not
   `X-User-ID`.
3. Confirm the response becomes `pending` and the double opt-in email arrives.
4. Open the confirmation link and verify the response becomes `active`.
5. Dispatch one daily summary or RED/YELLOW smoke notification with
   `X-Notification-Secret`.
6. Confirm `notification_deliveries` records `sent` or `failed`, and repeat
   the same dedupe key once to confirm duplicate tracking.
7. Open the unsubscribe link and verify the subscription becomes
   `unsubscribed`.

## Deployment risks

- A fresh hosted PostgreSQL database will be empty until setup and pipeline refresh run.
- `create_all()` is retained for tests only. Production setup must run
  `scripts/setup_db.py` or Alembic migrations against the deployed
  PostgreSQL database before traffic.
- `GDELT` can return `429` or timeout and should remain non-blocking.
- `GEMINI_API_KEY` can stay empty for static briefing fallback until Gemini integration is explicitly enabled.
- Hosted schedulers or cron jobs are not configured yet; data refresh may need a separate job after the API is live.
