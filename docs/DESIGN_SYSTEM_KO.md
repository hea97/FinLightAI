# FinLightAI 웹 디자인 시스템

이 문서는 현재 웹페이지(`src/dashboard/static`)에 실제 사용된 색상과 폰트를 기준으로 정리한 UI 토큰 가이드입니다.

## 컬러 시스템

### 브랜드 / 다크 UI 기본색

| 토큰 | 값 | 용도 |
| --- | --- | --- |
| `--color-bg` | `#001011` | 앱 전체 배경, 어두운 버튼 텍스트, 딥 네이비 블랙 |
| `--color-surface` | `#093a3e` | 기본 패널, 모달, 로그인 셸 배경 |
| `--color-surface-soft` | `#0d4448` | 보조 표면색, 확장 가능한 서피스 단계 |
| `--color-surface-deep` | `#05282b` | 깊이감 있는 어두운 표면, 확장 가능한 딥 서피스 |
| `--color-accent` | `#3aafb9` | 주요 브랜드 액센트, 활성 상태, 차트 라인 |
| `--color-accent-soft` | `#7fd5dd` | 부드러운 액센트, 아이브로우, 그라디언트 시작점 |
| `--color-text` | `#ecfbfc` | 다크 UI 기본 본문 텍스트 |
| `--color-text-muted` | `#9fc7cb` | 보조 텍스트, 설명, 차트 눈금 |
| `--color-border` | `rgba(58, 175, 185, 0.18)` | 다크 UI 기본 테두리 |

### 시그널 / 상태색

| 토큰 | 값 | 용도 |
| --- | --- | --- |
| `--color-red` | `#f04452` | RED 위험 신호, 하락/위험 도트, 리스크 바 |
| `--color-yellow` | `#f2c14e` | YELLOW 주의 신호, 경고 KPI, 리스크 중간값 |
| `--color-green` | `#31c46c` | GREEN 정상 신호, 상승/안정 도트 |
| `signal-red-text` | `#ff9aa3` | RED 배지/하락 텍스트 |
| `signal-yellow-text` | `#ffe19a` | YELLOW 배지/주의 텍스트 |
| `signal-green-text` | `#8df0b5` | GREEN 배지/상승 텍스트 |

상태 배경은 같은 색의 투명도 버전을 사용합니다.

| 상태 | Border | Background |
| --- | --- | --- |
| RED | `rgba(240, 68, 82, 0.34~0.36)` | `rgba(240, 68, 82, 0.12)` |
| YELLOW | `rgba(242, 193, 78, 0.34~0.36)` | `rgba(242, 193, 78, 0.11~0.12)` |
| GREEN | `rgba(49, 196, 108, 0.34~0.36)` | `rgba(49, 196, 108, 0.11~0.12)` |

### 배경 / 오버레이

| 값 | 용도 |
| --- | --- |
| `rgba(0, 16, 17, 0.86)` | 사이드바 배경 |
| `rgba(0, 16, 17, 0.72)` | 상단바, 모달 백드롭 |
| `rgba(0, 16, 17, 0.48)` | 입력 필드 배경 |
| `rgba(0, 16, 17, 0.24~0.34)` | 카드 내부 아이템, 태그, 버튼 배경 |
| `rgba(9, 58, 62, 0.58~0.98)` | 패널, 검색 박스, 히어로 그라디언트 |
| `rgba(58, 175, 185, 0.10~0.28)` | 활성/호버/강조 배경 |
| `rgba(127, 213, 221, 0.16~0.46)` | 부드러운 광원, 활성 테두리, 그라디언트 |
| `rgba(255, 255, 255, 0.03~0.16)` | 내부 하이라이트, 로그인 메트릭, 스와치 테두리 |

### 라이트 로그인 영역

| 값 | 용도 |
| --- | --- |
| `#ffffff` | 로그인 카드, Google 버튼 배경 |
| `#17202a` | 라이트 영역 기본 텍스트 |
| `#202124` | Google 버튼 텍스트 |
| `#687385` | 라이트 영역 보조 텍스트 |
| `#8993a3` | 구분선 라벨 |
| `#d7dce5` | 입력/버튼 테두리 |
| `#d9dce3` | Google 아이콘 테두리 |
| `#e4e8ef` | 로그인 구분선 |
| `#f7f9fc` | 라이트 입력 배경 |
| `#4285f4` | Google 아이콘 텍스트 |

