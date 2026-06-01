const titleMap = {
  dashboard: "Dashboard",
  market: "Market",
  news: "News Feed",
  portfolio: "My Portfolio",
  saved: "Saved News",
  login: "Login",
};

const formatPercent = (value) => `${(Number(value) * 100).toFixed(1)}%`;
const formatNumber = (value) => Number(value).toFixed(2);

function signalClass(signal) {
  const normalized = String(signal || "").toLowerCase();
  if (normalized === "red") return "red";
  if (normalized === "green") return "green";
  return "yellow";
}

function updateClock() {
  const clock = document.querySelector("#clock");
  if (!clock) return;
  clock.textContent = new Date().toLocaleTimeString("ko-KR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function switchView(view) {
  document.querySelectorAll(".nav-item").forEach((item) => {
    item.classList.toggle("active", item.dataset.view === view);
  });
  document.querySelectorAll(".view").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `view-${view}`);
  });
  const title = document.querySelector("#pageTitle");
  if (title) title.textContent = titleMap[view] || "FinLightAI";
}

function setupLoginEntry() {
  const enterButton = document.querySelector("#enterDashboardBtn");
  if (!enterButton) return;

  enterButton.addEventListener("click", () => {
    switchView("dashboard");
  });
}

function animateCounts() {
  document.querySelectorAll("[data-count]").forEach((el) => {
    const target = Number(el.dataset.count);
    let current = 0;
    const step = Math.max(1, Math.round(target / 34));

    const tick = () => {
      current += step;
      if (current >= target) current = target;
      el.textContent = current.toLocaleString("ko-KR");
      el.classList.add("bump");
      setTimeout(() => el.classList.remove("bump"), 120);
      if (current < target) requestAnimationFrame(tick);
    };

    tick();
  });
}

function initChart() {
  const canvas = document.querySelector("#sentimentChart");
  const fallback = document.querySelector("#chartFallback");
  if (!canvas || typeof Chart === "undefined") return;

  if (fallback) fallback.hidden = true;
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: "#9fc7cb", boxWidth: 10 } },
    },
    scales: {
      x: { ticks: { color: "#9fc7cb" }, grid: { color: "rgba(255,255,255,0.05)" } },
      y: { ticks: { color: "#9fc7cb" }, grid: { color: "rgba(255,255,255,0.05)" }, min: 30, max: 80 },
    },
  };

  new Chart(canvas, {
    type: "line",
    data: {
      labels: ["1일", "5일", "10일", "15일", "20일", "25일", "30일"],
      datasets: [
        {
          label: "시장 감성",
          data: [64, 59, 62, 54, 49, 58, 52],
          borderColor: "#3aafb9",
          backgroundColor: "rgba(58,175,185,0.18)",
          fill: true,
          tension: 0.35,
          pointRadius: 2.5,
        },
        {
          label: "리스크 온도",
          data: [44, 47, 45, 58, 66, 61, 68],
          borderColor: "#f04452",
          fill: false,
          tension: 0.35,
          pointRadius: 2.5,
        },
      ],
    },
    options,
  });
}

function renderSignal(signal) {
  const level = signalClass(signal.signal);
  const headline = signal.headline || "분석 대기 중인 신호입니다.";
  const sidebarSignal = document.querySelector("#sidebarSignal");

  document.querySelector("#currentSignal").textContent = signal.signal;
  document.querySelector("#currentSignal").style.color =
    level === "red" ? "var(--color-red)" : level === "green" ? "var(--color-green)" : "var(--color-yellow)";
  document.querySelector("#primaryTicker").textContent = signal.ticker;
  document.querySelector("#heroSummary").textContent = headline;
  document.querySelector("#trustRate").textContent = `신뢰도 ${formatNumber(signal.reliability_score)}`;
  document.querySelector("#sidebarHint").textContent = `${signal.ticker} · 수익률 ${formatPercent(signal.return_1d)} · 거래량 ${formatNumber(signal.volume_ratio)}x`;

  sidebarSignal.className = `signal-chip ${level}`;
  sidebarSignal.textContent = `${signal.signal} · ${level === "red" ? "Risk high" : level === "green" ? "Stable" : "Watch"}`;

  document.querySelector("#signalList").innerHTML = `
    <button class="signal-row active" type="button">
      <span class="dot ${level}"></span>
      <span>
        <strong>${signal.ticker} · ${headline}</strong>
        <small>신뢰도 ${formatNumber(signal.reliability_score)} · 거래량 ${formatNumber(signal.volume_ratio)}x</small>
      </span>
      <span class="badge ${level}">${signal.signal}</span>
    </button>
    <button class="signal-row" type="button">
      <span class="dot yellow"></span>
      <span><strong>연준 발언 감지</strong><small>금리 전망 관련 워딩 업데이트</small></span>
      <span class="badge yellow">YELLOW</span>
    </button>
    <button class="signal-row" type="button">
      <span class="dot green"></span>
      <span><strong>AI 섹터 반등</strong><small>클라우드와 서비스 종목 상대 강도 유지</small></span>
      <span class="badge green">GREEN</span>
    </button>
  `;
}

