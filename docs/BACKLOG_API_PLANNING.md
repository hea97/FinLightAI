# API 및 포트폴리오 기획 백로그

작성일: 2026-05-29

## 사용자 지시

- NewsAPI 관리 문서를 생성한다.
- GDELT DOC 2.0 API, The Guardian Open Platform, Finnhub News API, BBC News API/RSS를 채택한다.
- Naver Search News API는 한국어 뉴스 장점은 있으나 검색 결과/요약 중심이라는 이유로 제외한다.
- 금융 주가/주식 관련 API도 추천하고 정리한다.
- 프로젝트 전체 기획 문서를 한국어로 작성한다.
- 웹사이트 구축 시 자산 포트폴리오 기능을 추가하는 방향을 반영한다.
- Discord와 연결해 `!자산` 명령을 입력하면 포트폴리오 내용이 텍스트로 출력되도록 기획한다.

## 수행 내용

- `docs/NEWS_API_MANAGEMENT.md`를 추가했다.
- `docs/FINANCIAL_DATA_API_PLAN.md`를 추가했다.
- `docs/PRODUCT_PLANNING_KO.md`를 추가했다.
- BBC는 공식 공개 API가 제한적이므로 RSS 또는 비공식 API 후보를 검증 대상으로 문서화했다.
- 투자 추천 서비스가 아니라 정보 제공/리스크 알림 서비스라는 원칙을 기획서에 명시했다.

## 다음 구현 후보

- 뉴스 provider 설정 파일 추가
- GDELT collector 구현
- Guardian collector 구현
- Finnhub collector 구현
- BBC RSS collector 구현
- 포트폴리오 DB schema 추가
- Discord `!자산` formatter와 command handler 구현
