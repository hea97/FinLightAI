import { FormEvent, ReactNode, useMemo, useState } from "react";
import {
  industries,
  initialPortfolio,
  marketCopy,
  marketTabs,
  metrics,
  newsItems,
  searchIndex,
  type Industry,
  type MarketTab,
  type Metric,
  type NewsFilter,
  type NewsItem,
  type PortfolioAsset,
} from "./data/mockData";
import { navLabels, pageText, uiText, type Locale, type ViewId } from "./i18n/translations";

const navOrder: ViewId[] = [
  "overview",
  "market",
  "industry",
  "guard",
  "portfolio",
  "kakao",
  "briefing",
  "settings",
];

const navIcons: Record<ViewId, string> = {
  overview: "OV",
  market: "MK",
  industry: "IN",
  guard: "NG",
  portfolio: "PF",
  kakao: "KA",
  briefing: "AI",
  settings: "ST",
};

const filterLabels: Record<NewsFilter, string> = {
  all: "전체",
  verified: "검증 높음",
  watch: "추적 필요",
  rumor: "루머 주의",
};

function App() {
  const [view, setView] = useState<ViewId>("overview");
  const [locale, setLocale] = useState<Locale>("ko");
  const [market, setMarket] = useState<MarketTab>("global");
  const [newsFilter, setNewsFilter] = useState<NewsFilter>("all");
  const [selectedNewsId, setSelectedNewsId] = useState(newsItems[0].id);
  const [selectedIndustryId, setSelectedIndustryId] = useState(industries[0].id);
  const [portfolio, setPortfolio] = useState<PortfolioAsset[]>(initialPortfolio);
  const [portfolioFormOpen, setPortfolioFormOpen] = useState(false);
  const [query, setQuery] = useState("");

  const text = uiText[locale];
  const currentPage = pageText[locale][view];
  const selectedIndustry = industries.find((item) => item.id === selectedIndustryId) ?? industries[0];
  const visibleNews = newsItems.filter((item) => newsFilter === "all" || item.status === newsFilter);
  const selectedNews = newsItems.find((item) => item.id === selectedNewsId) ?? visibleNews[0] ?? newsItems[0];

  const searchResults = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return [];
    return searchIndex
      .filter((item) => `${item.type} ${item.title} ${item.description}`.toLowerCase().includes(normalized))
      .slice(0, 6);
  }, [query]);

  const totalWeight = portfolio.reduce((sum, item) => sum + item.weight, 0);

  function addAsset(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const name = String(form.get("name") ?? "").trim();
    const sector = String(form.get("sector") ?? "").trim() || "미분류";
    const weight = Number(form.get("weight") ?? 0);
    if (!name) return;

    setPortfolio((current) => [
      ...current,
      {
        id: `${name}-${Date.now()}`,
        name,
        sector,
        weight: Number.isFinite(weight) ? weight : 0,
        signal: "관찰",
        newsCount: 0,
      },
    ]);
    event.currentTarget.reset();
    setPortfolioFormOpen(false);
  }

  function selectNewsFilter(filter: NewsFilter) {
    setNewsFilter(filter);
    const firstMatch = newsItems.find((item) => filter === "all" || item.status === filter);
    if (firstMatch) setSelectedNewsId(firstMatch.id);
  }

  function openSearchResult(resultView: ViewId) {
    setView(resultView);
    setQuery("");
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo">FL</div>
          <div>
            <div className="brand-title">FinLightAI</div>
            <div className="brand-sub">Market Signal OS</div>
          </div>
        </div>

        <nav className="nav" aria-label="Primary">
          {navOrder.map((item) => (
            <button
              className={`nav-item ${view === item ? "active" : ""}`}
              key={item}
              type="button"
              onClick={() => setView(item)}
            >
              <span className="nav-ico">{navIcons[item]}</span>
              {navLabels[locale][item]}
            </button>
          ))}
        </nav>

        <div className="sidebar-card">
          <strong>오늘의 핵심</strong>
          <p>반도체는 긍정, 항공과 금융은 비용 변수 때문에 주의가 필요합니다.</p>
        </div>
      </aside>

      <main className="shell">
        <header className="header">
          <div>
            <h1>{currentPage.title}</h1>
            <p>{currentPage.subtitle}</p>
          </div>

          <div className="header-actions">
            <div className="search">
              <input
                aria-label={text.searchPlaceholder}
                placeholder={text.searchPlaceholder}
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
              {query ? (
                <div className="search-results">
                  {searchResults.length ? (
                    searchResults.map((item) => (
                      <button key={`${item.type}-${item.title}`} type="button" onClick={() => openSearchResult(item.view)}>
                        <strong>[{item.type}] {item.title}</strong>
                        <span>{item.description}</span>
                      </button>
                    ))
                  ) : (
                    <div className="search-empty">{text.searchEmpty}</div>
                  )}
                </div>
              ) : null}
            </div>
            <button className="top-btn kakao" type="button" onClick={() => setView("kakao")}>
              {text.kakaoCta}
            </button>
            <button className="top-btn" type="button" onClick={() => setLocale(locale === "ko" ? "en" : "ko")}>
              {text.language}
            </button>
            <span className="status-chip">{text.status}</span>
          </div>
        </header>

        <div className="content">
          {view === "overview" && (
            <Overview
              market={market}
              locale={locale}
              selectedIndustry={selectedIndustry}
              selectedNews={selectedNews}
              onMarketChange={setMarket}
              onViewChange={setView}
            />
          )}
          {view === "market" && <MarketView locale={locale} market={market} onMarketChange={setMarket} />}
          {view === "industry" && (
            <IndustryView
              selectedIndustry={selectedIndustry}
              selectedIndustryId={selectedIndustryId}
              onSelectIndustry={setSelectedIndustryId}
            />
          )}
          {view === "guard" && (
            <NewsGuardView
              filter={newsFilter}
              selectedNews={selectedNews}
              visibleNews={visibleNews}
              onFilterChange={selectNewsFilter}
              onSelectNews={setSelectedNewsId}
            />
          )}
          {view === "portfolio" && (
            <PortfolioView
              assets={portfolio}
              formOpen={portfolioFormOpen}
              totalWeight={totalWeight}
              onAddAsset={addAsset}
              onToggleForm={() => setPortfolioFormOpen((open) => !open)}
              text={text}
            />
          )}
          {view === "kakao" && <KakaoView />}
          {view === "briefing" && <BriefingView />}
          {view === "settings" && <SettingsView locale={locale} onLocaleChange={setLocale} />}
        </div>
      </main>
    </div>
  );
}

