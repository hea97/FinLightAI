# FinLightAI 현재 방향성과 목표 계획서

## 2026-07-12 전시 인증 결정

- Google OAuth 코드: 구현 완료, 운영 콘솔 미연결
- 전시 인증: 환경변수로 제한되는 데모 로그인
- 정식 회원가입: 전시 범위 제외
- 전시 알림 채널: 이메일-only MVP
- 이메일 실제 발송: provider 설정과 production smoke test 필요

작성일: 2026-06-21
최종 업데이트: 2026-07-12
기준 브랜치: `main`

## 1. 현재 목표

FinLightAI는 금융 뉴스와 시장 데이터를 함께 분석해 사용자가 시장 상태, 뉴스 신뢰도, 산업 영향, 관심 자산 리스크를 빠르게 이해하도록 돕는 AI 금융 상황판이다.

현재 MVP는 화면 시제품 단계를 지나 다음 흐름을 실제로 연결한 상태다.

```text
외부 뉴스/시장 데이터
-> 수집 및 DB 저장
-> 관련성/신뢰도/감성/이벤트 점수 계산
-> RED/YELLOW/GREEN 신호 생성
-> FastAPI
-> React 대시보드
```

제품은 투자 추천이나 자동 매매가 아니라 참고용 시장 상태와 근거를 제공한다.

## 2. 2026-07-12 구현 현황

### 완료

- Vite + React + TypeScript 대시보드와 FastAPI API 연결
- 브리핑, 뉴스 가드, 산업 영향도에 실제 저장 데이터 우선 적용
- Google News RSS 등 provider 기반 뉴스 수집과 중복/관련성 필터
- yfinance 기반 시장 데이터 수집과 DB upsert
- 뉴스 및 시장 반응 기반 신호 생성과 DB 저장
- 데이터 출처, provider, fallback, 경고 metadata 표시
- 포트폴리오 CRUD, 마이페이지, 설정, 사용자 알림 설정의 DB 저장
- Google OAuth 로그인, callback, 세션 쿠키, 로그아웃
- 로그인 사용자 기준 포트폴리오/설정/온보딩 데이터 분리
- 이메일 레터 구독 modal, 구독 API, 사용자별 DB 저장
- 이메일 double opt-in 확인, 수신 거부, 발송 이력 저장 모델과 API 초안
- SMTP/Resend 기반 이메일 발송 adapter와 provider webhook 처리 초안
- 일일 요약 발송 script와 RED/YELLOW 즉시 알림 dispatch 흐름
- 전시 및 MVP 알림 채널을 이메일로 확정
- 알림 delivery 중복 방지와 성공/실패/중복/bounce/complaint 상태 저장 구조
- 기존 SQLite `users` 테이블용 idempotent 호환 마이그레이션
- `email_subscriptions`, `notification_deliveries` Alembic migration 초안
- Vercel 프론트엔드와 Render 백엔드 배포 문서 및 설정
- `/about`, `/login`, `/signup`, `/privacy`, `/terms` 공개 페이지
- 2026-07-09 로컬 기준 backend test 78개, 알림 지정 테스트 12개, Alembic 신규/기존 SQLite DB 적용, frontend production build 통과

### 운영 환경 확인 필요

- Google Cloud OAuth Consent Screen 및 Web Client 설정
- 실제 Vercel/Render URL로 redirect URI와 CORS 설정
- Render 백엔드 및 PostgreSQL 배포
- 배포 환경에서 로그인과 사용자별 API smoke test
- 정기 데이터 refresh 스케줄러 연결
- 이메일 provider 결정 및 환경 변수 설정: Resend 권장, SMTP 대안
- `SMTP_FROM`, `EMAIL_PROVIDER`, `RESEND_API_KEY` 또는 SMTP 계정 설정
- `NOTIFICATION_SECRET`, `NOTIFICATION_TOKEN_SECRET`, `EMAIL_WEBHOOK_SECRET` 설정
- `alembic upgrade head`로 알림 관련 migration 적용 확인
- 이메일 구독, 확인 링크, 수신 거부, 일일 요약, RED/YELLOW 즉시 알림 smoke test

### 전시 범위에서 제외

- 카카오 관련 화면, 문구, 실제 발송, 채널 승인, 챗봇, n8n workflow
- 자체 회원가입/비밀번호 재설정/이메일 인증까지 포함한 풀 인증 시스템
- Guardian/Finnhub adapter와 선택적 pykrx provider
- 정확한 거래일 계산용 exchange calendar
- CI, Docker, 모델 고도화

## 3. 제품 원칙

- `매수`, `매도`, `수익 보장`, `상승 확정` 표현을 사용하지 않는다.
- RED/YELLOW/GREEN은 투자 지시가 아니라 시장 상태 신호다.
- 점수와 요약에는 가능한 한 데이터 출처와 판단 근거를 함께 표시한다.
- 실제 데이터가 없을 때 fallback을 실제 데이터처럼 보이게 하지 않는다.
- Gemini 요약 실패 시 원문 기반 정적 요약으로 대체하고 상태를 표시한다.
- 인증은 Google OAuth 코드 준비 완료 상태를 기준으로 한다. 남은 작업은 Google Cloud Console, Render, Vercel의 운영 설정과 smoke test다.
- 자체 회원가입/비밀번호 로그인/이메일 인증 기반 계정 시스템은 전시 범위에서 제외한다.
- 실제 카카오 메시지, 카카오 화면, 카카오 OAuth, n8n 운영 workflow는 전시 범위에서 제거한다.
- 현재 MVP 알림 채널은 이메일 하나로 고정한다.

