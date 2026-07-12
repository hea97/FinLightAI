# FinLightAI 전시 직전 TODO - 2026-07-12 KST

## 상태

- 전시 인증: 환경변수로 제한되는 데모 로그인
- Google OAuth: 코드 구현 완료, Google Cloud 운영 콘솔 미연결
- 정식 회원가입: 전시 범위 제외
- 알림 채널: 이메일-only MVP
- 카카오/n8n: 전시 사용자 화면 제외, backend legacy는 유지

## 완료된 구현

- `POST /api/auth/demo` 구현
- demo provider 사용자 조회 또는 생성
- 기존 `finlight_session` 쿠키와 `create_session_token` 재사용
- `/api/auth/me`, `/api/auth/logout` 호환 확인
- frontend 로그인 화면을 `전시용 데모 시작하기` 중심으로 전환
- access code를 localStorage/sessionStorage에 저장하지 않음
- frontend 사용자 노출 영역에서 카카오/n8n/챗봇 문구 제거
- backend 전체 테스트, frontend build, frontend E2E 통과

## 남은 전시 운영 작업

1. Render 환경변수 입력
   - `EXHIBITION_DEMO_LOGIN_ENABLED=true`
   - `EXHIBITION_DEMO_ACCESS_CODE=<secret>`
   - `EXHIBITION_DEMO_EMAIL=demo@finlightai.local`
   - `EXHIBITION_DEMO_NAME=FinLightAI Demo`
   - `FRONTEND_URL=<Vercel production origin>`
   - `BACKEND_URL=<Render backend origin>`
   - `CORS_ORIGINS=<Vercel production origin>`
   - `JWT_SECRET_KEY=<secret>`
   - `DATABASE_URL=<Render PostgreSQL URL>`

2. Vercel 환경변수 입력
   - `VITE_API_BASE_URL=<Render backend origin>`
   - `VITE_EXHIBITION_DEMO_LOGIN_ENABLED=true`
   - `VITE_API_BASE_URL`에는 `/api`를 붙이지 않는다.

3. PR 병합
   - separated commit history를 보존하기 위해 `Create a merge commit` 권장
   - `Squash and merge`는 사용하지 않는다.

4. Render/Vercel 재배포 확인
   - Render latest deployment 확인
   - Vercel Production deployment 확인
   - `/health/live`, `/health/ready` 확인

5. 전시 데모 로그인 smoke test
   - 로그인 화면 접속
   - `전시용 데모 시작하기`
   - `/api/auth/me`에서 demo 사용자 확인
   - 포트폴리오, 온보딩 preferences, 설정 저장 확인
   - 로그아웃 후 `/api/auth/me`가 anonymous 상태인지 확인

6. 이메일 smoke test
   - 이메일 구독 신청
   - 확인 메일 수신 및 confirm link 클릭
   - `active` 상태 확인
   - 일일 요약 dispatch 확인
   - 수신 거부 link 확인
   - provider 발송 실패 또는 bounce 처리는 별도 운영 검증으로 기록

7. 전시 종료 후 조치
   - `EXHIBITION_DEMO_LOGIN_ENABLED=false`로 전환
   - 필요하면 demo access code 회전
   - demo 계정에 입력된 시연 데이터 삭제 여부 결정

## 전시 중 주의 문구

- 데모 계정 데이터는 다른 시연 사용자와 공유될 수 있다.
- 민감한 개인정보나 실제 자산 정보를 입력하지 않는다.
- FinLightAI의 신호와 이메일 알림은 투자 추천이나 매수, 매도 지시가 아니라 참고용 시장 상태 정보다.
