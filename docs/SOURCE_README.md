# 🚦 AI 금융 신호등 시스템 (AI Financial Signal System)

> **데이터 분석 기반 금융 시장 상태 인식 및 실시간 알림 플랫폼**
> AI·정책·반도체 뉴스가 한국/미국 주식 시장에 미치는 영향을 분석하고, 신호등(RED/YELLOW/GREEN) 형태로 시각화합니다.

---

## 📋 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 프로젝트명 | AI 금융 신호등 시스템 |
| 버전 | v1.0.0 |
| 주 코딩 AI | OpenAI Codex |
| 개발 언어 | Python 3.11+ |
| 주요 기능 | 뉴스 수집, 가짜 뉴스 판별, 감성 분석, 신호등 생성, Discord/Email 알림, 웹 대시보드 |

---

## 🏗️ 파일 구조

```
ai_financial_signal/
├── README.md                   ← 이 파일
├── Agent.md                    ← Codex AI 작업 지시서
├── .env.example                ← 환경변수 템플릿
├── requirements.txt            ← 의존성 목록
├── config/
│   ├── settings.py             ← 전역 설정값 (API 키, 임계값 등)
│   └── tickers.yaml            ← 분석 대상 종목 목록
├── data/
│   ├── raw/                    ← 원본 수집 데이터
│   ├── processed/              ← 전처리 완료 데이터
│   └── models/                 ← 학습된 ML 모델 파일
├── src/
│   ├── __init__.py
│   ├── collector/
│   │   ├── news_collector.py   ← GDELT / NewsAPI 뉴스 수집
│   │   ├── stock_collector.py  ← yfinance / pykrx 주가 수집
│   │   └── fake_news_checker.py← 가짜 뉴스 판별 모듈 ⭐
│   ├── processor/
│   │   ├── news_filter.py      ← 신뢰도 기반 뉴스 필터링
│   │   ├── sentiment.py        ← FinBERT 감성 분석
│   │   ├── market_reaction.py  ← 수익률/거래량/변동성 계산
│   │   └── event_score.py      ← 이벤트 점수 통합 계산
│   ├── signal/
│   │   ├── generator.py        ← 신호등(RED/YELLOW/GREEN) 생성
│   │   └── thresholds.py       ← 임계값 관리
│   ├── notifier/
│   │   ├── discord_bot.py      ← Discord 실시간 알림
│   │   ├── email_sender.py     ← Email 뉴스레터
│   │   └── templates/          ← 알림 메시지 템플릿
│   ├── ml/
│   │   ├── trainer.py          ← ML 모델 학습 (XGBoost/LightGBM)
│   │   ├── predictor.py        ← 방향성 예측
│   │   └── backtest.py         ← 백테스트
│   └── dashboard/
│       ├── app.py              ← FastAPI 웹 서버
│       ├── routes/
│       │   ├── api.py          ← REST API 라우터
│       │   └── websocket.py    ← 실시간 데이터 스트림
│       └── static/
│           ├── index.html      ← 대시보드 메인 페이지
│           ├── css/
│           └── js/
├── database/
│   ├── schema.sql              ← PostgreSQL 스키마
│   └── migrations/             ← DB 마이그레이션
├── tests/
│   ├── test_collector.py
│   ├── test_fake_news.py       ← 가짜 뉴스 판별 테스트
│   ├── test_signal.py
│   └── test_notifier.py
├── scripts/
│   ├── run_pipeline.py         ← 전체 파이프라인 실행
│   └── setup_db.py             ← DB 초기화
└── docs/
    ├── SRS.md                  ← 시스템 요구사항 명세서
    ├── project_plan.md         ← 프로젝트 계획서
    └── design/                 ← 디자인 시안
```

---

## 🚀 빠른 시작

### 1. 환경 설정
```bash
git clone https://github.com/yourusername/ai-financial-signal.git
cd ai-financial-signal
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .env 파일에 API 키 입력
```

### 2. 데이터베이스 초기화
```bash
python scripts/setup_db.py
```

### 3. 전체 파이프라인 실행
```bash
python scripts/run_pipeline.py
```

### 4. 웹 대시보드 실행
```bash
uvicorn src.dashboard.app:app --reload --port 8000
# http://localhost:8000 접속
```

---

## 🛠️ 기술 스택

| 분류 | 기술 |
|------|------|
| 언어 | Python 3.11+ |
| 데이터 수집 | GDELT, NewsAPI, yfinance, pykrx |
| NLP / AI | FinBERT, KoELECTRA, scikit-learn, XGBoost |
| 가짜 뉴스 판별 | 출처 DB, 교차 검증 API, 날짜 검증 |
| 데이터베이스 | PostgreSQL 15 |
| 웹 프레임워크 | FastAPI + Jinja2 |
| 시각화 | Plotly.js, Chart.js |
| 알림 | Discord Webhook, SMTP |
| 배포 | Docker, GitHub Actions |

---

## ⚠️ 면책 조항

> 본 시스템은 **투자 추천 시스템이 아닙니다.**
> 모든 분석 결과는 참고용이며, 투자 판단의 근거로 사용될 수 없습니다.
> 뉴스와 시장 반응의 관계는 상관관계이며, 인과관계를 보장하지 않습니다.

---

## 📄 라이선스
MIT License — 자유롭게 사용하되 출처 명시 바랍니다.
