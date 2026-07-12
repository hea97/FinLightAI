# 전시용 데모 로그인 최종 readiness 기록

작성일: 2026-07-13 KST

## 1. 현재 브랜치

- `codex/demo-login-design-recheck`

## 2. 최종 commit 목록

```text
54634b1 docs(auth): design exhibition demo login fallback
58a53fc feat(auth): add gated exhibition demo login
07ba0f9 test(auth): cover exhibition demo login
d7076e2 chore(env): document demo login configuration
54e736f feat(frontend): add exhibition demo login flow
3560a73 refactor(ui): clarify demo authentication state
121997b docs(auth): switch exhibition fallback to demo login
879c3e0 docs(readme): document exhibition demo deployment
34ae2ad docs(todo): align remaining exhibition tasks
```

## 3. 데모 로그인 구조

```text
로그인 화면
-> 전시용 데모 시작하기
-> POST /api/auth/demo
-> demo provider 사용자 조회 또는 생성
-> 기존 create_session_token으로 signed session 생성
-> 기존 finlight_session 쿠키 발급
-> portfolio, preferences, settings, onboarding, email subscription API 재사용
```

## 4. 기능 플래그 정책

- backend 보안 기준: `EXHIBITION_DEMO_LOGIN_ENABLED`
- 기본값: `false`
- `true`, `1`, `yes`, `on`만 활성 값으로 인식
- 비활성 상태에서 `POST /api/auth/demo`는 세션을 발급하지 않음
- frontend `VITE_EXHIBITION_DEMO_LOGIN_ENABLED`는 CTA 표시용이며 보안 제어로 신뢰하지 않음

## 5. access code 정책

- 환경변수: `EXHIBITION_DEMO_ACCESS_CODE`
- JSON body `accessCode` 또는 `X-Demo-Access-Code` header로 전달
- URL query string 전달 없음
- 비교는 timing-safe `hmac.compare_digest` 사용
- 오류 응답과 테스트 assertion에서 access code 원문 미노출 확인
- frontend는 access code를 localStorage/sessionStorage에 저장하지 않음

## 6. Google OAuth 상태

- Google OAuth login/callback/me/logout 코드는 유지
- Google OAuth production console은 아직 미연결
- Google Client ID/Secret/Redirect URI는 전시 이후 운영 연결 작업으로 유지
- 정식 email/password 회원가입은 전시 범위 제외

## 7. backend 테스트 결과

```text
Command: python -m pytest -q
Result: 99 passed in 18.48s
```

## 8. frontend build 결과

```text
Command: npm.cmd run build
Result: tsc --noEmit 및 vite build 통과
```

## 9. E2E 결과

```text
Command: npm.cmd run test:e2e
Result: 4 passed in 12.8s
```

## 10. secret 검증 결과

- 실제 Google Client Secret 없음
- 실제 JWT secret 없음
- 실제 `DATABASE_URL` 없음
- 실제 `RESEND_API_KEY`, `SMTP_PASSWORD`, `EMAIL_WEBHOOK_SECRET` 없음
- 실제 `EXHIBITION_DEMO_ACCESS_CODE` 없음
- 검색 결과는 placeholder, 설정 변수명, 테스트용 fake 값만 포함
- `.env`, `.env.local`, `.env.production`, credential JSON, SQLite DB, dump, `frontend/dist`, `node_modules`, coverage, Playwright report 추적 없음

## 11. 카카오/n8n 검색 결과

- frontend 사용자 노출 영역 검색 결과: 0건
- backend legacy route/model/schema/test fixture에는 잔존 가능
- historical 문서와 과거 TODO에는 잔존 가능
- 현재 README와 현재 전시 범위 문서에서는 카카오/n8n을 현재 전시 기능으로 설명하지 않음

## 12. README 검증 결과

README에 다음 항목을 반영했다.

- 서비스가 투자 추천/매수/매도 지시가 아닌 금융 정보 모니터링 서비스임
- RED/YELLOW/GREEN은 시장 상태 정보 신호임
- 전시 인증은 환경변수 제한 데모 로그인임
- Google OAuth는 코드 구현 완료, 운영 콘솔 미연결 상태임
- 정식 회원가입은 전시 범위 제외임
- demo login flow와 보안 조건
- Render/Vercel 환경변수 placeholder
- `/api`를 `VITE_API_BASE_URL`에 붙이지 않는다는 주의
- post-merge smoke test 순서

## 13. TODO 문서 처리 결과

- `docs/TODO_NOW_2026-07-10_KO.md`: 과거 Google OAuth 중심 계획과 완료된 작업이 섞여 있어 제거
- `docs/TODO_NOW_2026-07-12_KO.md`: 최신 전시 운영 TODO 하나로 정리
- 완료된 구현 작업은 완료 목록으로 분리
- 남은 작업은 Render/Vercel 설정, PR 병합, 재배포 확인, demo login smoke, email smoke, 전시 종료 비활성화로 정리

## 14. Render 환경변수

```env
EXHIBITION_DEMO_LOGIN_ENABLED=true
EXHIBITION_DEMO_ACCESS_CODE=<secret>
EXHIBITION_DEMO_EMAIL=demo@finlightai.local
EXHIBITION_DEMO_NAME=FinLightAI Demo
FRONTEND_URL=<Vercel production origin>
BACKEND_URL=<Render backend origin>
CORS_ORIGINS=<Vercel production origin>
JWT_SECRET_KEY=<secret>
DATABASE_URL=<Render PostgreSQL URL>
```

Google OAuth는 전시 이후 운영 연결 시 다음을 설정한다.

```env
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=
```

## 15. Vercel 환경변수

```env
VITE_API_BASE_URL=<Render backend origin>
VITE_EXHIBITION_DEMO_LOGIN_ENABLED=true
```

`VITE_API_BASE_URL`에는 `/api`를 붙이지 않는다.

## 16. 배포 후 smoke test 순서

1. Render 환경변수 입력
2. Vercel 환경변수 입력
3. PR을 `main`에 merge
4. Render latest deployment 확인
5. Vercel Production deployment 확인
6. 로그인 화면에서 전시용 데모 시작
7. `/api/auth/me`에서 demo 사용자 확인
8. 포트폴리오, preferences, settings, email subscription 저장 확인
9. 로그아웃 후 anonymous 상태 확인
10. 이메일 구독, confirm, daily summary, unsubscribe smoke test

## 17. 전시 종료 후 비활성화 방법

1. Render에서 `EXHIBITION_DEMO_LOGIN_ENABLED=false`로 변경
2. 필요하면 `EXHIBITION_DEMO_ACCESS_CODE` 회전
3. demo 계정에 입력된 시연 데이터 삭제 여부 결정
4. Google OAuth 운영 연결을 진행할 경우 Google Cloud Console, Render, Vercel 설정 후 별도 smoke test 수행

## 18. 현재 알려진 한계

- demo 사용자는 하나의 전시 계정 데이터를 공유할 수 있음
- 실제 개인정보나 실제 자산 정보 입력 금지
- Google OAuth는 외부 Google Cloud Console 설정 전까지 운영 로그인으로 사용할 수 없음
- 실제 이메일 발송은 provider credential, sender verification, production smoke test가 필요
- backend legacy Kakao/n8n 코드는 이번 release에서 삭제하지 않음

## 19. 최종 병합 권장 여부

- 로컬 검증 기준 병합 가능
- separated commit history 보존을 위해 GitHub에서 `Create a merge commit` 권장
- `Squash and merge`는 사용하지 않는 것을 권장
