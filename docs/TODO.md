# TODO

## Real data integration audit (2026-06-29)

### Current structure

- Collectors live in `src/collector`; processing and scoring live in
  `src/processor` and `src/signal`.
- SQLAlchemy models and repositories live in `src/dashboard`.
- `/api/briefing`, `/api/news-guard`, and `/api/industry-impact` read the
  latest relevant filtered records from SQLite. External collection is only
  performed by `scripts/refresh_pipeline_data.py`.

### Hardcoded, mock, and seed inventory

- `src/collector/news_collector.py` keeps one explicitly labeled seed article
  as the last fallback tier.
- `/api/market` and `/api/signals` now read stored database rows.
- `src/dashboard/repository.py` creates demo portfolio assets with temporary
  reference prices, but portfolio GET responses replace supported symbols with
  yfinance rows and label unmatched values as `mock`.
- Frontend overview-only mock panels remain and are visibly disclosed as mock.

### Planned replacements

- [x] Collect daily OHLCV for NVDA, AMD, 005930.KS, and 000660.KS with
  yfinance; calculate returns, volume ratio, and volatility safely.
- [x] Persist stock rows by `(ticker, trade_date)` upsert and query the latest
  market reaction.
- [x] Normalize GDELT and BBC RSS through provider adapters, retain explicit
  provider failures, and keep seed fallback visibly labeled.
- [x] Persist raw and filtered news, including source/keyword scores,
  duplicate state, and content length.
- [x] Map news to affected tickers, combine news evidence with subsequent
  market reactions, persist signals, and prevent news-only RED signals.
- [x] Add backward-compatible camelCase response metadata to the three
  dashboard APIs: `dataSource`, `providers`, `isFallback`, `lastUpdated`, and
  `warnings`.

## Data pipeline stabilization (2026-06-29)

### Resolved blockers

- [x] All FastAPI tests use isolated temporary SQLite databases.
- [x] Fixture news and the four derived fixture signals were removed from the
  development database with an allowlisted cleanup command.
- [x] `AI` and other relevance terms use token/phrase boundaries.
- [x] Dashboard APIs prefer relevant stored news and never wait for external
  provider calls.
- [x] Low-confidence and seed records cannot be presented as trusted news.
- [x] Provider statuses, fallback metadata, and warnings use the same state.
- [x] Gemini/provider fallback is explicit; dashboard GET requests use a
  static briefing fallback rather than blocking on AI generation.
- [x] Industry evidence is restricted to matching sector articles and market
  tickers.
- [x] Signal evidence includes title, URL, source, provider, and publication
  time. No signal is generated when there is no qualifying real article.
- [x] The UI displays data source, providers, fallback state, last update, and
  warnings. Remaining overview mocks are visibly disclosed.
- [x] `/api/market`, `/api/signals`, and portfolio prices no longer silently
  present fixed values as real.

### Stabilization decision

- The stabilization branch is preserved remotely, but no stable tag has been
  created.
- Authentication work remains deferred until the real-news recovery branch is
  re-reviewed.

### Time and data-integrity rules

- Persist timestamps in UTC and preserve ticker market suffixes.
- A news event may map to multiple tickers; matching uses the latest market
  row on or after publication day when available, never a future return
  presented as contemporaneous evidence.
- Seed records must carry `provider=seed` and `data_source=seed_fallback`.
- Trading-calendar-aware next-session matching remains a documented follow-up;
  the first implementation isolates date matching so a calendar can replace it.

### Provider status

| Provider | Status | Behavior |
| --- | --- | --- |
| GDELT | Degraded | HTTP 429/timeouts are classified explicitly; no seed is disguised as GDELT data |
| BBC RSS | Implemented | Live RSS normalization and isolated failure status |
| Google News RSS | Implemented | Keyless finance-news search fallback with source and relevance metadata |
| NewsAPI | Optional | Enabled by `NEWS_API_KEY`; missing key returns disabled status |
| Guardian | Deferred | Credential setting exists; adapter remains TODO |
| Finnhub | Deferred | Credential setting exists; news adapter remains TODO |
| yfinance | Implemented | US/KR daily OHLCV for the four required tickers |
| pykrx | Deferred | `.KS` yfinance support is the current Korean-market path |

