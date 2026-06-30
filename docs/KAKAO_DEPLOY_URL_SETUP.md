# Kakao Developers deployment URL setup

Kakao OAuth implementation must wait until both frontend and backend deployment URLs are confirmed.

Current order:

1. Deploy frontend preview on Vercel.
2. Deploy FastAPI backend externally.
3. Set `VITE_API_BASE_URL` in Vercel to the backend URL.
4. Register frontend/backend URLs in Kakao Developers.
5. Implement Kakao OAuth.

## Required URLs

| URL | Source | Example |
| --- | --- | --- |
| Frontend URL | Vercel frontend deployment | `https://finlightai-preview.vercel.app` |
| Backend URL | FastAPI backend deployment | `https://finlightai-api.example.com` |
| Kakao redirect URI | Backend callback endpoint | `https://finlightai-api.example.com/api/auth/kakao/callback` |

Use the actual deployed URLs. Do not use localhost in Kakao production settings.

## Kakao Developers settings

In Kakao Developers, register these after URLs are confirmed.

### Platform > Web site domain

Register:

- `https://your-vercel-frontend.example`
- `https://your-backend-api.example`

### Kakao Login > Redirect URI

Register:

- `https://your-backend-api.example/api/auth/kakao/callback`

The redirect URI must exactly match the backend environment variable:

```env
KAKAO_REDIRECT_URI=https://your-backend-api.example/api/auth/kakao/callback
```

## Backend environment variables for later OAuth work

Do not commit real values.

```env
KAKAO_REST_API_KEY=
KAKAO_CLIENT_SECRET=
KAKAO_REDIRECT_URI=https://your-backend-api.example/api/auth/kakao/callback
JWT_SECRET_KEY=
JWT_EXPIRE_MINUTES=1440
FRONTEND_URL=https://your-vercel-frontend.example
BACKEND_URL=https://your-backend-api.example
CORS_ORIGINS=https://your-vercel-frontend.example
```

## Important matching rules

- `http` and `https` are different.
- Trailing slash differences can matter; keep the exact same callback URL everywhere.
- Confirm whether the final callback path is `/api/auth/kakao/callback` before implementation.
- If cookies or sessions are used later, CORS must allow credentials and must not use `*`.
- Keep local development redirect URIs separate from production settings.

## Not implemented in this step

- Kakao OAuth routes.
- Token exchange.
- User/session persistence.
- Onboarding data connection.
