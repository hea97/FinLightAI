# Google OAuth MVP setup

This document is retained as the post-exhibition production Google OAuth connection guide.

2026-07-13 exhibition authentication uses an environment-gated demo login fallback because Google Cloud Console production OAuth credentials are not connected yet.

- Google OAuth code: implemented, production console not connected.
- Exhibition authentication: `POST /api/auth/demo` gated by `EXHIBITION_DEMO_LOGIN_ENABLED`.
- Full signup/password account flows: outside the exhibition scope.
- Exhibition notification channel: email only.

## Deployment URL contract

OAuth callback is handled by the FastAPI backend, not the Vercel frontend.

```env
FRONTEND_URL=https://your-vercel-frontend.example
BACKEND_URL=https://your-render-backend.example
CORS_ORIGINS=https://your-vercel-frontend.example
GOOGLE_REDIRECT_URI=https://your-render-backend.example/api/auth/google/callback
```

The Google redirect URI configured in Google Cloud must exactly match `GOOGLE_REDIRECT_URI`.

If the real deployment URLs are not known yet, keep these placeholders until the
Vercel and Render production domains are confirmed:

```text
FRONTEND_ORIGIN=https://<vercel-production-domain>
BACKEND_ORIGIN=https://<render-production-domain>
GOOGLE_REDIRECT_URI=https://<render-production-domain>/api/auth/google/callback
```

## Google Cloud checklist

1. Create or select a Google Cloud Console project.
2. Configure OAuth Consent Screen.
3. Set User Type to `External`.
4. Add your Google account as a test user while the app is in testing mode.
5. Keep scopes minimal:
   - `openid`
   - `email`
   - `profile`
6. Create an OAuth Client ID.
7. Set Application type to `Web application`.
8. Register Authorized JavaScript origins:
   - `https://<vercel-production-domain>`
9. Register Authorized redirect URIs:
   - `https://<render-production-domain>/api/auth/google/callback`
10. Do not request Gmail, Drive, Calendar, or other sensitive Google API scopes
    for the MVP login flow.

## Production configuration contract

### Google Cloud Console

Authorized JavaScript origins:

```text
https://<vercel-production-domain>
```

Authorized redirect URIs:

```text
https://<render-production-domain>/api/auth/google/callback
```

OAuth scopes:

```text
openid
email
profile
```

### Render environment variables

| Variable | Required | Sensitive | Purpose |
|---|---:|---:|---|
| `GOOGLE_CLIENT_ID` | Yes | No | Google OAuth client identifier |
| `GOOGLE_CLIENT_SECRET` | Yes | Yes | Google OAuth token exchange |
| `GOOGLE_REDIRECT_URI` | Yes | No | Backend OAuth callback URL |
| `FRONTEND_URL` | Yes | No | Frontend redirect target after callback |
| `BACKEND_URL` | Yes | No | Backend origin used to validate callback origin |
| `CORS_ORIGINS` | Yes | No | Comma-separated credentialed CORS allowlist |
| `JWT_SECRET_KEY` | Yes | Yes | Session JWT signing secret |

### Vercel environment variables

| Variable | Required | Sensitive | Purpose |
|---|---:|---:|---|
| `VITE_API_BASE_URL` | Yes | No | Backend API origin used by browser requests |
| `VITE_EXHIBITION_DEMO_LOGIN_ENABLED` | Exhibition only | No | Display-only flag for the demo login CTA |

### Production value format

Render:

```env
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=https://<render-production-domain>/api/auth/google/callback
FRONTEND_URL=https://<vercel-production-domain>
BACKEND_URL=https://<render-production-domain>
CORS_ORIGINS=https://<vercel-production-domain>
JWT_SECRET_KEY=
```

Vercel:

```env
VITE_API_BASE_URL=https://<render-production-domain>
VITE_EXHIBITION_DEMO_LOGIN_ENABLED=true
```

### Configuration cautions

- Use `https` for all production URLs.
- Do not mix `http` and `https` in production settings.
- `GOOGLE_REDIRECT_URI` must exactly match the Google Cloud Console redirect URI.
- Do not add a trailing path to `FRONTEND_URL`; use only the frontend origin.
- Do not include `/about`, `/login`, `/privacy`, or `/terms` in `FRONTEND_URL`.
- Do not include a path in `CORS_ORIGINS`; use origins only.
- `CORS_ORIGINS` is a comma-separated string, not a JSON array.
- Do not append `/api` to `VITE_API_BASE_URL`; the frontend already adds API paths.
- Keep Preview and Production environment variables separate in Vercel and Render.
- After changing Render environment variables, redeploy the Render service.
- After changing Vercel environment variables, redeploy the Vercel production build.

## Google Authorized Domains caution

Google Auth Platform Authorized domains should use a top private domain that the project owner can own or verify.

Do not use a Vercel preview URL such as:

