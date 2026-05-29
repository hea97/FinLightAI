# 프로젝트 계획

## 명명 규칙

- 패키지, 모듈, 파일: `snake_case`
- 클래스: `PascalCase`
- 함수, 메서드, 변수: `snake_case`
- 상수: `UPPER_SNAKE_CASE`
- 테스트 파일: `test_<target>.py`
- 환경변수: `UPPER_SNAKE_CASE`
- AI 관련 컴포넌트는 역할이 드러나는 이름을 사용한다.
  - 좋은 예: `SentimentAnalyzer`, `FakeNewsDetector`, `EventScoreCalculator`
  - 피할 예: `AIManager`, `MagicAnalyzer`, `ModelThing`

## 단계별 계획

### Phase 1: 핵심 기능 검증

- 뉴스 샘플 수집 인터페이스 구현
- 가짜 뉴스 판별 로직 구현
- 뉴스 필터링 구현
- rule-based 감성 분석 구현
- 시장 반응 계산 구현
- RED/YELLOW/GREEN 신호 생성 구현
- Discord Webhook 알림 구현 및 테스트

### Phase 2: 실제 데이터 연동

- GDELT 수집기 연동
- NewsAPI 연동
- yfinance/pykrx 실제 주가 수집 연동
- API retry, timeout, rate limit 처리

### Phase 3: 저장소와 감사 로그

- SQLAlchemy ORM 모델 추가
- PostgreSQL 저장 구현
- `news_filter_results`에 모든 판별 결과 저장
- 마이그레이션 도구 도입

### Phase 4: 대시보드

- FastAPI API 확장
- Plotly.js 차트 추가
- WebSocket 실시간 신호 스트림 추가
- 가짜 뉴스 차단 현황 화면 추가

### Phase 5: ML 고도화

- KoFinBERT/FinBERT 감성 분석 연결
- XGBoost/LightGBM 방향성 예측 실험
- 백테스트 리포트 생성

## 현재 구현 상태

- Phase 1의 기본 코드와 테스트를 구현했다.
- 실제 외부 API 호출은 아직 하지 않고, 안전한 샘플 데이터와 인터페이스 중심으로 구성했다.
- Discord 알림은 payload 생성과 RED 신호 POST 호출까지 테스트로 검증했다.
