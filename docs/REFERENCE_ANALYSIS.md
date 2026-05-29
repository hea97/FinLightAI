# 유사 프로젝트 탐색 및 레퍼런스 분석

## 조사한 유사 프로젝트

1. [AlgoETS/AINewsTracker](https://github.com/AlgoETS/AINewsTracker)
   - 금융 뉴스 영향 분석, FastAPI, AI sentiment, backtesting을 다루는 구조가 유사하다.
   - 로컬 `references/AINewsTracker-main`에 ZIP 아카이브 방식으로 내려받아 분석했다.
   - `git clone`은 현재 로컬 Git의 `remote-https` helper 부재로 실패해 ZIP 다운로드로 대체했다.

2. GitHub 검색 키워드
   - `FastAPI financial news sentiment analysis stock signal discord webhook`
   - `stock news sentiment analysis yfinance FastAPI dashboard`
   - `FinBERT stock news sentiment yfinance`

## AINewsTracker에서 참고할 점

- `app/main.py`와 `app/routers/`로 API 진입점과 라우터를 분리한다.
- 뉴스 모델, 기사 모델, 서비스 계층을 분리해 수집 로직과 API 로직을 섞지 않는다.
- README에 실행, 테스트, Docker 흐름이 정리되어 있어 온보딩이 쉽다.
- `tests/`를 두고 모델과 API 단위 테스트를 분리한다.

## 우리 프로젝트에 적용한 점

- `src/dashboard/app.py`와 `src/dashboard/routes/api.py`로 FastAPI 구조를 분리했다.
- `src/collector`, `src/processor`, `src/signal`, `src/notifier`로 파이프라인 단계를 명확히 나눴다.
- 외부 서비스 의존도가 높은 부분은 인터페이스와 기본 구현을 먼저 두고 테스트 가능하게 만들었다.
- Discord Webhook은 실제 네트워크 대신 `httpx.MockTransport`로 POST 호출 여부를 검증한다.

## 적용하지 않은 점

- AINewsTracker는 MongoDB 중심 구조지만, FinLightAI SRS는 PostgreSQL을 요구하므로 PostgreSQL 스키마를 유지했다.
- 투자 실행/매매 전략 코드는 본 프로젝트의 면책 조항과 범위에 맞지 않아 제외했다.
- 대형 NLP 모델 로딩은 MVP 단계에서 제외하고, 후속 단계의 교체 가능한 `SentimentAnalyzer` 계약으로 남겼다.
