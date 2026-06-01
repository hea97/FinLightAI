# FinLightAI 작업 백로그

## 2026-05-29

### 사용자 지시

- SRS, Agent, README 문서를 바탕으로 프로젝트를 세팅한다.
- 이후 해야 할 일을 TODO 형식으로 정리한다.
- Discord 알림 기능이 제대로 추가되어 있는지 재차 검증한다.
- 기술 조사, 유사 프로젝트 탐색, 레퍼런스 분석, 계획 수립을 진행한다.
- 각 단계별로 사용 가능하고, 최초에 핵심 기능을 검증해 발전시키는 계획을 세운다.
- 1번 단계부터 구현을 시작한다.
- 작업 상태는 되도록 Markdown으로 저장한다.
- 필요하면 되돌아올 지점을 위해 git commit을 사용한다.
- Codex에게 지시한 내용과 수행 업무를 백로그 Markdown으로 정리한다.

### 수행 내용

- 문서를 `docs/SRS.md`, `docs/Agent.md`, `docs/SOURCE_README.md`로 복사했다.
- 프로젝트 기본 구조를 생성했다.
- Python 가상환경 `.venv`를 생성하고 `requirements.txt` 의존성을 설치했다.
- `config/settings.py`, `config/tickers.yaml`로 설정과 종목 목록을 추가했다.
- `src/collector/fake_news_checker.py`에 신뢰도 판별 로직을 구현했다.
- `src/notifier/discord_bot.py`에 Discord Webhook 알림 기능을 구현했다.
- `tests/test_discord_notifier.py`에서 payload 생성과 RED 신호 POST 호출을 검증했다.
- `src/dashboard/app.py`와 정적 대시보드 파일을 추가했다.
- `database/schema.sql`에 PostgreSQL 초기 테이블을 정의했다.
- `docs/TECH_RESEARCH.md`, `docs/REFERENCE_ANALYSIS.md`, `docs/PROJECT_PLAN.md`, `docs/TODO.md`를 작성했다.

### 검증 결과

- `.venv\Scripts\python.exe -m pytest`
- 결과: 7 passed

### Discord 알림 검증 메모

- `DiscordNotifier.send_signal_alert()`는 RED/YELLOW 신호만 Webhook POST를 수행한다.
- GREEN 신호는 전송하지 않는다.
- Webhook URL이 없으면 경고 로그 후 `False`를 반환한다.
- 테스트에서는 `httpx.MockTransport`로 실제 Discord 네트워크 호출 없이 POST 호출 여부를 검증했다.

### 다음 작업 후보

- 실제 Discord Webhook URL을 `.env`에 넣고 샌드박스 채널로 수동 전송 테스트
- GDELT/NewsAPI 실제 수집기 구현
- SQLAlchemy ORM과 DB 저장 연결
- 대시보드 차트와 WebSocket 추가

## 2026-06-01

### 사용자 지시

- 첨부한 이미지를 이 프로젝트의 로고로 사용한다.
- 웹페이지와 백로그 Markdown에 로고 관련 내용을 정리한다.

### 수행 내용

- 첨부 이미지의 어두운 배경, 민트색 번개형 심볼, `FinLightAI` 워드마크를 기준으로 웹용 SVG 로고 자산을 추가했다.
- 로고 파일 위치: `src/dashboard/static/assets/finlightai-logo.svg`
- 대시보드 첫 화면에서 로고와 브랜드명을 함께 노출하도록 `src/dashboard/static/index.html`을 수정했다.
- 대시보드 배경과 헤더 색상을 로고 톤에 맞춰 다크/민트 계열로 정리했다.

### 다음 작업 후보

- 원본 고해상도 PNG/SVG 로고 파일을 확보하면 현재 SVG 자산을 공식 원본으로 교체한다.
- favicon, Open Graph 이미지, README 상단 브랜드 영역에도 같은 로고를 반영한다.
