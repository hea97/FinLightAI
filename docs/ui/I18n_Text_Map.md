# FinLightAI I18n Text Map

## 목적

KO / EN 전환 시 버튼 길이, CTA 문구, 섹션 제목이 어긋나지 않도록 주요 UI 라벨을 객체로 관리한다.

## 현재 구조

대시보드 HTML 안에서 아래 객체를 사용한다.

```js
const translations = {
  ko: {
    brandSub: 'AI 금융 상황판',
    todaySignal: '오늘의 시장 신호',
    briefSummary: 'AI 브리핑 요약',
    filterDanger: '🔴 주의 필요',
    loginCta: '로그인 / 회원가입',
    kakaoCta: '카카오 채널 추가',
    status: 'YELLOW · 주의'
  },
  en: {
    brandSub: 'AI financial signal board',
    todaySignal: 'Today’s Market Signal',
    briefSummary: 'AI Briefing Summary',
    filterDanger: '🔴 Needs caution',
    loginCta: 'Login / Sign Up',
    kakaoCta: 'Add Kakao channel',
    status: 'YELLOW · Caution'
  }
};
```

## 적용 범위

- 상단 네비게이션
- 국내 / 해외 / 관심 산업 탭
- 검색 placeholder
- 로그인 / 회원가입 CTA
- 카카오 채널 추가 CTA
- 뉴스 가드 필터
- 주요 섹션 제목
- 상태 칩

## 남은 범위

아래는 추후 데이터 번역 객체로 확장한다.

- 뉴스 본문 요약
- 뉴스 상세 분석 문장
- 산업 상세 설명
- 포트폴리오 입력 placeholder
- 카카오 메시지 미리보기 본문
- 마이페이지 전체 텍스트
