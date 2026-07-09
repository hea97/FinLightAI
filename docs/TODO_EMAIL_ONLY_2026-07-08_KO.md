# FinLightAI 이메일 알림 MVP TODO - 2026-07-08

## 목표

실제 카카오 메시지 발송은 이번 범위에서 제외하고, 이메일을 기본 알림 채널로 사용한다.
7월 8일 기준 목표는 이메일 구독, 확인, 수신 거부, 일일 요약, RED/YELLOW 즉시 알림을
배포 환경에서 검증 가능한 MVP 상태로 고정하는 것이다.

## 범위 결정

- [x] 실제 카카오 메시지 발송 제외
- [x] n8n 카카오 운영 workflow 제외
- [x] 이메일 알림을 MVP 기본 알림 채널로 확정
- [ ] 문서와 발표 자료에서 "카카오는 향후 확장, 현재 MVP는 이메일 알림"으로 표현 통일

## 오늘 반드시 해야 할 일

### 1. 개발 환경 정리

- [ ] 현재 브랜치 확인: `codex/p0-deployment`
- [ ] 미커밋 변경 파일 확인
- [ ] `backend-local.log`, `backend-local.err.log` 처리 방향 결정
- [ ] `.gitignore`에 로컬 로그 제외 규칙 추가 여부 검토

### 2. 의존성 동기화

- [ ] `.venv`에 누락된 `exchange-calendars` 설치
- [ ] `requirements.txt` 기준으로 가상환경 의존성 동기화
- [ ] 의존성 설치 후 import 오류가 사라졌는지 확인

### 3. 백엔드 테스트

- [ ] 전체 테스트 실행: `python -m pytest`
- [ ] 이메일 알림 테스트 통과 확인
- [ ] 기존 인증, 데이터 파이프라인, DB 테스트 회귀 여부 확인
- [ ] 실패 테스트가 있으면 원인 기록 후 수정

### 4. 이메일 구독 API 검증

- [ ] `GET /api/email-subscription` 동작 확인
- [ ] `PUT /api/email-subscription` 동작 확인
- [ ] 이메일 형식 오류 처리 확인
- [ ] 수신 동의 없는 요청 차단 여부 확인
- [ ] 사용자별 구독 상태가 분리 저장되는지 확인

### 5. double opt-in 검증

- [ ] 구독 신청 시 확인 메일 생성 확인
- [ ] 확인 토큰 24시간 만료 로직 확인
- [ ] `GET /api/email-subscription/confirm` 정상 처리 확인
- [ ] 잘못된 토큰 또는 만료 토큰 오류 처리 확인
- [ ] 확인 완료 후 상태가 `active`로 변경되는지 확인

### 6. 수신 거부 검증

- [ ] 이메일 본문에 수신 거부 링크 포함 확인
- [ ] `GET /api/email-subscription/unsubscribe` 정상 처리 확인
- [ ] 수신 거부 후 상태가 `unsubscribed`로 변경되는지 확인
- [ ] 수신 거부 사용자는 이후 발송 대상에서 제외되는지 확인

### 7. 이메일 provider 설정

- [ ] MVP provider 결정: Resend 권장, SMTP 대안
- [ ] `EMAIL_PROVIDER` 설정
- [ ] `SMTP_FROM` 설정
- [ ] Resend 사용 시 `RESEND_API_KEY` 설정
- [ ] Resend webhook 사용 시 `EMAIL_WEBHOOK_SECRET` 설정
- [ ] 테스트 발신 도메인 또는 발신 주소 검증

### 8. 일일 요약 발송 검증

- [ ] `scripts/send_daily_summary.py` 실행 확인
- [ ] RED/YELLOW/GREEN 신호 수 요약 내용 확인
- [ ] 최신 신호 하이라이트 본문 확인
- [ ] 동일 날짜 중복 발송 방지 확인
- [ ] KST 기준 날짜가 반영되는지 확인

### 9. RED/YELLOW 즉시 알림 검증

- [ ] 데이터 refresh 후 RED/YELLOW 신호만 발송 대상이 되는지 확인
- [ ] GREEN 신호는 즉시 알림에서 제외되는지 확인
- [ ] 사용자 설정 `immediateRed`, `immediateYellow`가 반영되는지 확인
- [ ] 동일 `event_key + ticker + trade_date` 중복 발송 방지 확인
- [ ] 실패/성공/중복 이력이 `notification_deliveries`에 저장되는지 확인

### 10. DB migration 검증

- [ ] 새 migration 파일 추적 여부 확인
- [ ] `alembic upgrade head` 실행 확인
- [ ] `email_subscriptions` 테이블 생성 확인
- [ ] `notification_deliveries` 테이블 생성 확인
- [ ] 가능하면 `alembic check`로 drift 확인

## 배포 전 확인

- [ ] Render 백엔드 환경변수 설정
- [ ] Vercel 프론트 API URL 설정
- [ ] Google OAuth 운영 URL 설정
- [ ] PostgreSQL 연결 확인
- [ ] `/health/live` 확인
- [ ] `/health/ready` 확인
- [ ] 배포 환경에서 이메일 구독 smoke test
- [ ] 배포 환경에서 확인 링크 smoke test
- [ ] 배포 환경에서 수신 거부 smoke test
- [ ] 배포 환경에서 일일 요약 smoke test

## 문서 및 발표 반영

- [ ] SRS에서 이메일 발송 상태를 최신 코드 기준으로 수정
- [ ] PRODUCT_PLANNING에서 알림 채널 범위 수정
- [ ] BACKLOG에서 카카오/n8n을 후순위로 이동
- [ ] 발표 자료에 "이메일 알림 MVP 구현, 카카오는 향후 확장" 명시
- [ ] 보고서에 이메일 알림 흐름도 추가
- [ ] 한계점에 provider 설정, 도메인 검증, 발송 실패 처리 보완 필요성 작성

## 완료 기준

- [ ] 전체 백엔드 테스트 통과
- [ ] 프론트엔드 빌드 통과
- [ ] Alembic migration 적용 확인
- [ ] 이메일 구독, 확인, 수신 거부가 로컬에서 정상 동작
- [ ] 일일 요약 이메일이 실제 또는 provider sandbox로 발송 확인
- [ ] RED/YELLOW 즉시 알림 발송 이력 저장 확인
- [ ] 배포 환경 smoke test 통과
- [ ] 문서와 발표 자료의 기능 상태가 실제 코드와 일치

## 예상 소요

- 최소 개발 및 검증: 8~10시간
- 배포 smoke test와 문서 정리 포함: 12~16시간
- 안정화 여유 포함 권장 일정: 1.5~2일

## 이번 범위에서 제외

- 실제 카카오 메시지 발송
- n8n 운영 workflow 완성
- 카카오 채널 승인 및 알림톡 템플릿 심사
- FinBERT/KoELECTRA 모델 실험
- Guardian/Finnhub provider 추가
- WebSocket 실시간 업데이트
- Plotly.js 차트 고도화
