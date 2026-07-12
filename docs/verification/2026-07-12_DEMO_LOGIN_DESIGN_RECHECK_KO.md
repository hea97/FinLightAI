# FinLightAI 전시용 데모 로그인 설계 재검증

작성일: 2026-07-12
범위: 구현 전 구조 분석과 설계 검증

## 1. 현재 인증 구조

현재 인증 route는 `src/dashboard/routes/api.py`에 있다.

| Endpoint | 함수 | 역할 |
|---|---|---|
| `GET /api/auth/google/login` | `google_login` | Google authorization URL 생성, OAuth state cookie 저장 |
| `GET /api/auth/google/callback` | `google_callback` | OAuth state 검증, token/userinfo 조회, 사용자 조회/생성, session cookie 발급 |
| `GET /api/auth/me` | `auth_me` | session cookie에서 사용자 조회 후 인증 상태 반환 |
| `POST /api/auth/logout` | `auth_logout` | session cookie 삭제 |

사용자 조회 흐름은 `get_optional_session_user`와 `get_current_user_id`가 담당한다.

- `get_optional_session_user`: `finlight_session` cookie를 읽고 `verify_session_token`으로 `sub`를 검증한 뒤 `get_user_by_id`로 `users.id`를 조회한다.
- `get_current_user_id`: session user가 있으면 해당 `users.id`를 사용한다. session이 없고 `APP_ENV`가 local/development/dev/test이면 `X-User-ID` 또는 `demo-user` fallback을 허용한다. production에서는 `401 Authentication required`를 반환한다.

## 2. 재사용 가능한 함수

| 파일 | 함수 | 재사용 판단 |
|---|---|---|
| `src/dashboard/repository.py` | `get_or_create_oauth_user` | `provider="demo"`와 고정 `provider_user_id`를 넣으면 demo user 조회/생성에 재사용 가능 |
| `src/dashboard/auth.py` | `create_session_token` | 기존 session JWT 생성에 그대로 재사용해야 함 |
| `src/dashboard/auth.py` | `verify_session_token` | `/api/auth/me`와 보호 API의 기존 검증 흐름 유지 |
| `src/dashboard/routes/api.py` | `_cookie_options` | cookie `path`, `domain`, `secure` 계산에 재사용 |
| `src/dashboard/routes/api.py` | `_auth_user_dict` | demo login 직후 JSON 응답 또는 `/auth/me` 응답 형식에 재사용 |
| `src/dashboard/repository.py` | `get_user_by_id` | session token의 `sub` 조회에 이미 사용 중 |

`ensure_user`도 사용자를 만들 수 있지만 provider가 `local`이고 입력 `user_id`를 그대로 신뢰하므로 전시용 production demo login에는 덜 적합하다. demo login은 프론트가 사용자 ID를 지정하지 못하도록 `get_or_create_oauth_user(provider="demo", provider_user_id=<server-fixed-id>)` 형태가 더 안전하다.

## 3. 수정이 필요한 파일

구현 시 최소 수정 예상 파일은 다음과 같다.

| 파일 | 예상 변경 |
|---|---|
| `config/settings.py` | `EXHIBITION_DEMO_LOGIN_ENABLED`, `EXHIBITION_DEMO_ACCESS_CODE`, `EXHIBITION_DEMO_EMAIL`, `EXHIBITION_DEMO_NAME` 설정 추가 |
| `src/dashboard/routes/api.py` | `POST /api/auth/demo` endpoint 추가, access code 검증, demo user 조회/생성, session cookie 발급 |
| `src/dashboard/schemas.py` | request body에 `accessCode`를 받을 경우 `DemoLoginRequest` 같은 schema 추가 |
| `tests/test_auth.py` | disabled 기본값, access code 실패/성공, session cookie, `/auth/me`, production cookie 속성 테스트 추가 |
| `.env.example` | secret 값 없이 demo login 기본 비활성 env 예시 추가 |
| `docs/GOOGLE_OAUTH_MVP_SETUP.md` 또는 별도 runbook | 전시 fallback 사용 방법과 종료 후 비활성화 절차 문서화 |

