# 기술 조사

## 필요한 구성 요소

- Runtime: Python 3.11 이상
- API 서버: FastAPI, Uvicorn
- 설정 관리: pydantic-settings, `.env`
- 뉴스 수집: GDELT, NewsAPI 또는 RSS/GNews 계열 API
- 주가 수집: yfinance, pykrx
- 뉴스 신뢰도 판별: 출처 신뢰도 DB, 날짜 맥락 검증, 자극적 제목 탐지, 제목-본문 일관성, 교차 보도 검증
- 감성 분석: 초기 단계는 rule-based baseline, 고도화 단계는 FinBERT/KoELECTRA/KoFinBERT
- 시장 반응: 1일 수익률, 거래량 비율, 5일 변동성
- 신호 생성: RED/YELLOW/GREEN rule engine
- 알림: Discord Webhook, SMTP Email
- 저장소: PostgreSQL 15, SQLAlchemy
- 대시보드: FastAPI static UI, 이후 Plotly.js/WebSocket
- 검증: pytest, mock transport를 이용한 외부 알림 테스트

## 1단계 핵심 검증 기준

1. 신뢰 가능한 뉴스만 통과한다.
2. 단일 출처 또는 낮은 신뢰도 뉴스는 RED 신호를 만들지 않는다.
3. 시장 반응과 감성 점수로 RED/YELLOW/GREEN이 생성된다.
4. RED/YELLOW 신호만 Discord Webhook으로 전송된다.
5. API 키와 Webhook URL은 `.env`에서만 읽는다.

## 기술 선택

- FastAPI는 라우터 분리와 문서 자동화가 좋아 MVP API에 적합하다.
- PostgreSQL은 SRS의 감사 로그와 분석 결과 저장 요구사항에 맞다.
- Discord 알림은 HTTP POST만으로 검증 가능하므로 1단계에서 가장 빨리 폐쇄 루프를 만들 수 있다.
- FinBERT 계열 모델은 무겁기 때문에 1단계는 rule-based sentiment로 계약을 확정하고, 이후 모델을 교체한다.
