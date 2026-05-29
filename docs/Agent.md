# 🤖 Agent.md — Codex AI 작업 지시서

> **AI 금융 신호등 시스템** 개발을 위한 OpenAI Codex 전용 작업 지시서
> 이 파일을 읽은 Codex는 아래 규칙과 스킬 가이드를 따라 코드를 생성합니다.

---

## 📌 프로젝트 컨텍스트

- **목적**: AI·정책·반도체 관련 뉴스를 수집하고 가짜 뉴스를 필터링한 후, 시장 반응과 결합해 금융 신호등을 생성하는 데이터 분석 시스템
- **주 언어**: Python 3.11+
- **DB**: PostgreSQL 15
- **웹**: FastAPI + Plotly.js 대시보드
- **알림**: Discord Webhook + SMTP Email

---

## 🧠 Codex 스킬 정의

### Skill 1: `news_collection`
**목적**: 뉴스 API에서 원본 데이터 수집
```python
# 구현 패턴
class NewsCollector:
    def collect_from_gdelt(self, keywords: list[str], days: int) -> list[dict]
    def collect_from_newsapi(self, keywords: list[str], from_date: str) -> list[dict]
    def deduplicate(self, articles: list[dict]) -> list[dict]
```
- `source`, `title`, `content`, `published_at`, `url` 필드 필수 포함
- 중복 제거는 URL + 제목 해시 기반

---

### Skill 2: `fake_news_detection` ⭐ 핵심 스킬
**목적**: 수집된 뉴스의 신뢰도를 다층 검증하여 가짜/오보 뉴스를 필터링

#### 2-1. 출처 신뢰도 검증
```python
class SourceVerifier:
    TRUSTED_SOURCES = {
        # 한국 공신력 언론
        "yonhap.co.kr": 1.0, "chosun.com": 0.9, "joongang.co.kr": 0.9,
        "mk.co.kr": 0.85, "hankyung.com": 0.85, "edaily.co.kr": 0.8,
        # 미국 공신력 언론
        "reuters.com": 1.0, "bloomberg.com": 1.0, "wsj.com": 0.95,
        "ft.com": 0.95, "cnbc.com": 0.85, "apnews.com": 1.0
    }
    
    def get_source_score(self, url: str) -> float:
        """도메인 추출 후 신뢰도 점수 반환. 미등록 출처 = 0.3"""
    
    def check_author_byline(self, article: dict) -> bool:
        """기자명, 언론사명, 발행 날짜 필드 존재 여부 확인"""
```

#### 2-2. 날짜 조작 감지
```python
class DateManipulationDetector:
    def detect_recycled_news(self, article: dict, window_days: int = 30) -> bool:
        """
        오래된 뉴스를 최신 사건처럼 재편집한 경우 감지
        - published_at과 content 내 날짜 표현 비교
        - 유사 기사의 최초 발행 날짜와 차이가 window_days 이상이면 의심
        """
    
    def check_date_context_mismatch(self, title: str, content: str, published_at: str) -> float:
        """제목/본문의 날짜 표현과 실제 발행일 일치 여부 점수 반환 (0~1)"""
```

#### 2-3. 자극적 표현 감지 (어뷰징 필터)
```python
class SensationalismDetector:
    CLICKBAIT_PATTERNS = [
        r"충격[!！]?", r"긴급[!！]?", r"경악[!！]?", r"단독[!！]?",
        r"속보[!！]?", r"경보[!！]?", r"폭락[!！]?", r"폭등[!！]?",
        r"BREAKING", r"URGENT", r"SHOCKING", r"EXCLUSIVE"
    ]
    
    def calculate_sensationalism_score(self, title: str) -> float:
        """클릭베이트 패턴 매칭 점수 반환 (0=정상, 1=극도 자극적)"""
    
    def check_headline_body_consistency(self, title: str, content: str) -> float:
        """제목과 본문 내용의 일관성 점수 (코사인 유사도 기반)"""
```

#### 2-4. 교차 검증 (크로스 체킹)
```python
class CrossReferenceChecker:
    def check_multi_source_coverage(self, article: dict, all_articles: list[dict]) -> bool:
        """
        동일 사건을 2개 이상의 독립 공신력 매체가 다루는지 확인
        단일 출처 단독 보도이면 False (의심)
        """
    
    def calculate_coverage_score(self, article: dict, all_articles: list[dict]) -> float:
        """커버리지 점수: 보도 매체 수 / 5 (최대 1.0)"""
```

#### 2-5. 통합 가짜 뉴스 판별 파이프라인
```python
class FakeNewsDetector:
    """
    최종 판별 로직:
    - source_score >= 0.8 : 신뢰 출처 여부
    - date_mismatch_score <= 0.3 : 날짜 조작 없음
    - sensationalism_score <= 0.5 : 과도한 자극성 없음
    - headline_body_consistency >= 0.6 : 제목-본문 일관성
    - coverage_score >= 0.4 : 복수 매체 보도 (단독 제외)
    
    최종 신뢰도 = 가중 평균:
    source(30%) + date(20%) + sensationalism(15%) + consistency(20%) + coverage(15%)
    """
    
    THRESHOLDS = {
        "source_weight": 0.30,
        "date_weight": 0.20,
        "sensationalism_weight": 0.15,
        "consistency_weight": 0.20,
        "coverage_weight": 0.15,
        "min_final_score": 0.65  # 이 점수 이상만 분석에 사용
    }
    
    def analyze(self, article: dict, all_articles: list[dict]) -> dict:
        """
        Returns:
            {
                "is_reliable": bool,
                "final_score": float,
                "breakdown": {
                    "source": float,
                    "date": float,
                    "sensationalism": float,
                    "consistency": float,
                    "coverage": float
                },
                "flags": list[str]  # 의심 사유 목록
            }
        """
```

