# FinLightAI 전체 기획서

작성일: 2026-05-29
최종 업데이트: 2026-07-09
문서 상태: 실제 API, Google OAuth, 이메일 알림 MVP 범위 반영

## 1. 한 줄 정의

FinLightAI는 금융 뉴스의 신뢰도와 시장 반응을 분석해 시장 신호, 산업 영향, 관심 자산 리스크를 근거와 함께 보여주는 AI 금융 상황판이다.

## 2. 핵심 사용자 가치

1. 여러 뉴스를 읽기 전에 오늘 시장 상태를 빠르게 파악한다.
2. 뉴스의 영향도와 신뢰도를 분리해 과장되거나 관련성이 낮은 정보를 구분한다.
3. 산업과 관심 자산에 어떤 뉴스가 연결되는지 확인한다.
4. AI 요약의 근거와 데이터 상태를 함께 확인한다.

## 3. 사용자와 주요 흐름

주요 사용자는 AI, 반도체, 정책, 금융 뉴스가 시장에 미치는 영향을 추적하는 개인 사용자다.

```text
공개 페이지 확인
-> Google 로그인
-> 관심 시장/산업 온보딩
-> AI 브리핑
-> 뉴스 가드/산업 근거 확인
-> 관심 자산 등록
-> 이메일 레터 구독
-> 이메일 확인 및 알림 수신 설정
-> 설정 및 알림 규칙 관리
```

## 4. 기능 현황

| 기능 | 상태 | 비고 |
|---|---|---|
| AI 브리핑 | 구현 | 실제 API, Gemini 또는 정적 fallback |
| 뉴스 가드 | 구현 | 저장된 필터 뉴스, provider/품질 표시 |
| 산업 영향도 | 구현 | 산업 일치 뉴스만 근거로 사용 |
| 포트폴리오 CRUD | 구현 | 로그인 사용자별 DB 저장 |
| 마이페이지/설정 | 구현 | 사용자별 조회 및 변경 |
| Google OAuth | 구현 | 운영 Google/Render 설정 필요 |
| 이메일 레터 구독 | 구현 | modal, API, 사용자별 DB 저장 |
| 이메일 확인/수신 거부 | 구현 | double opt-in, unsubscribe API, 로컬 테스트 통과 |
| 이메일 실제 발송 | 구현, 운영 검증 필요 | Resend/SMTP adapter, provider 환경 검증 필요 |
| 일일 요약/즉시 알림 | 구현, 운영 검증 필요 | script와 dispatch 흐름, 배포 smoke test 필요 |
| 카카오 알림 규칙 | 구현, 외부 발송 제외 | 규칙/preview/준비 상태만 제공 |
| 카카오 챗봇 + n8n | 향후 확장 | 카카오 승인 후 별도 운영 기능 |

## 5. 핵심 기능 정책

### AI 브리핑

- 위험도와 RED/YELLOW/GREEN 상태를 제공한다.
- 저장된 실제 뉴스와 신호를 우선 사용한다.
- Gemini 상태가 unavailable/error이면 정적 요약으로 대체한다.
- 연결되지 않은 mock 시장 패널은 숨기거나 명확히 표시한다.

### 뉴스 가드

- `전체`, `신뢰`, `주의`, `차단` 필터를 제공한다.
- 출처, provider, 게시 시각, 신뢰도, 영향도, 감성, 판단 사유를 표시한다.
- 동일 제목과 금융 관련성이 낮은 기사를 제거한다.
- 자동 판정은 확정적 사실 검증이 아니라 검토 우선순위 정보다.

### 산업 영향도

- 산업별 점수, 상태, 관련 뉴스 수, 관련 종목을 표시한다.
- 선택한 산업과 일치하는 뉴스만 상세 근거에 노출한다.
- 데이터 부족 상태를 중립 점수로 위장하지 않는다.

### 포트폴리오

