const pageMeta = {
  overview: ["개요", "오늘의 시장 신호와 주요 뉴스를 한눈에 확인합니다."],
  market: ["시장 신호", "시장 위험도와 핵심 지표를 함께 해석합니다."],
  industry: ["산업 영향도", "산업별 영향 점수와 근거 뉴스를 확인합니다."],
  guard: ["뉴스 가드", "뉴스 영향도와 신뢰도를 분리해 검증합니다."],
  portfolio: ["포트폴리오", "관심 자산과 연결된 시장 신호를 요약합니다."],
  kakao: ["카카오 알림", "카카오 채널 봇 알림 조건과 발송 내역을 관리합니다."],
  briefing: ["AI 브리핑", "오늘의 해석과 판단 기준을 확인합니다."],
  settings: ["설정", "관심 시장과 알림 기준을 개인화합니다."],
};

function updateHeader(view) {
  const [titleText, descText] = pageMeta[view] || pageMeta.overview;
  const title = document.querySelector("#pageTitle");
  const desc = document.querySelector("#pageDesc");
  if (title) title.textContent = titleText;
  if (desc) desc.textContent = descText;
}

function switchView(view) {
  document.querySelectorAll(".nav-item").forEach((item) => {
    item.classList.toggle("active", item.dataset.view === view);
  });
  document.querySelectorAll(".view").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `view-${view}`);
  });
  updateHeader(view);
}

function initNavigation() {
  document.querySelectorAll("[data-view]").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view));
  });
  document.querySelectorAll("[data-view-shortcut]").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.viewShortcut));
  });
}

function initFilters() {
  document.querySelectorAll(".market-filter .filter, .filter-row .filter").forEach((button) => {
    button.addEventListener("click", () => {
      const group = button.parentElement;
      group.querySelectorAll(".filter").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
    });
  });
}

function initChart() {
  const canvas = document.querySelector("#signalChart");
  if (!canvas || typeof Chart === "undefined") return;

  new Chart(canvas, {
    type: "line",
    data: {
      labels: ["1일", "5일", "10일", "15일", "20일", "25일", "30일"],
      datasets: [
        {
          label: "시장 감성",
          data: [64, 59, 62, 54, 49, 58, 52],
          borderColor: "#3aafb9",
          backgroundColor: "rgba(58, 175, 185, 0.18)",
          fill: true,
          tension: 0.35,
          pointRadius: 2,
        },
        {
          label: "위험도",
          data: [44, 47, 45, 58, 66, 61, 68],
          borderColor: "#f04452",
          tension: 0.35,
          pointRadius: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: "#9fc7cb", boxWidth: 10 } } },
      scales: {
        x: { ticks: { color: "#9fc7cb" }, grid: { color: "rgba(255, 255, 255, 0.06)" } },
        y: { ticks: { color: "#9fc7cb" }, grid: { color: "rgba(255, 255, 255, 0.06)" }, min: 30, max: 80 },
      },
    },
  });
}

function setupPortfolioModal() {
  const modal = document.querySelector("[data-modal='asset']");
  const open = document.querySelector("#addAssetBtn");
  const save = document.querySelector("#saveAssetBtn");
  if (!modal || !open || !save) return;

  const closeModal = () => {
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
  };

  const openModal = () => {
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.querySelector("#assetName")?.focus();
  };

  open.addEventListener("click", openModal);
  document.querySelectorAll(".modal-close, [data-modal-close]").forEach((button) => {
    button.addEventListener("click", closeModal);
  });

  save.addEventListener("click", () => {
    const name = document.querySelector("#assetName").value.trim() || "신규 자산";
    const sector = document.querySelector("#assetSector").value.trim() || "미지정";
    const table = document.querySelector("#portfolioTable");
    table.insertAdjacentHTML(
      "beforeend",
      `<tr><td>${name}</td><td>${sector}</td><td>관심 신호</td><td>0건</td></tr>`,
    );
    document.querySelector("#assetCount").textContent = table.querySelectorAll("tr").length;
    document.querySelector("#assetName").value = "";
    document.querySelector("#assetSector").value = "";
    closeModal();
  });
}

initNavigation();
initFilters();
initChart();
setupPortfolioModal();
