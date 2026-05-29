# News API 관리 계획

작성일: 2026-05-29  
목적: FinLightAI의 뉴스 수집원을 명확히 정하고, 무료/준무료 API의 역할과 제한사항을 관리한다.

## 선정 원칙

- 투자 추천이 아니라 시장 상태 인식과 리스크 알림을 위한 뉴스 데이터만 수집한다.
- API Key는 `.env`로만 관리하고 코드에 하드코딩하지 않는다.
- 단일 뉴스 출처만으로 RED 신호를 만들지 않는다.
- 기사 원문 전문이 없는 API는 제목, 요약, URL, 발행시각, 출처 신뢰도 중심으로 사용한다.
- 상업적 배포 전 각 API의 이용 약관을 재확인한다.

## 채택 API 우선순위

| 우선순위 | API | 채택 여부 | 주요 역할 | 비고 |
|---:|---|---|---|---|
| 1 | GDELT DOC 2.0 API | 채택 | 글로벌 AI/반도체/정책 뉴스 수집 | API Key 없이 시작 가능, 글로벌 커버리지 강점 |
| 2 | The Guardian Open Platform | 채택 | 영문 기사 본문 기반 분석 보강 | Developer key 필요, 비상업 무료 조건 확인 |
| 3 | Finnhub News API | 채택 | 종목/시장 특화 금융 뉴스 및 sentiment 보강 | 주식 데이터 API와 함께 사용 가능 |
| 4 | BBC News API/RSS | 채택 후보 | 글로벌 공신력 뉴스 보조 수집원 | 공식 공개 API는 제한적이므로 RSS 또는 비공식 API 안정성 검증 필요 |
| 제외 | Naver Search News API | 제외 | 한국어 뉴스 검색 | 한국어 뉴스 장점은 있으나 검색 결과/요약 중심이라 MVP 수집원에서 제외 |

## API별 관리 방침

### 1. GDELT DOC 2.0 API

- 기본 수집원으로 사용한다.
- 키워드 예시: `AI chip`, `semiconductor export control`, `NVIDIA policy`, `Samsung semiconductor`, `TSMC foundry`
- 수집 필드: `title`, `url`, `source`, `published_at`, `language`, `domain`
- 장점: 글로벌 뉴스 커버리지가 넓고, API Key 없이 MVP 연동이 가능하다.
- 주의: 기사 전문 분석은 별도 본문 추출 또는 다른 API 보강이 필요하다.
- 문서: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/

### 2. The Guardian Open Platform

- 글로벌 정책/경제 맥락 기사 분석에 사용한다.
- 기사 본문 접근 가능성이 있어 감성 분석과 이벤트 요약 보강에 유리하다.
- 사용 조건: Developer key 필요, 비상업/개발 용도 무료 조건 확인, 호출량 제한 준수
- 수집 필드: `webTitle`, `webUrl`, `sectionName`, `webPublicationDate`, `fields.bodyText`
- 문서:
  - https://open-platform.theguardian.com/access
  - https://open-platform.theguardian.com/documentation

### 3. Finnhub News API

- 금융 특화 뉴스와 종목 기반 뉴스에 사용한다.
- 주가/종목 데이터 수집과 같은 provider에서 묶어 관리할 수 있다.
- 사용 예: `company_news(symbol, from, to)`, `market_news(category)`, `news_sentiment(symbol)`
- 장점: 금융 도메인과 직접 맞닿아 있고, 종목 단위 포트폴리오 알림과 연결하기 쉽다.
- 주의: 무료 한도와 데이터 품질은 실제 사용량으로 검증한다.
- 문서:
  - https://finnhub.io/docs/api
  - https://finnhub.io/docs/api/news-sentiment

### 4. BBC News API/RSS

- BBC는 공신력 있는 글로벌 뉴스 출처이므로 보조 수집원으로 채택한다.
- 단, 공개적으로 안정적인 공식 News API가 명확히 제공되는 형태는 아니므로 아래 순서로 검증한다.

검증 순서:

1. BBC 공식 RSS feed 사용 가능 여부 확인
2. RSS에서 제목, 요약, URL, 발행시각 수집
3. 필요하면 비공식 `bbc-news-api`를 개발/테스트 용도로만 평가
4. 운영 배포 전 라이선스와 안정성 재검토

문서:

- BBC RSS feed 안내: https://support.bbc.co.uk/platform/feeds/NewsFeeds.htm
- Microsoft BBC News connector 설명: https://learn.microsoft.com/en-us/connectors/bbcnews/
- 비공식 API 후보: https://bbc-news-api.vercel.app/doc

## 제외 API

### Naver Search News API

- 한국어 뉴스 수집원으로 매력은 있지만 MVP에서는 제외한다.
- 제외 이유:
  - 검색 결과/요약 중심이라 본문 기반 신뢰도 분석에 제한이 있다.
  - 포털 검색 결과 특성상 원문 언론사 검증과 중복 제거가 추가로 필요하다.
  - 프로젝트 초기에는 글로벌 정책/반도체/금융 데이터의 폐쇄 루프 검증이 더 중요하다.
- 재검토 조건:
  - 한국어 뉴스 커버리지 부족이 확인될 때
  - 한국 시장 종목 상세 페이지를 고도화할 때
  - 원문 언론사 URL 정규화 로직이 준비될 때

## 환경변수

```text
GDELT_BASE_URL=https://api.gdeltproject.org/api/v2/doc/doc
GUARDIAN_API_KEY=
FINNHUB_API_KEY=
BBC_NEWS_API_BASE_URL=
BBC_RSS_FEED_URL=https://feeds.bbci.co.uk/news/rss.xml
```

## 수집 실패 시 fallback

1. GDELT 실패: Guardian + Finnhub로 축소 수집
2. Guardian 실패: GDELT + Finnhub만 사용
3. Finnhub 실패: 뉴스 기반 신호만 생성하고 주식 상세 신호는 보류
4. BBC 실패: 기능 영향 없음, 보조 출처로만 취급

## TODO

- [ ] GDELT collector 구현
- [ ] Guardian collector 구현
- [ ] Finnhub news collector 구현
- [ ] BBC RSS collector 구현
- [ ] API별 rate limit 설정값 추가
- [ ] provider별 raw response 저장 옵션 추가
- [ ] provider별 장애 로그와 fallback 정책 테스트