프론트 UI 변경은 이번 분석 단계에서는 하지 않는다. 실제 구현 단계에서도 backend endpoint를 먼저 만들고, 전시 직전 필요할 때 login 화면 CTA만 별도 작업으로 연결하는 것이 안전하다.

## 4. 예상 endpoint 계약

권장 계약:

```text
POST /api/auth/demo
```

요청:

```json
{
  "accessCode": "optional-code"
}
```

대체 입력:

```text
X-Demo-Access-Code: optional-code
```

처리 순서:

1. `EXHIBITION_DEMO_LOGIN_ENABLED`가 명시적으로 true인지 확인한다.
2. false이거나 미설정이면 `404 Not found` 또는 `403 Demo login disabled`를 반환한다. 전시 외부 노출을 줄이려면 `404`가 더 낫다.
3. `EXHIBITION_DEMO_ACCESS_CODE`가 설정되어 있으면 request body의 `accessCode` 또는 `X-Demo-Access-Code`와 상수 시간 비교한다.
4. access code는 query string으로 받지 않는다.
5. `get_or_create_oauth_user`로 `provider="demo"` 사용자를 조회/생성한다.
6. `create_session_token(user.id, secret=settings.jwt_secret_key, expire_minutes=settings.jwt_expire_minutes)`를 호출한다.
7. 기존 `finlight_session` cookie 이름과 `_cookie_options`, `session_cookie_samesite`, `session_cookie_secure`를 사용해 HttpOnly cookie를 설정한다.
8. 응답은 JSON 또는 redirect 중 하나로 정한다.

권장 응답:

```json
{
  "authenticated": true,
  "user": {
    "id": "demo-...",
    "provider": "demo",
    "email": "demo@finlightai.local",
    "nickname": "FinLightAI Demo",
    "profileImageUrl": null
  }
}
```

프론트가 이미 API 기반 login 상태를 확인할 수 있으므로, API-first인 JSON 응답이 가장 단순하다. redirect가 필요하면 `FRONTEND_URL/?auth=demo_connected`를 사용할 수 있다.

## 5. 필요한 환경변수

| 환경변수 | 기본값 | 비밀 여부 | 설명 |
|---|---|---:|---|
| `EXHIBITION_DEMO_LOGIN_ENABLED` | `false` | No | 명시적으로 true일 때만 demo login 허용 |
| `EXHIBITION_DEMO_ACCESS_CODE` | empty | Yes | 설정된 경우 전시 접근 코드로 검증 |
| `EXHIBITION_DEMO_EMAIL` | `demo@finlightai.local` | No | 실제 개인정보가 아닌 local 전용 기본 email |
| `EXHIBITION_DEMO_NAME` | `FinLightAI Demo` | No | demo user 표시 이름 |

현재 사용자가 제공한 운영 URL은 Vercel `https://fin-light-ai.vercel.app/`, Render `https://finlightai.onrender.com`이다. 문서 예시에는 `finlightai.vercel.app`, `finlightai-api.onrender.com` 형태도 있으므로 실제 배포 전에는 `FRONTEND_URL`, `BACKEND_URL`, `GOOGLE_REDIRECT_URI`, `CORS_ORIGINS`, `VITE_API_BASE_URL` 값을 하나의 최종 URL 세트로 확정해야 한다.

## 6. 보안 위험과 대응

| 위험 | 대응 |
|---|---|
| demo login이 실수로 상시 열림 | 기본값 false, production에서도 env가 true일 때만 활성화 |
| access code 노출 | query string 금지, 로그 출력 금지, header/body만 허용 |
| 프론트에서 사용자 ID 임의 지정 | request에서 user id를 받지 않고 서버 고정 `provider_user_id` 사용 |
| session secret 우회 | 반드시 `create_session_token`과 기존 `JWT_SECRET_KEY` 사용 |
| production에서 `X-User-ID` 재활성화 | 기존 `get_current_user_id` 정책 유지, production fallback 금지 |
| Google OAuth 회귀 | Google endpoint는 삭제하지 않고 demo endpoint를 병렬 추가 |
| 개인정보 기본값 사용 | `demo@finlightai.local`, `FinLightAI Demo`처럼 실제 개인 정보가 아닌 값 사용 |
| access code 비교 timing leak | `hmac.compare_digest` 사용 |
| 전시 후 방치 | `EXHIBITION_DEMO_LOGIN_ENABLED=false`로 비활성화하고 Render env에서 access code 제거 |

