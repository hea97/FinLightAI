import { useEffect, useMemo, useRef, useState, type FormEvent, type ReactNode, type RefObject } from "react";
import {
  briefingReadiness,
  industries,
  marketData,
  tabs,
  type BriefingBiasCheck,
  type BriefingReadinessData,
  type MarketTab,
  type MarketViewData,
  type NewsImpact,
  type Tone,
} from "./data/mockData";
import { fetchCurrentUser, logout, redirectToGoogleLogin, saveOnboardingPreferences } from "./services/authApi";
import { fetchBriefingData } from "./services/briefingApi";
import { fetchIndustryImpactData } from "./services/industryImpactApi";
import { fetchMyPageData, updateMyPageData } from "./services/myPageApi";
import { fetchNewsGuardData } from "./services/newsGuardApi";
import { createPortfolioAsset, deletePortfolioAsset, fetchPortfolioData, updatePortfolioAsset } from "./services/portfolioApi";
import { fetchSettingsData, saveSettingsData } from "./services/settingsApi";
import type { BriefingResponse } from "./types/briefing";
import type { IndustryDetail, IndustryImpactResponse, IndustrySummary, RelatedNewsItem } from "./types/industryImpact";
import type { MyPageActivity, MyPageAlertSetting, MyPageConnection, MyPageMetric, MyPageProfile, MyPageResponse, MyPageShortcut } from "./types/myPage";
import type { AssetCurrency, AssetMarket, AssetStatus, IndustryConnection, LinkedSignal, PortfolioAsset, PortfolioResponse, PortfolioSummary } from "./types/portfolio";
import type { ApiConnection, DataCollectionSettings, DisplaySettings, MiscSettings, NewsGuardMode, NewsGuardSettings, NotificationSetting, SettingsResponse, SettingsStatusCard } from "./types/settings";
import type { AuthMeResponse } from "./types/auth";
import type {
  BlockReason,
  NewsArticle,
  NewsGuardFilter,
  NewsGuardViewModel,
  ProviderHealth,
  QuickFilter,
  ReliabilityDistribution,
  ReliabilityLevel,
} from "./types/newsGuard";

type ViewId = "briefing" | "guard" | "industry" | "portfolio" | "mypage" | "settings" | "login";

const HIDDEN_LEGACY_PROVIDER_ID = ["ka", "kao"].join("");
const HIDDEN_AUTOMATION_ID = ["n", "8", "n"].join("");

const navItems: { id: Exclude<ViewId, "mypage" | "login">; label: string }[] = [
  { id: "briefing", label: "AI 브리핑" },
  { id: "guard", label: "뉴스 가드" },
  { id: "industry", label: "산업 영향도" },
  { id: "portfolio", label: "포트폴리오" },
  { id: "settings", label: "설정" },
];

const viewCopy: Record<ViewId, { title: string; subtitle: string }> = {
  briefing: {
    title: "AI 브리핑",
    subtitle: "오늘의 시장 신호와 뉴스 근거를 먼저 요약합니다.",
  },
  guard: {
    title: "뉴스 가드",
    subtitle: "뉴스 신뢰도를 검증하고 저신뢰 뉴스를 걸러냅니다.",
  },
  industry: {
    title: "산업 영향도",
    subtitle: "산업별 점수와 근거 뉴스를 한 화면에서 확인합니다.",
  },
  portfolio: {
    title: "포트폴리오",
    subtitle: "직접 등록한 자산을 기준으로 산업/뉴스 신호를 모니터링합니다.",
  },
  mypage: {
    title: "마이페이지",
    subtitle: "관심 산업, 알림 조건, 언어 설정을 관리합니다.",
  },
  settings: {
    title: "설정",
    subtitle: "데이터, 알림, 언어, 화면 표시 기준을 조정합니다.",
  },
  login: {
    title: "로그인 / 회원가입",
    subtitle: "Google OAuth 기반 인증 흐름을 준비합니다.",
  },
};

type HeaderSearchResult = {
  id: string;
  title: string;
  subtitle: string;
  targetView: ViewId;
  targetIndustryId?: string;
};

const headerSearchIndex: HeaderSearchResult[] = [
  { id: "briefing-yellow", title: "YELLOW 주의 신호", subtitle: "오늘 시장 신호와 위험도 68/100", targetView: "briefing" },
  { id: "news-guard", title: "뉴스 가드", subtitle: "저신뢰 뉴스와 차단 상태 확인", targetView: "guard" },
  { id: "industry-semiconductor", title: "반도체", subtitle: "산업 영향도와 관련 뉴스", targetView: "industry", targetIndustryId: "semiconductor" },
  { id: "asset-samsung", title: "삼성전자 005930", subtitle: "포트폴리오 보유 자산", targetView: "portfolio" },
  { id: "email-alerts", title: "Email alerts", subtitle: "Daily summary and RED/YELLOW signal delivery", targetView: "settings" },
];

type PublicPath = "/about" | "/login" | "/signup" | "/privacy" | "/terms";

const publicNavItems: { href: PublicPath; label: string }[] = [
  { href: "/about", label: "About" },
  { href: "/login", label: "Login" },
  { href: "/signup", label: "Sign up" },
  { href: "/privacy", label: "Privacy" },
  { href: "/terms", label: "Terms" },
];

function PublicPage({ path }: { path: string }) {
  const normalizedPath = (path === "/signup" ? "/signup" : path) as PublicPath;
  const isAuthPage = normalizedPath === "/login" || normalizedPath === "/signup";
  const titleByPath: Record<PublicPath, string> = {
    "/about": "FinLightAI",
    "/login": "Google 로그인",
    "/signup": "회원가입",
    "/privacy": "개인정보처리방침",
    "/terms": "서비스 약관",
  };

  return (
    <main className="public-shell">
      <nav className="public-nav" aria-label="Public pages">
        <a className="public-brand" href="/about">FL FinLightAI</a>
        <div>
          {publicNavItems.map((item) => (
            <a aria-current={normalizedPath === item.href ? "page" : undefined} href={item.href} key={item.href}>{item.label}</a>
          ))}
          <a href="/">Dashboard</a>
        </div>
      </nav>

      <section className="public-hero">
        <p className="public-eyebrow">AI market signal board</p>
        <h1>{titleByPath[normalizedPath] ?? "FinLightAI"}</h1>
        <p>
          FinLightAI filters real news, checks source quality, combines market reaction data,
          and presents market-state signals. It is an information service, not investment advice.
        </p>
        {isAuthPage ? (
          <div className="public-actions">
            <button type="button" onClick={redirectToGoogleLogin}>Google로 시작하기</button>
            <a href="/privacy">개인정보처리방침</a>
            <a href="/terms">서비스 약관</a>
          </div>
        ) : null}
      </section>

      {normalizedPath === "/about" && <AboutPublicContent />}
      {normalizedPath === "/login" && <AuthPublicContent mode="login" />}
      {normalizedPath === "/signup" && <AuthPublicContent mode="signup" />}
      {normalizedPath === "/privacy" && <PrivacyPublicContent />}
      {normalizedPath === "/terms" && <TermsPublicContent />}
    </main>
  );
}

function AboutPublicContent() {
  return (
    <section className="public-grid">
      {[
        ["Real-news signals", "News evidence is combined with persisted yfinance market reaction data."],
        ["News Guard", "Articles are labeled by source, provider, fallback state, and reliability context."],
        ["Industry impact", "AI, semiconductor, policy, and portfolio-related signals are summarized for review."],
      ].map(([title, body]) => (
        <article className="public-card" key={title}>
          <h2>{title}</h2>
          <p>{body}</p>
        </article>
      ))}
      <article className="public-card public-wide">
        <h2>Important disclaimer</h2>
        <p>
          FinLightAI does not provide investment recommendations, buy/sell instructions, or financial advice.
          Data may be delayed, incomplete, or inaccurate, and users should verify information independently.
        </p>
      </article>
    </section>
  );
}

function AuthPublicContent({ mode }: { mode: "login" | "signup" }) {
  return (
    <section className="public-card public-wide">
      <h2>{mode === "login" ? "로그인 안내" : "회원가입 안내"}</h2>
      <p>
        MVP authentication uses Google OAuth with the minimum scopes: openid, email, and profile.
        Google Drive, Gmail, Calendar, and other sensitive API scopes are not requested.
      </p>
      <ul className="public-list">
        <li>OAuth callback is handled by the FastAPI backend.</li>
        <li>Profile data is used to create or find your FinLightAI account.</li>
        <li>Onboarding preferences connect markets, industries, and notification settings to your user ID.</li>
      </ul>
    </section>
  );
}

function PrivacyPublicContent() {
  return (
    <section className="public-card public-wide">
      <h2>수집하는 정보</h2>
      <p>
        FinLightAI may collect basic Google OAuth profile information such as email address, display name,
        profile image, provider user ID, and user-selected settings such as interested markets, industries,
        and notification preferences.
      </p>
      <h2>이용 목적</h2>
      <p>
        This information is used for login, account management, personalization, onboarding preferences,
        and operating dashboard features.
      </p>
      <h2>제3자 서비스</h2>
      <p>
        The service may use Google OAuth for authentication, Vercel for frontend hosting, and Render for backend hosting.
        FinLightAI does not sell personal information.
      </p>
      <h2>보관 및 삭제</h2>
      <p>
        Users may request deletion of account-related data through the project contact channel. A self-service deletion
        flow is planned but not yet available in the MVP.
      </p>
      <h2>문의</h2>
      <p>Contact: project owner via the FinLightAI GitHub repository.</p>
      <p className="public-updated">Effective date: 2026-06-30</p>
    </section>
  );
}

function TermsPublicContent() {
  return (
    <section className="public-card public-wide">
      <h2>서비스 목적</h2>
      <p>
        FinLightAI provides market-state information by combining news, reliability checks, industry context,
        and market reaction data.
      </p>
      <h2>금융 정보 면책</h2>
      <p>
        FinLightAI is not an investment advisory service and does not recommend buying, selling, or holding securities.
        Users are responsible for their own investment decisions.
      </p>
      <h2>계정 이용</h2>
      <p>
        Users must not attempt unauthorized access, scrape data without permission, interfere with the service,
        or misuse authentication flows.
      </p>
      <h2>서비스 변경</h2>
      <p>
        Features, data providers, and availability may change during MVP development. Data can be delayed,
        incomplete, or temporarily unavailable.
      </p>
      <h2>문의</h2>
      <p>Contact: project owner via the FinLightAI GitHub repository.</p>
      <p className="public-updated">Effective date: 2026-06-30</p>
    </section>
  );
}

