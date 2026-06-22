# FinLightAI Interaction Spec

## 목적

정적 화면처럼 보이지 않도록 현재 선택 상태와 사용자 행동에 따른 정보 변화를 명확히 제공한다.

## 상태 관리 기준

현재 대시보드는 정적 FastAPI 서빙 구조를 유지하되, 프론트 상태는 `appState` 객체로 분리한다.

```js
const appState = {
  screen: 'overview',
  lang: 'ko',
  market: 'global',
  newsFilter: 'all',
  selectedNews: 'rumor',
  selectedIndustry: 'semiconductor',
  portfolioFormOpen: false
};
```

## 적용된 상호작용

| 영역 | 동작 |
|---|---|
| 화면 네비게이션 | 상단 탭 클릭 시 화면 전환 |
| 국내/해외/관심 산업 탭 | 헤드라인, 요약, KPI 카드 변경 |
| 뉴스 가드 필터 | 전체 / 주의 필요 / 검토 필요 / 신뢰 높음 카드 필터링 |
| 뉴스 카드 | 클릭 시 상세 분석 패널 변경 |
| 산업 히트맵 | 클릭 시 선택 산업 상세 설명 변경 |
| 포트폴리오 | 자산 등록 폼 열기/닫기, 자산 추가 |
| 검색 | 뉴스/산업/주식 검색 후 관련 화면 이동 |
| KO/EN | 주요 UI 라벨, CTA, 탭 텍스트 변경 |

## 마이크로 인터랙션

- 화면 전환: `fade + slide-up`
- 탭 hover: 1px 위로 이동
- 카드 hover: border 강조
- 선택 카드: outline/glow 강조
- 포트폴리오 등록 폼: 열릴 때 짧은 등장 애니메이션

## 향후 개선

- 전체 콘텐츠 i18n 확대
- 숫자 KPI count-up 효과
- 카카오 말풍선 순차 등장
- 포트폴리오 등록을 modal 또는 side drawer로 확장
