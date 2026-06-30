# Google OAuth MVP setup

Google OAuth is the primary MVP login method for FinLightAI. Kakao OAuth and Kakao channel alerts are deferred until business app and channel setup are ready.

## Deployment URL contract

OAuth callback is handled by the FastAPI backend, not the Vercel frontend.

```env
FRONTEND_URL=https://your-vercel-frontend.example
BACKEND_URL=https://your-render-backend.example
CORS_ORIGINS=https://your-vercel-frontend.example
GOOGLE_REDIRECT_URI=https://your-render-backend.example/api/auth/google/callback
```

The Google redirect URI configured in Google Cloud must exactly match `GOOGLE_REDIRECT_URI`.

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
   - `https://your-vercel-frontend.example`
9. Register Authorized redirect URIs:
   - `https://your-render-backend.example/api/auth/google/callback`

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
FRONTEND_URL=https://your-vercel-frontend.example
BACKEND_URL=https://your-render-backend.example
CORS_ORIGINS=https://your-vercel-frontend.example
```

## Frontend environment variables

Set these in Vercel.

```env
VITE_API_BASE_URL=https://your-render-backend.example
VITE_USER_ID=demo-user
```

`VITE_` variables are exposed to browser JavaScript. Never put Google client secrets, JWT secrets, database URLs, or provider API keys in Vercel frontend variables.

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
