# FinLightAI 카카오 채널 챗봇 및 n8n 연동 기획

작성일: 2026-06-21

## 1. 변경 배경

기존 알림/챗봇 방향은 Discord Bot 중심이었다. 국내 사용자 접근성과 발표 전달력을 고려해 알림 채널을 카카오 채널 챗봇 중심으로 변경한다.

변경 전:

```text
FinLightAI -> Discord Webhook/Bot -> 사용자 알림/명령 응답
```

변경 후:

```text
사용자 카카오 채널 메시지
-> 카카오 채널 챗봇
-> n8n Webhook
-> FinLightAI API
-> n8n 응답 가공
-> 카카오 채널 챗봇 응답
```

## 2. n8n 사용 판단

n8n은 MVP와 발표용 구현에 적합하다.

이유:

- Webhook으로 카카오 챗봇 요청을 받을 수 있다.
- HTTP Request 노드로 FinLightAI API를 호출할 수 있다.
- 코드 수정 없이 질문별 응답 흐름을 빠르게 바꿀 수 있다.
- 발표 전까지 실제 챗봇 로직을 백엔드에 모두 구현하지 않아도 시연 흐름을 만들 수 있다.
- 추후 운영에서는 n8n을 연결/자동화 계층으로 유지하고, 핵심 판단 로직은 FinLightAI 서버에 둘 수 있다.

주의:

- 카카오 채널 정식 운영에는 비즈니스 채널, 앱/채널 연결, 챗봇 설정, 심사 절차가 필요할 수 있다.
- 2026-06-26 발표 전에는 정식 운영보다 "연동 구조와 데모 흐름"을 보여주는 것이 안전하다.
- 실제 사용자별 포트폴리오 조회는 인증/개인정보 처리 설계가 필요하므로 MVP에서는 예시 데이터 또는 데모 계정 기준으로 진행한다.

## 3. MVP 범위

### 발표 전 필수

- Kakao Channel Bot 화면 추가 또는 기존 Discord Alert 화면 교체
- n8n Webhook 기반 흐름 설명
- 카카오 챗봇 질문 예시 정리
- FinLightAI API 응답을 챗봇 메시지로 바꾸는 formatter 설계
- 투자 추천이 아니라 시장 상태 알림이라는 문구 반영

### 발표 후 진행

- 카카오 채널 실제 개설/운영 설정
- 카카오 챗봇 시나리오 정식 등록
- 앱/채널 연결 및 필요한 심사
- 사용자별 포트폴리오 인증/저장
- 실제 알림 발송 로그 저장

## 4. 사용자 질문 시나리오

### 오늘 시장 신호

사용자:

```text
오늘 시장 신호 알려줘
```

응답:

```text
FinLightAI 오늘의 시장 신호: YELLOW

요약:
- 반도체 섹터 관련 정책 뉴스가 증가했습니다.
- 신뢰도 높은 뉴스는 4건, 주의 뉴스는 1건입니다.
- 시장 반응은 아직 과도하지 않지만 변동성은 확대 중입니다.

주의: 이 내용은 투자 추천이 아니라 시장 상태 요약입니다.
```

### 주의 뉴스

사용자:

```text
주의 뉴스 있어?
```

응답:

```text
News Guard 주의 뉴스 1건

제목: AI 반도체 수출 규제 확대 가능성
영향 산업: 반도체
영향도: 76/100
신뢰도: 0.67

주의 사유:
- 단일 출처 중심 보도
- 가격 변동을 과도하게 단정하는 표현 포함

주의: 원문과 추가 출처 확인이 필요합니다.
```

### 포트폴리오 리스크

사용자:

```text
내 포트폴리오 리스크 알려줘
```

응답:

```text
FinLightAI 포트폴리오 리스크 요약

현재 상태: YELLOW

주요 노출:
1. 삼성전자 42.1% | 반도체 | YELLOW
2. NVIDIA 31.4% | AI Chip | GREEN
3. SK하이닉스 18.9% | HBM | YELLOW

리스크 메모:
- 반도체 섹터 비중이 높습니다.
- 정책 뉴스에 따른 단기 변동성 확인이 필요합니다.

주의: 이 내용은 투자 추천이 아닙니다.
```

## 5. 화면 기획 변경

기존 `Discord Alert` 화면을 `Kakao Channel Bot` 화면으로 변경한다.

화면 구성:

- 카카오 채널 연결 상태
- n8n Webhook 연결 상태
- 최근 챗봇 응답 내역
- 자동 알림 조건
- 사용자 질문 예시
- 테스트 메시지 보내기 버튼

표시할 상태 예시:

```text
Kakao Channel: 준비 중
n8n Webhook: 연결됨
FinLightAI API: 정상
최근 응답: 오늘 시장 신호 알려줘 -> YELLOW 요약 응답
```

## 6. API 초안

발표용 MVP에서는 기존 API를 활용하고, 추후 아래 API를 추가한다.

```text
GET  /api/signals
GET  /api/news
GET  /api/market
POST /api/kakao/test
POST /api/kakao/chatbot/market-summary
POST /api/kakao/chatbot/news-guard
POST /api/kakao/chatbot/asset-summary
```

## 7. n8n Workflow 초안

```text
Webhook Trigger
-> Parse user message
-> Switch by intent
   -> market-summary: GET /api/signals
   -> news-guard: GET /api/news
   -> industry-impact: GET /api/market
   -> asset-summary: GET /api/portfolio/risk
-> Format Kakao chatbot response
-> Respond to Webhook
```

## 8. 환경 변수 초안

```text
KAKAO_CHANNEL_ID=
KAKAO_CHATBOT_WEBHOOK_SECRET=
N8N_WEBHOOK_URL=
N8N_WEBHOOK_SECRET=
```

기존 `DISCORD_WEBHOOK_URL`은 발표 이후 제거하거나 legacy 설정으로 분리한다.

## 9. 발표 시 설명 문장

FinLightAI는 웹 대시보드뿐 아니라 카카오 채널 챗봇으로도 시장 상태를 확인할 수 있도록 설계했습니다. 사용자가 "오늘 시장 신호 알려줘"처럼 자연어로 질문하면, n8n이 FinLightAI API를 호출해 RED/YELLOW/GREEN 신호와 News Guard 결과를 카카오 챗봇 응답으로 요약합니다.

MVP 단계에서는 n8n을 연결 계층으로 사용해 빠르게 시연 가능한 구조를 만들고, 실제 운영 단계에서는 카카오 채널 심사, 사용자 인증, 포트폴리오 저장, 알림 로그 저장을 순차적으로 강화할 계획입니다.
