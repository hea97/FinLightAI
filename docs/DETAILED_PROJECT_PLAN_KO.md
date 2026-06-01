# FinLightAI 상세 계획 및 목표

작성일: 2026-06-01  
문서 목적: FinLightAI의 장기 목표, 단계별 개발 계획, 검증 기준, 우선순위를 하나의 실행 문서로 정리한다.

## 1. 프로젝트 비전

FinLightAI는 AI, 반도체, 정책, 금융 뉴스와 시장 데이터를 결합해 사용자가 시장 상태와 보유 자산의 뉴스 리스크를 빠르게 이해하도록 돕는 금융 인텔리전스 대시보드다.

이 프로젝트는 투자 추천 서비스가 아니다.  
서비스의 핵심은 `정보 수집`, `신뢰도 검증`, `시장 반응 분석`, `포트폴리오 리스크 요약`, `Discord 알림`이다.

## 2. 핵심 목표

### 목표 1. 신뢰 가능한 뉴스 기반 시장 신호 생성

- GDELT, Guardian, Finnhub, BBC RSS에서 뉴스를 수집한다.
- 출처 신뢰도, 날짜 맥락, 제목 자극성, 제목-본문 일관성, 교차 보도 여부를 평가한다.
- 신뢰도 기준을 통과한 뉴스만 감성 분석과 시장 반응 분석에 사용한다.
- 결과를 `RED`, `YELLOW`, `GREEN` 신호로 표현한다.

성공 기준:

- 낮은 신뢰도 뉴스는 신호 생성에 사용되지 않는다.
- RED/YELLOW 신호에는 신뢰도 점수와 주요 근거가 포함된다.
- 단일 출처 뉴스만으로 RED 신호가 생성되지 않는다.

### 목표 2. 시장 데이터와 뉴스의 결합

- 주가, 수익률, 거래량 비율, 변동성을 계산한다.
- 뉴스 이벤트와 시장 반응을 함께 평가한다.
- 뉴스 감성만으로 신호를 내지 않고 실제 가격/거래량 데이터를 함께 본다.

성공 기준:

- `return_1d`, `volume_ratio`, `volatility_5d`가 모든 신호 payload에 포함된다.
- 뉴스 신뢰도와 시장 반응 중 하나라도 부족하면 강한 경고를 낮춘다.
- API 실패 시 fallback 또는 보류 상태를 명확히 표시한다.

### 목표 3. 자산 포트폴리오 기반 리스크 요약

- 사용자가 보유 종목, 수량, 평균 매입가를 등록한다.
- 현재가 기준 평가금액, 수익률, 자산 비중을 계산한다.
- 보유 비중이 큰 종목의 RED/YELLOW 뉴스 리스크를 우선 표시한다.

성공 기준:

- 포트폴리오 총 평가금액과 일간 변동률을 계산한다.
- 종목별 비중과 뉴스 신호를 함께 보여준다.
- 섹터 또는 종목 집중 리스크를 텍스트로 요약한다.

### 목표 4. Discord 중심의 빠른 확인 경험

- RED/YELLOW 신호 발생 시 Discord로 알림을 보낸다.
- `!자산` 명령으로 포트폴리오 요약을 텍스트로 확인한다.
- `!뉴스`, `!신호`, `!리스크` 같은 명령으로 주요 상태를 빠르게 조회한다.

성공 기준:

- RED/YELLOW만 자동 알림으로 전송된다.
- `!자산` 응답에는 평가금액, 일간 변동, 상위 보유 자산, 주요 리스크가 포함된다.
- 모든 Discord 응답에 투자 추천이 아니라는 문구가 포함된다.

### 목표 5. 운영 가능한 웹 대시보드 구축

- 메인 화면에서 전체 신호, 포트폴리오, 최신 뉴스, 차단 뉴스 현황을 볼 수 있다.
- 종목 상세 화면에서 뉴스 타임라인과 가격 반응을 볼 수 있다.
- 포트폴리오 화면에서 자산 CRUD와 비중 차트를 제공한다.

