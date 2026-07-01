# FinLightAI 최신 문서 위치

최종 업데이트: 2026-07-01

## 핵심 문서

| 목적 | 위치 |
|---|---|
| 기획 문서 모음 | `docs/planning/README.md` |
| 현재 방향과 우선순위 | `docs/CURRENT_DIRECTION_AND_GOALS_KO.md` |
| 전체 제품 기획 | `docs/PRODUCT_PLANNING_KO.md` |
| 기능 요구사항(SRS) | `docs/SRS.md` |
| 디자이너 전달용 기능 명세 | `docs/design/FINLIGHTAI_DESIGN_FUNCTION_SPEC_KO.md` |
| API/운영 백로그 | `docs/BACKLOG_API_PLANNING.md` |
| 상세 작업 및 검증 기록 | `docs/TODO.md` |

## 배포 및 인증 문서

| 목적 | 위치 |
|---|---|
| Google OAuth 설정 | `docs/GOOGLE_OAUTH_MVP_SETUP.md` |
| Vercel 프론트 배포 | `docs/VERCEL_FRONTEND_DEPLOY.md` |
| Render 등 백엔드 배포 | `docs/BACKEND_DEPLOY.md` |
| 카카오 URL 준비 참고 | `docs/KAKAO_DEPLOY_URL_SETUP.md` |
| 카카오 + n8n 장기 계획 | `docs/KAKAO_N8N_CHATBOT_PLAN_KO.md` |

## 디자인 보조 문서

| 목적 | 위치 |
|---|---|
| 디자인 시스템 | `docs/design/FINLIGHTAI_DESIGN_SYSTEM_V2.md` |
| 인터랙션 기준 | `docs/ui/Interaction_Spec.md` |
| 디자이너 화면 콘텐츠 요청 | `docs/ui/Designer_Page_Content_Request.md` |
| 대시보드 탭 콘텐츠 | `docs/ui/Dashboard_Tab_Content_Spec.md` |

## 구현 기준 위치

| 범위 | 위치 |
|---|---|
| React 화면 | `frontend/src/App.tsx` |
| 프론트 API 호출 | `frontend/src/services/` |
| 프론트 API 타입 | `frontend/src/types/` |
| FastAPI route | `src/dashboard/routes/api.py` |
| API schema | `src/dashboard/schemas.py` |
| OAuth/세션 | `src/dashboard/auth.py` |
| DB model/repository | `src/dashboard/models.py`, `src/dashboard/repository.py` |
| 데이터 파이프라인 | `src/dashboard/services/data_pipeline.py` |
| 배포 전 테스트 | `tests/` |

문서가 충돌할 경우 이 파일의 핵심 문서와 실제 코드/테스트를 우선한다.
