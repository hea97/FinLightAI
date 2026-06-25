# FinLightAI 전체 기획서

작성일: 2026-05-29
최종 업데이트: 2026-06-25
문서 목적: FinLightAI의 서비스 방향, 핵심 기능, 화면 구성, 포트폴리오 기능, 카카오 채널 챗봇 연동 계획을 최신 구현 기준으로 정리한다.

## 1. 프로젝트 한 줄 설명

FinLightAI는 AI, 반도체, 정책, 금융 뉴스와 시장 데이터를 결합해 사용자가 시장 상태와 관심 자산 리스크를 빠르게 이해하도록 돕는 AI 금융 상황판이다.

## 2. 중요한 원칙

- 이 서비스는 투자 추천 서비스가 아니다.
- `매수`, `매도`, `수익 보장`, `상승 확정` 표현을 사용하지 않는다.
- 모든 결과는 참고용 시장 상태, 뉴스 리스크, 포트폴리오 현황 정보로 제공한다.
- 카카오 채널 챗봇 알림도 투자 지시가 아니라 상태 요약과 리스크 알림으로 제한한다.
- RED/YELLOW/GREEN은 투자 행동 지시가 아니라 시장 상태 신호다.

## 3. 핵심 사용자

- AI/반도체/정책 뉴스가 주식시장에 주는 영향을 빠르게 보고 싶은 사용자
- 삼성전자, SK하이닉스, NVIDIA, TSMC 등 반도체 관련 종목을 추적하는 사용자
- 여러 관심 자산을 등록하고, 뉴스 리스크와 자산 연결성을 함께 보고 싶은 사용자
- 웹 대시보드보다 카카오 채널에서 빠르게 상태를 확인하고 싶은 사용자
- 뉴스 신뢰도와 영향도를 분리해 보고 싶은 사용자

## 4. 최신 MVP 화면 구성

현재 MVP의 중심 화면은 다음과 같다.

| 화면 | 목적 |
|---|---|
| AI 브리핑 | 오늘 시장 신호와 핵심 요약을 첫 화면에서 제공 |
| 뉴스 가드 | 뉴스 신뢰도, 영향도, 주의/차단 사유 제공 |
| 산업 영향도 | 산업별 영향도 점수와 상세 근거 제공 |
| 포트폴리오 | 관심 자산 등록과 관련 뉴스/리스크 연결 |
| 카카오 알림 | 카카오 채널 챗봇 + n8n 흐름과 알림 조건 관리 |
| 마이페이지 | 사용자 개인화 허브 |
| 설정 | 데이터, 뉴스 가드, 알림, API 연결, 표시 설정 관리 |
| 로그인/회원가입 | 카카오/이메일 인증 및 온보딩 흐름 |

## 5. 핵심 기능

### 5-1. AI 브리핑

첫 화면에서 바로 보여줄 정보:

- 오늘의 시장 신호
- 위험도 점수
- 국내 시장 / 해외 시장 / 관심 산업 탭
- AI 브리핑 요약
- 주요 지표 카드
- 뉴스 영향도 TOP 5
- 산업 영향도 요약
- 뉴스 가드 경고
- 최근 카카오 알림

### 5-2. 뉴스 가드

News Guard는 FinLightAI의 핵심 차별 기능이다.

기능:

- GDELT, NewsAPI, Guardian, Finnhub, BBC RSS 등 provider 상태 표시
- 수집 뉴스 수, 신뢰 뉴스, 주의 뉴스, 차단 뉴스, 평균 신뢰도 표시
- 뉴스별 신뢰도 점수, 영향도 점수, 감성 점수 표시
- 뉴스 카드별 의심 사유 또는 신뢰 근거 표시
- `전체`, `신뢰 뉴스`, `주의 뉴스`, `차단 뉴스` 필터 제공

판단 기준:

- 출처 신뢰도
- 날짜 맥락
- 자극적인 제목
- 제목-본문 일관성
- 교차 보도 여부

### 5-3. 산업 영향도

산업별 뉴스 영향도와 시장 반응을 함께 보여준다.

포함 산업 예시:

- 반도체
- 금융
- IT
- 자동차
- 에너지
- 바이오
- 항공
- 소비재
- 정유
- 철강

제공 정보:

- 산업 영향도 점수
- 긍정/주의/부정 상태
- 관련 뉴스 수
- 관련 종목
- 리스크 요약
- 선택 산업 상세 패널

### 5-4. 관심 자산 포트폴리오

포트폴리오는 실제 매매 기능이 아니라 관심 자산 기반 리스크 확인 기능이다.

사용자가 직접 등록하는 항목:

- 자산명
- 종목 코드
- 시장
- 산업
- 보유 수량
- 평균 매입가
- 현재가
- 통화
- 상태 메모

계산/표시 항목:

- 총 입력 금액
- 현재 평가금액
- 평가손익
- 평가손익률
- 관심 산업 연결 수
- 관련 뉴스 수
- 주의 뉴스 수
- 자산별 오늘 신호

주의:

- 실제 증권 계좌 자동 연동은 후순위다.
- MVP에서는 사용자가 직접 입력한 관심 자산과 mock data 기반 흐름으로 시작한다.
- 계좌 연동은 보안, 인증, 개인정보 처리 정책이 준비된 뒤 진행한다.

### 5-5. 카카오 채널 챗봇 연동

카카오 채널 챗봇은 빠른 조회와 알림 채널로 사용한다. 기존 Discord Bot 중심 계획은 카카오 채널 챗봇 중심으로 변경한다.

