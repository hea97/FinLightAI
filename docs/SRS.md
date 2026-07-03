# 소프트웨어 요구사항 명세서 (SRS)

**프로젝트명**: FinLightAI
**버전**: v4.1
**최종 업데이트**: 2026-07-03
**상태**: 실제 API, Google OAuth, 이메일 구독 구현 기준

## 1. 목적과 범위

FinLightAI는 금융 뉴스와 시장 데이터를 분석해 시장 상태, 뉴스 품질, 산업 영향, 관심 자산 리스크를 근거와 함께 제공한다. 투자 추천, 주문 실행, 수익 보장은 범위에 포함하지 않는다.

```text
provider 수집
-> DB 저장
-> 관련성/신뢰도/감성/시장 반응 분석
-> 시장 신호 생성
-> FastAPI
-> React UI
```

## 2. 사용자 역할

| 역할 | 권한 |
|---|---|
| 비로그인 사용자 | 공개 페이지와 기본 대시보드 조회, Google 로그인 시작 |
| 로그인 사용자 | 온보딩, 포트폴리오, 마이페이지, 설정, 알림 규칙 관리 |
| 운영자 | 환경 변수, 데이터 refresh, provider와 배포 상태 관리 |

## 3. 기능 요구사항

| ID | 기능 | 요구사항 | 상태 |
|---|---|---|---|
| R01 | AI 브리핑 | 신호, 위험도, 요약, 근거 뉴스를 표시한다. | 구현 |
| R02 | 데이터 상태 | source, provider, fallback, warning을 표시한다. | 구현 |
| R03 | 뉴스 가드 | 전체/신뢰/주의/차단 필터와 판정 사유를 제공한다. | 구현 |
| R04 | 산업 영향도 | 산업 점수와 해당 산업에 일치하는 근거 뉴스를 제공한다. | 구현 |
| R05 | 포트폴리오 | 관심 자산을 생성, 조회, 수정, 삭제한다. | 구현 |
| R06 | 사용자 설정 | 마이페이지, preference, 설정을 사용자별 저장한다. | 구현 |
| R07 | Google 인증 | login, callback, me, logout과 세션 쿠키를 제공한다. | 구현 |
| R08 | 온보딩 | 관심 시장, 산업, 알림 여부를 저장한다. | 구현 |
| R09 | 카카오 규칙 | 알림 규칙을 조회하고 변경한다. | 구현 |
| R10 | 카카오 발송 | n8n과 카카오 채널을 통해 메시지를 발송한다. | 미구현 |
| R11 | 데이터 갱신 | 요청 처리와 분리된 명령으로 파이프라인을 갱신한다. | 구현 |
| R12 | 운영 배포 | Vercel/Render/PostgreSQL 환경에서 전체 흐름을 검증한다. | 검증 필요 |
| R13 | 이메일 구독 | 이메일과 수신 동의를 사용자별 저장하고 상태를 조회한다. | 구현 |
| R14 | 이메일 발송 | 인증, 해지, 발송 및 실패 이력을 관리한다. | 미구현 |

## 4. 상세 요구사항

### 4.1 AI 브리핑

- API: `GET /api/briefing`
- 최신 저장 signal과 필터 뉴스를 우선 사용한다.
- Gemini를 사용할 수 있으면 AI 요약을 제공한다.
- Gemini unavailable/error 시 정적 요약으로 대체하고 상태를 노출한다.
- 실제 데이터가 없는 demo/mock 패널은 숨기거나 명시적으로 표시한다.

### 4.2 뉴스 가드

- API: `GET /api/news-guard?filter={all|trusted|watch|blocked}`
- 기사별 제목, 출처, provider, 게시 시각, 신뢰도, 영향도, 감성, 판정 사유를 제공한다.
- 중복 제목과 금융 관련성이 낮은 기사를 제거한다.
- provider 장애 시 저장 데이터 또는 fallback 사용 여부를 경고한다.
- 자동 판정을 사실 확정이나 법적 판단처럼 표현하지 않는다.

### 4.3 산업 영향도

- API: `GET /api/industry-impact`
- 산업별 점수, 상태, 관련 뉴스 수, 관련 종목을 제공한다.
- 상세 패널은 선택 산업 키워드에 일치한 뉴스만 사용한다.
- 근거가 부족하면 빈 상태 또는 데이터 부족 상태를 표시한다.

### 4.4 포트폴리오

- API:
  - `GET /api/portfolio`
  - `POST /api/portfolio`
  - `PATCH /api/portfolio/{asset_id}`
  - `DELETE /api/portfolio/{asset_id}`
- 자산명, symbol, 시장, 산업, 수량, 평균 매입가, 통화, 메모를 관리한다.
- 가격 출처가 yfinance인지 저장된 reference/fallback인지 표시한다.
- 자산은 인증 사용자에게 귀속되며 다른 사용자 데이터에 접근할 수 없어야 한다.
- 거래 주문이나 증권 계좌 연동은 제공하지 않는다.

### 4.5 인증과 온보딩

- API:
  - `GET /api/auth/google/login`
  - `GET /api/auth/google/callback`
  - `GET /api/auth/me`
  - `POST /api/auth/logout`
  - `GET/PUT /api/onboarding/preferences`