### 차트 / 로고 보조색

| 값 | 용도 |
| --- | --- |
| `rgba(255,255,255,0.05)` | 차트 그리드 |
| `rgba(58,175,185,0.18)` | 차트 영역 채움 |
| `#050b14`, `#071321` | SVG 로고 배경/마크 |
| `#8af0c7`, `#8eeed0`, `#83e9d3`, `#7bdfe3`, `#6fd7df`, `#87ead5`, `#a0f4d1`, `#73d9e1`, `#84e6d7`, `#72dbe3`, `#87ead9`, `#a3f2cc` | SVG 로고의 민트/시안 픽셀 톤 |
| `#f9fbff` | SVG 로고의 밝은 텍스트 |

## 타입 시스템

### 폰트 패밀리

| 토큰 | 값 | 용도 |
| --- | --- | --- |
| `font-sans` | `"Plus Jakarta Sans", "Segoe UI", Arial, sans-serif` | 전체 UI 기본 폰트 |
| `font-mono` | `"JetBrains Mono", "Cascadia Mono", monospace` | 수치, 시계, LIVE, 코드형 라벨 |
| `logo-font` | `Arial, sans-serif` | SVG 로고 내부 텍스트 |

현재 CSS에는 웹폰트 import가 없습니다. 사용자의 기기에 `Plus Jakarta Sans` 또는 `JetBrains Mono`가 설치되어 있지 않으면 각각 `Segoe UI`, `Cascadia Mono` 또는 기본 폰트로 대체됩니다.

### 텍스트 스케일

| 스타일 | 크기 | 행간 | 굵기 | 용도 |
| --- | --- | --- | --- | --- |
| Display | `clamp(2rem, 4vw, 3.7rem)` | `1.05` | 기본/상속 | 독립 로그인 페이지 메인 카피 |
| Hero heading | `clamp(1.6rem, 3vw, 3rem)` | `1.08` | 기본/상속 | 대시보드 섹션 히어로 제목 |
| Page title | `1.28rem` | 기본 | 기본/상속 | 상단바 현재 페이지 제목 |
| Card title | `0.98rem~1rem` | 기본 | `850` | 브랜드명, 저장 카드 제목 |
| KPI value | `1.72rem` | 기본 | 기본/상속 | 주요 수치, 인덱스 값 |
| Body | 기본 브라우저 크기 | `1.5~1.8` | 기본/상속 | 설명문, 메모, 리스트 |
| Eyebrow | `0.68rem` | 기본 | `850` | 섹션 라벨, 대문자 라벨 |
| Badge / Chip | `0.72rem` | 기본 | `800` | 시그널 칩, 필터, 세그먼트 |
| Small label | `0.70rem~0.78rem` | 기본 | `800~850` | KPI 라벨, 테이블 헤더, 폼 라벨 |
| Link helper | `0.82rem` | 기본 | 기본/상속 | 로그인 보조 링크 |

### 타입 사용 규칙

- 금융 수치, 시간, 상태 코드처럼 정렬감이 중요한 값은 `font-mono`를 사용합니다.
- 섹션 라벨은 `Eyebrow` 스타일을 사용하고 `letter-spacing: 0.08em`, `text-transform: uppercase`를 유지합니다.
- 주요 화면 제목은 `h2` 스케일을 사용하고, 패널 내부 제목은 과하게 키우지 않습니다.
- 버튼, 칩, 배지는 굵은 폰트(`750~850`)로 정보 밀도를 높입니다.

## 권장 토큰 정리안

현재 색상은 대부분 `:root`에 정리되어 있지만, 상태 텍스트와 라이트 로그인 색상은 하드코딩되어 있습니다. 장기적으로는 아래처럼 토큰을 추가하면 재사용성이 좋아집니다.

```css
:root {
  --color-signal-red-text: #ff9aa3;
  --color-signal-yellow-text: #ffe19a;
  --color-signal-green-text: #8df0b5;

  --color-light-bg: #ffffff;
  --color-light-surface: #f7f9fc;
  --color-light-text: #17202a;
  --color-light-text-strong: #202124;
  --color-light-text-muted: #687385;
  --color-light-border: #d7dce5;
  --color-google-blue: #4285f4;

  --font-sans: "Plus Jakarta Sans", "Segoe UI", Arial, sans-serif;
  --font-mono: "JetBrains Mono", "Cascadia Mono", monospace;
}
```