```text
fin-light-xxxx.vercel.app
```

The top private domain is `vercel.app`, which is owned by Vercel, not by this project. That can trigger a "top private domain" or ownership-related validation error in Google Auth Platform.

### Current MVP path

- Use Google OAuth testing mode with explicitly added test users while the app is not public production.
- Use the real frontend deployment URL for Authorized JavaScript origins when possible.
- Use the real Render backend URL for Authorized redirect URIs.
- Before public production, consider connecting a custom domain such as `finlightai.com` or another owned domain.

### Future recommendation

1. Buy or use an owned custom domain.
2. Connect the custom domain to Vercel.
3. Verify the domain in Google Search Console if required.
4. Register the custom domain in Google Auth Platform Authorized domains.

## Google Cloud URL template

### Branding > App Domain

Homepage URL:

```text
https://your-frontend-domain.example/about
```

Privacy Policy URL:

```text
https://your-frontend-domain.example/privacy
```

Terms of Service URL:

```text
https://your-frontend-domain.example/terms
```

### OAuth Client > Authorized JavaScript origins

```text
https://your-frontend-domain.example
```

### OAuth Client > Authorized redirect URIs

```text
https://your-render-backend.example/api/auth/google/callback
```

## Backend environment variables

Set these in Render. Do not commit real values.

```env
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=https://your-render-backend.example/api/auth/google/callback
JWT_SECRET_KEY=
JWT_EXPIRE_MINUTES=1440
AUTH_COOKIE_SAMESITE=none
AUTH_COOKIE_SECURE=true
FRONTEND_URL=https://your-vercel-frontend.example
BACKEND_URL=https://your-render-backend.example
CORS_ORIGINS=https://your-vercel-frontend.example
```

Leave `AUTH_COOKIE_DOMAIN` empty when using the default Vercel and Render
hostnames. Production sessions use `Secure; HttpOnly; SameSite=None`, and the
frontend must call the API with credentials enabled. Because `vercel.app` and
`onrender.com` are different sites, browser third-party-cookie policies can
still block the session. Owned sibling domains (for example
`app.example.com` and `api.example.com`) or a same-origin API proxy are the
reliable public-production topology.

## Frontend environment variables

Set these in Vercel.

```env
VITE_API_BASE_URL=https://your-render-backend.example
```

Leave `VITE_ENABLE_DEV_USER_HEADER` unset (or `false`) in production.
`VITE_USER_ID` is for local development only.

`VITE_` variables are exposed to browser JavaScript. Never put Google client secrets, JWT secrets, database URLs, or provider API keys in Vercel frontend variables.

## Production preflight check

Before deployment smoke testing, run the local configuration checker with the
same variable names that will be configured in Render:

```bash
python scripts/check_oauth_production_config.py
```

The checker does not call external services. It validates that required
environment variables exist, URL origins use HTTPS, callback path is
`/api/auth/google/callback`, callback origin matches `BACKEND_URL`,
`CORS_ORIGINS` includes `FRONTEND_URL`, wildcard CORS is absent, placeholders
are gone, and `JWT_SECRET_KEY` is long enough. It prints only pass/fail status
and never prints secret values.

## Production OAuth smoke test

Run this manually after Render and Vercel have been redeployed with production
environment variables.

### Pre-check

```text
GET <BACKEND_URL>/health/live
GET <BACKEND_URL>/health/ready
GET <BACKEND_URL>/api/auth/me
```

Expected results:

- Health endpoints return 200.
- Before login, `/api/auth/me` returns a normal anonymous response or the
  documented unauthenticated response.
- Browser requests from the Vercel origin do not show CORS errors.

### Browser login flow

1. Open the Vercel production URL.
2. Click the Google login button.
3. Select a Google account that is allowed by the OAuth consent screen.
4. Confirm the browser is sent to the Render callback URL.
5. Confirm callback completion returns to the Vercel frontend.
6. Confirm `/api/auth/me` returns the logged-in Google user.
7. Open a user-scoped screen such as portfolio or settings.
8. Click logout.
9. Confirm `/api/auth/me` returns the anonymous state again.

### Browser developer tools checks

- `finlight_session` cookie exists on the backend host.
- Cookie has `HttpOnly`.
- Cookie has `Secure`.
- Cookie has `SameSite=None`.
- Frontend API requests include the session cookie.
- API responses include the exact `Access-Control-Allow-Origin` for the Vercel
  origin.
- API responses include `Access-Control-Allow-Credentials: true`.
- Console has no CORS or cookie-blocking errors.

## MVP auth flow

```text
Google login
→ FastAPI /api/auth/google/callback
→ provider-based user create/read
→ httpOnly session cookie
→ GET /api/auth/me
→ onboarding preferences saved by user_id
→ mypage/settings saved by user_id
```

## Development fallback policy

`X-User-ID` remains only as a local/development fallback. Production must use the authenticated session user.