## 7. 테스트 계획

`tests/test_auth.py`에 다음 테스트를 추가하는 것이 적절하다.

1. 기본 설정에서 `POST /api/auth/demo`는 `404` 또는 비활성 응답을 반환한다.
2. `EXHIBITION_DEMO_LOGIN_ENABLED=true`이고 access code 미설정이면 demo user를 생성하고 session cookie를 발급한다.
3. access code가 설정된 경우 누락/오답은 실패한다.
4. access code 정답은 성공하고 cookie에 `HttpOnly`, production에서 `Secure`, `SameSite=none`이 붙는다.
5. 성공 후 `GET /api/auth/me`가 `provider="demo"` user를 반환한다.
6. 같은 demo login을 반복해도 `users(provider, provider_user_id)` unique constraint 때문에 동일 사용자를 재사용한다.
7. `X-User-ID`는 production에서 계속 `401`인지 유지 테스트를 보강한다.
8. portfolio, onboarding preferences, settings, email subscription API가 demo session의 `users.id`로 분리되는지 smoke 테스트한다.

## 8. 기존 Google OAuth와의 공존 방식

Google OAuth는 그대로 둔다.

- `GET /api/auth/google/login`
- `GET /api/auth/google/callback`
- `GET /api/auth/me`
- `POST /api/auth/logout`

Demo login은 별도 endpoint로만 추가한다.

```text
POST /api/auth/demo
```

두 방식은 모두 같은 `users` 테이블, 같은 `finlight_session` cookie, 같은 `create_session_token`, 같은 `/api/auth/me`를 사용한다. 차이는 사용자 provider뿐이다.

- Google: `provider="google"`, `provider_user_id=<Google sub>`
- Demo: `provider="demo"`, `provider_user_id=<server-fixed demo identity>`

이 구조라면 기존 portfolio, preferences, settings, email subscription은 모두 `users.id` foreign key 또는 user id primary key를 그대로 사용하므로 추가 schema 변경이 필요 없다.

## 9. 전시 종료 후 비활성화 방법

1. Render에서 `EXHIBITION_DEMO_LOGIN_ENABLED=false`로 변경한다.
2. `EXHIBITION_DEMO_ACCESS_CODE` 값을 삭제하거나 rotate한다.
3. 필요하면 `/api/auth/demo` endpoint는 코드에 남겨도 disabled 상태에서는 `404`만 반환하게 둔다.
4. 전시 데이터 정리가 필요하면 `provider="demo"` 사용자와 연결된 portfolio/preferences/settings/email subscription 데이터를 운영 정책에 따라 별도 정리한다.
5. Google OAuth가 정상 운영되면 login UI에서는 Google만 노출한다.

## 10. 구현 권장 여부

구현 가능하며, Google Cloud Console을 사용할 수 없는 전시 직전 fallback으로 적합하다.

권장 조건:

- backend만 먼저 구현한다.
- 기본 비활성으로 둔다.
- access code를 header/body로만 받는다.
- session cookie는 기존 함수를 재사용한다.
- 사용자는 서버가 고정한 `provider="demo"` identity로만 생성한다.
- Google OAuth 코드는 삭제하지 않는다.

권장하지 않는 방식:

- 정식 회원가입/비밀번호 저장을 전시 직전에 새로 구현
- production에서 `X-User-ID` fallback 허용
- 프론트에서 demo user id를 직접 보내게 함
- URL query string으로 access code 전달
- 실제 개인 email을 기본 demo 값으로 사용

최소 구현 파일 수는 backend 기준 4개(`config/settings.py`, `src/dashboard/routes/api.py`, `src/dashboard/schemas.py`, `tests/test_auth.py`)로 예상된다. 문서/env 예시까지 포함하면 `.env.example`과 운영 runbook 문서가 추가된다.