## Real news provider recovery (2026-06-29)

### Completed

- [x] Classified GDELT HTTP 429, timeout, network, and response parsing failures.
- [x] Added keyless Google News RSS as an alternative provider.
- [x] Normalized source, URL, publication time, raw payload, matched keywords,
  and relevance score across RSS articles.
- [x] Calibrated RSS summary length separately from full-article content while
  preserving source and keyword thresholds.
- [x] Stored filter pass/rejection reasons in raw payload metadata.
- [x] Preserved raw syndicated articles while suppressing repeated normalized
  titles from filtered/display results across refreshes.
- [x] Limited signal generation to verified, non-seed, non-duplicate articles
  with traceable URL/source/provider evidence.
- [x] Preserved exchange-local trade dates and replaced stale signal snapshots
  during refresh.
- [x] Exposed verification state and evidence through `/api/signals`.

### Latest verification

- Backend test suite: 42 passed (one upstream Starlette/httpx deprecation warning).
- Frontend TypeScript and Vite production build passed.
- Explicit refresh: 90 collected articles, 12 verified articles, 86 downloaded
  market rows, and 26 generated signals.
- Stored DB: 90 stock rows, 174 raw/filtered news rows, and 26 signals.
- Signals: 23 GREEN, 3 YELLOW, 0 RED; fixture/example.com evidence 0.
- Missing signal URL/source/provider evidence: 0.
- Duplicate URL groups: 0; duplicate titles exposed by the filtered layer: 0.
- Dashboard APIs report `dataSource=real`, providers `Google News RSS` and
  `yfinance`, and `isFallback=false`.
- GDELT remains degraded and is reported as HTTP 429 or timeout; Google News
  RSS remains the healthy live news path.
- Stable tag and main merge remain prohibited until review approval.

## Final stable consistency corrections (2026-06-29)

- [x] Dashboard reads honor persisted `news_filtered.passed_filter` and
  `duplicate_flag`; News Guard displays the same 12 valid rows stored in DB.
- [x] Google News RSS articles distinguish the collection provider from the
  original publisher and no longer claim they were collected by GDELT.
- [x] Unconnected briefing demo panels are hidden, fixed mock timestamps are
  removed, and the static Gemini fallback remains explicitly labeled.
- [x] Portfolio prices expose `priceDataSource`, `priceProvider`,
  `priceStatusLabel`, and `priceAsOf`; yfinance prices no longer carry
  contradictory Finnhub/KIS temporary-price messages.
- [x] `/api/signals` now returns the dashboard metadata envelope plus
  `signalCount`, `verifiedSignalCount`, and the evidence-bearing signal list.
- [x] Browser verification confirmed News Guard count 12, corrected provider
  text, hidden briefing mock values, yfinance labels on both demo assets, and
  no console errors.

### Stable candidate decision

- The five display and contract blockers are resolved.
- `v0.1.0-real-news-signal` is the recommended candidate tag after explicit
  final approval.
- No stable tag, main merge, or authentication work was performed in this
  correction step.

### Remaining pipeline TODO

- [ ] Add an exchange-calendar implementation for exact next-trading-session matching.
- [ ] Add Guardian and Finnhub provider adapters when their credentials are provisioned.
- [ ] Add pykrx as an optional Korean-market provider and compare adjustment semantics.
- [ ] Move schema evolution from `create_all` to versioned migrations before production.
- [ ] Schedule the explicit refresh command outside request handling.

## MVP authentication plan (2026-06-30)

### Current decision

