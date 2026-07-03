# FinLightAI API 연동 TODO

기준일: 2026-07-02  
목적: 데모 UI와 실제 API 상태를 분리하고, 운영 가능한 API 연동까지 필요한 작업을 우선순위대로 정리한다.

## 현재 상태 요약

- [x] FastAPI 라우터와 Pydantic 응답 스키마 구현
- [x] React 서비스 계층에서 FastAPI 호출
- [x] Google News RSS 실제 뉴스 수집
- [x] yfinance 실제 시장 데이터 수집 및 저장
- [x] GDELT 수집기, timeout, 오류 상태 처리
- [x] BBC RSS provider와 fallback 처리
- [x] 뉴스 필터, 중복 제거, 신호 계산 파이프라인
- [x] 핵심 API·파이프라인 테스트 28개 통과
- [ ] 사용자 기반 API의 로컬 DB 스키마 오류 해결
- [ ] NewsAPI를 실제 메인 수집 파이프라인에 연결
- [ ] Guardian/Finnhub provider 구현
- [ ] Gemini 실제 요약 성공 상태 확보
- [ ] Google OAuth 운영 키 설정 및 로그인 검증
- [ ] Kakao 실제 메시지 발송
- [ ] 이메일 구독 저장 및 실제 레터 발송

현재 실제 provider 상태:

| Provider | 상태 | 비고 |
|---|---|---|
| Google News RSS | 연결됨 | 실제 뉴스 사용 중 |
| yfinance | 연결됨 | 저장된 시장 데이터 사용 중 |
| GDELT | 오류 | 구현 완료, 현재 외부 호출 실패 |
| BBC RSS | fallback | 보조 데이터 상태 |
| NewsAPI | disabled | 키 없음, 메인 파이프라인 미연결 |
| Guardian | disabled | 키·adapter 없음 |
| Finnhub | disabled | 키·adapter 없음 |
| Gemini | fallback | 키는 있으나 정적 요약 사용 중 |
| OpenAI | disabled | 키·호출 경로 없음 |
| KIS | disabled | 키 없음 |
| Kakao | disabled | 키 및 실제 발송 미연결 |
| Email | local demo | 브라우저 구독 상태만 저장 |

## P0. API 500 오류 및 DB 마이그레이션

- [ ] SQLite `users` 테이블에 현재 모델 컬럼이 없는 문제를 해결한다.
  - 누락 확인 컬럼: `provider`, `provider_user_id`, `profile_image_url` 등
  - 기존 사용자 데이터 보존 방식 결정
  - 개발 DB와 배포 DB에 동일한 migration 적용
- [ ] `create_all()` 의존을 줄이고 Alembic 또는 명시적 migration 체계를 추가한다.
- [ ] migration 전 DB 백업 절차를 문서화한다.
- [ ] 아래 API가 모두 `200`을 반환하도록 복구한다.
  - [ ] `GET /api/portfolio`
  - [ ] `GET /api/kakao-alert`
  - [ ] `GET /api/mypage`
  - [ ] `GET /api/settings`
- [ ] 사용자별 쓰기 API 회귀 테스트를 추가한다.
  - [ ] 포트폴리오 추가·수정·삭제
  - [ ] 알림 규칙 수정
  - [ ] 마이페이지 관심 산업·알림 설정 수정
  - [ ] 설정 저장

완료 조건:

- 로컬 기존 DB와 신규 빈 DB 모두에서 migration 성공
- 사용자 기반 API smoke test 전체 `2xx`
- 테스트 실행 시 임시 DB와 실제 개발 DB의 스키마 차이 없음

## P0. 화면의 실제 API 상태 표시

- [ ] 데모용 `정상` 표시와 백엔드 provider 상태를 분리한다.
- [ ] API 상태 카드는 `/api/briefing` 또는 전용 provider 상태 API를 기준으로 렌더링한다.
- [ ] 상태 라벨을 다음 값으로 통일한다.
  - `connected`
  - `disabled`
  - `timeout`
  - `rate_limited`
  - `fallback`
  - `error`
- [ ] 마지막 성공 시각과 마지막 실패 사유를 provider별로 표시한다.
- [ ] 수동 새로고침 버튼이 실제 상태 재조회만 수행하도록 한다.
  - 외부 데이터 전체 수집은 별도 관리자 작업으로 분리
- [ ] 데모 화면에는 `DEMO`, 실제 화면에는 `LIVE` 배지를 명확히 표시한다.

완료 조건:

- GDELT 오류를 화면에서 `정상`으로 표시하지 않음
- 키가 없는 NewsAPI/Guardian/Finnhub를 `비활성`으로 표시
- fallback 데이터를 실제 연결 데이터처럼 표시하지 않음