**구현 시 주의사항**:
- 모든 점수는 0.0 ~ 1.0 범위로 정규화
- flags 목록에 구체적인 의심 사유를 한국어로 기록
- DB `news_filter_results` 테이블에 판별 결과 저장

---

### Skill 3: `sentiment_analysis`
```python
class SentimentAnalyzer:
    # 한국어: KoFinBERT 또는 KoELECTRA-finance 사용
    # 영어: FinBERT (ProsusAI/finbert) 사용
    
    def analyze(self, text: str, lang: str = "ko") -> dict:
        """
        Returns: {"score": float(-1~1), "label": "positive|neutral|negative", "confidence": float}
        """
    
    def batch_analyze(self, texts: list[str]) -> list[dict]
```

---

### Skill 4: `signal_generator`
```python
class SignalGenerator:
    """
    RED: volatility >= threshold*2 AND volume_ratio >= 2.0 AND sentiment <= -0.3
    YELLOW: return_1d 절대값 >= threshold OR volume_ratio >= 2.0
    GREEN: 위 조건 미해당
    """
    def generate(self, event_score: float, market_data: dict, fake_news_flags: list) -> str
```

---

### Skill 5: `discord_notifier`
```python
class DiscordNotifier:
    def send_signal_alert(self, signal: str, ticker: str, data: dict) -> bool
    def send_daily_summary(self, summary: dict) -> bool
    
    # 메시지 포맷:
    # 🔴 RED 신호 발생
    # 종목: 삼성전자 (005930)
    # 수익률 변화: -3.2%
    # 거래량 비율: 3.5x
    # 주요 뉴스: [기사 제목]
    # 신뢰도: 0.87 (가짜뉴스 점수 포함)
    # 발생 시각: 2026-05-29 14:30 KST
```

---

### Skill 6: `web_dashboard`
```python
# FastAPI 엔드포인트
GET  /api/signals          # 최근 신호 목록
GET  /api/signals/{ticker} # 종목별 신호 히스토리
GET  /api/news             # 필터링된 뉴스 목록 (신뢰도 점수 포함)
GET  /api/market           # 시장 데이터 요약
WS   /ws/live              # 실시간 신호 스트림
```

---

## 📏 코딩 규칙

1. **타입 힌트 필수** — 모든 함수에 타입 힌트 사용
2. **에러 처리** — API 호출 실패 시 retry(3회) 후 로그 기록
3. **로깅** — `logging` 모듈 사용, DEBUG/INFO/WARNING/ERROR 레벨 구분
4. **테스트** — 각 스킬마다 `tests/test_<skill>.py` 파일 생성
5. **환경변수** — API 키는 반드시 `.env`에서 로드, 하드코딩 금지
6. **DB 연결** — SQLAlchemy ORM 사용, 커넥션 풀 관리
7. **가짜 뉴스 결과** — 판별 결과를 Discord 알림에 반드시 포함

---

## 🔄 개발 순서 (Codex 작업 우선순위)

```
Phase 1: 기반 구축
  1. config/settings.py → 환경변수, 임계값 설정
  2. database/schema.sql → PostgreSQL 테이블 생성
  3. scripts/setup_db.py → DB 초기화

Phase 2: 데이터 수집
  4. src/collector/news_collector.py
  5. src/collector/stock_collector.py

Phase 3: 가짜 뉴스 판별 ⭐ 최우선
  6. src/collector/fake_news_checker.py (FakeNewsDetector 전체 구현)
  7. tests/test_fake_news.py

Phase 4: 분석 파이프라인
  8. src/processor/news_filter.py
  9. src/processor/sentiment.py
  10. src/processor/market_reaction.py
  11. src/processor/event_score.py

Phase 5: 신호 생성 및 알림
  12. src/signal/generator.py
  13. src/notifier/discord_bot.py
  14. src/notifier/email_sender.py

Phase 6: 웹 대시보드
  15. src/dashboard/app.py
  16. src/dashboard/routes/api.py
  17. src/dashboard/static/ (HTML/CSS/JS)

Phase 7: ML 모델
  18. src/ml/trainer.py
  19. src/ml/backtest.py

Phase 8: 통합 및 배포
  20. scripts/run_pipeline.py
  21. Dockerfile, docker-compose.yml
```

---

## ❌ Codex가 하면 안 되는 것

- API 키를 코드에 직접 하드코딩
- 가짜 뉴스 판별 없이 모든 뉴스를 분석에 사용
- 투자 추천 문구 생성 ("매수", "매도" 권고 등)
- 단일 출처 뉴스만으로 RED 신호 생성