- 사용자가 관심 자산, 수량, 평균 매입가, 메모를 관리한다.
- 현재가는 yfinance 또는 저장된 reference price의 출처를 표시한다.
- 평가금액과 손익은 정보 표시이며 주문 기능은 제공하지 않는다.
- 데이터는 인증된 사용자 ID 기준으로 분리한다.

### 인증과 온보딩

- MVP 로그인은 Google OAuth다.
- 요청 scope는 `openid`, `email`, `profile`로 제한한다.
- callback 성공 후 httpOnly 세션 쿠키를 발급한다.
- 관심 시장, 산업, 알림 여부를 사용자 preference에 저장한다.
- 카카오 OAuth는 사업자 요건 때문에 후순위다.

### 카카오 알림

- 현재 화면과 규칙 저장 API는 구현됐다.
- 실제 카카오 채널 발송과 n8n 운영 workflow는 2026-07-08 MVP 범위에서 제외한다.
- 발표와 문서에서는 `카카오는 향후 확장, 현재 MVP는 이메일 알림`으로 표현을 통일한다.
- 메시지는 투자 행동 유도가 아니라 상태, 근거, 대시보드 CTA로 구성한다.
- 알림 채널 범위는 MVP에서 `이메일`로 한정하고, 카카오는 규칙/preview/향후 연동 안내만 제공한다.
- 카카오 OAuth는 MVP 로그인 경로가 아니며, 실제 사용자 인증은 Google OAuth로 설명한다.
- 카카오 관련 화면은 완료 기능이 아니라 향후 확장 계획과 상태 확인 화면으로만 소개한다.

### 이메일 레터

- 카카오 채널 승인 전 MVP 기본 알림 채널로 사용한다.
- 사용자는 modal에서 이메일과 수신 동의를 제출한다.
- `GET/PUT /api/email-subscription`으로 사용자별 구독 상태를 조회·저장한다.
- 구독 완료 상태는 헤더, 포트폴리오, 마이페이지, 설정, 로그인 화면에 일관되게 표시한다.
- 구독 신청 후 double opt-in 확인 링크로 `active` 상태를 만든다.
- 사용자는 이메일 링크로 수신 거부할 수 있으며 이후 발송 대상에서 제외한다.
- 일일 요약은 RED/YELLOW/GREEN 수와 최신 신호 하이라이트를 제공한다.
- 즉시 알림은 RED/YELLOW 신호만 대상으로 하며 GREEN은 제외한다.
- 동일 날짜 또는 동일 `event_key + ticker + trade_date` 발송은 중복 저장/발송을 막는다.
- 실제 운영 전 provider 도메인, 발신 주소, webhook, bounce/complaint 처리를 검증한다.
- 발송 실패 재시도, provider rate limit, suppression list 운영은 P1 안정화 과제로 관리한다.

## 6. 기술 및 데이터 구조

프론트엔드:

- `frontend/`: Vite + React + TypeScript
- `frontend/src/services/`: FastAPI 호출
- `frontend/src/types/`: API 계약 타입
- `frontend/src/data/`: fallback/표시 보조 데이터

백엔드:

- `src/dashboard/routes/api.py`: API와 인증 route
- `src/dashboard/schemas.py`: Pydantic 응답 계약
- `src/dashboard/repository.py`: 사용자/시장 데이터 저장
- `src/dashboard/services/data_pipeline.py`: 수집-분석-저장 orchestration
- `src/collector/`, `src/processor/`, `src/signal/`: 분석 파이프라인
- `src/notifier/email_sender.py`: SMTP/Resend 이메일 발송 adapter
- `src/notifier/notification_service.py`: 구독 확인, 수신 거부, dispatch, 발송 이력 관리
- `scripts/send_daily_summary.py`: KST 기준 일일 요약 발송 entrypoint

저장소:

