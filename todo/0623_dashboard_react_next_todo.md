# FinLightAI Dashboard TODO - 2026-06-23

## GitHub Push

- [x] `main` 브랜치 GitHub push 완료
- [x] Push 범위: `129de96..2a61b2a`
- [x] 원격 저장소: `https://github.com/hea97/FinLightAI.git`

## 이번에 진행한 작업

- [x] 고충실도 웹앱 UI 초안 구현
  - `FinLightAI_high_fidelity_product_ui_v2.html` 기준으로 정적 대시보드 UI 구현
  - 주요 IA 반영: AI 브리핑, 뉴스 가드, 산업 영향도, 포트폴리오, 마이페이지, 로그인/회원가입, 설정

- [x] 카카오 Auth / 채널 알림 흐름 반영
  - 이메일 로그인과 카카오 로그인 UI 반영
  - 개인톡 연결이 아닌 카카오톡 채널 추가 방식으로 문구 수정
  - 최근 발송 내역과 채널 추가 CTA 중심으로 정리

- [x] Discord 알림 제거 및 카카오 채널 알림으로 전환
  - 카카오 메시지 미리보기 구성
  - 테스트 카카오 메시지 포맷 문서화

- [x] 뉴스 가드 화면 고도화
  - 뉴스 출처와 제목 포맷 반영
  - 영향도/신뢰도/주의 신호를 신호등 기준으로 정리
  - 뉴스 카드 클릭 시 상세 분석 패널 변경
  - 주의 필요 / 검토 필요 / 신뢰 높음 필터링 동작 추가

- [x] 산업 영향도 히트맵 고도화
  - 산업 카드 클릭 시 우측 상세 패널 변경
  - 반도체, 금융, 자동차, 에너지, 바이오, 항공, IT 상세 맥락 추가
  - 누락된 소비재, 원자재, 방산, 게임, 유틸리티 상세 데이터 추가

- [x] 포트폴리오 기능 보강
  - 관심 자산 기반 포트폴리오 구조 반영
  - 직접 자산 등록 폼 열기/닫기 및 등록 UI 추가

- [x] 검색 인터랙션 추가
  - 뉴스, 산업, 주식 검색 후보 노출
  - 검색 결과 클릭 시 관련 화면으로 이동

- [x] KO / EN 언어 전환 구조 정리
  - 주요 네비게이션, CTA, 카드 제목 중심의 i18n 텍스트 맵 분리
  - 향후 React 전환 시 확장 가능한 구조로 정리

- [x] 대시보드 첫 화면 레이아웃 시스템 정리
  - Desktop 12-column grid 기준 반영
  - 1행: 오늘의 시장 신호 8 / AI 브리핑 요약 4
  - 2행: 주요 지표 카드 5 / 산업 히트맵 7
  - 3행: 뉴스 TOP 5 5 / 뉴스 가드 경고 3 / 최근 카카오 알림 4
  - `grid-column: span 2.4` 제거
  - Tablet 6-column, Mobile 1-column 기준 추가

- [x] 문서화
  - 디자이너 전달용 페이지별 콘텐츠 요청 정리
  - 인터랙션 명세, i18n 기준, 탭별 콘텐츠 기준, 히트맵 샘플 데이터 문서 추가

## 다음에 해야 할 작업

- [ ] React 전환 시작
  - 권장: Vite + React + TypeScript
  - 현재 FastAPI 백엔드는 유지
  - `frontend/` 디렉터리 신규 구성
  - 현재 정적 HTML UI를 React 컴포넌트로 분리

- [ ] 컴포넌트 분리
  - `AppShell`
  - `TopHeader`
  - `MarketTabs`
  - `OverviewDashboard`
  - `MetricPanel`
  - `IndustryHeatmap`
  - `NewsGuard`
  - `Portfolio`
  - `KakaoChannel`
  - `MyPage`
  - `AuthPage`

- [ ] 상태 관리 구조화
  - 현재 선택된 화면
  - 현재 선택된 시장 탭
  - 현재 선택된 뉴스 카드
  - 현재 선택된 산업 카드
  - 뉴스 필터
  - KO / EN 언어
  - 포트폴리오 등록 폼 열림 상태

- [ ] i18n 전면 정리
  - 상단 네비게이션
  - 검색 placeholder
  - CTA 버튼
  - 탭 이름
  - 카드 제목/설명
  - 상태값
  - 뉴스 상세 패널
  - 마이페이지 전체 텍스트

- [ ] 탭별 콘텐츠 차별화 추가
  - 국내 시장: KOSPI, KOSDAQ, USD/KRW, 국내 금리, 국내 뉴스
  - 해외 시장: NASDAQ, S&P 500, DOW, VIX, WTI, USD Index, 미국 금리
  - 관심 산업: 관심 산업, 관련 종목, 관련 뉴스, 포트폴리오 위험 신호, 카카오 알림 조건

- [ ] 실제 API 연결 준비
  - 현재 샘플 데이터를 별도 mock data 파일로 분리
  - 이후 FastAPI endpoint와 연결 가능한 타입 정의
  - 뉴스/산업/포트폴리오 데이터 스키마 정리

- [ ] 시각 검증
  - Desktop / Tablet / Mobile 스크린샷 확인
  - 첫 화면 빈 공간 재검증
  - 카드 간 gap, 카드 height, scroll 발생 여부 확인

- [ ] 접근성 및 UX 보강
  - 키보드 포커스 이동
  - 선택 상태 aria 속성
  - 버튼 hover / active / selected 상태 통일
  - 검색 결과 empty state

- [ ] 배포 준비
  - React build 결과를 FastAPI에서 서빙할지 결정
  - 또는 frontend와 backend를 분리 배포할지 결정
  - README 실행 방법 업데이트
