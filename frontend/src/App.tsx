import { useEffect, useMemo, useState } from "react";
import { industries, marketData, tabs, type MarketTab, type MarketViewData, type NewsImpact, type Tone } from "./data/mockData";
import { fetchNewsGuardData } from "./services/newsGuardApi";
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

type ViewId = "briefing" | "guard" | "industry" | "portfolio" | "kakao" | "mypage" | "settings" | "login";

const navItems: { id: ViewId; label: string }[] = [
  { id: "briefing", label: "AI 브리핑" },
  { id: "guard", label: "뉴스 가드" },
  { id: "industry", label: "산업 영향도" },
  { id: "portfolio", label: "포트폴리오" },
  { id: "kakao", label: "카카오 알림" },
  { id: "mypage", label: "마이페이지" },
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
    subtitle: "보유 관심 자산을 산업 신호와 연결해 모니터링합니다.",
  },
  kakao: {
    title: "카카오 알림",
    subtitle: "시장 신호와 뉴스 가드 알림 조건을 관리합니다.",
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
    subtitle: "카카오 계정 또는 이메일 기반 인증 흐름을 준비합니다.",
  },
};

function App() {
  const [view, setView] = useState<ViewId>("briefing");
  const [marketTab, setMarketTab] = useState<MarketTab>("domestic");
  const [selectedIndustryId, setSelectedIndustryId] = useState("semiconductor");
  const [locale, setLocale] = useState<"ko" | "en">("ko");

  const currentMarket = marketData[marketTab];
  const selectedIndustry = useMemo(
    () => industries.find((industry) => industry.id === selectedIndustryId) ?? industries[0],
    [selectedIndustryId],
  );
  const page = viewCopy[view];

  function handleIndustryClick(industryId: string) {
    setSelectedIndustryId(industryId);
    setMarketTab("watchIndustry");
    setView("industry");
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
          <label className="search-box">
            <span aria-hidden="true">⌕</span>
            <input placeholder="뉴스, 산업, 주식 검색" />
            <kbd>⌘K</kbd>
          </label>
          <div className="language-toggle" aria-label="언어 전환">
            <button className={locale === "ko" ? "active" : ""} type="button" onClick={() => setLocale("ko")}>
              KO
            </button>
            <button className={locale === "en" ? "active" : ""} type="button" onClick={() => setLocale("en")}>
              EN
            </button>
          </div>
          <button className="icon-button" type="button" onClick={() => setView("kakao")} aria-label="알림">
            ♡<span className="notification-dot">3</span>
          </button>
          <button className="user-menu" type="button" onClick={() => setView("mypage")}>
            <span className="avatar">U</span>
            finlight_user
          </button>
          <button className="small-btn yellow" type="button" onClick={() => setView("guard")}>
            YELLOW · 주의
          </button>
        </div>

        {view !== "guard" ? (
          <div className="page-heading">
            <h1>{page.title}</h1>
            <p>{page.subtitle}</p>
          </div>
        ) : null}
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
            <IndustryImpactView
              selectedIndustryId={selectedIndustryId}
              selectedIndustryName={selectedIndustry.name}
              selectedIndustryScore={selectedIndustry.score}
              onIndustryClick={handleIndustryClick}
            />
          )}
          {view === "portfolio" && <PortfolioView onViewChange={setView} />}
          {view === "kakao" && <KakaoChannelView onViewChange={setView} />}
          {view === "mypage" && <MyPageView locale={locale} onLocaleToggle={() => setLocale(locale === "ko" ? "en" : "ko")} onViewChange={setView} />}
          {view === "settings" && <SettingsView locale={locale} onLocaleToggle={() => setLocale(locale === "ko" ? "en" : "ko")} />}
          {view === "login" && <LoginView onViewChange={setView} />}
        </main>
      )}

      <div className="prototype-chip">FinLightAI High-Fidelity UI Prototype · v3</div>
    </div>
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
  return (
    <main className="dashboard">
      <section className="panel market-signal">
        <div className="section-title-row">
          <h2>오늘의 시장 신호</h2>
          <span>업데이트 {currentMarket.updatedAt}</span>
        </div>
        <div className="signal-content">
          <div className="signal-badge" aria-label="주의 신호">
            <span>!</span>
            <strong>YELLOW</strong>
            <em>주의</em>
          </div>
          <div className="signal-copy">
            <h3>{currentMarket.title}</h3>
            <p>{currentMarket.description}</p>
            <div className="risk-row">
              <div className="risk-track" aria-label={`위험도 ${currentMarket.risk}점`}>
                <span style={{ width: `${currentMarket.risk}%` }} />
              </div>
              <strong>위험도 {currentMarket.risk} / 100</strong>
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
          {currentMarket.briefing.map((point) => (
            <li key={point.text}>
              <span className={`briefing-dot ${point.tone}`} />
              {point.text}
            </li>
          ))}
        </ul>
      </section>

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

        <section className="panel kakao-panel">
          <div className="section-title-row">
            <h2>최근 카카오 알림</h2>
            <button type="button" onClick={() => onViewChange("kakao")}>
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

function NewsGuardPage() {
  const [filter, setFilter] = useState<NewsGuardFilter>("all");
  const [data, setData] = useState<NewsGuardViewModel | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let ignore = false;

    async function load() {
      setIsLoading(true);
      try {
        const result = await fetchNewsGuardData(filter);
        if (!ignore) setData(result);
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
        <header className="news-guard-heading">
          <div className="page-icon" aria-hidden="true">◆</div>
          <div>
            <h1>뉴스 가드</h1>
            <p>뉴스 신뢰도를 검증하고 저신뢰 뉴스를 걸러냅니다.</p>
          </div>
        </header>

        <NewsGuardKpiGrid data={data} />

        <section className="news-list-panel" aria-label="뉴스 가드 목록">
          <NewsFilterTabs value={filter} onChange={setFilter} />
          <div className="news-list-toolbar">
            <button type="button">최신순⌄</button>
            <button type="button" className="filter-button">필터</button>
          </div>
          <div className="news-guard-list">
            {data.articles.map((article) => (
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
          <span>{article.source}</span>
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
        <p>자산 등록, 산업 매핑, 카카오 알림 조건 설정 순서로 확장 예정입니다.</p>
        <button type="button" onClick={() => onViewChange("kakao")}>카카오 알림 설정으로 이동</button>
      </section>
    </>
  );
}

function KakaoChannelView({ onViewChange }: { onViewChange: (view: ViewId) => void }) {
  return (
    <>
      <section className="panel sub-hero kakao-panel">
        <div className="section-title-row">
          <h2>카카오 알림</h2>
          <span>알림 연결</span>
        </div>
        <p>주의 신호, 저신뢰 뉴스 감지, 일일 요약을 카카오 채널 알림으로 받을 수 있도록 준비하는 화면입니다.</p>
        <ul>
          <li><time>1단계</time><span>카카오 채널 추가</span></li>
          <li><time>2단계</time><span>알림 항목 선택</span></li>
          <li><time>3단계</time><span>테스트 메시지 발송</span></li>
        </ul>
      </section>
      <section className="panel action-panel">
        <h2>알림 기준</h2>
        <p>위험도 상승, 저신뢰 뉴스 반복 확산, 관심 산업 급변 시 알림 대상으로 분류합니다.</p>
        <button type="button" onClick={() => onViewChange("mypage")}>마이페이지 설정으로 이동</button>
      </section>
    </>
  );
}

function MyPageView({
  locale,
  onLocaleToggle,
  onViewChange,
}: {
  locale: "ko" | "en";
  onLocaleToggle: () => void;
  onViewChange: (view: ViewId) => void;
}) {
  return (
    <section className="panel sub-hero">
      <div className="section-title-row">
        <h2>마이페이지</h2>
        <span>개인화 설정</span>
      </div>
      <p>관심 산업, 언어, 알림 채널을 관리합니다. 현재 언어 버튼은 상태 전환까지 연결되어 있습니다.</p>
      <div className="settings-list">
        <button type="button" onClick={onLocaleToggle}>언어 전환: 현재 {locale === "ko" ? "한국어" : "English"}</button>
        <button type="button" onClick={() => onViewChange("kakao")}>카카오 채널 설정</button>
        <button type="button" onClick={() => onViewChange("industry")}>관심 산업 관리</button>
      </div>
    </section>
  );
}

function SettingsView({ locale, onLocaleToggle }: { locale: "ko" | "en"; onLocaleToggle: () => void }) {
  return (
    <section className="panel sub-hero">
      <div className="section-title-row">
        <h2>설정</h2>
        <span>서비스 기준</span>
      </div>
      <p>데이터 수집, 뉴스 가드 필터, 알림 기준, 언어 표시를 조정합니다.</p>
      <div className="settings-list">
        <button type="button" onClick={onLocaleToggle}>언어: {locale === "ko" ? "한국어" : "English"}</button>
        <button type="button">뉴스 가드 기본 필터: 전체 뉴스</button>
        <button type="button">API 상태 카드 표시: 켜짐</button>
      </div>
    </section>
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
        <button type="button">카카오로 계속하기</button>
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

export default App;