- 개발 기본값은 SQLite다.
- 운영은 `DATABASE_URL` 기반 PostgreSQL을 지원한다.
- 일반 `postgres://`/`postgresql://` URL은 psycopg v3 형식으로 정규화한다.
- 알림 관련 테이블은 Alembic migration으로 관리하며, 신규 및 기존 SQLite DB 기준 `alembic upgrade head` 검증을 통과했다. 운영 PostgreSQL에서는 배포 후 동일 migration 적용을 확인해야 한다.
- 기존 SQLite 사용자 테이블에는 누락 OAuth 컬럼을 보완하는 idempotent 호환 패치를 적용한다.

## 7. 실제 API

```text
GET  /api/auth/google/login
GET  /api/auth/google/callback
GET  /api/auth/me
POST /api/auth/logout

GET  /api/briefing
GET  /api/news-guard
GET  /api/industry-impact
GET  /api/signals
GET  /api/market

GET/POST          /api/portfolio
PATCH/DELETE      /api/portfolio/{asset_id}
GET/PUT           /api/onboarding/preferences
GET/PUT           /api/email-subscription
GET               /api/email-subscription/confirm
GET               /api/email-subscription/unsubscribe
POST              /api/notifications/dispatch
POST              /api/notifications/email-events
GET/PATCH         /api/mypage
GET/PUT           /api/settings
GET               /api/kakao-alert
PATCH             /api/kakao-alert/rules/{rule_id}
```

## 8. 배포 계획

- 프론트엔드: Vercel
- 백엔드: Render 권장
- 운영 DB: Render PostgreSQL 등 외부 PostgreSQL
- 브라우저 요청: `VITE_API_BASE_URL`로 백엔드 지정
- 쿠키 인증을 위해 정확한 CORS origin과 credentials 설정 필수

## 9. 다음 마일스톤

1. 실제 Vercel/Render 주소 확정 및 환경 변수 설정
2. Google OAuth Consent Screen/Client 등록
3. 배포 로그인과 사용자별 API smoke test
4. 데이터 refresh scheduler 구성
5. 이메일 provider 환경 변수와 발신 도메인 검증
6. 이메일 구독/확인/수신 거부/일일 요약/RED-YELLOW 알림 smoke test
7. DB migration 적용과 CI 도입
8. 발송 실패 재시도와 suppression list 운영 정책 정리
9. 카카오 채널 + n8n 연동 착수

## 10. 발표 및 보고서 문구

발표 PPT의 기능 상태 문구는 아래 한 문장으로 통일한다.

> 이메일 알림 MVP 구현, 카카오는 향후 확장

발표에서 구현 완료로 말할 수 있는 범위:

- Google OAuth 기반 로그인 API와 httpOnly 세션 쿠키
- 이메일 구독 저장, 24시간 double opt-in 확인 링크, 수신 거부 링크
- 일일 요약과 RED/YELLOW 즉시 알림 dispatch, GREEN 즉시 발송 제외
- `notification_deliveries` 기반 발송 성공/실패/중복/bounce/complaint 이력 구조

발표에서 운영 검증 필요로 말해야 하는 범위:

- Render/Vercel 실제 URL 기반 OAuth callback, CORS, cookie smoke test
- Resend 또는 SMTP 실제 발신 도메인 검증과 테스트 메일 수신
- provider webhook signature와 bounce/complaint 운영 검증
- 카카오 채널, n8n workflow, 실제 카카오 메시지 발송

## 11. 최신 검증

- 2026-07-08: 이메일 알림 MVP TODO 기준으로 제품 범위를 이메일 우선으로 재정렬
- 2026-07-09: backend `python -m pytest` 78개 통과
- 2026-07-09: 알림 지정 테스트 `python -m pytest tests/test_notifications.py tests/test_daily_summary.py` 12개 통과
- 2026-07-09: 신규 및 기존 SQLite DB 기준 Alembic `upgrade head` 통과, `email_subscriptions`와 `notification_deliveries` 생성 확인
- 2026-07-09: frontend TypeScript 검사 및 Vite production build 통과
