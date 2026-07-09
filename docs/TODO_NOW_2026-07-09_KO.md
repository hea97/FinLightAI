# FinLightAI 오늘 지금 기준 TODO - 2026-07-09 15:44 KST

## 현재 기준

- 기준 브랜치: `codex/p0-deployment`
- 현재 브랜치 상태: `origin/codex/p0-deployment`보다 2커밋 앞섬
- 최신 커밋: `64f2ea2 Add email notification MVP`
- 현재 범위: 실제 카카오 메시지 발송 제외, 이메일 알림 MVP 중심
- 현재 작업 트리: 문서와 `render.yaml`에 미커밋 변경 있음
- 새 문서 후보: `docs/PRE_DEPLOY_CHECKLIST_KO.md`

## 오늘 목표

이메일 알림 MVP를 "로컬 구현 완료"가 아니라 "배포 전 검증 가능한 상태"로 고정한다.
오늘은 기능 추가보다 테스트, 환경변수, 배포 체크리스트, 문서 정합성, 커밋 정리가 우선이다.

## 1순위: 지금 바로 해야 할 일

- [ ] 현재 미커밋 변경 diff 확인
- [ ] 내가 수정한 문서와 코드 변경 범위 분리
- [ ] `docs/PRE_DEPLOY_CHECKLIST_KO.md`를 추적할지 결정
- [ ] `render.yaml` 변경 내용이 실제 Render 환경변수 정책과 맞는지 확인
- [ ] 문서들이 모두 "카카오 제외, 이메일 MVP" 기준으로 같은 표현을 쓰는지 확인
- [ ] 변경 파일에 민감정보나 실제 API key가 포함되지 않았는지 확인

## 2순위: 테스트와 빌드

- [ ] 백엔드 전체 테스트 실행: `python -m pytest`
- [ ] 알림 관련 테스트만 별도 실행: `python -m pytest tests/test_notifications.py tests/test_daily_summary.py`
- [ ] migration 관련 테스트 또는 Alembic 검증 실행
- [ ] 프론트엔드 빌드 실행: `npm.cmd run build`
- [ ] 테스트 결과를 문서의 검증 기록과 맞추기
- [ ] 실패나 warning이 있으면 발표 자료에는 "검증 필요"로 표현

## 3순위: DB migration 검증

- [ ] `database/migrations/versions` 최신 revision 확인
- [ ] `alembic upgrade head` 실행
- [ ] `email_subscriptions` 테이블 생성 확인
- [ ] `notification_deliveries` 테이블 생성 확인
- [ ] 기존 SQLite 또는 PostgreSQL에서 migration 충돌 여부 확인
- [ ] `create_all` 의존이 운영 경로에 남아 있지 않은지 확인

## 4순위: 이메일 provider 설정

- [ ] 이메일 provider 최종 선택: Resend 권장, SMTP 대안
- [ ] `EMAIL_PROVIDER` 설정
- [ ] `SMTP_FROM` 설정
- [ ] Resend 선택 시 `RESEND_API_KEY` 설정
- [ ] provider webhook을 쓸 경우 `EMAIL_WEBHOOK_SECRET` 설정
- [ ] `NOTIFICATION_SECRET` 설정
- [ ] `NOTIFICATION_TOKEN_SECRET` 설정
- [ ] 발신 도메인 또는 발신 주소 검증 상태 확인

## 5순위: 이메일 기능 smoke test

- [ ] `GET /api/email-subscription`으로 초기 상태 확인
- [ ] `PUT /api/email-subscription`으로 구독 신청
- [ ] 확인 메일 본문에 confirm link 포함 확인
- [ ] `GET /api/email-subscription/confirm?token=...`으로 구독 활성화
- [ ] 일일 요약 발송 실행
- [ ] RED/YELLOW 즉시 알림 dispatch 실행
- [ ] 중복 발송 방지 확인
- [ ] 이메일 본문에 unsubscribe link 포함 확인
- [ ] `GET /api/email-subscription/unsubscribe?token=...`으로 수신 거부 확인
- [ ] 발송 성공, 실패, 중복 이력이 `notification_deliveries`에 남는지 확인

## 6순위: 배포 전 체크

- [ ] Render backend URL 확정
- [ ] Vercel frontend URL 확정
- [ ] Render PostgreSQL 연결 확인
- [ ] Google OAuth redirect URI를 실제 Render URL로 설정
- [ ] Vercel `VITE_API_BASE_URL` 확인
- [ ] CORS 허용 origin 확인
- [ ] SameSite/cookie 설정이 프론트와 백엔드 분리 배포에 맞는지 확인
- [ ] `/health/live` 확인
- [ ] `/health/ready` 확인
- [ ] 배포 환경에서 Google OAuth smoke test
- [ ] 배포 환경에서 이메일 구독 smoke test

## 7순위: 문서와 발표 자료 정리

- [ ] `docs/SRS.md`의 구현 상태가 실제 코드와 일치하는지 확인
- [ ] `docs/PRODUCT_PLANNING_KO.md`에서 카카오 제외 범위가 명확한지 확인
- [ ] `docs/BACKLOG_API_PLANNING.md`에서 남은 일을 배포/운영 중심으로 정리
- [ ] `docs/BACKEND_DEPLOY.md`에 이메일 환경변수 누락이 없는지 확인
- [ ] `docs/PRE_DEPLOY_CHECKLIST_KO.md`를 최종 배포 체크리스트로 다듬기
- [ ] 발표 PPT에는 "이메일 알림 MVP 구현, 카카오는 향후 확장"으로 통일
- [ ] 보고서에는 double opt-in, unsubscribe, 발송 이력, 중복 방지 구조를 설명

## 오늘 완료 기준

- [ ] 테스트 결과가 최신 상태로 확인됨
- [ ] 프론트 빌드가 통과함
- [ ] Alembic migration이 적용 가능함
- [ ] 이메일 구독, 확인, 수신 거부, 일일 요약, RED/YELLOW 알림 흐름이 검증됨
- [ ] 배포 환경변수 목록이 확정됨
- [ ] 실제 카카오 메시지는 이번 범위 제외로 문서화됨
- [ ] 미커밋 변경을 검토하고 의미 있는 단위로 커밋 준비 완료

## 오늘 끝나지 않아도 되는 일

- [ ] 실제 카카오 메시지 발송
- [ ] n8n 운영 workflow 완성
- [ ] 카카오 채널 승인 및 알림톡 템플릿 심사
- [ ] FinBERT 또는 KoELECTRA 모델 실험
- [ ] Guardian, Finnhub provider 추가
- [ ] WebSocket 실시간 업데이트
- [ ] Plotly.js 차트 고도화

## 추천 작업 순서

1. 미커밋 diff 확인
2. 테스트와 빌드 재실행
3. migration 검증
4. 이메일 provider 환경변수 확정
5. 로컬 이메일 smoke test
6. 배포 체크리스트 보완
7. 문서 상태 정리
8. 커밋 단위 정리
