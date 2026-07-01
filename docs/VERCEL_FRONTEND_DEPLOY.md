# Vercel frontend deployment

This project currently deploys the React/Vite frontend separately from the FastAPI backend.

## Why the Vercel root directory must be `frontend`

The repository root contains the FastAPI dashboard code, so Vercel can detect the backend first and fail with a FastAPI entrypoint error. For the frontend preview deployment, configure Vercel to build only the Vite app under `frontend`.

## Recommended Vercel settings

| Setting | Value |
| --- | --- |
| Root Directory | `frontend` |
| Framework Preset | `Vite` |
| Install Command | `npm install` |
| Build Command | `npm run build` |
| Output Directory | `dist` |

## Environment variables

Define these in Vercel Project Settings for the frontend project. Do not commit real values.

```env
VITE_API_BASE_URL=https://your-backend-api.example.com
```

Do not set `VITE_USER_ID` or enable `VITE_ENABLE_DEV_USER_HEADER` in
production. Those values are development-only fallbacks, not authentication.

If `VITE_API_BASE_URL` is empty, frontend API calls use relative `/api` paths. That works only when a backend or proxy is available on the same deployment origin.

## Branch strategy

Use a deployment-only branch based on the stable real-news signal milestone:

```bash
git switch -c deploy/vercel-frontend v0.1.0-real-news-signal
git push -u origin deploy/vercel-frontend
```

Do not merge this branch into `main` just to trigger a frontend preview deployment. Keep backend Vercel entrypoint configuration separate until backend deployment is explicitly planned.
