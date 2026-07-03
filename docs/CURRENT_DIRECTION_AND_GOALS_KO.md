# FinLightAI 현재 방향성과 목표 계획서

작성일: 2026-06-21
최종 업데이트: 2026-07-03
기준 브랜치: `deploy/vercel-frontend`

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

## 2. 2026-07-01 구현 현황

### 완료

- Vite + React + TypeScript 대시보드와 FastAPI API 연결
- 브리핑, 뉴스 가드, 산업 영향도에 실제 저장 데이터 우선 적용
- Google News RSS 등 provider 기반 뉴스 수집과 중복/관련성 필터
- yfinance 기반 시장 데이터 수집과 DB upsert
- 뉴스 및 시장 반응 기반 신호 생성과 DB 저장
- 데이터 출처, provider, fallback, 경고 metadata 표시
- 포트폴리오 CRUD, 마이페이지, 설정, 카카오 알림 규칙의 DB 저장
- Google OAuth 로그인, callback, 세션 쿠키, 로그아웃
- 로그인 사용자 기준 포트폴리오/설정/온보딩 데이터 분리
- 이메일 레터 구독 modal, 구독 API, 사용자별 DB 저장
- 카카오 승인 전 이메일을 기본 알림 채널로 표시
- 기존 SQLite `users` 테이블용 idempotent 호환 마이그레이션
- Vercel 프론트엔드와 Render 백엔드 배포 문서 및 설정
- `/about`, `/login`, `/signup`, `/privacy`, `/terms` 공개 페이지

### 운영 환경 확인 필요

- Google Cloud OAuth Consent Screen 및 Web Client 설정
- 실제 Vercel/Render URL로 redirect URI와 CORS 설정
- Render 백엔드 및 PostgreSQL 배포
- 배포 환경에서 로그인과 사용자별 API smoke test
- 정기 데이터 refresh 스케줄러 연결
- 실제 이메일 발송 provider, double opt-in, 수신 거부 연결

### 후속 범위

- 카카오 채널 챗봇 + n8n 실연동 및 심사
- Guardian/Finnhub adapter와 선택적 pykrx provider
- DB migration 도구 도입
- 정확한 거래일 계산용 exchange calendar
- CI, Docker, 모델 고도화

## 3. 제품 원칙

- `매수`, `매도`, `수익 보장`, `상승 확정` 표현을 사용하지 않는다.
- RED/YELLOW/GREEN은 투자 지시가 아니라 시장 상태 신호다.
- 점수와 요약에는 가능한 한 데이터 출처와 판단 근거를 함께 표시한다.
- 실제 데이터가 없을 때 fallback을 실제 데이터처럼 보이게 하지 않는다.
- Gemini 요약 실패 시 원문 기반 정적 요약으로 대체하고 상태를 표시한다.
- 인증은 최소 권한 Google OAuth(`openid`, `email`, `profile`)를 사용한다.
- 카카오 OAuth와 카카오 알림은 별도 기능이며, MVP 로그인은 Google이다.

## 4. 화면별 목표

| 화면 | 현재 역할 | 데이터 상태 |
|---|---|---|
| AI 브리핑 | 시장 신호, 위험도, AI 요약, 주요 뉴스 | 실제 API, 명시적 fallback |
| 뉴스 가드 | 신뢰/주의/차단 뉴스와 판단 사유 | 저장된 필터 뉴스 |
| 산업 영향도 | 산업별 점수와 산업 일치 근거 뉴스 | 실제 뉴스 기반 계산 |
| 포트폴리오 | 관심 자산 CRUD와 평가/뉴스 연결 | 사용자별 DB 저장 |
| 카카오 알림 | 규칙 관리와 향후 연동 흐름 | 사용자별 DB, 외부 전송 미연결 |
| 이메일 레터 | 이메일 구독 및 기본 알림 채널 설정 | 사용자별 DB 저장, 실제 발송 미연결 |
| 마이페이지 | 프로필, 관심 산업, 연결 상태 | 사용자별 DB 저장 |
| 설정 | 데이터/뉴스/알림/표시 설정 | 사용자별 DB 저장 |
| 로그인/온보딩 | Google 로그인과 관심 설정 | API 구현, 운영 OAuth 설정 필요 |

## 5. 인증 및 사용자 데이터 방향

```text
사용자
-> Google OAuth
-> FastAPI callback
-> httpOnly 세션 쿠키
-> 사용자별 portfolio / preferences / settings / alert rules
```

- 운영 환경에서는 세션 쿠키를 `Secure`, `SameSite=None`으로 사용한다.
- `X-User-ID` fallback은 로컬/개발 환경에서만 허용한다.
- Google의 Gmail, Drive, Calendar 등 민감 권한은 요청하지 않는다.
- 카카오 OAuth 프로토타입 화면은 레거시 참고용이며 실제 MVP 진입 경로가 아니다.
- 이메일 구독은 인증 사용자 기준으로 저장하며, 현재 실제 메일을 발송하지 않는다.

## 6. 데이터 신뢰성 방향

- 대시보드 요청 중 외부 provider를 동기 호출하지 않는다.
- 데이터 갱신은 `scripts/refresh_pipeline_data.py` 명령으로 분리한다.
- API는 저장된 필터 뉴스와 시장 데이터부터 제공한다.
- provider 장애, 오래된 데이터, fallback 사용 여부를 metadata로 전달한다.
- 뉴스 제목은 refresh 간 중복을 제거하고 금융 관련성 경계를 적용한다.
- 산업 상세 근거에는 해당 산업 키워드와 실제로 일치한 뉴스만 사용한다.

## 7. 개발 우선순위

### P0: 배포 검증

- Render + PostgreSQL 배포
- Vercel 환경 변수와 CORS 설정
- Google OAuth 운영 설정 및 로그인 smoke test
- refresh command 정기 실행
- 이메일 구독 API의 배포 DB smoke test

### P1: 운영 안정성

- Alembic 등 versioned migration 도입
- provider 장애 모니터링과 refresh 로그
- exchange calendar 기반 거래일 정합성
- GitHub Actions CI
- 이메일 provider 선정, double opt-in, 해지와 발송 이력 구현

### P2: 기능 확장

- 카카오 채널 챗봇 + n8n
- 추가 뉴스/시장 provider
- 알림 전송 이력과 재시도
- 분석 모델 및 백테스트 고도화

## 8. 현재 판단

FinLightAI MVP의 핵심 화면과 API 연결은 완료됐다. 지금 가장 중요한 일은 기능을 더 늘리는 것이 아니라 배포 환경에서 인증, DB, CORS, 데이터 갱신을 끝까지 검증하는 것이다.

2026-07-03 로컬 검증 기준으로 백엔드 테스트 62개와 프론트엔드 production build가 통과했다. 이메일 레터는 구독 저장 단계까지 완료됐으며 실제 발송 기능으로 오해되지 않게 표시해야 한다.