## P1. 뉴스 provider 실제 연동

### GDELT

- [ ] 현재 실패 원인을 HTTP 상태·timeout·응답 형식별로 재현한다.
- [ ] 제한적인 재시도와 지수 backoff를 추가한다.
- [ ] 429 응답 시 rate-limit 상태와 다음 재시도 가능 시각을 저장한다.
- [ ] GDELT 장애 시 Google News RSS로 정상 전환되는지 통합 테스트한다.

### NewsAPI

- [ ] `NEWS_API_KEY`를 개발·배포 환경에 안전하게 설정한다.
- [ ] 기존 `collect_from_newsapi()`를 `collect_all()`에 연결한다.
- [ ] provider별 최대 기사 수와 중복 제거 순서를 결정한다.
- [ ] NewsAPI 이용 약관과 기사 본문 저장 가능 범위를 확인한다.
- [ ] 키 누락, 401, 429, timeout 테스트를 추가한다.

### Guardian

- [ ] Guardian provider adapter를 구현한다.
- [ ] `GUARDIAN_API_KEY` 설정 여부에 따라 활성화한다.
- [ ] 제목·요약·원문 URL·발행시각·section을 표준 기사 형식으로 변환한다.
- [ ] 이용 약관과 상업적 사용 조건을 확인한다.

### Finnhub

- [ ] Finnhub company/market news adapter를 구현한다.
- [ ] 포트폴리오 ticker와 Finnhub symbol 매핑을 정의한다.
- [ ] 뉴스 수집과 시세 수집 역할을 분리한다.
- [ ] 무료 요금제 rate limit과 캐시 정책을 적용한다.

### BBC RSS / Google News RSS

- [ ] RSS 날짜 파싱과 timezone 표준화를 재검증한다.
- [ ] Google News 중계 URL과 실제 원문 URL 처리 정책을 결정한다.
- [ ] 원문 URL이 없는 기사는 UI의 원문 링크를 숨긴다.
- [ ] 동일 기사 URL·제목 기준 중복 제거 테스트를 확장한다.

완료 조건:

- 최소 2개 뉴스 provider가 동시에 실제 수집 성공
- 모든 기사에 출처, 발행시각, 원문 URL 존재
- 임의 기사 제목·날짜·URL 생성 금지
- 한 provider 장애가 전체 파이프라인 실패로 이어지지 않음

## P1. 시장 데이터 연동

- [ ] yfinance 수집 결과의 마지막 거래일과 지연 여부를 표시한다.
- [ ] ticker별 통화·거래소·timezone 정보를 저장한다.
- [ ] 주말·휴장일 처리 테스트를 확대한다.
- [ ] 실패 ticker만 재시도하도록 수집 작업을 분리한다.
- [ ] 포트폴리오 현재가의 provider와 기준 시각을 API에 포함한다.
- [ ] KIS/Alpha Vantage/Finnhub 중 운영용 보조 provider를 결정한다.
- [ ] 실제 계좌 연동은 별도 보안 검토 전까지 제외한다.

완료 조건:

- 가격마다 provider, 거래일, 수집시각을 확인 가능
- 오래된 가격을 실시간 가격처럼 표시하지 않음
- 시세 provider 장애 시 마지막 저장 가격임을 명시

## P1. AI 브리핑 연동

- [ ] Gemini fallback 원인을 확인한다.
  - 인증 오류
  - quota/rate limit
  - 모델명 또는 권한 오류
  - 응답 파싱 오류
- [ ] Gemini 요청·응답 schema 검증을 강화한다.
- [ ] 입력 기사에 원문 URL, 출처, 발행시각, 신뢰도 라벨을 포함한다.
- [ ] AI가 생성한 사실과 원문 근거를 연결한다.
- [ ] provider 실패 시 정적 문구가 아닌 규칙 기반 요약 fallback을 만든다.
- [ ] OpenAI를 사용할지 Gemini 단일 provider로 유지할지 결정한다.
- [ ] AI 비용, timeout, 캐시, 재시도 기준을 설정한다.

완료 조건:

- 실제 AI 요약 성공 여부가 provider 상태에 반영됨
- 요약 문장별 근거 기사 확인 가능
- AI 실패 시에도 임의 사실·날짜·수치를 생성하지 않음

## P1. 인증과 사용자 API

- [ ] Google OAuth 개발용 client ID/secret을 설정한다.
- [ ] callback URL을 로컬·배포 환경별로 등록한다.
- [ ] 로그인, callback, 세션 쿠키, 로그아웃을 브라우저에서 검증한다.
- [ ] CORS와 `credentials: include`를 실제 배포 도메인에서 검증한다.
- [ ] `X-User-ID` 임시 브리지를 인증 세션 기반 사용자 ID로 교체한다.
- [ ] 사용자별 데이터 접근 권한 테스트를 추가한다.
- [ ] 세션 만료·잘못된 callback·중복 계정 처리 테스트를 추가한다.

