# P2 알림 운영 가이드

## 구현 범위

- 이메일 provider: SMTP 또는 Resend (`EMAIL_PROVIDER=resend` 권장)
- 24시간 만료 double opt-in, one-click 수신 거부
- 일일 요약과 RED/YELLOW 즉시 알림 분리
- 채널별 idempotency와 중복 차단 횟수
- `sent`, `delivered`, `failed`, `delayed`, `bounced`, `complained` 이력
- bounce/complaint 발생 구독자 자동 `suppressed`
- 카카오 채널 승인 전 발송 차단
- 승인 후 FinLightAI → 인증된 n8n webhook → 카카오 공식 딜러사 API 연결

## 환경변수

```dotenv
BACKEND_URL=https://finlightai-api.example

EMAIL_PROVIDER=resend
RESEND_API_KEY=re_xxx
SMTP_FROM=FinLightAI <alerts@updates.example.com>
EMAIL_WEBHOOK_SECRET=whsec_xxx

NOTIFICATION_SECRET=long-random-job-secret
NOTIFICATION_TOKEN_SECRET=long-random-token-secret

KAKAO_CHANNEL_ID=_your_channel_id
KAKAO_CHANNEL_APPROVED=false
N8N_KAKAO_WEBHOOK_URL=https://n8n.example/webhook/finlight-kakao
N8N_WEBHOOK_TOKEN=long-random-n8n-token
```

Resend에서 발신 도메인을 검증한 뒤 webhook URL을
`POST /api/notifications/email-events`로 등록한다. `EMAIL_WEBHOOK_SECRET`에는
webhook 상세 화면의 `whsec_...` signing secret을 넣는다. 서버는 원본 body와
`svix-id`, `svix-timestamp`, `svix-signature`를 검증한다.

## 실행

파이프라인 갱신 시 새 RED/YELLOW 신호는 자동 발송된다. 동일
`event_key + ticker + trade_date`는 재발송되지 않고 중복 횟수만 기록된다.

일일 요약은 KST 기준 하루 한 번 실행한다.

```powershell
python scripts/send_daily_summary.py
```

n8n Schedule Trigger 또는 Render Cron에서 위 스크립트를 실행할 수 있다.
수동/외부 job 호출은 `X-Notification-Secret` 헤더와 함께
`POST /api/notifications/dispatch`를 사용한다.

## n8n → 카카오 계약

FinLightAI가 n8n webhook에 보내는 JSON:

```json
{
  "eventId": "signal:...",
  "userId": "user-id",
  "type": "signal",
  "signal": "RED",
  "title": "[FinLightAI] ...",
  "message": "..."
}
```

n8n workflow는 다음 순서로 구성한다.

1. Webhook 노드에서 `Authorization: Bearer <N8N_WEBHOOK_TOKEN>`을 검증한다.
2. `eventId`로 workflow 중복 실행을 차단한다.
3. 사용자 CRM에서 공식 딜러사가 요구하는 수신 식별자(일반적으로 휴대전화)를 조회한다.
4. HTTP Request 노드에서 승인된 알림톡 템플릿으로 공식 딜러사 API를 호출한다.
5. 딜러사 응답의 메시지 ID를 `{"messageId":"..."}`로 FinLightAI에 반환한다.

카카오 알림톡은 카카오가 직접 일반 REST key로 제공하는 발송 API가 아니라
공식 딜러사를 통해 제공된다. 따라서 다음 외부 작업이 끝나기 전에는
`KAKAO_CHANNEL_APPROVED=false`를 유지한다.

- 카카오톡 채널 생성 및 비즈니스 채널 심사
- 공식 딜러사 계약과 발신 프로필 등록
- RED/YELLOW/일일 요약 템플릿 심사
- 사용자 휴대전화 수집·이용 및 알림 수신 동의 검토
- 딜러사 API credential을 n8n Credentials에 저장
- 테스트 수신, 실패 callback, 재시도 정책 검증

위 승인이 완료된 뒤에만 `KAKAO_CHANNEL_APPROVED=true`로 변경한다. 승인 전
카카오 발송 시도는 `failed` 이력으로 남고 외부 webhook은 호출하지 않는다.
