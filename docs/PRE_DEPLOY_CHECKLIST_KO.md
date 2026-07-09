# 배포 전 운영 확인 체크리스트

이 체크리스트는 Render 백엔드, Vercel 프론트엔드, Google OAuth, PostgreSQL,
이메일 알림 플로우를 운영 환경에서 확인하기 위한 최종 점검 순서다.

## 1. Render 백엔드 환경변수

Render Web Service `finlightai-api`에 아래 값을 설정한다. 실제 secret은 Git에
커밋하지 않는다.

```dotenv
APP_ENV=production
FRONTEND_URL=https://your-vercel-app.vercel.app
BACKEND_URL=https://your-render-api.onrender.com
CORS_ORIGINS=https://your-vercel-app.vercel.app
DATABASE_URL=postgresql://...

GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=https://your-render-api.onrender.com/api/auth/google/callback

JWT_SECRET_KEY=...
JWT_EXPIRE_MINUTES=1440
AUTH_COOKIE_SAMESITE=none
AUTH_COOKIE_SECURE=true

EMAIL_PROVIDER=resend
RESEND_API_KEY=re_...
SMTP_FROM=FinLightAI <alerts@your-verified-domain.example>
EMAIL_WEBHOOK_SECRET=whsec_...
NOTIFICATION_SECRET=...
NOTIFICATION_TOKEN_SECRET=...
```

선택 API 키는 기능을 켤 때만 설정한다.

- `GEMINI_API_KEY`
- `NEWS_API_KEY`
- `GUARDIAN_API_KEY`
- `FINNHUB_API_KEY`
- `ALPHA_VANTAGE_API_KEY`
- `OPENDART_API_KEY`

## 2. Vercel 프론트 API URL

Vercel 프로젝트의 Production 환경변수에 백엔드 API URL을 설정한다.

```dotenv
VITE_API_BASE_URL=https://your-render-api.onrender.com
```

운영 Vercel에는 `VITE_USER_ID`, `VITE_ENABLE_DEV_USER_HEADER`, API secret,
DB URL, OAuth secret을 넣지 않는다.

## 3. Google OAuth 운영 URL

Google Cloud Console의 OAuth 클라이언트 설정을 운영 URL과 정확히 맞춘다.

- Authorized JavaScript origins:
  `https://your-vercel-app.vercel.app`
- Authorized redirect URIs:
  `https://your-render-api.onrender.com/api/auth/google/callback`
- Render `GOOGLE_REDIRECT_URI`:
  `https://your-render-api.onrender.com/api/auth/google/callback`
- Render `FRONTEND_URL`:
  `https://your-vercel-app.vercel.app`
- Render `CORS_ORIGINS`:
  `https://your-vercel-app.vercel.app`

## 4. PostgreSQL 연결 확인

Render Shell 또는 배포 로그에서 마이그레이션이 성공했는지 확인한다.

```powershell
python scripts/setup_db.py
python scripts/refresh_pipeline_data.py
```

`/health/ready`가 200을 반환하면 애플리케이션에서 DB `SELECT 1`이 성공한
상태다.

## 5. Health smoke test

로컬 터미널에서 운영 백엔드 URL을 대상으로 확인한다.

```powershell
$api = "https://your-render-api.onrender.com"
Invoke-RestMethod "$api/health/live"
Invoke-RestMethod "$api/health/ready"
Invoke-RestMethod "$api/api/briefing"
Invoke-RestMethod "$api/api/news-guard"
Invoke-RestMethod "$api/api/industry-impact"
Invoke-RestMethod "$api/api/signals"
```

기대 결과:

- `/health/live`: HTTP 200, `{"status":"ok"}`
- `/health/ready`: HTTP 200, `{"status":"ok"}`
- 주요 API: HTTP 200
- Render 로그에 DB 연결 오류가 없어야 한다.

자동 점검은 아래 스크립트로 실행할 수 있다.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check_deploy_smoke.ps1 `
  -ApiBaseUrl "https://your-render-api.onrender.com" `
  -FrontendOrigin "https://your-vercel-app.vercel.app"
```

이 스크립트는 `/health/live`, `/health/ready`, 주요 공개 API, CORS preflight,
Google OAuth 시작 redirect를 확인한다.

## 6. 이메일 구독 smoke test

운영 환경의 `APP_ENV=production`에서는 `X-User-ID` 개발 헤더를 사용할 수 없다.
먼저 Vercel 프론트에서 Google OAuth 로그인을 완료하고, 브라우저 개발자 도구에서
Render API host의 `finlight_session` HttpOnly 쿠키가 생성됐는지 확인한다.

쿠키 속성 기대값:

- Host: Render API host
- `HttpOnly`
- `Secure`
- `SameSite=None`
- `Path=/`

그 다음 프론트 UI에서 실제로 받을 수 있는 테스트 메일 주소로 이메일 구독을 저장한다.
터미널에서 확인하려면 브라우저의 `Cookie` 요청 헤더 값을 안전하게 복사해 일회성으로
사용한다. 이 값은 secret으로 취급하고 커밋하지 않는다.

```powershell
$api = "https://your-render-api.onrender.com"
$email = "your-test-inbox@example.com"
$sessionCookie = "finlight_session=..."