성공 기준:

- 사용자는 첫 화면에서 오늘의 위험도를 10초 안에 파악할 수 있다.
- 포트폴리오 등록부터 요약 조회까지 한 흐름으로 동작한다.
- 데이터가 없거나 API가 실패해도 화면이 깨지지 않는다.

## 3. 범위

## 포함 범위

- 뉴스 수집
- 가짜뉴스/저신뢰 뉴스 필터링
- 감성 분석
- 시장 반응 분석
- 신호 생성
- Discord 알림
- 포트폴리오 관리
- 웹 대시보드
- PostgreSQL 저장
- 백테스트와 모델 고도화 기반

## 제외 범위

- 자동 매매
- 매수/매도 추천
- 수익률 보장 표현
- 개인 계좌 자동 연동 MVP 포함
- 고빈도 트레이딩
- 인증이 필요한 민감 금융 정보 처리

## 4. 사용자 시나리오

### 시나리오 1. 오늘의 시장 상태 확인

1. 사용자가 웹 대시보드에 접속한다.
2. 전체 신호와 주요 RED/YELLOW 종목을 확인한다.
3. 각 신호의 뉴스 신뢰도, 거래량 비율, 변동성을 확인한다.
4. 필요하면 종목 상세로 이동해 관련 뉴스를 본다.

### 시나리오 2. Discord에서 자산 확인

1. 사용자가 Discord에 `!자산`을 입력한다.
2. Bot이 포트폴리오 평가금액과 일간 변동률을 계산한다.
3. 상위 보유 자산과 뉴스 리스크를 함께 보여준다.
4. 투자 추천이 아니라는 안내를 함께 출력한다.

### 시나리오 3. 저신뢰 뉴스 차단

1. 수집기가 단일 출처 또는 자극적 제목의 뉴스를 수집한다.
2. FakeNewsDetector가 낮은 신뢰도 점수를 부여한다.
3. 해당 뉴스는 신호 생성에서 제외된다.
4. 대시보드의 차단 뉴스 현황에 사유가 기록된다.

## 5. 단계별 개발 계획

### Phase 0. 기반 정리

목표: 기존 문서와 코드 구조를 개발 가능한 상태로 정리한다.

작업:

- 문서 인코딩 UTF-8 정리
- README, TODO, BACKLOG 최신화
- `.env.example`에 신규 API key 항목 추가
- 코드 네이밍 규칙 점검
- 테스트 실행 경로 정리

완료 기준:

- `python -m pytest`가 로컬에서 통과한다.
- 핵심 문서가 한국어로 깨지지 않고 읽힌다.
- 신규 개발자가 README만 보고 로컬 실행을 시작할 수 있다.

### Phase 1. 실제 뉴스 수집 MVP

목표: 실제 외부 뉴스 데이터를 파이프라인에 넣는다.

작업:

- `NewsProvider` 인터페이스 설계
- `GdeltNewsProvider` 구현
- `GuardianNewsProvider` 구현
- `FinnhubNewsProvider` 구현
- `BbcRssNewsProvider` 구현
- provider별 timeout, retry, rate limit 설정
- 수집 결과를 공통 article schema로 정규화

완료 기준:

- 최소 GDELT에서 실제 뉴스 10건 이상을 수집한다.
- 수집 결과가 FakeNewsDetector 입력 형식과 호환된다.
- API 실패 시 전체 파이프라인이 중단되지 않는다.

### Phase 2. 저장소와 감사 로그

목표: 분석 결과를 PostgreSQL에 저장하고 추적 가능하게 만든다.

작업:

- SQLAlchemy 설정 추가
- `news_articles` ORM 모델 구현
- `news_filter_results` ORM 모델 구현
- `market_signals` ORM 모델 구현
- repository 계층 추가
- 파이프라인 결과 저장

완료 기준:

- 수집 뉴스, 신뢰도 판별 결과, 신호 결과가 DB에 저장된다.
- 차단된 뉴스도 사유와 함께 저장된다.
- 같은 URL 뉴스가 중복 저장되지 않는다.

### Phase 3. 시장 데이터 연동

목표: 뉴스 신호에 실제 가격/거래량 데이터를 결합한다.

작업:

- `MarketDataProvider` 인터페이스 설계
- `YFinanceProvider` 구현
- `PyKrxProvider` 구현
- Finnhub market data 연동 검토
- 수익률, 거래량 비율, 변동성 계산 고도화
- provider fallback 구현

완료 기준:

- 한국/미국 주요 종목의 OHLCV를 가져온다.
- `return_1d`, `volume_ratio`, `volatility_5d`를 계산한다.
- 데이터 누락 시 신호 상태를 `UNKNOWN` 또는 보류로 처리한다.

### Phase 4. 포트폴리오 MVP

목표: 사용자가 직접 보유 자산을 등록하고 상태를 볼 수 있게 한다.

작업:

- `portfolio_accounts` 테이블 설계
- `portfolio_positions` 테이블 설계
- 자산 추가/수정/삭제 API 구현
- 현재가 기반 평가금액 계산
- 평가손익, 수익률, 자산 비중 계산
- 웹 대시보드에 포트폴리오 요약 추가

완료 기준:

- 사용자가 종목, 수량, 평균단가를 등록할 수 있다.
- 포트폴리오 총 평가금액과 종목별 비중이 계산된다.
- 보유 종목의 뉴스 신호가 포트폴리오 화면에 표시된다.

### Phase 5. Discord 명령 기능

목표: Discord에서 주요 정보를 빠르게 조회한다.

작업:

- Discord command handler 설계
- `!자산` formatter 구현
- `!신호` formatter 구현
- `!뉴스` formatter 구현
- `!리스크` formatter 구현
- Discord 응답 테스트 추가

완료 기준:

- `!자산` 입력 시 포트폴리오 요약 텍스트가 생성된다.
- Discord 응답에는 투자 추천이 아니라는 문구가 포함된다.
- 실제 Discord 채널에서 샌드박스 테스트를 통과한다.

### Phase 6. 웹 대시보드 고도화

목표: 실제 사용자 경험을 갖춘 웹사이트로 만든다.

작업:

- 메인 대시보드 정보 구조 정리
- 포트폴리오 화면 구현
- 뉴스 검증 화면 구현
- 종목 상세 화면 구현
- Plotly.js 차트 추가
- WebSocket 실시간 업데이트 추가

완료 기준:

- 주요 화면이 모바일과 데스크톱에서 모두 깨지지 않는다.
- 사용자가 포트폴리오를 등록하고 리스크를 확인할 수 있다.
- 최신 신호가 화면에서 갱신된다.

### Phase 7. 모델 고도화와 백테스트

목표: 신호 품질을 개선하고 과거 데이터로 검증한다.

작업:

- KoFinBERT 또는 FinBERT 연동
- XGBoost/LightGBM 이벤트 방향성 실험
- 과거 뉴스와 가격 데이터를 이용한 백테스트
- 신호별 precision, recall, false positive 분석

완료 기준:

- rule-based baseline과 모델 기반 결과를 비교한다.
- RED/YELLOW 신호의 오탐 원인을 기록한다.
- 백테스트 리포트를 생성한다.

## 6. 데이터 구조 초안

### 뉴스

```text
news_articles
- id
- provider
- source
- title
- content
- url
- author
- published_at
- collected_at
```

### 뉴스 신뢰도

```text
news_filter_results
- id
- article_id
- is_reliable
- final_score
- source_score
- date_score
- sensationalism_score
- consistency_score
- coverage_score
- flags
- created_at
```

### 시장 신호

```text
market_signals
- id
- ticker
- signal
- event_score
- return_1d
- volume_ratio
- volatility_5d
- sentiment_score
- reliability_score
- created_at
```

### 포트폴리오