function newsCardTemplate(item, index) {
  const score = Number(item.reliability_score || 0.75);
  const trustClass = score >= 0.75 ? "high" : "mid";
  const starred = index === 0 ? "true" : "false";
  return `
    <article class="news-card" data-starred="${starred}">
      <div class="news-top">
        <span class="trust ${trustClass}">신뢰도 ${formatNumber(score)}</span>
        <button class="star-btn ${starred === "true" ? "active" : ""}" type="button" aria-label="뉴스 저장">${starred === "true" ? "★" : "☆"}</button>
      </div>
      <h3>${item.title}</h3>
      <p>${item.source} · ${item.url || "상세 링크 준비 중"}</p>
      <div class="tag-row"><span>#AI</span><span>#시장신호</span><span>#FinLightAI</span></div>
    </article>
  `;
}

function bindStarButtons() {
  document.querySelectorAll(".star-btn").forEach((button) => {
    button.addEventListener("click", () => {
      const card = button.closest(".news-card");
      const next = card.dataset.starred !== "true";
      card.dataset.starred = String(next);
      button.classList.toggle("active", next);
      button.textContent = next ? "★" : "☆";
      renderSaved();
    });
  });
}

function renderSaved() {
  const savedStack = document.querySelector("#savedStack");
  const savedCounter = document.querySelector("#savedCounter");
  if (!savedStack || !savedCounter) return;

  const savedCards = [...document.querySelectorAll(".news-card[data-starred='true']")];
  savedCounter.textContent = `${savedCards.length} saved`;

  if (!savedCards.length) {
    savedStack.innerHTML = '<div class="empty-state">별표한 뉴스가 여기에 표시됩니다.</div>';
    return;
  }

  savedStack.innerHTML = savedCards
    .map((card) => {
      const title = card.querySelector("h3").textContent;
      const summary = card.querySelector("p").textContent;
      return `<article class="saved-item"><h3>${title}</h3><p>${summary}</p></article>`;
    })
    .join("");
}

function setupPortfolioModal() {
  const modal = document.querySelector("[data-modal='asset']");
  const open = document.querySelector("#addAssetBtn");
  const closeButtons = document.querySelectorAll(".modal-close, [data-modal-close]");
  const save = document.querySelector("#saveAssetBtn");

  if (!modal || !open || !save) return;

  const closeModal = () => {
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
  };

  const openModal = () => {
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.querySelector("#assetName").focus();
  };

  closeModal();

  open.addEventListener("click", () => {
    openModal();
  });

  closeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      closeModal();
    });
  });

  save.addEventListener("click", () => {
    const name = document.querySelector("#assetName").value.trim() || "신규 자산";
    const type = document.querySelector("#assetType").value;
    const qty = document.querySelector("#assetQty").value || "0";
    const price = document.querySelector("#assetPrice").value.trim() || "-";
    const table = document.querySelector("#portfolioTable");
    table.insertAdjacentHTML("beforeend", `<tr><td>${name}</td><td>${type}</td><td>${qty}</td><td>${price}</td><td>신규</td></tr>`);
    document.querySelector("#assetCount").textContent = table.querySelectorAll("tr").length;
    document.querySelector("#assetName").value = "";
    document.querySelector("#assetQty").value = "";
    document.querySelector("#assetPrice").value = "";
    closeModal();
  });
}

async function loadDashboardData() {
  try {
    const [signalsResponse, newsResponse] = await Promise.all([fetch("/api/signals"), fetch("/api/news")]);
    const signals = await signalsResponse.json();
    const news = await newsResponse.json();

    if (signals.length) renderSignal(signals[0]);
    if (news.length) {
      document.querySelector("#newsList").insertAdjacentHTML("afterbegin", news.map(newsCardTemplate).join(""));
      bindStarButtons();
      renderSaved();
    }
  } catch (error) {
    console.warn("Dashboard API unavailable", error);
  }
}

document.querySelectorAll(".nav-item").forEach((button) => {
  button.addEventListener("click", () => switchView(button.dataset.view));
});

document.querySelectorAll(".seg").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".seg").forEach((seg) => seg.classList.remove("active"));
    button.classList.add("active");
  });
});

updateClock();
setInterval(updateClock, 1000);
animateCounts();
initChart();
bindStarButtons();
renderSaved();
setupPortfolioModal();
setupLoginEntry();
loadDashboardData();