- [x] Use Google OAuth as the primary MVP login method.
- [x] Keep Kakao OAuth as a deferred TODO because Kakao business app and
  business-owner information requirements can block the MVP.
- [x] Keep Kakao channel/alert integration as a separate later feature.
- [x] Preserve the real-news pipeline stable tag; do not merge to `main` just
  to start authentication work.

### Google OAuth requirements

- [ ] Google Cloud OAuth Consent Screen configured with External user type.
- [ ] Test user Google account added while the app is in testing mode.
- [ ] Minimal scopes only: `openid`, `email`, and `profile`.
- [ ] Web OAuth Client ID created.
- [ ] Authorized JavaScript origin set to the Vercel frontend URL.
- [ ] Authorized redirect URI set to
  `https://<backend-render-url>/api/auth/google/callback`.

### Auth implementation checklist

- [x] Add provider-based `users` fields using `provider` and
  `provider_user_id`.
- [x] Add `user_preferences` for onboarding interests and notification
  preferences.
- [x] Implement Google login, callback, current-user, and logout endpoints.
- [x] Save a browser session using an httpOnly cookie.
- [x] Use authenticated user context for portfolio, mypage, settings, and
  onboarding data.
- [x] Restrict `X-User-ID` fallback to local/development environments.
- [x] Connect the Vite frontend to Google login, `/api/auth/me`, logout, and
  onboarding preference persistence.

### Remaining auth TODO

- [ ] Configure Google Cloud OAuth Consent Screen and Web Client ID with the
  real Vercel/Render URLs.
- [ ] Deploy backend to Render and set `GOOGLE_*`, `JWT_SECRET_KEY`, and CORS
  environment variables.
- [ ] Run deployed smoke tests for Google login, callback, `/api/auth/me`, and
  user-scoped onboarding/settings APIs.
- [ ] Replace `create_all` schema evolution with migrations before production
  data is relied on.

## Done

- [x] 문서 기반 프로젝트 구조 생성
- [x] `.env.example`, `requirements.txt`, `.gitignore`, `pytest.ini` 추가
- [x] 설정 모듈 `config/settings.py` 추가
- [x] 분석 대상 종목 파일 `config/tickers.yaml` 추가
- [x] 가짜 뉴스 판별 MVP 구현
- [x] 뉴스 필터, 감성 분석 baseline, 시장 반응, 이벤트 점수 구현
- [x] RED/YELLOW/GREEN 신호 생성 구현
- [x] Discord Webhook 알림 모듈 추가
- [x] Discord payload 및 POST 호출 테스트 추가
- [x] FastAPI 대시보드 기본 화면과 API 추가
- [x] PostgreSQL 초기 스키마 작성
- [x] 유사 프로젝트 탐색 및 레퍼런스 분석 문서화

## Next

- [x] 실제 GDELT API 연동
- [x] NewsAPI 연동 및 API 키 누락 시 graceful fallback 구현
- [x] yfinance 기반 실제 데이터 수집 구현 (`pykrx`는 선택 TODO)
- [x] SQLAlchemy ORM 모델과 repository 계층 추가
- [x] 파이프라인 결과 DB 저장
- [ ] Discord 실제 Webhook URL로 샌드박스 채널 전송 테스트
- [ ] Email 뉴스레터 템플릿과 SMTP 통합 테스트
- [ ] Plotly.js 차트와 WebSocket 실시간 업데이트 추가
- [ ] FinBERT/KoELECTRA 모델 실험
- [ ] Dockerfile 및 docker-compose.yml 추가
- [ ] GitHub Actions CI 추가

## Risks

- 무료 뉴스 API 호출 제한이 파이프라인 처리량을 제한할 수 있다.
- 한국어 금융 감성 분석은 일반 모델만으로 정확도가 낮을 수 있다.
- 가짜 뉴스 판별은 100% 자동화가 어렵기 때문에 사람이 검토할 수 있는 로그와 사유가 필요하다.