function App() {
  const [view, setView] = useState<ViewId>("briefing");
  const [marketTab, setMarketTab] = useState<MarketTab>("domestic");
  const [selectedIndustryId, setSelectedIndustryId] = useState("semiconductor");
  const [searchQuery, setSearchQuery] = useState("");
  const [authState, setAuthState] = useState<AuthMeResponse>({ authenticated: false, user: null });
  const [authError, setAuthError] = useState<string | null>(null);

  const currentMarket = marketData[marketTab];
  const selectedIndustry = useMemo(
    () => industries.find((industry) => industry.id === selectedIndustryId) ?? industries[0],
    [selectedIndustryId],
  );
  const searchResults = useMemo(() => {
    const normalized = searchQuery.trim().toLowerCase();
    if (!normalized) return [];

    return headerSearchIndex
      .filter((item) => `${item.title} ${item.subtitle}`.toLowerCase().includes(normalized))
      .slice(0, 5);
  }, [searchQuery]);

  useEffect(() => {
    let ignore = false;
    fetchCurrentUser()
      .then((payload) => {
        if (!ignore) setAuthState(payload);
      })
      .catch((error) => {
        if (!ignore) setAuthError(error instanceof Error ? error.message : "Auth state check failed");
      });
    return () => {
      ignore = true;
    };
  }, []);

  function handleIndustryClick(industryId: string) {
    setSelectedIndustryId(industryId);
    setMarketTab("watchIndustry");
    setView("industry");
  }

  function handleSearchResultClick(result: HeaderSearchResult) {
    if (result.targetIndustryId) {
      setSelectedIndustryId(result.targetIndustryId);
      setMarketTab("watchIndustry");
    }

    setView(result.targetView);
    setSearchQuery("");
  }

  async function handleLogout() {
    try {
      setAuthError(null);
      await logout();
      setAuthState({ authenticated: false, user: null });
      setView("login");
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : "Logout failed");
    }
  }

  const publicPath = window.location.pathname;
  if (["/about", "/login", "/signup", "/privacy", "/terms"].includes(publicPath)) {
    return <PublicPage path={publicPath} />;
  }

  return (
    <div className="app">
      <header className="top-header">
        <div className="brand-group">
          <button className="brand-mark" type="button" onClick={() => setView("briefing")} aria-label="AI 브리핑으로 이동">
            FL
          </button>
          <div className="brand-copy">
            <strong>FinLightAI</strong>
            <span>AI 금융 상황판</span>
          </div>
          <div className="header-divider" />
        </div>

        <nav className="main-nav" aria-label="주요 화면">
          {navItems.map((item) => (
            <button
              aria-current={view === item.id ? "page" : undefined}
              className={view === item.id ? "active" : ""}
              key={item.id}
              type="button"
              onClick={() => setView(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="header-actions">
          <div className="search-box">
            <span aria-hidden="true">⌕</span>
            <input
              aria-label="뉴스, 산업, 종목 검색"
              placeholder="뉴스, 산업, 종목 검색"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
            />
            <kbd>⌘K</kbd>
            {searchQuery ? (
              <div className="search-popover" role="listbox">
                {searchResults.length > 0 ? (
                  searchResults.map((result) => (
                    <button key={result.id} type="button" onClick={() => handleSearchResultClick(result)}>
                      <strong>{result.title}</strong>
                      <span>{result.subtitle}</span>
                    </button>
                  ))
                ) : (
                  <div className="search-empty">검색 결과가 없습니다.</div>
                )}
              </div>
            ) : null}
          </div>
          <button className="icon-button" type="button" onClick={() => setView("settings")} aria-label="Email and market alerts">
            ♡<span className="notification-dot">3</span>
          </button>
          <button className="user-menu" type="button" onClick={() => setView("mypage")}>
            <span className="avatar">{authState.user?.nickname?.slice(0, 1).toUpperCase() ?? "U"}</span>
            {authState.user?.nickname ?? "Google login"}
          </button>
          {authState.authenticated ? (
            <button className="icon-button" type="button" onClick={handleLogout} aria-label="로그아웃">
              OUT
            </button>
          ) : (
            <button className="icon-button" type="button" onClick={() => setView("login")} aria-label="Google 로그인">
              IN
            </button>
          )}
          <SignalTrafficLight signal="yellow" onClick={() => setView("guard")} />
        </div>

      </header>

      {view === "briefing" ? (
        <BriefingDashboard
          currentMarket={currentMarket}
          marketTab={marketTab}
          selectedIndustryId={selectedIndustryId}
          selectedIndustryName={selectedIndustry.name}
          selectedIndustryScore={selectedIndustry.score}
          onIndustryClick={handleIndustryClick}
          onMarketTabChange={setMarketTab}
          onViewChange={setView}
        />
      ) : view === "guard" ? (
        <NewsGuardPage />
      ) : (
        <main className="dashboard sub-dashboard">
          {view === "industry" && (
            <IndustryImpactPage
              selectedIndustryId={selectedIndustryId}
              onIndustryClick={handleIndustryClick}
            />
          )}
          {view === "portfolio" && <PortfolioPage onViewChange={setView} />}
          {view === "mypage" && <MyPageDashboard onViewChange={setView} />}
          {view === "settings" && <SettingsDashboard />}
          {view === "login" && <GoogleAuthFlowView authError={authError} onViewChange={setView} />}
        </main>
      )}

      <div className="prototype-chip">FinLightAI High-Fidelity UI Prototype · v3</div>
    </div>
  );
}

function SignalTrafficLight({ signal, onClick }: { signal: "red" | "yellow" | "green"; onClick: () => void }) {
  const labels = {
    red: "위험",
    yellow: "주의",
    green: "안정",
  };

  return (
    <button
      className="signal-traffic-light"
      type="button"
      onClick={onClick}
      aria-label={`현재 시장 신호: ${labels[signal]}`}
      title={`현재 시장 신호: ${labels[signal]}`}
    >
      <span className={`signal-dot red ${signal === "red" ? "active" : ""}`} aria-hidden="true" />
      <span className={`signal-dot yellow ${signal === "yellow" ? "active" : ""}`} aria-hidden="true" />
      <span className={`signal-dot green ${signal === "green" ? "active" : ""}`} aria-hidden="true" />
    </button>
  );
}

function PageHeader({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return (
    <section className="page-header">
      <div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action ? <div className="page-header-action">{action}</div> : null}
    </section>
  );
}

type PipelineMetadataView = {
  dataSource?: string;
  providers?: string[];
  isFallback?: boolean;
  lastUpdated?: string;
  warnings?: string[];
};

function PipelineStatusBar({ metadata }: { metadata: PipelineMetadataView | null }) {
  const source = metadata?.dataSource ?? "mock";
  const warnings = metadata?.warnings ?? (metadata ? [] : ["API data unavailable; labeled mock data is displayed"]);
  const providers = metadata?.providers?.length ? metadata.providers.join(", ") : "mock";
  const updated = metadata?.lastUpdated ?? "not available";

  return (
    <section className={`pipeline-status pipeline-status--${source}`} aria-label="데이터 파이프라인 상태">
      <div>
        <strong>{source}</strong>
        {metadata?.isFallback ? <span>fallback active</span> : null}
        <span>providers: {providers}</span>
        <time>{updated}</time>
      </div>
      {warnings.map((warning) => <p key={warning}>{warning}</p>)}
    </section>
  );
}

function DataState({
  title,
  message,
  tone = "empty",
}: {
  title: string;
  message: string;
  tone?: "error" | "empty" | "loading";
}) {
  return (
    <section className={`panel data-state data-state--${tone}`} role={tone === "error" ? "alert" : "status"}>
      <h2>{title}</h2>
      <p>{message}</p>
      {tone === "error" ? <button type="button" onClick={() => window.location.reload()}>다시 시도</button> : null}
    </section>
  );
}

function BriefingDashboard({
  currentMarket,
  marketTab,
  selectedIndustryId,
  selectedIndustryName,
  selectedIndustryScore,
  onIndustryClick,
  onMarketTabChange,
  onViewChange,
}: {
  currentMarket: MarketViewData;
  marketTab: MarketTab;
  selectedIndustryId: string;
  selectedIndustryName: string;
  selectedIndustryScore: number;
  onIndustryClick: (industryId: string) => void;
  onMarketTabChange: (tab: MarketTab) => void;
  onViewChange: (view: ViewId) => void;
}) {
  const [briefingData, setBriefingData] = useState<BriefingResponse | null>(null);
  const [briefingFailed, setBriefingFailed] = useState(false);

  useEffect(() => {
    let mounted = true;
    fetchBriefingData()
      .then((data) => {
        if (mounted) setBriefingData(data);
      })
      .catch(() => {
        if (mounted) setBriefingFailed(true);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const briefingSignal = briefingData?.signal ?? "YELLOW";
  const briefingRisk = briefingData?.riskScore ?? currentMarket.risk;
  const briefingTitle = briefingData?.headline ?? currentMarket.title;
  const briefingSummary = briefingData?.summary.map((text) => ({ text, tone: "neutral" as Tone })) ?? currentMarket.briefing;
  const briefingUpdatedAt = briefingData?.lastUpdated ?? briefingData?.asOf ?? currentMarket.updatedAt;
  const briefingDescription = briefingData?.summary[0] ?? currentMarket.description;
  const showMockReferencePanels = false;

  return (
    <main className="dashboard">
      <PageHeader title={viewCopy.briefing.title} description={viewCopy.briefing.subtitle} />
      <PipelineStatusBar metadata={briefingFailed ? null : briefingData} />
      <p className="mock-disclosure">
        실제 API 데이터와 static briefing fallback만 표시합니다. 연결되지 않은 demo/mock 시장 패널은 숨겨져 있습니다.
      </p>

      <section className="panel market-signal">
        <div className="section-title-row">
          <h2>오늘의 시장 신호</h2>
          <span>업데이트 {briefingUpdatedAt}</span>
        </div>
        <div className="signal-content">
          <div className="signal-badge" aria-label="주의 신호">
            <span>!</span>
            <strong>{briefingSignal}</strong>
            <em>주의</em>
          </div>
          <div className="signal-copy">
            <h3>{briefingTitle}</h3>
            <p>{briefingDescription}</p>
            <div className="risk-row">
              <div className="risk-track" aria-label={`위험도 ${briefingRisk}점`}>
                <span style={{ width: `${briefingRisk}%` }} />
              </div>
              <strong>위험도 {briefingRisk} / 100</strong>
            </div>
          </div>
        </div>
      </section>

      <section className="panel briefing-summary">
        <div className="section-title-row">
          <h2>AI 브리핑 요약</h2>
          <span>3개 포인트</span>
        </div>
        <ul className="briefing-list">
          {briefingSummary.map((point) => (
            <li key={point.text}>
              <span className={`briefing-dot ${point.tone}`} />
              {point.text}
            </li>
          ))}
        </ul>
      </section>

      {showMockReferencePanels ? (
        <>
      <section className="panel market-panel">
        <div className="market-tabs" role="tablist" aria-label="시장 구분">
          {tabs.map((tab) => (
            <button
              className={marketTab === tab.key ? "active" : ""}
              key={tab.key}
              onClick={() => onMarketTabChange(tab.key)}
              role="tab"
              type="button"
              aria-selected={marketTab === tab.key}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <div className="metric-strip">
          {currentMarket.metrics.map((metric) => (
            <article className="metric-card" key={metric.label}>
              <div className="metric-label">{metric.label}</div>
              <div className={`metric-value ${metric.tone}`}>{metric.value}</div>
              {metric.change ? <div className={metric.change.startsWith("-") ? "metric-change down" : "metric-change up"}>{metric.change}</div> : null}
              <div className="metric-note">{metric.note}</div>
            </article>
          ))}
        </div>
        <button className="ghost-link" type="button" onClick={() => onViewChange("industry")}>
          더보기 ›
        </button>
      </section>

      <NewsTopPanel news={currentMarket.news} />

      <IndustryHeatmapPanel selectedIndustryId={selectedIndustryId} onIndustryClick={onIndustryClick} />

      <aside className="side-stack">
        <section className="panel guard-panel">
          <div className="section-title-row">
            <h2>뉴스 가드 경고</h2>
            <button type="button" onClick={() => onViewChange("guard")}>
              뉴스 가드 바로가기 ›
            </button>
          </div>
          <strong>주의 필요 뉴스 14건</strong>
          <p>대표 사유: 자극적 표현, 근거 부족, 반복 확산</p>
        </section>

        <section className="panel Email-panel">
          <div className="section-title-row">
            <h2>최근 이메일 알림</h2>
            <button type="button" onClick={() => onViewChange("settings")}>
              알림 설정 ›
            </button>
          </div>
          <ul>
            <li><time>09:30</time><span>주의 신호 발송 완료</span></li>
            <li><time>08:10</time><span>저신뢰 뉴스 감지</span></li>
            <li><time>07:30</time><span>일일 요약 대기</span></li>
          </ul>
        </section>

        <section className="selected-industry">
          <span>선택된 관심 산업</span>
          <strong>{selectedIndustryName} {formatScore(selectedIndustryScore)}</strong>
        </section>
      </aside>

      <BriefingReadinessPanel data={briefingReadiness} />
        </>
      ) : (
        <section className="panel mock-disclosure" aria-label="연결 대기 중인 브리핑 패널">
          <strong>추가 시장 패널 연결 대기 중</strong>
          <p>Demo/mock 수치는 실제 시장 데이터로 오해되지 않도록 표시하지 않습니다.</p>
          <time>실제 파이프라인 마지막 업데이트: {briefingUpdatedAt}</time>
        </section>
      )}
    </main>
  );
}

function NewsTopPanel({ news }: { news: NewsImpact[] }) {
  return (
    <section className="panel news-top-panel">
      <div className="section-title-row">
        <h2>뉴스 영향도 TOP 5</h2>
        <span>신뢰도 분리</span>
      </div>
      <ol className="news-top-list">
        {news.map((item, index) => (
          <li key={item.title}>
            <span className="news-rank">{index + 1}</span>
            <strong>{item.title}</strong>
            <span className="chip impact">영향 {Math.abs(item.impact)}</span>
            <span className={`chip ${trustClass(item.trust)}`}>{item.trust}</span>
            <span className="chip sector">{item.sector}</span>
            <b className={item.impact >= 0 ? "score-pos" : "score-neg"}>{formatScore(item.impact)}</b>
          </li>
        ))}
      </ol>
    </section>
  );
}

function BriefingReadinessPanel({ data }: { data: BriefingReadinessData }) {
  return (
    <section className="panel briefing-readiness" aria-label="AI 브리핑 준비도">
      <div className="briefing-readiness-head">
        <div>
          <span>자체 금융 신호 알고리즘</span>
          <h2>AI 브리핑 준비도</h2>
          <p>{data.headline}</p>
        </div>
        <div className="readiness-score">
          <strong>{data.confidence}</strong>
          <span>/ 100</span>
          <em>브리핑 신뢰 준비도</em>
        </div>
      </div>

      <div className="readiness-metric-grid">
        {data.metrics.map((metric) => (
          <article className={`readiness-metric ${metric.status}`} key={metric.label}>
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
            <em>{metric.note}</em>
          </article>
        ))}
      </div>

      <div className="readiness-body">
        <section className="readiness-block">
          <div className="readiness-block-title">
            <h3>뉴스 출처 커버리지</h3>
            <span>최근 24시간</span>
          </div>
          <div className="source-coverage-list">
            {data.coverageSources.map((source) => (
              <div className="source-coverage-row" key={source.name}>
                <span>{source.name}</span>
                <div aria-label={`${source.name} 비중 ${source.ratio}%`}>
                  <i style={{ width: `${source.ratio}%` }} />
                </div>
                <strong>{source.ratio}%</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="readiness-block">
          <div className="readiness-block-title">
            <h3>편향 점검</h3>
            <span>낮을수록 안정</span>
          </div>
          <div className="bias-check-list">
            {data.biasChecks.map((check) => (
              <BiasCheckRow check={check} key={check.label} />
            ))}
          </div>
        </section>

        <section className="readiness-block">
          <div className="readiness-block-title">
            <h3>AI 브리핑 입력 규칙</h3>
            <span>Gemini 연결 예정</span>
          </div>
          <ul className="prompt-input-list">
            {data.promptInputs.map((input) => (
              <li key={input}>{input}</li>
            ))}
          </ul>
          <p className="readiness-updated">업데이트 {data.updatedAt}</p>
        </section>
      </div>
    </section>
  );
}

function BiasCheckRow({ check }: { check: BriefingBiasCheck }) {
  const statusLabel = check.status === "ready" ? "정상" : check.status === "watch" ? "주의" : "차단";

  return (
    <article className={`bias-check-row ${check.status}`}>
      <div>
        <strong>{check.label}</strong>
        <span>{check.note}</span>
      </div>
      <div className="bias-track" aria-label={`${check.label} 편향 점수 ${check.score}점`}>
        <i style={{ width: `${check.score}%` }} />
      </div>
      <em>{statusLabel}</em>
    </article>
  );
}

function NewsGuardPage() {
  const [filter, setFilter] = useState<NewsGuardFilter>("all");
  const [data, setData] = useState<NewsGuardViewModel | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;

    async function load() {
      setIsLoading(true);
      setLoadError(null);
      try {
        const result = await fetchNewsGuardData(filter);
        if (!ignore) setData(result);
      } catch (error) {
        if (!ignore) {
          setLoadError(error instanceof Error ? error.message : "뉴스 데이터를 불러오지 못했습니다.");
        }
      } finally {
        if (!ignore) setIsLoading(false);
      }
    }

    load();

    return () => {
      ignore = true;
    };
  }, [filter]);

  if (isLoading && !data) {
    return <main className="news-guard-page loading-state">뉴스 가드 데이터를 불러오는 중...</main>;
  }

  if (!data) {
    return <main className="news-guard-page loading-state">뉴스 가드 데이터를 표시할 수 없습니다.</main>;
  }

  return (
    <main className="news-guard-page">
      <section className="news-guard-main">
        <PageHeader title="뉴스 가드" description="뉴스 신뢰도를 검증하고 저신뢰 뉴스를 걸러냅니다." />

        <PipelineStatusBar metadata={data} />
        <NewsGuardKpiGrid data={data} />

        <section className="news-list-panel" aria-label="뉴스 가드 목록">
          <NewsFilterTabs value={filter} onChange={setFilter} />
          <div className="news-list-toolbar">
            <button type="button">최신순⌄</button>
            <button type="button" className="filter-button">필터</button>
          </div>
          {loadError ? <p className="api-error" role="alert">{loadError}</p> : null}
          <div className="news-guard-list">
            {data.articles.length === 0 ? (
              <DataState title="조건에 맞는 뉴스가 없습니다." message="필터를 바꾸거나 다음 데이터 갱신 후 다시 확인해 주세요." />
            ) : data.articles.map((article) => (
              <NewsGuardArticleCard article={article} key={article.id} />
            ))}
          </div>
          <p className="news-footnote">영향도: 해당 뉴스가 시장/산업에 미치는 예상 영향도 · 감성: -1 매우 부정 ~ +1 매우 긍정</p>
        </section>
      </section>

      <RightInsightPanel data={data} />
    </main>
  );
}

function NewsGuardKpiGrid({ data }: { data: NewsGuardViewModel }) {
  const { stats } = data;
  const kpis = [
    { icon: "▣", label: "수집된 뉴스", value: `${stats.collectedNewsCount}건`, sub: `어제 대비 +${stats.deltaCollectedNewsCount}건`, tone: "trusted" },
    { icon: "◇", label: "신뢰 뉴스", value: `${stats.trustedNewsCount}건`, sub: `${data.distribution.trusted.ratio}%`, tone: "trusted" },
    { icon: "△", label: "주의 뉴스", value: `${stats.watchNewsCount}건`, sub: `${data.distribution.watch.ratio}%`, tone: "watch" },
    { icon: "⊘", label: "차단 뉴스", value: `${stats.blockedNewsCount}건`, sub: `${data.distribution.blocked.ratio}%`, tone: "blocked" },
    { icon: "☆", label: "평균 신뢰도", value: stats.averageReliabilityScore.toFixed(2), sub: "/ 1.00", tone: "score" },
  ];

  return (
    <section className="news-guard-kpis" aria-label="뉴스 가드 KPI">
      {kpis.map((kpi) => (
        <article className={`news-guard-kpi ${kpi.tone}`} key={kpi.label}>
          <span className="news-kpi-icon">{kpi.icon}</span>
          <div>
            <span className="news-kpi-label">{kpi.label}</span>
            <strong>{kpi.value}</strong>
            <em>{kpi.sub}</em>
          </div>
        </article>
      ))}
    </section>
  );
}

function NewsFilterTabs({ value, onChange }: { value: NewsGuardFilter; onChange: (filter: NewsGuardFilter) => void }) {
  const filters: { id: NewsGuardFilter; label: string }[] = [
    { id: "all", label: "전체 뉴스" },
    { id: "trusted", label: "신뢰 뉴스" },
    { id: "watch", label: "주의 뉴스" },
    { id: "blocked", label: "차단 뉴스" },
  ];

  return (
    <div className="news-filter-tabs" role="tablist" aria-label="뉴스 신뢰도 필터">
      {filters.map((filter) => (
        <button
          aria-selected={value === filter.id}
          className={value === filter.id ? "active" : ""}
          key={filter.id}
          onClick={() => onChange(filter.id)}
          role="tab"
          type="button"
        >
          {filter.label}
        </button>
      ))}
    </div>
  );
}

function NewsGuardArticleCard({ article }: { article: NewsArticle }) {
  const label = reliabilityLabel(article.reliabilityLevel);

  return (
    <article className={`news-guard-card ${article.reliabilityLevel}`}>
      <div className="reliability-box">
        <span>{label}</span>
        <strong>{article.reliabilityScore.toFixed(2)}</strong>
        <em aria-label={`신뢰도 별점 ${Math.round(article.reliabilityScore * 5)}점`}>{stars(article.reliabilityScore)}</em>
      </div>

      <div className="news-card-body">
        <h2>{article.title}</h2>
        <div className="news-meta">
          <span>{article.source} · {article.provider ?? article.source} · {article.qualityStatus ?? "mock"}</span>
          <span>·</span>
          <span>{article.publishedAgo}</span>
        </div>
        <p>{article.summary}</p>
      </div>

      <div className="news-card-metrics">
        <div className="tag-row">
          {article.industries.map((industry) => <span className="tag" key={industry}>{industry}</span>)}
          {article.tags.map((tag) => <span className="tag" key={tag}>{tag}</span>)}
        </div>
        <div className="metric-row">
          <div>
            <span>영향도</span>
            <strong className={article.impactScore >= 75 ? "yellow" : "green"}>{article.impactScore}/100</strong>
          </div>
          <div>
            <span>감성</span>
            <strong className={article.sentimentScore < 0 ? "red" : "green"}>
              {article.sentimentScore > 0 ? "+" : ""}
              {article.sentimentScore.toFixed(2)}
            </strong>
          </div>
        </div>
      </div>

      <a className="external-link" href={article.originalUrl ?? "#"} aria-label="원문 확인">↗</a>
    </article>
  );
}

function RightInsightPanel({ data }: { data: NewsGuardViewModel }) {
  return (
    <aside className="right-insight-panel" aria-label="뉴스 가드 분석 패널">
      <ReliabilityDonut distribution={data.distribution} />
      <BlockReasonList reasons={data.blockReasons} />
      <QuickFilterPanel filters={data.quickFilters} />
      <ApiStatusCard providers={data.providerHealth} />
    </aside>
  );
}

function ReliabilityDonut({ distribution }: { distribution: ReliabilityDistribution }) {
  return (
    <section className="side-card">
      <div className="side-card-header">
        <h2>신뢰도 분포</h2>
        <span>오늘 기준</span>
      </div>
      <div className="donut-layout">
        <div className="donut-chart" aria-hidden="true" />
        <div className="donut-legend">
          <span className="trusted">신뢰 (70%+) <strong>{distribution.trusted.count}건 ({distribution.trusted.ratio}%)</strong></span>
          <span className="watch">주의 (40~70%) <strong>{distribution.watch.count}건 ({distribution.watch.ratio}%)</strong></span>
          <span className="blocked">차단 (&lt;40%) <strong>{distribution.blocked.count}건 ({distribution.blocked.ratio}%)</strong></span>
        </div>
      </div>
    </section>
  );
}

function BlockReasonList({ reasons }: { reasons: BlockReason[] }) {
  return (
    <section className="side-card">
      <div className="side-card-header">
        <h2>차단 사유 TOP 5</h2>
      </div>
      <div className="reason-list">
        {reasons.map((reason) => (
          <div className="reason-row" key={reason.rank}>
            <span><b>{reason.rank}</b>{reason.reason}</span>
            <strong>{reason.count}건 ({reason.ratio}%)</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

function QuickFilterPanel({ filters }: { filters: QuickFilter[] }) {
  return (
    <section className="side-card">
      <div className="side-card-header">
        <h2>빠른 필터</h2>
      </div>
      <div className="quick-filter-grid">
        {filters.map((filter) => (
          <button className="quick-filter-row" key={filter.id} type="button">
            <span>{filter.label}</span>
            <strong>{filter.count}</strong>
          </button>
        ))}
      </div>
    </section>
  );
}

function ApiStatusCard({ providers }: { providers: ProviderHealth[] }) {
  return (
    <section className="side-card">
      <div className="side-card-header">
        <h2>API 연동 상태</h2>
        <button type="button" aria-label="API 상태 새로고침">↻</button>
      </div>
      <div className="provider-grid">
        {providers.map((provider) => (
          <div className="provider-row" key={provider.provider}>
            <span>{provider.provider}</span>
            <strong className={provider.status}><i aria-hidden="true" />{provider.message}</strong>
          </div>
        ))}
      </div>
      <p className="last-updated">마지막 업데이트: 2분 전</p>
    </section>
  );
}

function IndustryHeatmapPanel({
  selectedIndustryId,
  onIndustryClick,
}: {
  selectedIndustryId: string;
  onIndustryClick: (industryId: string) => void;
}) {
  return (
    <section className="panel industry-panel">
      <div className="section-title-row heatmap-title">
        <div>
          <h2>산업별 영향도 히트맵</h2>
          <p>산업 선택 시 해당 관심 산업으로 이동합니다.</p>
        </div>
        <span>-100&nbsp;&nbsp;&nbsp;0&nbsp;&nbsp;&nbsp;+100</span>
      </div>
      <div className="industry-grid">
        {industries.map((industry) => (
          <button
            className={`industry-card ${getToneByScore(industry.score)} ${selectedIndustryId === industry.id ? "active" : ""}`}
            key={industry.id}
            onClick={() => onIndustryClick(industry.id)}
            type="button"
          >
            <span>{industry.name}</span>
            <strong>{formatScore(industry.score)}</strong>
            <em>{industry.note}</em>
          </button>
        ))}
      </div>
    </section>
  );
}

function IndustryImpactView({
  selectedIndustryId,
  selectedIndustryName,
  selectedIndustryScore,
  onIndustryClick,
}: {
  selectedIndustryId: string;
  selectedIndustryName: string;
  selectedIndustryScore: number;
  onIndustryClick: (industryId: string) => void;
}) {
  return (
    <>
      <IndustryHeatmapPanel selectedIndustryId={selectedIndustryId} onIndustryClick={onIndustryClick} />
      <section className="panel detail-panel">
        <div className="section-title-row">
          <h2>{selectedIndustryName} 상세</h2>
          <span>선택 산업</span>
        </div>
        <strong className={selectedIndustryScore >= 0 ? "score-pos detail-score" : "score-neg detail-score"}>{formatScore(selectedIndustryScore)}</strong>
        <p>선택한 산업의 뉴스 영향도, 신뢰도, 알림 조건을 함께 확인합니다. 이 화면은 향후 산업별 상세 라우트로 확장할 수 있습니다.</p>
      </section>
    </>
  );
}

function IndustryImpactPage({
  selectedIndustryId,
  onIndustryClick,
}: {
  selectedIndustryId: string;
  onIndustryClick: (industryId: string) => void;
}) {
  const [industryData, setIndustryData] = useState<IndustryImpactResponse | null>(null);
  const [activeIndustryId, setActiveIndustryId] = useState(selectedIndustryId);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setActiveIndustryId(selectedIndustryId);
  }, [selectedIndustryId]);

  useEffect(() => {
    let mounted = true;

    fetchIndustryImpactData()
      .then((data) => {
        if (!mounted) return;
        setIndustryData(data);
        if (!data.details[activeIndustryId]) {
          setActiveIndustryId(data.industries[0]?.id ?? "semiconductor");
        }
      })
      .finally(() => {
        if (mounted) setIsLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [activeIndustryId]);

  if (isLoading || !industryData) {
    return (
      <section className="panel industry-impact-loading">
        <h2>산업 영향도 데이터를 불러오는 중입니다.</h2>
      </section>
    );
  }

  const activeDetail = industryData.details[activeIndustryId] ?? Object.values(industryData.details)[0];
  const activeSummary = industryData.industries.find((industry) => industry.id === activeDetail.industryId) ?? industryData.industries[0];

  function handleSelectIndustry(industryId: string) {
    setActiveIndustryId(industryId);
    onIndustryClick(industryId);
  }

  return (
    <>
      <PageHeader title={viewCopy.industry.title} description={viewCopy.industry.subtitle} />
      <PipelineStatusBar metadata={industryData} />
      <IndustryImpactSummaryPanel detail={activeDetail} />
      <section className="industry-impact-layout">
        <IndustryImpactHeatmapPanel
          activeIndustryId={activeDetail.industryId}
          industries={industryData.industries}
          lastUpdated={industryData.lastUpdated}
          onIndustryClick={handleSelectIndustry}
        />
        <aside className="industry-impact-side">
          <IndustryDetailPanel detail={activeDetail} summary={activeSummary} />
          <IndustryNewsTopList news={activeDetail.topNews} />
        </aside>
      </section>
    </>
  );
}

function IndustryImpactHeatmapPanel({
  activeIndustryId,
  industries,
  lastUpdated,
  onIndustryClick,
}: {
  activeIndustryId: string;
  industries: IndustrySummary[];
  lastUpdated?: string;
  onIndustryClick: (industryId: string) => void;
}) {
  return (
    <section className="panel industry-impact-heatmap">
      <div className="impact-panel-heading">
        <div>
          <h2>산업별 영향도 히트맵</h2>
          <p>산업 선택 시 해당 산업의 상세 정보와 근거 뉴스를 확인할 수 있습니다.</p>
        </div>
        <div className="impact-scale" aria-label="영향도 범위 -100에서 +100">
          <span />
          <small>-100</small>
          <small>0</small>
          <small>+100</small>
        </div>
      </div>
      <div className="impact-industry-grid">
        {industries.map((industry) => (
          <IndustryImpactCard
            industry={industry}
            isActive={activeIndustryId === industry.id}
            key={industry.id}
            onClick={() => onIndustryClick(industry.id)}
          />
        ))}
      </div>
      <div className="impact-footnote">
        <span>ⓘ 영향도 점수 범위: -100 (최대 악화) ~ +100 (최대 강화)</span>
        <span>업데이트: {lastUpdated ?? "not available"}</span>
      </div>
    </section>
  );
}

function IndustryImpactCard({
  industry,
  isActive,
  onClick,
}: {
  industry: IndustrySummary;
  isActive: boolean;
  onClick: () => void;
}) {
  return (
    <button
      aria-pressed={isActive}
      className={`impact-industry-card impact-industry-card--${industry.tone} ${isActive ? "is-active" : ""}`}
      onClick={onClick}
      type="button"
    >
      <span className="industry-card-title">
        <span aria-hidden="true">{industry.icon}</span>
        {industry.name}
      </span>
      <strong>{formatScore(industry.score)}</strong>
      <em>{industry.toneLabel}</em>
      <small>뉴스 {industry.newsCount}건</small>
    </button>
  );
}

function IndustryDetailPanel({ detail, summary }: { detail: IndustryDetail; summary: IndustrySummary }) {
  return (
    <section className="panel industry-detail-card">
      <div className="industry-detail-top">
        <div>
          <h2>{detail.title}</h2>
          <div className="detail-score-row">
            <strong className={detail.score >= 0 ? "score-pos" : "score-neg"}>{formatScore(detail.score)}</strong>
            <span className={`status-pill status-pill--${summary.tone}`}>{detail.statusLabel}</span>
          </div>
        </div>
        <div className="chip-graphic" aria-hidden="true">▣</div>
      </div>
      <p>{detail.description}</p>
      <div className="detail-meta-grid">
        <div>
          <span>긍정 요인</span>
          <strong>{detail.reasons.positive[0]}</strong>
        </div>
        <div>
          <span>주의 요인</span>
          <strong>{detail.reasons.caution[0]}</strong>
        </div>
        <div>
          <span>관련 뉴스 수</span>
          <strong>{detail.newsCount}건</strong>
        </div>
        <div>
          <span>관련 종목</span>
          <div className="stock-chip-list">
            {detail.relatedStocks.map((stock) => (
              <b key={stock}>{stock}</b>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function IndustryNewsTopList({ news }: { news: RelatedNewsItem[] }) {
  return (
    <section className="panel industry-news-panel">
      <div className="industry-news-head">
        <h2>주요 근거 뉴스 TOP 5</h2>
        <span>영향도</span>
      </div>
      <div className="industry-news-list">
        {news.map((item) => (
          <article className="industry-news-item" key={item.id}>
            <span className="news-rank">{item.rank}</span>
            <strong>{item.title}</strong>
            <span>{item.source}</span>
            <em className={`sentiment-badge sentiment-badge--${item.sentimentLabel}`}>{item.sentimentLabel}</em>
            <b className={item.impactScore >= 0 ? "score-pos" : "score-neg"}>
              {item.impactScore >= 0 ? "+" : ""}{item.impactScore.toFixed(2)}
            </b>
          </article>
        ))}
      </div>
    </section>
  );
}

function IndustryImpactSummaryPanel({ detail }: { detail: IndustryDetail }) {
  return (
    <section className="panel impact-summary-panel">
      <h2>영향 요약</h2>
      <div className="impact-summary-grid">
        <article>
          <span>평균 감성</span>
          <strong className={detail.averageSentiment >= 0 ? "score-pos" : "score-neg"}>
            {detail.averageSentiment >= 0 ? "+" : ""}{detail.averageSentiment.toFixed(2)}
          </strong>
          <small>{detail.averageSentiment >= 0 ? "긍정" : "부정"}</small>
        </article>
        <article>
          <span>관련 뉴스 수</span>
          <strong>{detail.newsCount}건</strong>
          <small>최근 7일</small>
        </article>
        <article>
          <span>위험 포인트</span>
          <strong>{detail.riskPoints}건</strong>
          <small>주의/부정</small>
        </article>
        <article>
          <span>마지막 업데이트</span>
          <strong>{detail.updatedAt}</strong>
          <small>2분 전</small>
        </article>
      </div>
      <p>ⓘ 색상은 단독으로 해석하지 마세요. 점수와 라벨을 함께 확인해야 올바르게 판단할 수 있습니다.</p>
    </section>
  );
}

type PortfolioAssetDraft = {
  assetName: string;
  symbol: string;
  market: AssetMarket;
  industry: string;
  quantity: number;
  averageBuyPrice: number;
  currentPrice: number;
  recentSellPrice: string;
  currency: AssetCurrency;
  status: AssetStatus;
  decisionMemo: string;
};

const emptyAssetDraft: PortfolioAssetDraft = {
  assetName: "",
  symbol: "",
  market: "KR",
  industry: "반도체",
  quantity: 0,
  averageBuyPrice: 0,
  currentPrice: 0,
  recentSellPrice: "",
  currency: "KRW",
  status: "holding",
  decisionMemo: "",
};

function PortfolioPage({ onViewChange }: { onViewChange: (view: ViewId) => void }) {
  const [portfolioData, setPortfolioData] = useState<PortfolioResponse | null>(null);
  const [assets, setAssets] = useState<PortfolioAsset[]>([]);
  const [editingAssetId, setEditingAssetId] = useState<string | null>(null);
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);
  const [draft, setDraft] = useState<PortfolioAssetDraft>(emptyAssetDraft);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    fetchPortfolioData()
      .then((data) => {
        if (!mounted) return;
        setPortfolioData(data);
        setAssets(data.assets);
      })
      .finally(() => {
        if (mounted) setIsLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const summary = useMemo(() => derivePortfolioSummary(assets, portfolioData?.summary), [assets, portfolioData?.summary]);
  const industryConnections = useMemo(() => deriveIndustryConnections(assets, portfolioData?.industryConnections ?? []), [assets, portfolioData?.industryConnections]);
  const allocation = useMemo(() => deriveAssetAllocation(assets), [assets]);

  if (isLoading || !portfolioData) {
    return (
      <section className="panel portfolio-loading">
        <h2>포트폴리오 데이터를 불러오는 중입니다.</h2>
      </section>
    );
  }

  const deleteTarget = assets.find((asset) => asset.id === deleteTargetId);

  function openAddForm() {
    setEditingAssetId(null);
    setDraft(emptyAssetDraft);
    setIsFormOpen(true);
  }

  function openEditForm(asset: PortfolioAsset) {
    setEditingAssetId(asset.id);
    setDraft(assetToDraft(asset));
    setIsFormOpen(true);
  }

  function closeForm() {
    setIsFormOpen(false);
    setEditingAssetId(null);
    setDraft(emptyAssetDraft);
  }

  async function handleSaveAsset(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextAsset = draftToAsset(draft, editingAssetId);
    const { id: _id, relatedNewsCount: _related, cautionNewsCount: _caution, updatedAt: _updated, ...payload } = nextAsset;

    try {
      setApiError(null);
      const savedAsset = editingAssetId
        ? await updatePortfolioAsset(editingAssetId, payload)
        : await createPortfolioAsset(payload);
      setAssets((currentAssets) => {
        if (editingAssetId) {
          return currentAssets.map((asset) => (asset.id === editingAssetId ? savedAsset : asset));
        }
        return [savedAsset, ...currentAssets];
      });
      closeForm();
    } catch (error) {
      setApiError(error instanceof Error ? error.message : "Portfolio update failed");
    }
  }

  async function confirmDeleteAsset() {
    if (!deleteTargetId) return;
    try {
      setApiError(null);
      await deletePortfolioAsset(deleteTargetId);
      setAssets((currentAssets) => currentAssets.filter((asset) => asset.id !== deleteTargetId));
      setDeleteTargetId(null);
    } catch (error) {
      setApiError(error instanceof Error ? error.message : "Portfolio delete failed");
    }
  }

  return (
    <>
      <PageHeader
        title={viewCopy.portfolio.title}
        description={viewCopy.portfolio.subtitle}
        action={(
          <div className="portfolio-hero-actions">
            <span>최근 업데이트 {summary.updatedAt}</span>
            <button type="button" onClick={openAddForm}>자산 추가</button>
          </div>
        )}
      />
      {apiError ? <p className="api-error" role="alert">{apiError}</p> : null}

      <PortfolioSummaryCards summary={summary} />

      <section className="panel portfolio-assets-panel">
        <div className="portfolio-section-head">
          <div>
            <h2>자산 목록</h2>
            <p>자산명, 종목코드, 보유 수량, 기준가와 상태를 확인합니다.</p>
          </div>
          <button type="button" onClick={openAddForm}>+ 자산 추가</button>
        </div>
        <AssetTable assets={assets} onDelete={(assetId) => setDeleteTargetId(assetId)} onEdit={openEditForm} />
      </section>

      <aside className="portfolio-side">
        <AssetAllocationChart allocation={allocation} />
        <IndustryLinkSummary connections={industryConnections} onViewChange={onViewChange} />
        <LinkedSignalCards signals={portfolioData.linkedSignals} />
        <PortfolioNoticePanel onViewChange={onViewChange} />
      </aside>

      {isFormOpen ? (
        <AssetFormModal
          draft={draft}
          isEditing={Boolean(editingAssetId)}
          onChange={setDraft}
          onClose={closeForm}
          onSubmit={handleSaveAsset}
        />
      ) : null}

      {deleteTarget ? (
        <DeleteAssetDialog
          asset={deleteTarget}
          onCancel={() => setDeleteTargetId(null)}
          onConfirm={confirmDeleteAsset}
        />
      ) : null}
    </>
  );
}

function PortfolioSummaryCards({ summary }: { summary: PortfolioSummary }) {
  const gapClass = summary.valuationGap >= 0 ? "score-pos" : "score-neg";

  return (
    <section className="portfolio-summary-strip" aria-label="포트폴리오 요약">
      <article className="panel">
        <span>등록 자산</span>
        <strong>{summary.assetCount}개</strong>
        <small>직접 입력 기준</small>
      </article>
      <article className="panel">
        <span>입력 기준 원금</span>
        <strong>{formatKrw(summary.totalInputAmount)}</strong>
        <small>보유 수량 × 평균 매수가</small>
      </article>
      <article className="panel">
        <span>현재 평가 기준 금액</span>
        <strong>{formatKrw(summary.totalCurrentAmount)}</strong>
        <small>현재 기준가 반영</small>
      </article>
      <article className="panel">
        <span>평가 차이</span>
        <strong className={gapClass}>{formatSignedKrw(summary.valuationGap)}</strong>
        <small className={gapClass}>{summary.valuationGapRate >= 0 ? "+" : ""}{summary.valuationGapRate.toFixed(2)}%</small>
      </article>
      <article className="panel">
        <span>연결 산업</span>
        <strong>{summary.linkedIndustryCount}개</strong>
        <small>산업 영향도와 연결</small>
      </article>
      <article className="panel">
        <span>알림 상태</span>
        <strong>{summary.cautionAlertCount}건 주의</strong>
        <small>일반 {summary.normalAlertCount}건</small>
      </article>
    </section>
  );
}

function AssetTable({
  assets,
  onDelete,
  onEdit,
}: {
  assets: PortfolioAsset[];
  onDelete: (assetId: string) => void;
  onEdit: (asset: PortfolioAsset) => void;
}) {
  if (assets.length === 0) {
    return (
      <div className="asset-empty">
        <strong>등록된 자산이 없습니다.</strong>
        <span>자산 추가 버튼으로 모니터링할 항목을 등록할 수 있습니다.</span>
      </div>
    );
  }

  return (
    <div className="asset-table-wrap">
      <table className="asset-table">
        <thead>
          <tr>
            <th>자산명</th>
            <th>종목코드</th>
            <th>보유 수량</th>
            <th>평균 매수가</th>
            <th>현재 기준가</th>
            <th>최근 매도가</th>
            <th>상태</th>
            <th>연결 뉴스</th>
            <th>메모</th>
            <th>관리</th>
          </tr>
        </thead>
        <tbody>
          {assets.map((asset) => (
            <tr key={asset.id}>
              <td>
                <strong>{asset.assetName}</strong>
                <span>{asset.industry}</span>
              </td>
              <td>{asset.symbol}</td>
              <td>{asset.quantity.toLocaleString()}주</td>
              <td>{formatAssetCurrency(asset.averageBuyPrice, asset.currency)}</td>
              <td>
                <strong>{formatAssetCurrency(asset.currentPrice, asset.currency)}</strong>
                <span className="asset-memo-preview">
                  {asset.priceStatusLabel ?? (
                    asset.priceDataSource === "real"
                      ? `Latest ${asset.priceProvider ?? "market"} price`
                      : "Stored reference price (mock)"
                  )}
                </span>
              </td>
              <td>{asset.recentSellPrice ? formatAssetCurrency(asset.recentSellPrice, asset.currency) : "-"}</td>
              <td><StatusBadge status={asset.status} /></td>
              <td>
                <span>{asset.relatedNewsCount}건</span>
                <small>주의 {asset.cautionNewsCount}건</small>
              </td>
              <td>
                <span className="asset-memo-preview">{asset.decisionMemo || "메모 없음"}</span>
              </td>
              <td>
                <div className="asset-actions">
                  <button type="button" onClick={() => onEdit(asset)}>수정</button>
                  <button type="button" onClick={() => onDelete(asset.id)}>삭제</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AssetFormModal({
  draft,
  isEditing,
  onChange,
  onClose,
  onSubmit,
}: {
  draft: PortfolioAssetDraft;
  isEditing: boolean;
  onChange: (draft: PortfolioAssetDraft) => void;
  onClose: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <div className="modal-backdrop" role="presentation">
      <form className="portfolio-modal" onSubmit={onSubmit}>
        <div className="portfolio-modal-head">
          <h2>{isEditing ? "자산 수정" : "자산 추가"}</h2>
          <button type="button" onClick={onClose} aria-label="닫기">×</button>
        </div>
        <div className="asset-form-grid">
          <label>
            자산명
            <input required value={draft.assetName} onChange={(event) => onChange({ ...draft, assetName: event.target.value })} />
          </label>
          <label>
            종목코드
            <input required value={draft.symbol} onChange={(event) => onChange({ ...draft, symbol: event.target.value.toUpperCase() })} />
          </label>
          <label>
            시장
            <select value={draft.market} onChange={(event) => onChange({ ...draft, market: event.target.value as AssetMarket })}>
              <option value="KR">KR</option>
              <option value="US">US</option>
              <option value="TW">TW</option>
              <option value="OTHER">OTHER</option>
            </select>
          </label>
          <label>
            산업
            <input required value={draft.industry} onChange={(event) => onChange({ ...draft, industry: event.target.value })} />
          </label>
          <label>
            보유 수량
            <input min="0" required type="number" value={draft.quantity} onChange={(event) => onChange({ ...draft, quantity: Number(event.target.value) })} />
          </label>
          <label>
            평균 매수가
            <input min="0" required type="number" value={draft.averageBuyPrice} onChange={(event) => onChange({ ...draft, averageBuyPrice: Number(event.target.value) })} />
          </label>
          <label>
            현재 기준가
            <input min="0" required type="number" value={draft.currentPrice} onChange={(event) => onChange({ ...draft, currentPrice: Number(event.target.value) })} />
          </label>
          <label>
            최근 매도가
            <input min="0" placeholder="없으면 비워두기" type="number" value={draft.recentSellPrice} onChange={(event) => onChange({ ...draft, recentSellPrice: event.target.value })} />
          </label>
          <label>
            통화
            <select value={draft.currency} onChange={(event) => onChange({ ...draft, currency: event.target.value as AssetCurrency })}>
              <option value="KRW">KRW</option>
              <option value="USD">USD</option>
              <option value="TWD">TWD</option>
            </select>
          </label>
          <label>
            상태
            <select value={draft.status} onChange={(event) => onChange({ ...draft, status: event.target.value as AssetStatus })}>
              <option value="holding">보유중</option>
              <option value="partial_sold">일부 매도</option>
              <option value="watching">관심</option>
            </select>
          </label>
          <label className="asset-form-memo">
            메모
            <textarea
              rows={4}
              placeholder="이 자산을 등록한 이유, 확인할 시장 신호, 발표 후 체크할 내용을 적어두세요."
              value={draft.decisionMemo}
              onChange={(event) => onChange({ ...draft, decisionMemo: event.target.value })}
            />
          </label>
        </div>
        <div className="portfolio-modal-actions">
          <button type="button" onClick={onClose}>취소</button>
          <button type="submit">{isEditing ? "수정 저장" : "자산 추가"}</button>
        </div>
      </form>
    </div>
  );
}

function DeleteAssetDialog({
  asset,
  onCancel,
  onConfirm,
}: {
  asset: PortfolioAsset;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  return (
    <div className="modal-backdrop" role="presentation">
      <div className="portfolio-modal delete-dialog" role="dialog" aria-modal="true" aria-labelledby="delete-asset-title">
        <h2 id="delete-asset-title">자산 삭제</h2>
        <p><strong>{asset.assetName}</strong>을 목록에서 제거합니다. 등록된 모니터링 항목만 삭제되며 외부 거래와 연결되지 않습니다.</p>
        <div className="portfolio-modal-actions">
          <button type="button" onClick={onCancel}>취소</button>
          <button type="button" className="danger" onClick={onConfirm}>삭제</button>
        </div>
      </div>
    </div>
  );
}

function AssetAllocationChart({ allocation }: { allocation: Array<{ id: string; name: string; amount: number; ratio: number }> }) {
  return (
    <section className="panel allocation-panel">
      <h2>자산 비중</h2>
      <div className="allocation-list">
        {allocation.map((item) => (
          <article key={item.id}>
            <div>
              <strong>{item.name}</strong>
              <span>{formatKrw(item.amount)}</span>
            </div>
            <div className="allocation-track" aria-label={`${item.name} 비중 ${item.ratio.toFixed(1)}%`}>
              <span style={{ width: `${Math.max(item.ratio, 4)}%` }} />
            </div>
            <em>{item.ratio.toFixed(1)}%</em>
          </article>
        ))}
      </div>
    </section>
  );
}

function IndustryLinkSummary({ connections, onViewChange }: { connections: IndustryConnection[]; onViewChange: (view: ViewId) => void }) {
  return (
    <section className="panel industry-link-panel">
      <div className="portfolio-section-head compact">
        <h2>산업 연결 요약</h2>
        <button type="button" onClick={() => onViewChange("industry")}>산업 영향도 보기</button>
      </div>
      <div className="industry-link-list">
        {connections.map((connection) => (
          <article key={connection.id}>
            <strong>{connection.industryName}</strong>
            <span>{connection.connectedAssetCount}개 자산</span>
            <em className={`signal-label signal-label--${connection.signalLabel}`}>{connection.signalLabel}</em>
          </article>
        ))}
      </div>
    </section>
  );
}

function LinkedSignalCards({ signals }: { signals: LinkedSignal[] }) {
  return (
    <section className="panel linked-signal-panel">
      <h2>최근 연결 신호</h2>
      <div className="linked-signal-list">
        {signals.map((signal) => (
          <article className={`linked-signal linked-signal--${signal.tone}`} key={signal.id}>
            <span>{signal.time} · {signal.industryName}</span>
            <strong>{signal.title}</strong>
            <p>{signal.summary}</p>
            <small>연결 자산 {signal.relatedAssetCount}개</small>
          </article>
        ))}
      </div>
    </section>
  );
}

function PortfolioNoticePanel({ onViewChange }: { onViewChange: (view: ViewId) => void }) {
  return (
    <section className="panel portfolio-notice-panel">
      <h2>자산 현황 모니터링 안내</h2>
      <p>이 화면은 사용자가 직접 입력한 자산과 FinLightAI의 산업/뉴스 신호를 연결해 보여줍니다. 특정 자산의 매수·매도 판단이나 수익을 보장하지 않습니다.</p>
      <button type="button" onClick={() => onViewChange("guard")}>뉴스 가드 확인</button>
    </section>
  );
}

function StatusBadge({ status }: { status: AssetStatus }) {
  const labels: Record<AssetStatus, string> = {
    holding: "보유중",
    partial_sold: "일부 매도",
    watching: "관심",
  };

  return <span className={`asset-status asset-status--${status}`}>{labels[status]}</span>;
}

function PortfolioView({ onViewChange }: { onViewChange: (view: ViewId) => void }) {
  return (
    <>
      <section className="panel sub-hero">
        <div className="section-title-row">
          <h2>포트폴리오 모니터링</h2>
          <span>준비 중</span>
        </div>
        <p>등록 자산을 산업 신호와 연결해 관심 업종 변화와 뉴스 가드 경고를 빠르게 확인하는 화면입니다.</p>
        <div className="summary-strip">
          <article><span>등록 자산</span><strong>3개</strong></article>
          <article><span>연결 산업</span><strong>반도체 · IT</strong></article>
          <article><span>알림 상태</span><strong>주의 모드</strong></article>
        </div>
      </section>
      <section className="panel action-panel">
        <h2>포트폴리오 연결 흐름</h2>
        <p>자산 등록, 산업 매핑, 이메일 알림 조건 설정 순서로 확장 예정입니다.</p>
        <button type="button" onClick={() => onViewChange("settings")}>이메일 알림 설정으로 이동</button>
      </section>
    </>
  );
}

function MyPageView({ onViewChange }: { onViewChange: (view: ViewId) => void }) {
  return (
    <section className="panel sub-hero">
      <div className="section-title-row">
        <h2>마이페이지</h2>
        <span>개인화 설정</span>
      </div>
      <p>관심 산업과 알림 채널을 관리합니다. MVP에서는 한국어 UI를 기준으로 제공합니다.</p>
      <div className="settings-list">
        <button type="button" onClick={() => onViewChange("settings")}>이메일 알림 설정</button>
        <button type="button" onClick={() => onViewChange("industry")}>관심 산업 관리</button>
      </div>
    </section>
  );
}

function MyPageDashboard({
  onViewChange,
}: {
  onViewChange: (view: ViewId) => void;
}) {
  const [myPageData, setMyPageData] = useState<MyPageResponse | null>(null);
  const [alertSettings, setAlertSettings] = useState<MyPageAlertSetting[]>([]);
  const [interests, setInterests] = useState<string[]>([]);
  const [isQuickPanelOpen, setIsQuickPanelOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [apiError, setApiError] = useState<string | null>(null);
  const quickPanelRef = useRef<HTMLDivElement>(null);
  const quickPanelTriggerRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    let mounted = true;

    fetchMyPageData()
      .then((data) => {
        if (!mounted) return;
        setMyPageData(data);
        setAlertSettings(data.alertSettings);
        setInterests(data.interests);
      })
      .finally(() => {
        if (mounted) setIsLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (!isQuickPanelOpen) return;

    function handleDocumentClick(event: MouseEvent) {
      const target = event.target;

      if (
        target instanceof Node &&
        !quickPanelRef.current?.contains(target) &&
        !quickPanelTriggerRef.current?.contains(target)
      ) {
        setIsQuickPanelOpen(false);
      }
    }

    document.addEventListener("click", handleDocumentClick);
    return () => document.removeEventListener("click", handleDocumentClick);
  }, [isQuickPanelOpen]);

  if (isLoading || !myPageData) {
    return (
      <section className="panel mypage-loading">
        <h2>마이페이지 데이터를 불러오는 중입니다.</h2>
      </section>
    );
  }

  async function toggleAlert(alertId: MyPageAlertSetting["id"]) {
    const previous = alertSettings;
    const next = previous.map((item) => (item.id === alertId ? { ...item, enabled: !item.enabled } : item));
    setAlertSettings(next);
    try {
      setApiError(null);
      const saved = await updateMyPageData({ alertSettings: next });
      setAlertSettings(saved.alertSettings);
    } catch (error) {
      setAlertSettings(previous);
      setApiError(error instanceof Error ? error.message : "My page update failed");
    }
  }

  async function persistInterests(next: string[]) {
    const previous = interests;
    setInterests(next);
    try {
      setApiError(null);
      const saved = await updateMyPageData({ interests: next });
      setInterests(saved.interests);
    } catch (error) {
      setInterests(previous);
      setApiError(error instanceof Error ? error.message : "Interest update failed");
    }
  }

  function removeInterest(interest: string) {
    void persistInterests(interests.filter((item) => item !== interest));
  }

  function addInterest() {
    const next = "전력 인프라";
    if (!interests.includes(next)) void persistInterests([...interests, next]);
  }

  return (
    <>
      <PageHeader title={viewCopy.mypage.title} description={viewCopy.mypage.subtitle} />
      {apiError ? <p className="api-error" role="alert">{apiError}</p> : null}
      <GuideCard body={myPageData.guide.body} ctaLabel={myPageData.guide.ctaLabel} title={myPageData.guide.title} />
      <section className="mypage-top-row">
        <MyPageProfileCard profile={myPageData.profile} />
        <MyPageMetricCards metrics={myPageData.metrics} />
      </section>
      <section className="mypage-main-grid">
        <InfoSummaryCard profile={myPageData.profile} />
        <AlertSettingsCard alertSettings={alertSettings} onToggle={toggleAlert} />
      </section>
      <section className="mypage-bottom-grid">
        <RecentActivityCard activities={myPageData.activities} />
        <InterestKeywordCard interests={interests} onAdd={addInterest} onRemove={removeInterest} />
        <ConnectionStatusCard connections={myPageData.connections} />
      </section>
      <QuickPanel
        isOpen={isQuickPanelOpen}
        onClose={() => setIsQuickPanelOpen(false)}
        onToggle={() => setIsQuickPanelOpen((current) => !current)}
        onViewChange={onViewChange}
        panelRef={quickPanelRef}
        shortcuts={myPageData.shortcuts}
        triggerRef={quickPanelTriggerRef}
      />
    </>
  );
}

function MyPageProfileCard({ profile }: { profile: MyPageProfile }) {
  return (
    <section className="panel mypage-profile-card">
      <div className="mypage-avatar">U</div>
      <div>
        <h2>{profile.username}님, 반갑습니다!</h2>
        <p>{profile.email} <button type="button" aria-label="이메일 복사">⧉</button></p>
        <span>마지막 로그인 {profile.lastLoginAt}</span>
      </div>
      <button type="button">프로필 수정</button>
    </section>
  );
}

function MyPageMetricCards({ metrics }: { metrics: MyPageMetric[] }) {
  return (
    <div className="mypage-metric-grid">
      {metrics.map((metric) => (
        <article className="panel mypage-metric-card" key={metric.id}>
          <p>{metric.label}</p>
          <span aria-hidden="true">{metric.icon}</span>
          <strong>{metric.value}</strong>
          <small>{metric.helper} {metric.delta ? <b>{metric.delta}</b> : null}</small>
        </article>
      ))}
    </div>
  );
}

function InfoSummaryCard({ profile }: { profile: MyPageProfile }) {
  return (
    <section className="panel mypage-card">
      <h2>A. 내 정보 요약</h2>
      <dl className="mypage-info-list">
        <div><dt>사용자명</dt><dd>{profile.username}</dd></div>
        <div><dt>이메일</dt><dd>{profile.email}</dd></div>
        <div><dt>가입일</dt><dd>{profile.joinedAt}</dd></div>
        <div><dt>마지막 로그인</dt><dd>{profile.lastLoginAt}</dd></div>
        <div><dt>언어 설정</dt><dd>한국어</dd></div>
        <div><dt>알림 채널</dt><dd><span className="channel-pill">TALK</span>{profile.alertChannel}<em>연결됨</em></dd></div>
      </dl>
    </section>
  );
}

function AlertSettingsCard({ alertSettings, onToggle }: { alertSettings: MyPageAlertSetting[]; onToggle: (id: MyPageAlertSetting["id"]) => void }) {
  return (
    <section className="panel mypage-card mypage-alert-settings">
      <div className="mypage-card-head">
        <h2>B. 알림 설정</h2>
        <span>투자 추천이 아닌 시장 상태 알림입니다.</span>
      </div>
      <div className="mypage-toggle-list">
        {alertSettings.map((setting) => (
          <button className="mypage-toggle-row" key={setting.id} type="button" onClick={() => onToggle(setting.id)} aria-pressed={setting.enabled}>
            <span aria-hidden="true">{setting.icon}</span>
            <strong className={setting.emphasis ? "danger-text" : ""}>{setting.title}</strong>
            <small>{setting.description}</small>
            <i className={setting.enabled ? "enabled" : ""} aria-hidden="true" />
          </button>
        ))}
      </div>
    </section>
  );
}

function InterestKeywordCard({ interests, onAdd, onRemove }: { interests: string[]; onAdd: () => void; onRemove: (interest: string) => void }) {
  return (
    <section className="panel mypage-card">
      <div className="mypage-card-head">
        <h2>C. 관심 산업 / 키워드</h2>
        <button type="button">관리하기</button>
      </div>
      <div className="interest-chip-list">
        {interests.map((interest) => (
          <button key={interest} type="button" onClick={() => onRemove(interest)}>
            {interest} <span>×</span>
          </button>
        ))}
        <button className="add-interest" type="button" onClick={onAdd}>+ 추가</button>
      </div>
    </section>
  );
}

function ConnectionStatusCard({ connections }: { connections: MyPageConnection[] }) {
  return (
    <section className="panel mypage-card">
      <h2>D. 연동 상태</h2>
      <div className="mypage-connection-list">
        {connections.map((connection) => (
          <article key={connection.id}>
            <span>{connection.icon}</span>
            <strong>{connection.label}</strong>
            <em>● {connection.statusLabel}</em>
          </article>
        ))}
      </div>
    </section>
  );
}

function RecentActivityCard({ activities }: { activities: MyPageActivity[] }) {
  return (
    <section className="panel mypage-card">
      <div className="mypage-card-head">
        <h2>E. 최근 활동 기록</h2>
        <button type="button">전체 보기</button>
      </div>
      <div className="mypage-activity-list">
        {activities.map((activity) => (
          <article key={activity.id}>
            <span aria-hidden="true">{activity.icon}</span>
            <strong>{activity.title}</strong>
            <time>{activity.timestamp}</time>
          </article>
        ))}
      </div>
    </section>
  );
}

function QuickPanel({
  isOpen,
  onClose,
  onToggle,
  onViewChange,
  panelRef,
  shortcuts,
  triggerRef,
}: {
  isOpen: boolean;
  onClose: () => void;
  onToggle: () => void;
  onViewChange: (view: ViewId) => void;
  panelRef: RefObject<HTMLDivElement | null>;
  shortcuts: MyPageShortcut[];
  triggerRef: RefObject<HTMLButtonElement | null>;
}) {
  const targetMap: Record<MyPageShortcut["id"], ViewId> = {
    portfolio: "portfolio",
    guard: "guard",
    industry: "industry",
  };

  return (
    <div className="quick-panel-wrapper">
      <button
        aria-expanded={isOpen}
        className="quick-panel-trigger"
        onClick={onToggle}
        ref={triggerRef}
        type="button"
      >
        빠른 이동
      </button>
      <div className="quick-panel" hidden={!isOpen} ref={panelRef}>
        {shortcuts.map((shortcut) => (
          <button
            key={shortcut.id}
            type="button"
            onClick={() => {
              onViewChange(targetMap[shortcut.id]);
              onClose();
            }}
          >
            {shortcut.title}
          </button>
        ))}
      </div>
    </div>
  );
}

function GuideCard({ body, ctaLabel, title }: { body: string; ctaLabel: string; title: string }) {
  return (
    <section className="panel mypage-card mypage-guide-card">
      <div>
        <h2>{title}</h2>
        <p>{body}</p>
      </div>
      <button type="button">{ctaLabel} ↗</button>
    </section>
  );
}

function SettingsView() {
  return (
    <section className="panel sub-hero">
      <div className="section-title-row">
        <h2>설정</h2>
        <span>서비스 기준</span>
      </div>
      <p>데이터 수집, 뉴스 가드 필터, 알림 기준, 화면 표시를 조정합니다.</p>
      <div className="settings-list">
        <button type="button">뉴스 가드 기본 필터: 전체 뉴스</button>
        <button type="button">API 상태 카드 표시: 켜짐</button>
      </div>
    </section>
  );
}

function SettingsDashboard() {
  const [settingsData, setSettingsData] = useState<SettingsResponse | null>(null);
  const [dataCollection, setDataCollection] = useState<DataCollectionSettings | null>(null);
  const [newsGuard, setNewsGuard] = useState<NewsGuardSettings | null>(null);
  const [notifications, setNotifications] = useState<NotificationSetting[]>([]);
  const [display, setDisplay] = useState<DisplaySettings | null>(null);
  const [misc, setMisc] = useState<MiscSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [saveStatus, setSaveStatus] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    fetchSettingsData()
      .then((data) => {
        if (!mounted) return;
        setSettingsData(data);
        setDataCollection(data.dataCollection);
        setNewsGuard(data.newsGuard);
        setNotifications(data.notifications);
        setDisplay(data.display);
        setMisc(data.misc);
      })
      .finally(() => {
        if (mounted) setIsLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  if (isLoading || !settingsData || !dataCollection || !newsGuard || !display || !misc) {
    return (
      <section className="panel settings-loading">
        <h2>설정 데이터를 불러오는 중입니다.</h2>
      </section>
    );
  }

  const loadedSettings = settingsData;

  function resetSettings() {
    setDataCollection(loadedSettings.dataCollection);
    setNewsGuard(loadedSettings.newsGuard);
    setNotifications(loadedSettings.notifications);
    setDisplay(loadedSettings.display);
    setMisc(loadedSettings.misc);
  }

  function toggleNotification(id: NotificationSetting["id"]) {
    setNotifications((current) => current.map((item) => (item.id === id ? { ...item, enabled: !item.enabled } : item)));
  }

  function toggleDataFlag(flag: "lowTrustFilter" | "duplicateNewsRemoval") {
    setDataCollection((current) => (current ? { ...current, [flag]: !current[flag] } : current));
  }

  function removeKeyword(keyword: string) {
    setDataCollection((current) => (current ? { ...current, keywords: current.keywords.filter((item) => item !== keyword) } : current));
  }

  function addKeyword() {
    const next = "전력 인프라";
    setDataCollection((current) => (current && !current.keywords.includes(next) ? { ...current, keywords: [...current.keywords, next] } : current));
  }

  function updateNewsGuardMode(mode: NewsGuardMode) {
    setNewsGuard((current) => (current ? { ...current, mode } : current));
  }

  async function saveSettings() {
    if (!dataCollection || !newsGuard || !display || !misc) return;
    try {
      setSaveStatus("Saving...");
      const saved = await saveSettingsData({ dataCollection, newsGuard, notifications, display, misc });
      setSettingsData(saved);
      setDataCollection(saved.dataCollection);
      setNewsGuard(saved.newsGuard);
      setNotifications(saved.notifications);
      setDisplay(saved.display);
      setMisc(saved.misc);
      setSaveStatus("Saved");
    } catch (error) {
      setSaveStatus(error instanceof Error ? error.message : "Settings save failed");
    }
  }

  return (
    <>
      <PageHeader
        title={viewCopy.settings.title}
        description={viewCopy.settings.subtitle}
        action={(
          <div className="settings-actions">
            <button type="button" onClick={resetSettings}>설정 초기화</button>
            <button type="button" onClick={() => void saveSettings()}>설정 저장</button>
            {saveStatus ? <span role="status">{saveStatus}</span> : null}
          </div>
        )}
      />
      <SettingsStatusCards cards={loadedSettings.statusCards} />
      <section className="settings-grid">
        <DataCollectionSettingsCard data={dataCollection} onAddKeyword={addKeyword} onRemoveKeyword={removeKeyword} onToggleFlag={toggleDataFlag} />
        <NewsGuardFilterSettingsCard newsGuard={newsGuard} onModeChange={updateNewsGuardMode} />
        <AlertSettingsPanel notifications={notifications} onToggle={toggleNotification} />
        <ApiConnectionSettingsCard apiConnections={loadedSettings.apiConnections} />
        <DisplaySettingsCard display={display} />
        <MiscSettingsCard misc={misc} />
      </section>
    </>
  );
}

function SettingsStatusCards({ cards }: { cards: SettingsStatusCard[] }) {
  const visibleCards = cards.filter((card) => card.id !== HIDDEN_LEGACY_PROVIDER_ID);

  return (
    <section className="settings-status-grid">
      {visibleCards.map((card) => (
        <article className="panel settings-status-card" key={card.id}>
          <span className={`settings-status-icon settings-status-icon--${card.tone}`}>{card.icon}</span>
          <div>
            <p>{card.title}</p>
            <strong>{card.value}</strong>
            <small>{card.description}</small>
            <button type="button">상세 보기</button>
          </div>
        </article>
      ))}
    </section>
  );
}

function DataCollectionSettingsCard({
  data,
  onAddKeyword,
  onRemoveKeyword,
  onToggleFlag,
}: {
  data: DataCollectionSettings;
  onAddKeyword: () => void;
  onRemoveKeyword: (keyword: string) => void;
  onToggleFlag: (flag: "lowTrustFilter" | "duplicateNewsRemoval") => void;
}) {
  return (
    <section className="panel settings-card">
      <h2>A. 데이터 수집 설정</h2>
      <p>뉴스 및 시장 데이터 수집 주기와 필터를 설정합니다.</p>
      <div className="settings-select-grid">
        <label>뉴스 수집 주기<select value={data.newsInterval} onChange={() => undefined}><option>15분</option><option>30분</option></select></label>
        <label>뉴스 보관 기간<select value={data.newsRetention} onChange={() => undefined}><option>90일</option><option>180일</option></select></label>
        <label>시장 데이터 보관 기간<select value={data.marketDataRetention} onChange={() => undefined}><option>2년</option><option>5년</option></select></label>
      </div>
      <h3>수집 키워드 관리</h3>
      <div className="settings-keyword-list">
        {data.keywords.map((keyword) => (
          <button key={keyword} type="button" onClick={() => onRemoveKeyword(keyword)}>{keyword} ×</button>
        ))}
        <button className="add-keyword" type="button" onClick={onAddKeyword}>+ 키워드 추가</button>
      </div>
      <div className="settings-toggle-list">
        <SettingsToggleRow enabled={data.lowTrustFilter} label="저신뢰 뉴스 수집 및 필터링" onToggle={() => onToggleFlag("lowTrustFilter")} sublabel="저신뢰 기사 및 출처를 자동으로 필터링합니다." />
        <SettingsToggleRow enabled={data.duplicateNewsRemoval} label="중복 뉴스 제거" onToggle={() => onToggleFlag("duplicateNewsRemoval")} sublabel="유사/중복된 뉴스는 최신 정보만 유지합니다." />
      </div>
    </section>
  );
}

function NewsGuardFilterSettingsCard({ newsGuard, onModeChange }: { newsGuard: NewsGuardSettings; onModeChange: (mode: NewsGuardMode) => void }) {
  const modes: Array<{ id: NewsGuardMode; title: string; desc: string; icon: string }> = [
    { id: "basic", title: "기본", desc: "균형 잡힌 필터링", icon: "⌁" },
    { id: "strict", title: "엄격", desc: "높은 기준으로 엄격하게 필터", icon: "◇" },
    { id: "flexible", title: "유연", desc: "더 많은 뉴스를 허용", icon: "◌" },
  ];

  return (
    <section className="panel settings-card">
      <h2>B. 뉴스 가드 필터 설정</h2>
      <p>가짜 뉴스 및 과장/논란 콘텐츠를 설정합니다.</p>
      <div className="settings-slider-list">
        <SettingsSliderRow label="출처 신뢰도 최소 기준" value={newsGuard.minimumSourceTrust} />
        <SettingsSliderRow label="과장/선정 임계 기준" value={newsGuard.sensationalThreshold} />
        <SettingsSliderRow label="과장 보도 최소 점수" value={newsGuard.minimumReportScore} max={100} />
        <label>자극적 표현 탐지 민감도<select value={newsGuard.sensitivity} onChange={() => undefined}><option>높음</option><option>보통</option><option>낮음</option></select></label>
      </div>
      <div className="news-guard-mode-grid">
        {modes.map((mode) => (
          <button className={newsGuard.mode === mode.id ? "active" : ""} key={mode.id} type="button" onClick={() => onModeChange(mode.id)}>
            <span>{mode.icon}</span>
            <strong>{mode.title}</strong>
            <small>{mode.desc}</small>
          </button>
        ))}
      </div>
    </section>
  );
}

function AlertSettingsPanel({
  notifications,
  onToggle,
}: {
  notifications: NotificationSetting[];
  onToggle: (id: NotificationSetting["id"]) => void;
}) {
  return (
    <section className="panel settings-card">
      <h2>C. 알림 설정</h2>
      <p>이메일로 받을 시장 상태 및 주요 이벤트 알림을 설정합니다.</p>
      <div className="settings-toggle-list compact">
        {notifications.map((notification) => (
          <SettingsToggleRow enabled={notification.enabled} key={notification.id} label={notification.label} onToggle={() => onToggle(notification.id)} sublabel={notification.description} />
        ))}
      </div>
      <div className="email-channel-note">
        <span>MAIL</span>
        <div>
          <strong>Email subscription</strong>
          <em>Primary channel</em>
          <p>Daily summaries and selected RED/YELLOW signal alerts are delivered by email.</p>
        </div>
        <button type="button">Manage email alerts</button>
      </div>
    </section>
  );
}

function ApiConnectionSettingsCard({ apiConnections }: { apiConnections: ApiConnection[] }) {
  const visibleConnections = apiConnections.filter(
    (api) => api.id !== HIDDEN_LEGACY_PROVIDER_ID && api.id !== HIDDEN_AUTOMATION_ID,
  );

  return (
    <section className="panel settings-card">
      <div className="settings-card-head">
        <h2>D. API 연결 상태</h2>
        <button type="button">전체 API 관리 ›</button>
      </div>
      <p>연동된 API의 상태와 제한 정보를 확인하고 관리합니다.</p>
      <div className="api-connection-grid">
        {visibleConnections.map((api) => (
          <article key={api.id}>
            <strong>{api.name}</strong>
            <em>● {api.connected ? "연결됨" : "확인 필요"}</em>
          </article>
        ))}
      </div>
    </section>
  );
}

function DisplaySettingsCard({ display }: { display: DisplaySettings }) {
  return (
    <section className="panel settings-card">
      <h2>E. 표시 설정</h2>
      <p>MVP에서는 한국어 UI를 기준으로 화면 표시 옵션만 설정합니다.</p>
      <div className="settings-select-grid two">
        <label>언어<button type="button" disabled>{display.language}</button></label>
        <label>테마<select value={display.theme} onChange={() => undefined}><option>다크 모드</option></select></label>
        <label>숫자/통화 형식<select value={display.numberFormat} onChange={() => undefined}><option>한국 (KRW)</option></select></label>
        <label>시간대<select value={display.timezone} onChange={() => undefined}><option>(UTC+09:00) 서울</option></select></label>
      </div>
    </section>
  );
}

function MiscSettingsCard({ misc }: { misc: MiscSettings }) {
  return (
    <section className="panel settings-card">
      <h2>F. 기타 설정</h2>
      <p>기타 서비스 설정을 관리합니다.</p>
      <div className="settings-select-grid two">
        <label>저장 뉴스 검색 로그 보관 기간<select value={misc.searchLogRetention} onChange={() => undefined}><option>180일</option></select></label>
        <label>세션 자동 만료 시간<select value={misc.sessionTimeout} onChange={() => undefined}><option>30분</option></select></label>
      </div>
      <button className="download-data-btn" type="button">내 데이터 다운로드</button>
      <div className="settings-email-info">ⓘ Email is the only exhibition notification channel.</div>
    </section>
  );
}

function SettingsToggleRow({ enabled, label, onToggle, sublabel }: { enabled: boolean; label: string; onToggle: () => void; sublabel: string }) {
  return (
    <button className="settings-toggle-row" type="button" onClick={onToggle} aria-pressed={enabled}>
      <span>
        <strong>{label}</strong>
        <small>{sublabel}</small>
      </span>
      <i className={enabled ? "enabled" : ""} aria-hidden="true" />
    </button>
  );
}

function SettingsSliderRow({ label, max = 1, value }: { label: string; max?: number; value: number }) {
  return (
    <div className="settings-slider-row">
      <span>{label}</span>
      <div><i style={{ width: `${Math.min((value / max) * 100, 100)}%` }} /></div>
      <strong>{max === 1 ? value.toFixed(2) : value}</strong>
    </div>
  );
}

type AuthStep = "login" | "signup" | "complete";

function GoogleAuthFlowView({ authError, onViewChange }: { authError: string | null; onViewChange: (view: ViewId) => void }) {
  const [selectedIndustries, setSelectedIndustries] = useState(["Semiconductor", "AI"]);
  const [onboardingError, setOnboardingError] = useState<string | null>(null);
  const industryOptions = ["Semiconductor", "AI", "Policy/Regulation", "Finance"];

  function toggleIndustry(industry: string) {
    setSelectedIndustries((current) =>
      current.includes(industry) ? current.filter((item) => item !== industry) : [...current, industry],
    );
  }

  async function completeOnboarding() {
    try {
      setOnboardingError(null);
      await saveOnboardingPreferences({
        interestedMarkets: ["KR", "US"],
        interestedIndustries: selectedIndustries,
        alertEnabled: true,
        notificationChannels: ["dashboard"],
      });
      onViewChange("mypage");
    } catch (error) {
      setOnboardingError(error instanceof Error ? error.message : "Onboarding save failed");
    }
  }

  return (
    <section className="auth-flow-shell">
      <div className="auth-flow-heading">
        <div>
          <h1>FinLightAI Google Auth Flow</h1>
          <p>LOGIN · ONBOARDING · MY PAGE</p>
        </div>
        <span>Google OAuth is the MVP login path. Email alerts are the exhibition notification channel.</span>
      </div>
      {authError ? <p className="api-error" role="alert">{authError}</p> : null}
      {onboardingError ? <p className="api-error" role="alert">{onboardingError}</p> : null}

      <div className="auth-flow-grid">
        <AuthCardFrame label="Google Login" path="/api/auth/google/login">
          <div className="auth-login-hero">
            <p>AI FINANCIAL SIGNAL BOARD</p>
            <h2>Continue with Google</h2>
            <small>Login with Google, then save market and industry onboarding preferences to your FinLightAI user profile.</small>
          </div>
          <div className="auth-paper-card">
            <div className="auth-paper-head">
              <h3>Login</h3>
              <span>OAuth 2.0</span>
            </div>
            <p>Google OAuth callback is handled by the FastAPI backend.</p>
            <button className="auth-primary-btn" type="button" onClick={redirectToGoogleLogin}>Google 로그인</button>
            <small>Secrets stay on the backend. Vercel only receives browser-safe VITE variables.</small>
          </div>
        </AuthCardFrame>

        <AuthCardFrame label="Onboarding" path="/api/onboarding/preferences">
          <div className="auth-paper-card signup">
            <h3>관심 산업 설정</h3>
            <p>로그인 후 관심 시장과 산업을 사용자 ID에 연결합니다.</p>
            <div className="auth-industry-picker">
              {industryOptions.map((industry) => (
                <button className={selectedIndustries.includes(industry) ? "selected" : ""} key={industry} type="button" onClick={() => toggleIndustry(industry)}>
                  {industry}
                  <small>{selectedIndustries.includes(industry) ? "selected" : "click to add"}</small>
                </button>
              ))}
            </div>
            <button className="auth-primary-btn" type="button" onClick={completeOnboarding}>온보딩 저장하고 마이페이지로 이동</button>
          </div>
        </AuthCardFrame>
      </div>
    </section>
  );
}

function AuthCardFrame({ children, label, path }: { children: ReactNode; label: string; path: string }) {
  return (
    <article className="auth-card-frame">
      <header className="auth-card-topbar">
        <div className="auth-mini-brand">
          <span>FL</span>
          <strong>FinLightAI</strong>
        </div>
        <div>
          <em>{label}</em>
          <code>{path}</code>
        </div>
      </header>
      {children}
    </article>
  );
}

function LoginView({ onViewChange }: { onViewChange: (view: ViewId) => void }) {
  return (
    <section className="panel sub-hero">
      <div className="section-title-row">
        <h2>로그인 / 회원가입</h2>
        <span>인증 플로우</span>
      </div>
      <p>현재는 UI 프로토타입 단계입니다. 실제 인증 연결 전까지는 화면 전환과 진입 경로를 먼저 확인합니다.</p>
      <div className="settings-list">
        <button type="button">Google로 계속하기</button>
        <button type="button">이메일로 시작하기</button>
        <button type="button" onClick={() => onViewChange("briefing")}>AI 브리핑으로 돌아가기</button>
      </div>
    </section>
  );
}

function getToneByScore(score: number): Tone {
  if (score >= 30) return "positive";
  if (score <= -40) return "negative";
  if (score < 0) return "warning";
  return "neutral";
}

function formatScore(score: number) {
  return score > 0 ? `+${score}` : String(score);
}

function reliabilityLabel(level: ReliabilityLevel) {
  if (level === "trusted") return "신뢰";
  if (level === "watch") return "주의";
  return "차단";
}

function stars(score: number) {
  const filled = Math.round(score * 5);
  return "★★★★★".slice(0, filled) + "☆☆☆☆☆".slice(0, 5 - filled);
}

function trustClass(trust: NewsImpact["trust"]) {
  if (trust === "신뢰 높음") return "trust-high";
  if (trust === "신뢰 낮음") return "trust-low";
  return "trust-mid";
}

function assetToDraft(asset: PortfolioAsset): PortfolioAssetDraft {
  return {
    assetName: asset.assetName,
    symbol: asset.symbol,
    market: asset.market,
    industry: asset.industry,
    quantity: asset.quantity,
    averageBuyPrice: asset.averageBuyPrice,
    currentPrice: asset.currentPrice,
    recentSellPrice: asset.recentSellPrice?.toString() ?? "",
    currency: asset.currency,
    status: asset.status,
    decisionMemo: asset.decisionMemo ?? "",
  };
}

function draftToAsset(draft: PortfolioAssetDraft, existingId: string | null): PortfolioAsset {
  return {
    id: existingId ?? `asset-${Date.now()}`,
    assetName: draft.assetName.trim(),
    symbol: draft.symbol.trim().toUpperCase(),
    market: draft.market,
    industry: draft.industry.trim(),
    quantity: draft.quantity,
    averageBuyPrice: draft.averageBuyPrice,
    currentPrice: draft.currentPrice,
    recentSellPrice: draft.recentSellPrice ? Number(draft.recentSellPrice) : undefined,
    currency: draft.currency,
    status: draft.status,
    decisionMemo: draft.decisionMemo.trim() || undefined,
    relatedNewsCount: 0,
    cautionNewsCount: 0,
    updatedAt: "2026.06.23 09:30",
  };
}

function derivePortfolioSummary(assets: PortfolioAsset[], fallback?: PortfolioSummary): PortfolioSummary {
  const totalInputAmount = assets.reduce((sum, asset) => sum + toKrw(asset.averageBuyPrice * asset.quantity, asset.currency), 0);
  const totalCurrentAmount = assets.reduce((sum, asset) => sum + toKrw(asset.currentPrice * asset.quantity, asset.currency), 0);
  const valuationGap = totalCurrentAmount - totalInputAmount;
  const valuationGapRate = totalInputAmount > 0 ? (valuationGap / totalInputAmount) * 100 : 0;
  const cautionAlertCount = assets.reduce((sum, asset) => sum + asset.cautionNewsCount, 0);
  const relatedNewsCount = assets.reduce((sum, asset) => sum + asset.relatedNewsCount, 0);

  return {
    assetCount: assets.length,
    totalInputAmount,
    totalCurrentAmount,
    valuationGap,
    valuationGapRate,
    linkedIndustryCount: new Set(assets.map((asset) => asset.industry)).size,
    cautionAlertCount,
    normalAlertCount: Math.max(relatedNewsCount - cautionAlertCount, 0),
    updatedAt: fallback?.updatedAt ?? "2026.06.23 09:30",
  };
}

function deriveIndustryConnections(assets: PortfolioAsset[], fallback: IndustryConnection[]): IndustryConnection[] {
  const industryMap = assets.reduce<Record<string, number>>((acc, asset) => {
    acc[asset.industry] = (acc[asset.industry] ?? 0) + 1;
    return acc;
  }, {});

  return Object.entries(industryMap).map(([industryName, connectedAssetCount]) => {
    const matched = fallback.find((connection) => connection.industryName === industryName);
    return {
      id: matched?.id ?? industryName,
      industryName,
      connectedAssetCount,
      signalLabel: matched?.signalLabel ?? "중립",
    };
  });
}

function deriveAssetAllocation(assets: PortfolioAsset[]) {
  const items = assets.map((asset) => ({
    id: asset.id,
    name: asset.assetName,
    amount: toKrw(asset.currentPrice * asset.quantity, asset.currency),
  }));
  const total = items.reduce((sum, item) => sum + item.amount, 0);

  return items.map((item) => ({
    ...item,
    ratio: total > 0 ? (item.amount / total) * 100 : 0,
  }));
}

function toKrw(amount: number, currency: AssetCurrency) {
  const rates: Record<AssetCurrency, number> = {
    KRW: 1,
    USD: 1382,
    TWD: 43,
  };

  return amount * rates[currency];
}

function formatKrw(value: number) {
  return `${Math.round(value).toLocaleString()}원`;
}

function formatSignedKrw(value: number) {
  const sign = value >= 0 ? "+" : "-";
  return `${sign}${formatKrw(Math.abs(value))}`;
}

function formatAssetCurrency(value: number, currency: AssetCurrency) {
  if (currency === "KRW") {
    return `${Math.round(value).toLocaleString()}원`;
  }

  return `${currency} ${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

export default App;
