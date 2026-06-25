# FinLightAI 최신 문서 위치

최종 업데이트: 2026-06-25

## 핵심 문서

| 구분 | 문서 | 위치 |
|---|---|---|
| 현재 방향/목표 | FinLightAI 현재 방향성과 목표 계획서 | `docs/CURRENT_DIRECTION_AND_GOALS_KO.md` |
| 전체 기획 | FinLightAI 전체 기획서 | `docs/PRODUCT_PLANNING_KO.md` |
| 기능 명세 | 소프트웨어 요구사항 명세서 | `docs/SRS.md` |
| 디자인 기능 명세 | FinLightAI 디자인 기능 명세서 | `docs/design/FINLIGHTAI_DESIGN_FUNCTION_SPEC_KO.md` |
| 디자인 시스템 | FinLightAI Design System v2 | `docs/design/FINLIGHTAI_DESIGN_SYSTEM_V2.md` |
| API/포트폴리오 백로그 | API 및 포트폴리오 기획 백로그 | `docs/BACKLOG_API_PLANNING.md` |

## 디자이너 전달용 보조 문서

| 구분 | 위치 |
|---|---|
| 페이지별 콘텐츠 요청 | `docs/ui/Designer_Page_Content_Request.md` |
| UI 수정 요청 | `docs/ui/FinLightAI_UI_Fix_Request.md` |
| 인터랙션 명세 | `docs/ui/Interaction_Spec.md` |
| 첫 화면 탭별 콘텐츠 | `docs/ui/Dashboard_Tab_Content_Spec.md` |
| 카카오 테스트 메시지 | `docs/ui/Kakao_Test_Message.md` |
| 산업 히트맵 샘플 데이터 | `docs/ui/Industry_Heatmap_Sample_Data.md` |
| i18n 텍스트 맵 | `docs/ui/I18n_Text_Map.md` |

## 최신 구현 참고 위치

| 구분 | 위치 |
|---|---|
| React 앱 진입점 | `frontend/src/App.tsx` |
| 공통 브리핑/시장 mock data | `frontend/src/data/mockData.ts` |
| 화면별 mock data | `frontend/src/data/*.mock.ts` |
| 화면별 타입 | `frontend/src/types/*.ts` |
| 화면별 service | `frontend/src/services/*Api.ts` |
| 프론트 스타일 | `frontend/src/styles.css` |
| FastAPI 앱 | `src/dashboard/app.py` |
| FastAPI route | `src/dashboard/routes/api.py` |

## 문서별 사용 기준

- 서비스 방향을 설명할 때는 `docs/CURRENT_DIRECTION_AND_GOALS_KO.md`를 기준으로 본다.
- 제품 범위와 단계별 개발 계획은 `docs/PRODUCT_PLANNING_KO.md`를 기준으로 본다.
- 기능 요구사항과 API 전환 기준은 `docs/SRS.md`를 기준으로 본다.
- 디자이너에게 화면 구성과 UX 기준을 전달할 때는 `docs/design/FINLIGHTAI_DESIGN_FUNCTION_SPEC_KO.md`를 기준으로 본다.
- 색상, 타이포, 간격, 카드 밀도는 `docs/design/FINLIGHTAI_DESIGN_SYSTEM_V2.md`를 기준으로 본다.
