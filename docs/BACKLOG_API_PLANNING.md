# API 및 제품 백로그

작성일: 2026-06-23
최종 업데이트: 2026-07-01

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

## P0: 배포 완료

- [ ] Render 백엔드와 PostgreSQL 생성
- [ ] `DATABASE_URL`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` 설정
- [ ] `GOOGLE_REDIRECT_URI`, `FRONTEND_URL`, `CORS_ORIGINS` 설정
- [ ] 충분히 긴 `JWT_SECRET_KEY` 설정
- [ ] Vercel `VITE_API_BASE_URL` 설정
- [ ] Google OAuth Consent Screen, test user, Web Client 설정
- [ ] login/callback/me/logout 배포 smoke test
- [ ] portfolio/preferences/settings 사용자 격리 smoke test
- [ ] refresh command 정기 스케줄 등록

## P1: 운영 안정성

- [ ] Alembic 기반 versioned migration
- [ ] exchange calendar 기반 다음 거래일 계산
- [ ] refresh 실행 이력과 provider 장애 모니터링
- [ ] GitHub Actions에서 backend test와 frontend build 실행
- [ ] 세션 만료/로그아웃/교차 origin 쿠키 E2E 테스트
- [ ] API 오류와 빈 데이터 UI 상태 시각 검증

## P2: 데이터 확장

- [ ] Guardian provider adapter
- [ ] Finnhub provider adapter
- [ ] 선택적 pykrx provider와 조정주가 비교
- [ ] provider별 호출량/쿼터 정책
- [ ] Gemini 품질 평가와 비용/timeout 기준

## P3: 알림 확장

- [ ] 카카오 비즈니스 채널과 챗봇 준비
- [ ] n8n webhook workflow
- [ ] 시장 요약/관심 자산 intent
- [ ] 실제 메시지 발송, 재시도, 이력 저장
- [ ] 투자 추천 아님 고지와 대시보드 CTA 검수

## 보류/정리 대상

- Discord 실제 연동은 현재 제품 방향에서 제외한다.
- 카카오 OAuth 프로토타입은 MVP 인증 경로로 사용하지 않는다.
- `src/dashboard/static/` 레거시 화면은 React 배포 안정화 후 유지 여부를 결정한다.
