# API 및 포트폴리오 기획 백로그

작성일: 2026-05-29
최종 업데이트: 2026-06-25

## 사용자 지시 및 최신 방향

- NewsAPI 관리 문서를 생성한다.
- GDELT DOC 2.0 API, The Guardian Open Platform, Finnhub News API, BBC RSS를 채택한다.
- Naver Search News API는 한국어 뉴스 장점은 있으나 검색 결과/요약 중심이라는 이유로 제외한다.
- 금융 주가/주식 관련 API도 추천하고 정리한다.
- 프로젝트 전체 기획 문서를 한국어로 작성한다.
- 웹사이트 구축 시 관심 자산 포트폴리오 기능을 추가한다.
- 기존 Discord 알림/명령 방향은 카카오 채널 챗봇 + n8n Webhook 방향으로 전환한다.

## 수행 내용

- `docs/NEWS_API_MANAGEMENT.md`를 추가했다.
- `docs/FINANCIAL_DATA_API_PLAN.md`를 추가했다.
- `docs/PRODUCT_PLANNING_KO.md`를 최신 방향으로 업데이트했다.
- `docs/SRS.md`를 React MVP와 카카오+n8n 기준으로 업데이트했다.
- BBC는 공식 공개 API가 제한적이므로 RSS 또는 비공식 API 후보를 검증 대상으로 문서화했다.
- 투자 추천 서비스가 아니라 정보 제공/리스크 알림 서비스라는 원칙을 기획서에 명시했다.

## 최신 구현 기준

- 프론트엔드: `frontend/`의 Vite + React + TypeScript
- 화면별 mock data: `frontend/src/data/*.mock.ts`
- 화면별 타입: `frontend/src/types/*.ts`
- 화면별 API service: `frontend/src/services/*Api.ts`
- 백엔드: 기존 FastAPI 구조 유지
- 현재 service 계층은 mock data를 반환하며, 이후 FastAPI endpoint로 전환한다.

## 다음 구현 후보

- News Guard API 응답 스키마 확정
- Industry Impact API 응답 스키마 확정
- Portfolio CRUD API 구현
- Kakao Alert 테스트 API 구현
- MyPage/Settings API 응답 스키마 확정
- GDELT collector 구현
- Guardian collector 구현
- Finnhub collector 구현
- BBC RSS collector 구현
- n8n Webhook workflow 초안 작성
- 카카오 채널 챗봇 질문/응답 시나리오 작성
- 투자 추천이 아님을 모든 화면과 카카오 챗봇 응답에 표시
