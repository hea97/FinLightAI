import { useMemo, useState } from "react";
import { industries, marketData, tabs, type IndustryImpact, type MarketTab, type NewsImpact, type Tone } from "./data/mockData";

const navItems = ["AI 브리핑", "뉴스 가드", "산업 영향도", "포트폴리오", "마이페이지"];

function App() {
  const [marketTab, setMarketTab] = useState<MarketTab>("domestic");
  const [selectedIndustryId, setSelectedIndustryId] = useState("semiconductor");

  const currentMarket = marketData[marketTab];
  const selectedIndustry = useMemo(
    () => industries.find((industry) => industry.id === selectedIndustryId) ?? industries[0],
    [selectedIndustryId],
  );

  function handleIndustryClick(industryId: string) {
    setSelectedIndustryId(industryId);
    setMarketTab("watchIndustry");
  }

  return (
    <div className="app">
      <header className="top-header">
        <div className="brand-group">
          <div className="brand-mark">FL</div>
          <div className="brand-copy">
            <strong>FinLightAI</strong>
            <span>AI 금융 상황판</span>
          </div>
          <div className="header-divider" />
          <div className="page-heading">
            <h1>AI 브리핑</h1>
            <p>오늘의 시장 신호와 뉴스 근거를 먼저 요약합니다.</p>
          </div>
        </div>

        <div className="header-actions">
          <label className="search-box">
            <span aria-hidden="true">⌕</span>
            <input placeholder="뉴스, 산업, 주식 검색" />
            <kbd>⌘K</kbd>
          </label>
          <button className="small-btn" type="button">🌐 EN</button>
          <button className="small-btn login" type="button">로그인 / 회원가입</button>
          <button className="small-btn kakao" type="button">카카오 채널 추가</button>
          <button className="small-btn yellow" type="button">YELLOW · 주의</button>
        </div>

        <nav className="main-nav" aria-label="주요 화면">
          {navItems.map((item, index) => (
            <button className={index === 0 ? "active" : ""} key={item} type="button">
              {item}
            </button>
          ))}
        </nav>
      </header>

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
                onClick={() => setMarketTab(tab.key)}
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
          <button className="ghost-link" type="button">더보기 ›</button>
        </section>

        <NewsTopPanel news={currentMarket.news} />

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
                className={`industry-card ${getToneByScore(industry.score)} ${selectedIndustryId === industry.id ? "active" : ""} ${
                  currentMarket.highlightedIndustries.includes(industry.id) ? "highlighted" : ""
                }`}
                key={industry.id}
                onClick={() => handleIndustryClick(industry.id)}
                type="button"
              >
                <span>{industry.name}</span>
                <strong>{formatScore(industry.score)}</strong>
                <em>{industry.note}</em>
              </button>
            ))}
          </div>
        </section>

        <aside className="side-stack">
          <section className="panel guard-panel">
            <div className="section-title-row">
              <h2>뉴스 가드 경고</h2>
              <button type="button">뉴스 가드 바로가기 ›</button>
            </div>
            <strong>주의 필요 뉴스 14건</strong>
            <p>대표 사유: 자극적 표현, 근거 부족, 반복 확산</p>
          </section>

          <section className="panel kakao-panel">
            <div className="section-title-row">
              <h2>최근 카카오 알림</h2>
              <button type="button">알림 설정 ›</button>
            </div>
            <ul>
              <li><time>09:30</time><span>주의 신호 발송 완료</span></li>
              <li><time>08:10</time><span>저신뢰 뉴스 감지</span></li>
              <li><time>07:30</time><span>일일 요약 대기</span></li>
            </ul>
          </section>

          <section className="selected-industry">
            <span>선택된 관심 산업</span>
            <strong>{selectedIndustry.name} {formatScore(selectedIndustry.score)}</strong>
          </section>
        </aside>
      </main>

      <div className="prototype-chip">FinLightAI High-Fidelity UI Prototype · v3</div>
    </div>
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

function getToneByScore(score: number): Tone {
  if (score >= 30) return "positive";
  if (score <= -40) return "negative";
  if (score < 0) return "warning";
  return "neutral";
}

function formatScore(score: number) {
  return score > 0 ? `+${score}` : String(score);
}

function trustClass(trust: NewsImpact["trust"]) {
  if (trust === "신뢰 높음") return "trust-high";
  if (trust === "신뢰 낮음") return "trust-low";
  return "trust-mid";
}

export default App;
