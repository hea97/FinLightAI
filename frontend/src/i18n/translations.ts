export type Locale = "ko" | "en";

export type ViewId =
  | "overview"
  | "market"
  | "industry"
  | "guard"
  | "portfolio"
  | "kakao"
  | "briefing"
  | "settings";

type PageText = {
  title: string;
  subtitle: string;
};

export const navLabels: Record<Locale, Record<ViewId, string>> = {
  ko: {
    overview: "개요",
    market: "시장 신호",
    industry: "산업 영향도",
    guard: "뉴스 가드",
    portfolio: "포트폴리오",
    kakao: "카카오 알림",
    briefing: "AI 브리핑",
    settings: "설정",
  },
  en: {
    overview: "Overview",
    market: "Market Signals",
    industry: "Industry Impact",
    guard: "News Guard",
    portfolio: "Portfolio",
    kakao: "Kakao Alerts",
    briefing: "AI Briefing",
    settings: "Settings",
  },
};

export const pageText: Record<Locale, Record<ViewId, PageText>> = {
  ko: {
    overview: {
      title: "오늘의 시장 신호",
      subtitle: "뉴스, 산업, 포트폴리오 위험을 한 화면에서 확인합니다.",
    },
    market: {
      title: "시장 신호",
      subtitle: "국내, 해외, 관심 산업별로 위험 지표와 주요 변수를 분리합니다.",
    },
    industry: {
      title: "산업 영향도",
      subtitle: "산업별 점수와 근거 뉴스를 함께 확인합니다.",
    },
    guard: {
      title: "뉴스 가드",
      subtitle: "영향도와 신뢰도를 나누어 과장 신호를 걸러냅니다.",
    },
    portfolio: {
      title: "포트폴리오",
      subtitle: "보유 자산을 등록하고 산업 신호와 연결합니다.",
    },
    kakao: {
      title: "카카오 알림",
      subtitle: "카카오 로그인과 채널 알림 흐름을 관리합니다.",
    },
    briefing: {
      title: "AI 브리핑",
      subtitle: "오늘의 핵심 신호를 짧은 실행 메모로 정리합니다.",
    },
    settings: {
      title: "설정",
      subtitle: "언어, 알림 기준, 관심 산업을 조정합니다.",
    },
  },
  en: {
    overview: {
      title: "Today Market Signals",
      subtitle: "Scan news, industries, and portfolio risk in one workspace.",
    },
    market: {
      title: "Market Signals",
      subtitle: "Split risk indicators by Korea, overseas, and watched industries.",
    },
    industry: {
      title: "Industry Impact",
      subtitle: "Review industry scores with the news behind each move.",
    },
    guard: {
      title: "News Guard",
      subtitle: "Separate impact from trust to avoid overreacting to noise.",
    },
    portfolio: {
      title: "Portfolio",
      subtitle: "Register assets and map them to industry signals.",
    },
    kakao: {
      title: "Kakao Alerts",
      subtitle: "Manage Kakao auth and channel notification flows.",
    },
    briefing: {
      title: "AI Briefing",
      subtitle: "Turn market signals into short action notes.",
    },
    settings: {
      title: "Settings",
      subtitle: "Tune language, alert thresholds, and watched sectors.",
    },
  },
};

export const uiText = {
  ko: {
    searchPlaceholder: "뉴스, 산업, 종목 검색",
    searchEmpty: "검색 결과가 없습니다.",
    kakaoCta: "카카오 채널 연결",
    loginCta: "카카오 로그인",
    status: "데모 데이터",
    language: "EN",
    addAsset: "자산 등록",
    closeForm: "닫기",
    save: "저장",
  },
  en: {
    searchPlaceholder: "Search news, sectors, assets",
    searchEmpty: "No matching result.",
    kakaoCta: "Connect Kakao Channel",
    loginCta: "Kakao Login",
    status: "Demo Data",
    language: "KO",
    addAsset: "Add Asset",
    closeForm: "Close",
    save: "Save",
  },
} satisfies Record<Locale, Record<string, string>>;