## 4. 화면별 목표

| 화면 | 현재 역할 | 데이터 상태 |
|---|---|---|
| AI 브리핑 | 시장 신호, 위험도, AI 요약, 주요 뉴스 | 실제 API, 명시적 fallback |
| 뉴스 가드 | 신뢰/주의/차단 뉴스와 판단 사유 | 저장된 필터 뉴스 |
| 산업 영향도 | 산업별 점수와 산업 일치 근거 뉴스 | 실제 뉴스 기반 계산 |
| 포트폴리오 | 관심 자산 CRUD와 평가/뉴스 연결 | 사용자별 DB 저장 |
| 이메일 레터 | 이메일 구독, 확인, 수신 거부, 기본 알림 채널 | 사용자별 DB 저장, provider 검증 필요 |
| 마이페이지 | 프로필, 관심 산업, 연결 상태 | 사용자별 DB 저장 |
| 설정 | 데이터/뉴스/알림/표시 설정 | 사용자별 DB 저장 |
| 로그인/온보딩 | Google OAuth 로그인과 관심 설정 | 코드 준비 완료, 운영 설정 필요 |

## 5. 인증 및 사용자 데이터 방향

```text
사용자
-> Google OAuth
-> FastAPI callback
-> httpOnly 세션 쿠키
-> 사용자별 portfolio / preferences / settings / email subscription
```

- 운영 환경에서는 세션 쿠키를 `Secure`, `SameSite=None`으로 사용한다.
- `X-User-ID` fallback은 로컬/개발 환경에서만 허용한다.
- Google의 Gmail, Drive, Calendar 등 민감 권한은 요청하지 않는다.
- 카카오 OAuth 프로토타입 화면은 전시 버전에서 노출하지 않는다.
- 이메일 구독은 인증 사용자 기준으로 저장하며, 확인 전 상태는 `pending`, 확인 완료 후 `active`로 관리한다.
- 수신 거부와 bounce/complaint 발생 사용자는 후속 발송 대상에서 제외한다.

## 6. 데이터 신뢰성 방향

- 대시보드 요청 중 외부 provider를 동기 호출하지 않는다.
- 데이터 갱신은 `scripts/refresh_pipeline_data.py` 명령으로 분리한다.
- API는 저장된 필터 뉴스와 시장 데이터부터 제공한다.
- provider 장애, 오래된 데이터, fallback 사용 여부를 metadata로 전달한다.
- 뉴스 제목은 refresh 간 중복을 제거하고 금융 관련성 경계를 적용한다.
- 산업 상세 근거에는 해당 산업 키워드와 실제로 일치한 뉴스만 사용한다.

## 7. 개발 우선순위

### P0: 전시용 이메일 알림 MVP 완성

- Render + PostgreSQL 배포
- Vercel 환경 변수와 CORS 설정
- Google Cloud Console, Render, Vercel 운영 설정
- Google OAuth login/callback/me/logout smoke test
- 카카오/n8n 메뉴와 문구 제거 상태 재확인
- refresh command 정기 실행
- 이메일 구독/확인/수신 거부 API smoke test
- 일일 요약 이메일과 RED/YELLOW 즉시 알림 dispatch 검증
- `notification_deliveries` 중복 방지와 실패 이력 저장 검증
- 로컬 백업 데모, 핵심 화면 스크린샷, 3분 발표 동선 준비

### P1: 운영 안정성

- Alembic 등 versioned migration 도입
- provider 장애 모니터링과 refresh 로그
- exchange calendar 기반 거래일 정합성
- GitHub Actions CI
- 이메일 provider 도메인 검증, webhook 운영 검증, bounce/complaint 대응 정책 정리

### P2: 전시 이후 기능 확장

- 정식 인증 정책: Google OAuth 운영 유지 또는 자체 회원가입/로그인 구현
- 추가 뉴스/시장 provider
- 알림 전송 이력과 재시도
- 분석 모델 및 백테스트 고도화

## 8. 현재 판단

FinLightAI MVP의 핵심 화면과 API 연결은 완료됐다. 2026-07-13 작품 전시 기준 제품 방향은 카카오/n8n을 화면과 발표에서 제거하고, 이메일 알림 기반 MVP로 단순하고 안정적으로 보여주는 것이다.

Google OAuth 코드는 전시용으로 준비됐고, 실제 전시 전에는 사용자가 Google Cloud Console origin/callback, Render 환경 변수, Vercel `VITE_API_BASE_URL`을 설정한 뒤 smoke test를 끝내야 한다. 남은 시간은 계정 기능 확장보다 배포, 이메일 smoke test, 화면 문구 정리, 백업 데모 준비에 써야 한다.
