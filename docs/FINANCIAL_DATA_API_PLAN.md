# 금융/주가 데이터 API 계획

작성일: 2026-05-29  
목적: FinLightAI가 뉴스 신호와 자산 포트폴리오 기능을 제공하기 위해 필요한 금융 데이터 API를 정리한다.

## 전제

FinLightAI는 투자 매수/매도 추천 서비스가 아니다.  
주가, 수익률, 변동성, 포트폴리오 비중, 뉴스 리스크를 보여주는 정보 제공 서비스로 기획한다.

## 필요한 데이터

- 종목 현재가 또는 지연 현재가
- 일봉 OHLCV
- 거래량 및 평균 거래량
- 1일/5일/20일 수익률
- 5일/20일 변동성
- 환율
- ETF/주식 기본 정보
- 포트폴리오 평가금액 계산용 가격
- 종목별 뉴스와 sentiment

## 추천 API 우선순위

| 우선순위 | API/라이브러리 | 역할 | 장점 | 주의 |
|---:|---|---|---|---|
| 1 | yfinance | MVP 가격 데이터 | 설치와 사용이 쉽고 무료로 빠르게 검증 가능 | 비공식 Yahoo Finance 기반이라 운영 안정성 검증 필요 |
| 2 | pykrx | 한국 주식 가격 데이터 | KRX 한국 종목 데이터에 적합 | 실시간보다는 일봉/과거 데이터 중심 |
| 3 | Finnhub | 미국 주식/금융 뉴스/종목 뉴스 | 뉴스와 주가 데이터를 같은 provider로 관리 가능 | 무료 한도와 품질 검증 필요 |
| 4 | Alpha Vantage | 글로벌 주식, 기술지표, 시장 뉴스 | 무료 API key로 시작 가능, 문서가 좋음 | 일부 실시간/고급 기능은 premium |
| 5 | Financial Modeling Prep | 재무제표/기업 fundamentals | 포트폴리오 분석 고도화에 적합 | 무료 요청 수 제한 확인 필요 |
| 6 | Twelve Data | 글로벌 시세/기술지표 보조 | 다양한 시장 지원 | 무료 한도와 endpoint credit 관리 필요 |
| 7 | 한국투자증권 Open API | 국내 실시간/계좌 연동 후보 | 실제 국내 주식 서비스 확장에 유리 | 인증과 보안, 계좌 연동 리스크가 커서 후순위 |

## MVP 적용 전략

### Phase 1

- `yfinance`와 `pykrx` 중심으로 가격 데이터 수집
- 포트폴리오 평가금액은 지연 가격 기준으로 계산
- 신호 생성에는 `return_1d`, `volume_ratio`, `volatility_5d`만 사용

### Phase 2

- Finnhub 연동
- 종목 뉴스, market news, news sentiment를 포트폴리오 리스크와 연결
- Alpha Vantage를 fallback provider로 추가

### Phase 3

- Financial Modeling Prep으로 기업 fundamentals 추가
- 포트폴리오 화면에 밸류에이션, 섹터, 재무 안정성 지표 추가

### Phase 4

- 한국투자증권 Open API 검토
- 실제 계좌 연동은 별도 보안 설계 후 진행

## 환경변수

```text
FINNHUB_API_KEY=
ALPHA_VANTAGE_API_KEY=
FMP_API_KEY=
TWELVE_DATA_API_KEY=
KIS_APP_KEY=
KIS_APP_SECRET=
KIS_ACCOUNT_NO=
```

## 데이터 저장 테이블 후보

- `market_prices`
- `portfolio_accounts`
- `portfolio_positions`
- `portfolio_snapshots`
- `portfolio_risk_events`
- `asset_alert_subscriptions`

## TODO

- [ ] `MarketDataProvider` 인터페이스 설계
- [ ] `YFinanceProvider` 구현
- [ ] `PyKrxProvider` 구현
- [ ] `FinnhubProvider` 구현
- [ ] provider fallback 순서 구현
- [ ] 포트폴리오 평가금액 계산기 구현
- [ ] 포트폴리오 Discord 요약 formatter 구현