Invoke-RestMethod "$api/api/email-subscription" `
  -Method Put `
  -Headers @{ Cookie = $sessionCookie } `
  -ContentType "application/json" `
  -Body (@{
    email = $email
    dailySummary = $true
    immediateRed = $true
    immediateYellow = $true
  } | ConvertTo-Json)
```

기대 결과:

- 응답 `status`가 `pending`
- 테스트 메일함에 double opt-in 확인 메일 도착
- Render 또는 Resend 로그에 발송 성공 이력 기록

스크립트로 함께 실행하려면 아래처럼 세션 쿠키와 테스트 메일을 추가한다.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check_deploy_smoke.ps1 `
  -ApiBaseUrl "https://your-render-api.onrender.com" `
  -FrontendOrigin "https://your-vercel-app.vercel.app" `
  -SessionCookie "finlight_session=..." `
  -TestEmail "your-test-inbox@example.com"
```

## 7. 확인 링크 smoke test

구독 확인 메일의 링크를 브라우저 또는 터미널에서 연다.

```powershell
Invoke-RestMethod "https://your-render-api.onrender.com/api/email-subscription/confirm?token=..."
```

기대 결과:

- HTTP 200
- 응답 `status`가 `active`
- `consentedAt`이 `null`이 아님

## 8. 일일 요약 smoke test

확인된 테스트 구독자에게 운영 dispatch API로 일일 요약을 한 번 보낸다.

```powershell
$api = "https://your-render-api.onrender.com"
$secret = "your-render-NOTIFICATION_SECRET"
$dedupe = "smoke-daily-summary-$(Get-Date -Format yyyyMMddHHmmss)"

Invoke-RestMethod "$api/api/notifications/dispatch" `
  -Method Post `
  -Headers @{ "X-Notification-Secret" = $secret } `
  -ContentType "application/json" `
  -Body (@{
    type = "daily_summary"
    subject = "[FinLightAI] smoke daily summary"
    body = "Production smoke test daily summary."
    dedupeKey = $dedupe
    channels = @("email")
  } | ConvertTo-Json)
```

기대 결과:

- 응답 `sent`가 1 이상
- 테스트 메일함에 일일 요약 메일 도착
- 메일 본문에 수신 거부 링크 포함

스크립트에서 dispatch까지 확인하려면 `-NotificationSecret`을 추가한다.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check_deploy_smoke.ps1 `
  -ApiBaseUrl "https://your-render-api.onrender.com" `
  -FrontendOrigin "https://your-vercel-app.vercel.app" `
  -SessionCookie "finlight_session=..." `
  -TestEmail "your-test-inbox@example.com" `
  -NotificationSecret "your-render-NOTIFICATION_SECRET"
```

## 9. 수신 거부 smoke test

일일 요약 메일의 수신 거부 링크를 연다.

```powershell
Invoke-RestMethod "https://your-render-api.onrender.com/api/email-subscription/unsubscribe?token=..."
```

기대 결과:

- HTTP 200
- 응답 `status`가 `unsubscribed`

수신 거부 이후 같은 사용자에게 새 dedupe key로 일일 요약을 다시 호출하면
수신 거부 사용자는 발송 대상에서 제외되어야 한다.

## 10. 최종 판정

아래 항목이 모두 통과하면 운영 배포 smoke test를 통과한 것으로 본다.

- Render 백엔드 환경변수 설정 완료
- Vercel `VITE_API_BASE_URL` 설정 완료
- Google OAuth 운영 URL 설정 완료
- PostgreSQL 마이그레이션과 연결 확인 완료
- `/health/live` HTTP 200
- `/health/ready` HTTP 200
- CORS 응답이 실제 Vercel origin과 `Access-Control-Allow-Credentials: true`를 반환
- Google OAuth login/callback/me/logout smoke test 통과
- `finlight_session` cookie가 API host에 `HttpOnly`, `Secure`, `SameSite=None`, `Path=/`로 생성됨
- 이메일 구독 `pending` 생성 확인
- 확인 링크로 `active` 전환 확인
- 일일 요약 발송 확인
- `notification_deliveries`에 발송 성공/실패 이력과 중복 호출 이력이 남는지 확인
- 수신 거부 링크로 `unsubscribed` 전환 확인
- 수신 거부 사용자가 후속 dispatch 발송 대상에서 제외되는지 확인