```text
portfolio_positions
- id
- symbol
- name
- quantity
- average_price
- currency
- asset_class
- created_at
- updated_at
```

```text
portfolio_snapshots
- id
- total_market_value
- total_cost
- unrealized_pnl
- return_rate
- snapshot_at
```

## 7. API 설계 초안

```text
GET    /api/signals
GET    /api/signals/{ticker}
GET    /api/news
GET    /api/news/blocked
GET    /api/market
GET    /api/portfolio
POST   /api/portfolio/positions
PATCH  /api/portfolio/positions/{id}
DELETE /api/portfolio/positions/{id}
GET    /api/portfolio/risk
POST   /api/discord/test
POST   /api/discord/commands/asset-summary
```

## 8. 품질 기준

### 기능 품질

- API 실패가 전체 파이프라인 장애로 이어지지 않는다.
- 외부 API 호출은 timeout과 retry를 갖는다.
- 모든 신호는 생성 근거를 함께 저장한다.
- 저신뢰 뉴스의 차단 사유가 기록된다.

### 데이터 품질

- 중복 URL은 중복 저장하지 않는다.
- provider별 원본 payload를 선택적으로 보관한다.
- 날짜와 timezone은 UTC 기준으로 저장한다.
- 한국 시간 표시는 UI layer에서 처리한다.

### 보안 기준

- API key는 `.env` 또는 배포 환경변수로만 관리한다.
- Discord Webhook URL은 로그에 노출하지 않는다.
- 계좌 연동은 MVP에서 제외한다.
- 사용자 포트폴리오 데이터는 추후 인증 도입 전까지 로컬/단일 사용자 기준으로 제한한다.

### 사용자 경험 기준

- 대시보드 첫 화면에서 오늘의 상태가 바로 보인다.
- RED/YELLOW는 색상과 텍스트를 함께 사용한다.
- Discord 응답은 10줄 내외로 빠르게 읽힌다.
- 모든 화면과 알림에 투자 추천이 아님을 표시한다.

## 9. 우선순위 백로그

### P0

- 문서 인코딩 정리
- GDELT 실제 수집 구현
- NewsProvider 인터페이스
- SQLAlchemy DB 연결
- 신호 결과 DB 저장

### P1

- Guardian/Finnhub/BBC RSS provider
- MarketDataProvider 인터페이스
- yfinance/pykrx 실제 데이터 연동
- 포트폴리오 position schema
- 포트폴리오 평가금액 계산

### P2

- Discord `!자산` formatter
- Discord command handler
- 포트폴리오 API
- 포트폴리오 대시보드 카드
- 뉴스 검증 화면

### P3

- Plotly.js 차트
- WebSocket 실시간 업데이트
- FinBERT/KoFinBERT 연동
- 백테스트 리포트
- Docker/CI/CD

## 10. 다음 2주 실행 계획

### Week 1

1. 문서 인코딩과 README 정리
2. `NewsProvider` 인터페이스 추가
3. GDELT provider 구현
4. GDELT 수집 테스트 추가
5. 수집 뉴스와 FakeNewsDetector 연결

### Week 2

1. SQLAlchemy 설정 추가
2. 뉴스/신뢰도/신호 ORM 모델 추가
3. 파이프라인 결과 DB 저장
4. yfinance provider 초안 구현
5. 포트폴리오 schema 설계 시작

## 11. 완료 정의

이 상세 계획의 1차 완료는 다음 상태를 의미한다.

- 실제 뉴스가 수집된다.
- 저신뢰 뉴스가 차단된다.
- 신뢰 가능한 뉴스와 시장 데이터가 결합된다.
- RED/YELLOW/GREEN 신호가 생성된다.
- 신호와 근거가 DB에 저장된다.
- Discord가 RED/YELLOW 신호를 알린다.
- 사용자는 웹에서 신호와 포트폴리오 요약을 볼 수 있다.
- 사용자는 Discord에서 `!자산`으로 포트폴리오 요약을 확인할 수 있다.
