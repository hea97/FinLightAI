# API 및 제품 백로그

작성일: 2026-06-23
최종 업데이트: 2026-07-08

## 현재 완료 범위

- [x] React service 계층을 FastAPI endpoint에 연결
- [x] 브리핑, 뉴스 가드, 산업 영향도 응답 schema 구현
- [x] 실제 뉴스/시장 수집 결과 DB 저장
- [x] signal 생성 결과 DB 저장 및 dashboard metadata 제공
- [x] 포트폴리오 CRUD
- [x] 마이페이지와 설정 조회/변경
- [x] 카카오 알림 규칙 조회/변경
- [x] provider/fallback/warning metadata
- [x] Google OAuth login/callback/me/logout
- [x] 사용자 preference 온보딩 저장
- [x] 인증 사용자 기준 데이터 분리
- [x] Vercel SPA 및 Render/CORS/PostgreSQL 설정 준비
- [x] 이메일 구독 조회/저장 API와 DB model
- [x] 이메일 구독 modal과 주요 화면 상태 연결
- [x] SQLite 기존 사용자 테이블 OAuth 필드 호환 패치
- [x] backend test 70개 및 frontend production build 통과
- [x] 이메일 double opt-in 확인/수신 거부 API 초안
- [x] SMTP/Resend 이메일 발송 adapter 초안
- [x] 일일 요약 발송 script 초안
- [x] RED/YELLOW 즉시 알림 dispatch와 GREEN 제외 로직 초안
- [x] `notification_deliveries` 기반 발송 성공/실패/중복/bounce/complaint 이력 구조 초안
- [x] 알림 관련 Alembic migration 초안

## P0: 이메일 알림 MVP 및 배포 완료

- [ ] Render 백엔드와 PostgreSQL 생성
- [ ] `DATABASE_URL`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` 설정
- [ ] `GOOGLE_REDIRECT_URI`, `FRONTEND_URL`, `CORS_ORIGINS` 설정
- [ ] 충분히 긴 `JWT_SECRET_KEY` 설정
- [ ] Vercel `VITE_API_BASE_URL` 설정
- [ ] Google OAuth Consent Screen, test user, Web Client 설정
- [ ] `EMAIL_PROVIDER` 결정: Resend 권장, SMTP 대안
- [ ] `SMTP_FROM`, `RESEND_API_KEY` 또는 SMTP 계정 설정
- [ ] `NOTIFICATION_SECRET`, `NOTIFICATION_TOKEN_SECRET`, `EMAIL_WEBHOOK_SECRET` 설정
- [ ] `alembic upgrade head`로 `email_subscriptions`, `notification_deliveries` 생성 확인
- [ ] login/callback/me/logout 배포 smoke test
- [ ] portfolio/preferences/settings 사용자 격리 smoke test
- [ ] refresh command 정기 스케줄 등록
- [ ] 이메일 구독 API 배포 smoke test
- [ ] 이메일 확인 링크와 수신 거부 링크 smoke test
- [ ] `scripts/send_daily_summary.py` 배포 환경 실행 확인
- [ ] RED/YELLOW 즉시 알림 dispatch와 중복 방지 smoke test
- [ ] provider webhook bounce/complaint 처리 smoke test

## P1: 운영 안정성

- [ ] 알림 migration을 포함한 Alembic versioned migration 운영 검증
- [ ] exchange calendar 기반 다음 거래일 계산
- [ ] refresh 실행 이력과 provider 장애 모니터링
- [ ] GitHub Actions에서 backend test와 frontend build 실행
- [ ] 세션 만료/로그아웃/교차 origin 쿠키 E2E 테스트
- [ ] API 오류와 빈 데이터 UI 상태 시각 검증
- [ ] SQLite 임시 패치를 Alembic 등 versioned migration으로 대체
- [ ] 이메일 발신 도메인, SPF/DKIM/DMARC, provider rate limit 운영 기준 정리

## P2: 데이터 확장

- [ ] Guardian provider adapter
- [ ] Finnhub provider adapter
- [ ] 선택적 pykrx provider와 조정주가 비교
- [ ] provider별 호출량/쿼터 정책
- [ ] Gemini 품질 평가와 비용/timeout 기준

## P3: 알림 확장

- [ ] 주간 레터와 개인화 요약 고도화
- [ ] 이메일 템플릿 HTML 버전과 브랜드 스타일 적용
- [ ] 개인정보처리방침과 수신 동의 문구 법무/운영 검토
- [ ] 발송 실패 재시도 정책과 suppression list 운영

- [ ] 카카오 비즈니스 채널과 챗봇 준비
- [ ] n8n webhook workflow
- [ ] 시장 요약/관심 자산 intent
- [ ] 실제 메시지 발송, 재시도, 이력 저장
- [ ] 투자 추천 아님 고지와 대시보드 CTA 검수

## 보류/정리 대상

- Discord 실제 연동은 현재 제품 방향에서 제외한다.
- 카카오 OAuth 프로토타입은 MVP 인증 경로로 사용하지 않는다.
- 실제 카카오 메시지와 n8n 운영 workflow는 이번 MVP 범위에서 제외한다.
- 이메일은 카카오 승인 전 기본 채널이며, provider 환경과 배포 smoke test가 끝나야 운영 완료로 본다.
- `src/dashboard/static/` 레거시 화면은 React 배포 안정화 후 유지 여부를 결정한다.