MVP에서는 n8n을 카카오 챗봇과 FinLightAI API 사이의 자동화/연결 계층으로 사용한다. n8n은 카카오 챗봇 요청을 Webhook으로 받고, FinLightAI API에서 시장 신호와 뉴스 데이터를 조회한 뒤 챗봇 응답 형태로 가공한다.

연동 구조:

```text
사용자 카카오 채널 메시지
-> 카카오 채널 챗봇
-> n8n Webhook
-> FinLightAI API
-> n8n 응답 가공
-> 카카오 채널 챗봇 응답
```

사용자 질문 후보:

```text
오늘 시장 신호 알려줘
주의 뉴스 있어?
반도체 영향도 보여줘
내 포트폴리오 리스크 알려줘
삼성전자 관련 뉴스 알려줘
RED 신호 이유가 뭐야?
```

자동 알림 조건:

- 시장 위험도 70 이상
- 관심 산업 영향도 ±60 이상
- 신뢰도 낮은 뉴스 감지
- 내 포트폴리오 관련 부정 뉴스 발생
- RED 신호 발생
- 일일 AI 브리핑 요약

MVP 구현 기준:

- 카카오 채널 챗봇의 전체 운영 심사가 완료되지 않아도 발표용 흐름은 n8n Webhook 기반으로 시연한다.
- 실제 운영 단계에서는 카카오 비즈니스 채널, 챗봇 설정, 앱/채널 연결, 필요한 심사 절차를 완료한 뒤 정식 배포한다.
- 사용자별 포트폴리오 저장과 인증은 후순위로 두고, 발표용 MVP에서는 예시 포트폴리오와 예시 질문 흐름을 우선 제공한다.

## 6. 최신 개발 구조

프론트엔드:

- `frontend/`: Vite + React + TypeScript
- `frontend/src/App.tsx`: 주요 화면과 상태 전환
- `frontend/src/data/*.mock.ts`: 화면별 mock data
- `frontend/src/types/*.ts`: 화면별 타입 정의
- `frontend/src/services/*Api.ts`: mock/API 전환 가능한 service 계층
- `frontend/src/styles.css`: 고충실도 UI 스타일

백엔드:

- `src/dashboard/app.py`: FastAPI 앱
- `src/dashboard/routes/api.py`: API route
- `src/collector/`: 뉴스/주가 수집
- `src/processor/`: 뉴스 필터링, 감성, 시장 반응, 이벤트 점수
- `src/signal/`: 신호 생성
- `src/notifier/`: 기존 Discord/Email 코드가 남아 있으나 신규 방향은 카카오 채널 챗봇 + n8n

## 7. 개발 단계

### Phase 1: 발표용 React MVP

- AI 브리핑 화면 완성
- 뉴스 가드 화면 완성
- 산업 영향도 화면 완성
- 포트폴리오 화면 완성
- 카카오 알림 화면 완성
- 마이페이지/설정/로그인 흐름 완성
- mock data 기반 시연 안정화

### Phase 2: API 연결 준비

- 화면별 service의 `USE_MOCK` 전환 구조 유지
- FastAPI endpoint 스키마 정리
- 뉴스/산업/포트폴리오/카카오/마이페이지/설정 응답 타입 확정
- 실제 API 오류 fallback 정의

### Phase 3: 실제 데이터 연동

- GDELT collector 구현 및 연결
- Guardian collector 구현 및 연결
- Finnhub collector 구현 및 연결
- BBC RSS collector 구현 및 연결
- yfinance/pykrx 가격 데이터 연결
- News Guard provider 상태 표시 연결

### Phase 4: 카카오 + n8n 고도화

- n8n Webhook workflow 구성
- 카카오 챗봇 질문 intent 설계
- `오늘 시장 신호 알려줘` 응답 구현
- `내 포트폴리오 리스크 알려줘` 응답 구현
- 카카오 챗봇 응답 formatter 구현

### Phase 5: 운영 기능 고도화

- 사용자 인증
- 사용자별 포트폴리오 저장
- 운영 DB 연결
- 카카오 채널 정식 심사 및 운영 연결
- 모델 고도화
- 백테스트 리포트

## 8. DB 테이블 초안

```text
users
portfolio_accounts
portfolio_positions
portfolio_snapshots
market_prices
news_articles
news_filter_results
market_signals
industry_impacts
kakao_channels
kakao_chatbot_sessions
n8n_workflow_logs
asset_alert_rules
user_settings
```

## 9. API 엔드포인트 초안

```text
GET    /api/briefing
GET    /api/news-guard
GET    /api/industry-impact
GET    /api/portfolio
POST   /api/portfolio/assets
PATCH  /api/portfolio/assets/{id}
DELETE /api/portfolio/assets/{id}
GET    /api/kakao-alert
POST   /api/kakao-alert/test
POST   /api/kakao/chatbot/market-summary
POST   /api/kakao/chatbot/asset-summary
GET    /api/mypage
GET    /api/settings
PATCH  /api/settings
```

## 10. 당장 추가할 TODO

- [ ] React 화면 시각 검증
- [ ] `USE_MOCK` false 전환 시 필요한 endpoint 목록 확정
- [ ] News Guard API 응답 스키마 확정
- [ ] Industry Impact API 응답 스키마 확정
- [ ] Portfolio CRUD API 구현
- [ ] Kakao Alert 테스트 API 구현
- [ ] n8n Webhook workflow 초안 작성
- [ ] 투자 추천이 아님을 모든 화면과 카카오 챗봇 응답에 표시