function Overview({
  market,
  locale,
  selectedIndustry,
  selectedNews,
  onMarketChange,
  onViewChange,
}: {
  market: MarketTab;
  locale: Locale;
  selectedIndustry: Industry;
  selectedNews: NewsItem;
  onMarketChange: (market: MarketTab) => void;
  onViewChange: (view: ViewId) => void;
}) {
  return (
    <section className="grid-12">
      <article className="card hero-signal">
        <div className="signal-top">
          <span>통합 시장 신호</span>
          <span>09:30 KST 기준</span>
        </div>
        <div className="signal-main">
          <div className="signal-badge-xl">
            <strong>68</strong>
            <span>주의</span>
          </div>
          <div>
            <h2>{marketCopy[locale][market].headline}</h2>
            <p>{marketCopy[locale][market].summary}</p>
            <div className="score-bar" aria-label="Risk score 68">
              <span />
            </div>
          </div>
        </div>
      </article>

      <article className="card brief-card">
        <SectionTitle title="빠른 전환" hint="주요 화면" />
        <div className="quick-actions">
          <button type="button" onClick={() => onViewChange("guard")}>뉴스 가드 확인</button>
          <button type="button" onClick={() => onViewChange("industry")}>산업 상세 보기</button>
          <button type="button" onClick={() => onViewChange("portfolio")}>포트폴리오 등록</button>
        </div>
      </article>

      <article className="card metric-panel">
        {metrics[market].map((metric) => (
          <MetricCard key={metric.label} metric={metric} />
        ))}
      </article>

      <article className="card heatmap-card">
        <SectionTitle title="산업 히트맵" hint={`${selectedIndustry.name} 선택됨`} />
        <IndustryHeatmap selectedId={selectedIndustry.id} onSelect={() => onViewChange("industry")} />
      </article>

      <article className="card news-card">
        <SectionTitle title="뉴스 가드 요약" hint={selectedNews.source} />
        <strong>{selectedNews.title}</strong>
        <p>{selectedNews.summary}</p>
        <div className="badge-row">
          <span className="badge impact">영향도 {selectedNews.impact}</span>
          <span className={`badge ${trustTone(selectedNews.trust)}`}>신뢰도 {selectedNews.trust}</span>
        </div>
      </article>

      <div className="market-tabs overview-tabs">
        {marketTabs[locale].map((item) => (
          <button
            className={`tab ${market === item.id ? "active" : ""}`}
            key={item.id}
            type="button"
            onClick={() => onMarketChange(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>
    </section>
  );
}

function MarketView({
  locale,
  market,
  onMarketChange,
}: {
  locale: Locale;
  market: MarketTab;
  onMarketChange: (market: MarketTab) => void;
}) {
  return (
    <section className="grid">
      <div className="market-tabs">
        {marketTabs[locale].map((item) => (
          <button
            className={`tab ${market === item.id ? "active" : ""}`}
            key={item.id}
            type="button"
            onClick={() => onMarketChange(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>
      <article className="card market-hero">
        <h2>{marketCopy[locale][market].headline}</h2>
        <p>{marketCopy[locale][market].summary}</p>
      </article>
      <div className="metric-grid">
        {metrics[market].map((metric) => (
          <MetricCard key={metric.label} metric={metric} />
        ))}
      </div>
    </section>
  );
}

function IndustryView({
  selectedIndustry,
  selectedIndustryId,
  onSelectIndustry,
}: {
  selectedIndustry: Industry;
  selectedIndustryId: string;
  onSelectIndustry: (id: string) => void;
}) {
  return (
    <section className="grid-12">
      <article className="card industry-map">
        <SectionTitle title="산업별 영향도" hint="점수 카드 선택" />
        <IndustryHeatmap selectedId={selectedIndustryId} onSelect={onSelectIndustry} />
      </article>
      <article className="card industry-detail">
        <SectionTitle title={selectedIndustry.name} hint={selectedIndustry.state} />
        <div className={`score-pill ${scoreClass(selectedIndustry.score)}`}>{formatScore(selectedIndustry.score)}</div>
        <p>{selectedIndustry.description}</p>
        <div className="detail-block">
          <strong>근거</strong>
          <span>{selectedIndustry.reason}</span>
        </div>
        <div className="detail-grid">
          <div>
            <strong>관련 자산</strong>
            <ul>{selectedIndustry.assets.map((asset) => <li key={asset}>{asset}</li>)}</ul>
          </div>
          <div>
            <strong>확인 리스크</strong>
            <ul>{selectedIndustry.risks.map((risk) => <li key={risk}>{risk}</li>)}</ul>
          </div>
        </div>
      </article>
    </section>
  );
}

function NewsGuardView({
  filter,
  selectedNews,
  visibleNews,
  onFilterChange,
  onSelectNews,
}: {
  filter: NewsFilter;
  selectedNews: NewsItem;
  visibleNews: NewsItem[];
  onFilterChange: (filter: NewsFilter) => void;
  onSelectNews: (id: string) => void;
}) {
  return (
    <section className="grid-12">
      <article className="card news-list-card">
        <SectionTitle title="뉴스 목록" hint="필터와 상세 연동" />
        <div className="market-tabs">
          {(Object.keys(filterLabels) as NewsFilter[]).map((item) => (
            <button
              className={`tab ${filter === item ? "active" : ""}`}
              key={item}
              type="button"
              onClick={() => onFilterChange(item)}
            >
              {filterLabels[item]}
            </button>
          ))}
        </div>
        <div className="news-list">
          {visibleNews.map((item) => (
            <button
              className={`news-item ${selectedNews.id === item.id ? "active" : ""}`}
              key={item.id}
              type="button"
              onClick={() => onSelectNews(item.id)}
            >
              <span className="news-source">{item.source}</span>
              <strong>{item.title}</strong>
              <span>{item.summary}</span>
            </button>
          ))}
        </div>
      </article>
      <article className="card news-detail-card">
        <SectionTitle title="상세 검증" hint={selectedNews.source} />
        <h2>{selectedNews.title}</h2>
        <p>{selectedNews.summary}</p>
        <div className="metric-grid two">
          <MetricCard metric={{ label: "영향도", value: String(selectedNews.impact), description: "시장 반응 가능성", tone: "blue" }} />
          <MetricCard metric={{ label: "신뢰도", value: selectedNews.trust, description: selectedNews.reason, tone: trustMetricTone(selectedNews.trust) }} />
        </div>
        <div className="warning-panel">
          출처, 공시 여부, 반복 확산 패턴을 분리해서 판단합니다. 신뢰도 낮음 뉴스는 포트폴리오 알림에 바로 반영하지 않습니다.
        </div>
      </article>
    </section>
  );
}

function PortfolioView({
  assets,
  formOpen,
  totalWeight,
  onAddAsset,
  onToggleForm,
  text,
}: {
  assets: PortfolioAsset[];
  formOpen: boolean;
  totalWeight: number;
  onAddAsset: (event: FormEvent<HTMLFormElement>) => void;
  onToggleForm: () => void;
  text: Record<string, string>;
}) {
  return (
    <section className="grid">
      <div className="portfolio-summary">
        <MetricCard metric={{ label: "등록 자산", value: `${assets.length}개`, description: "감시 대상", tone: "teal" }} />
        <MetricCard metric={{ label: "총 비중", value: `${totalWeight}%`, description: "데모 입력 기준", tone: "blue" }} />
        <MetricCard metric={{ label: "관련 뉴스", value: `${assets.reduce((sum, item) => sum + item.newsCount, 0)}건`, description: "최근 24시간", tone: "neutral" }} />
      </div>
      <article className="card">
        <SectionTitle
          title="자산 목록"
          hint={
            <button className="inline-btn" type="button" onClick={onToggleForm}>
              {formOpen ? text.closeForm : text.addAsset}
            </button>
          }
        />
        {formOpen ? (
          <form className="portfolio-form open" onSubmit={onAddAsset}>
            <input name="name" placeholder="종목명" />
            <input name="sector" placeholder="산업" />
            <input name="weight" min="0" max="100" placeholder="비중" type="number" />
            <button type="submit">{text.save}</button>
          </form>
        ) : null}
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>자산</th>
                <th>산업</th>
                <th>비중</th>
                <th>신호</th>
                <th>뉴스</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((asset) => (
                <tr key={asset.id}>
                  <td>{asset.name}</td>
                  <td>{asset.sector}</td>
                  <td>{asset.weight}%</td>
                  <td>{asset.signal}</td>
                  <td>{asset.newsCount}건</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  );
}

function KakaoView() {
  return (
    <section className="grid-12">
      <article className="card kakao-flow">
        <SectionTitle title="카카오 Auth 흐름" hint="프론트 준비 상태" />
        <div className="flow-steps">
          {["로그인 요청", "인가 코드 수신", "백엔드 토큰 교환", "채널 알림 동의"].map((step, index) => (
            <div key={step}>
              <strong>0{index + 1}</strong>
              <span>{step}</span>
            </div>
          ))}
        </div>
      </article>
      <article className="card kakao-preview">
        <SectionTitle title="알림 미리보기" hint="채널 메시지" />
        <div className="phone">
          <div className="phone-top">FinLightAI</div>
          <div className="bubble">
            <strong>시장 주의 신호</strong>
            <p>항공 산업 영향도 -58. 유가와 환율 부담이 동시에 확대됐습니다.</p>
            <button type="button">상세 보기</button>
          </div>
        </div>
      </article>
    </section>
  );
}

function BriefingView() {
  return (
    <section className="grid-12">
      {[
        ["핵심 판단", "시장 전체는 주의권입니다. 반도체 강세가 지수를 방어하지만 비용 민감 업종은 압박을 받습니다."],
        ["확인 필요", "NVIDIA 공급 병목 뉴스는 영향도가 높지만 추정 표현이 있어 추가 확인이 필요합니다."],
        ["실행 메모", "포트폴리오의 항공, 금융 비중을 먼저 확인하고 카카오 알림 기준을 보수적으로 유지합니다."],
      ].map(([title, body]) => (
        <article className="card briefing-card" key={title}>
          <SectionTitle title={title} hint="AI 요약" />
          <p>{body}</p>
        </article>
      ))}
    </section>
  );
}

function SettingsView({ locale, onLocaleChange }: { locale: Locale; onLocaleChange: (locale: Locale) => void }) {
  return (
    <section className="grid-12">
      <article className="card settings-card">
        <SectionTitle title="환경 설정" hint="로컬 상태" />
        <div className="settings-row">
          <div>
            <strong>언어</strong>
            <span>한국어와 영어 UI 텍스트를 전환합니다.</span>
          </div>
          <button className="top-btn" type="button" onClick={() => onLocaleChange(locale === "ko" ? "en" : "ko")}>
            {locale === "ko" ? "English" : "Korean"}
          </button>
        </div>
        <div className="settings-row">
          <div>
            <strong>뉴스 가드</strong>
            <span>신뢰도 낮음 뉴스는 알림 전송 전 확인 대상으로 유지합니다.</span>
          </div>
          <span className="badge warn">주의 모드</span>
        </div>
        <div className="settings-row">
          <div>
            <strong>관심 산업</strong>
            <span>반도체, 금융, 항공, 방산을 우선 표시합니다.</span>
          </div>
          <span className="badge impact">4개</span>
        </div>
      </article>
    </section>
  );
}

function IndustryHeatmap({ selectedId, onSelect }: { selectedId: string; onSelect: (id: string) => void }) {
  return (
    <div className="heatmap">
      {industries.map((industry) => (
        <button
          className={`hm ${industry.tone} ${selectedId === industry.id ? "active" : ""}`}
          key={industry.id}
          type="button"
          onClick={() => onSelect(industry.id)}
        >
          <span>{industry.name}</span>
          <strong>{formatScore(industry.score)}</strong>
          <em>{industry.state}</em>
        </button>
      ))}
    </div>
  );
}

function MetricCard({ metric }: { metric: Metric }) {
  return (
    <article className="metric-card">
      <span>{metric.label}</span>
      <strong className={metric.tone}>{metric.value}</strong>
      <em>{metric.description}</em>
    </article>
  );
}

function SectionTitle({ title, hint }: { title: string; hint?: string | ReactNode }) {
  return (
    <div className="section-title">
      <h3>{title}</h3>
      {hint ? <div className="hint">{hint}</div> : null}
    </div>
  );
}

function formatScore(score: number) {
  return score > 0 ? `+${score}` : String(score);
}

function scoreClass(score: number) {
  if (score > 30) return "positive";
  if (score < -30) return "negative";
  return "neutral";
}

function trustTone(trust: NewsItem["trust"]) {
  if (trust === "높음") return "trust-hi";
  if (trust === "낮음") return "trust-lo";
  return "warn";
}

function trustMetricTone(trust: NewsItem["trust"]): Metric["tone"] {
  if (trust === "높음") return "teal";
  if (trust === "낮음") return "down";
  return "neutral";
}

export default App;