완료 조건:

- 다른 사용자의 포트폴리오·설정을 조회하거나 수정할 수 없음
- 로컬과 배포 환경에서 로그인·로그아웃 성공
- 인증 오류가 500이 아닌 명확한 401/403으로 반환됨

## P2. 이메일 레터 실제 발송

- [ ] 이메일 provider를 선정한다.
  - 후보: Resend, AWS SES, SendGrid
- [ ] 구독 API를 구현한다.
  - [ ] `POST /api/email-subscriptions`
  - [ ] `GET /api/email-subscriptions/me`
  - [ ] `PATCH /api/email-subscriptions/me`
  - [ ] `DELETE /api/email-subscriptions/me`
- [ ] 이메일 주소, 수신 동의 시각, 상태, 인증 token을 DB에 저장한다.
- [ ] double opt-in 인증 메일을 구현한다.
- [ ] 수신 거부 링크와 즉시 해지 처리를 구현한다.
- [ ] RED/YELLOW 즉시 알림과 일일·주간 레터를 분리한다.
- [ ] 템플릿에 기사 원문 링크와 데이터 기준 시각을 포함한다.
- [ ] bounce, complaint, 발송 실패 상태를 기록한다.
- [ ] 개인정보처리방침과 수신 동의 문구를 검토한다.
- [ ] 현재 localStorage 기반 데모 구독을 실제 API로 교체한다.

완료 조건:

- 인증된 이메일에만 발송
- 모든 메일에 수신 거부 제공
- 발송 성공·실패·반송 상태 확인 가능
- API 키와 사용자 이메일이 로그에 노출되지 않음

## P2. Kakao 채널 및 n8n

- [ ] Kakao 비즈니스 채널 승인 상태를 확인한다.
- [ ] 메시지 API 사용 권한과 템플릿 심사를 완료한다.
- [ ] `KAKAO_REST_API_KEY`와 필요한 secret을 배포 환경에 설정한다.
- [ ] n8n webhook 인증 방식을 결정한다.
- [ ] 알림 규칙 충족 시 실제 webhook event를 생성한다.
- [ ] 중복 발송 방지 idempotency key를 추가한다.
- [ ] 발송 결과와 실패 사유를 DB에 기록한다.
- [ ] 재시도·dead-letter 처리 방식을 추가한다.
- [ ] Kakao 승인 전에는 이메일을 기본 수신 채널로 사용한다.

완료 조건:

- 테스트 사용자에게 실제 메시지 1건 발송 성공
- 동일 이벤트 중복 발송 없음
- Kakao 실패 시 이메일 fallback 정책이 동작

## P2. 배포와 운영

- [ ] FastAPI 백엔드와 PostgreSQL 배포 환경을 확정한다.
- [ ] Vercel `VITE_API_BASE_URL`을 실제 백엔드 URL로 설정한다.
- [ ] 개발·스테이징·운영 환경변수를 분리한다.
- [ ] 데이터 수집 scheduler/cron을 구성한다.
- [ ] 외부 provider별 timeout, retry, rate limit, circuit breaker 정책을 정한다.
- [ ] `/health`와 `/readiness`를 분리한다.
- [ ] provider 장애율, API 5xx, 수집 건수, 마지막 성공 시각을 모니터링한다.
- [ ] 로그에서 API key, token, 이메일을 마스킹한다.
- [ ] 배포 후 전체 API smoke test를 자동화한다.

## 권장 실행 순서

1. DB migration과 사용자 API 500 오류 해결
2. 화면의 가짜 `정상` 표시 제거 및 실제 상태 API 연결
3. NewsAPI를 메인 파이프라인에 연결하고 GDELT 오류 대응
4. Gemini 실제 요약 성공 상태 확보
5. Google OAuth 운영 검증
6. 이메일 구독 DB·double opt-in·실제 발송 구현
7. Kakao 승인 후 n8n 및 실제 메시지 발송 연결
8. 배포 scheduler, 모니터링, 보안 점검

## 검증 명령

```powershell
.venv\Scripts\python.exe -m pytest
npm.cmd --prefix frontend run build
```

API smoke test 대상:

```text
GET    /api/briefing
GET    /api/news-guard?filter=all
GET    /api/industry-impact
GET    /api/portfolio
POST   /api/portfolio
GET    /api/kakao-alert
PATCH  /api/kakao-alert/rules/{rule_id}
GET    /api/mypage
PATCH  /api/mypage
GET    /api/settings
PUT    /api/settings
GET    /api/auth/me
```
