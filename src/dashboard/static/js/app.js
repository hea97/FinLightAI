async function loadDashboard() {
  const [signalsResponse, newsResponse] = await Promise.all([fetch("/api/signals"), fetch("/api/news")]);
  const signals = await signalsResponse.json();
  const news = await newsResponse.json();
  const latest = signals[0];
  document.querySelector("#signal").textContent = `${latest.ticker} ${latest.signal} | reliability ${latest.reliability_score}`;
  document.querySelector("#news").innerHTML = news
    .map((item) => `<li>${item.source}: ${item.title} (${item.reliability_score})</li>`)
    .join("");
}

loadDashboard();