- Google scope는 `openid`, `email`, `profile`만 요청한다.
- callback의 state를 검증하고 사용자/provider 식별자를 저장한다.
- 세션은 서명된 httpOnly 쿠키를 사용한다.
- production 쿠키는 `Secure`, `SameSite=None`이어야 한다.
- `X-User-ID` 개발 fallback은 production에서 거부한다.
- 카카오 OAuth는 현재 MVP 인증 방식이 아니다.

### 4.6 마이페이지와 설정

- API: `GET/PATCH /api/mypage`, `GET/PUT /api/settings`
- 프로필, 관심 산업, 알림/표시/데이터 설정을 사용자별 저장한다.
- 저장 성공, 실패, 로딩 상태를 UI에 제공한다.

### 4.7 카카오 알림

- API: `GET /api/kakao-alert`, `PATCH /api/kakao-alert/rules/{rule_id}`
- 알림 규칙 저장과 메시지 preview를 제공한다.
- 실제 카카오 채널 발송과 n8n webhook은 후속 요구사항이다.
- 메시지에는 상태, 근거, 갱신 시각, 투자 추천 아님 고지를 포함한다.

### 4.8 이메일 레터

- API: `GET/PUT /api/email-subscription`
- 이메일 주소는 trim 후 소문자로 정규화한다.
- 명시적 수신 동의가 없거나 형식이 잘못된 이메일은 `400`으로 거부한다.
- 구독 상태, 이메일, 동의 시각을 인증 사용자 기준으로 저장한다.
- 활성 구독은 마이페이지와 알림 화면의 기본 전달 채널로 표시한다.
- 실제 메일 발송 전에는 UI에 `발송 준비` 또는 `발송 서비스 연결 전` 상태를 표시한다.
- 운영 전 double opt-in, 수신 거부, 발송 실패, bounce/complaint 요구사항을 구현한다.

## 5. 데이터 및 API 계약

모든 주요 분석 응답은 가능한 경우 다음 metadata를 포함한다.

```text
dataSource
generatedAt
providers[]
warnings[]
fallbackUsed
```

- API schema는 `src/dashboard/schemas.py`를 기준으로 한다.
- 프론트 타입은 `frontend/src/types/`에서 API와 동기화한다.
- 프론트 service는 `frontend/src/services/`에서 `apiFetch`를 사용한다.
- cross-origin 인증 요청은 `credentials: include`를 사용한다.

## 6. 저장 요구사항

- 개발 환경은 SQLite를 사용할 수 있다.
- 운영 환경은 `DATABASE_URL` 기반 PostgreSQL을 사용한다.
- users, preferences, portfolio, settings, alert rules, news, market prices, signals, provider status를 저장한다.
- email subscriptions에는 user ID, 이메일, 상태, 동의 시각, 변경 시각을 저장한다.
- 외부 PostgreSQL URL은 psycopg v3 driver 형식으로 정규화한다.
- 운영 데이터 사용 전 `create_all`을 versioned migration으로 교체해야 한다.
- 기존 SQLite `users` 테이블은 idempotent 호환 패치로 OAuth 필드를 보완한다.

## 7. 비기능 요구사항

| ID | 분야 | 요구사항 |
|---|---|---|
| NF01 | 보안 | secret은 백엔드 환경 변수로만 관리한다. |
| NF02 | 개인정보 | OAuth 최소 정보와 최소 scope만 사용한다. |
| NF03 | 신뢰성 | fallback과 provider 장애를 숨기지 않는다. |
| NF04 | 성능 | dashboard GET 요청 중 외부 수집을 동기 실행하지 않는다. |
| NF05 | 접근성 | 키보드 조작, focus, label, 색상 외 상태 텍스트를 제공한다. |
| NF06 | 반응형 | 모바일/데스크톱에서 overflow와 겹침이 없어야 한다. |
| NF07 | 테스트 | auth, API, pipeline, DB, settings 회귀 테스트를 유지한다. |
| NF08 | 규정 표현 | 투자 추천 또는 확정적 수익 표현을 금지한다. |
| NF09 | 이메일 준수 | 동의, 해지, 개인정보 및 발송 상태를 추적할 수 있어야 한다. |

## 8. 배포 요구사항

- 프론트엔드는 Vercel, 백엔드는 Render 구성을 우선한다.
- `VITE_API_BASE_URL`은 실제 백엔드 origin을 가리켜야 한다.
- CORS는 실제 프론트 origin만 허용하고 credentials를 활성화한다.
- Google redirect URI는 백엔드 callback과 정확히 일치해야 한다.
- 배포 후 로그인, callback, me, logout과 사용자별 CRUD를 smoke test한다.
- 데이터 refresh는 scheduler에서 명시적 명령으로 실행한다.

## 9. 알려진 제약

- 카카오 채널 실제 발송과 n8n은 연결 전이다.
- Guardian/Finnhub는 credential 준비 후 추가한다.
- 거래일 계산은 exchange calendar 도입 전까지 제한이 있다.
- 무료 provider의 rate limit과 일시 장애가 데이터 최신성에 영향을 줄 수 있다.
- 자동 뉴스 품질 점수는 사람의 검토를 대체하지 않는다.
- 이메일 구독 정보는 저장되지만 실제 이메일 발송은 아직 제공하지 않는다.

## 10. 검증 기준

- 2026-07-03 기준 backend test 62개 통과
- 이메일 구독 저장, 동의 필수, 이메일 형식 오류 테스트 포함
- frontend TypeScript 검사와 Vite production build 통과
