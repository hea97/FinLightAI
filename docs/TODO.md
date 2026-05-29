# TODO

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

- [ ] 실제 GDELT API 연동
- [ ] NewsAPI 연동 및 API 키 누락 시 graceful fallback 구현
- [ ] yfinance/pykrx 실제 데이터 수집 구현
- [ ] SQLAlchemy ORM 모델과 repository 계층 추가
- [ ] 파이프라인 결과 DB 저장
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
