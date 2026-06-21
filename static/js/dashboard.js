// dashboard.js — Your prediction charts + live WHO GHO data charts

const EMPTY_ICON_CHART = '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/></svg>';

document.addEventListener("DOMContentLoaded", () => {
  Chart.defaults.font.family = "'Inter', system-ui, sans-serif";
  Chart.defaults.color       = "#767b8a";

  // ── 1. Your predictions: Donut ──────────────────────────────
  const donutCtx = document.getElementById("donutChart");
  if (donutCtx && (LOW + MODERATE + HIGH) === 0) {
    donutCtx.parentElement.innerHTML = `<div class="empty-chart">${EMPTY_ICON_CHART}<div>No predictions yet<br><a href="/predict">Run your first assessment</a></div></div>`;
  } else if (donutCtx) {
    new Chart(donutCtx, {
      type: "doughnut",
      data: {
        labels: ["Low Risk", "Moderate Risk", "High Risk"],
        datasets: [{ data:[LOW,MODERATE,HIGH], backgroundColor:["#1a9e5c","#d97a1f","#d62839"], borderWidth:2, borderColor:"#fff", hoverOffset:6 }]
      },
      options: { responsive:true, maintainAspectRatio:false, cutout:"68%", plugins:{ legend:{ position:"bottom", labels:{padding:16,font:{size:12},usePointStyle:true,pointStyle:"circle"} } } }
    });
  }

  // ── 2. Your predictions: Trend ──────────────────────────────
  const trendCtx = document.getElementById("trendChart");
  if (trendCtx && SCORES.length === 0) {
    trendCtx.parentElement.innerHTML = `<div class="empty-chart">${EMPTY_ICON_CHART}<div>No trend data yet<br><a href="/predict">Run your first assessment</a></div></div>`;
  } else if (trendCtx) {
    new Chart(trendCtx, {
      type: "line",
      data: {
        labels: SCORES.map((_,i) => "#"+(i+1)),
        datasets:[{ label:"Risk Score (%)", data:SCORES, borderColor:"#d62839", backgroundColor:"rgba(214,40,57,0.07)", tension:0.4, fill:true, pointBackgroundColor:"#d62839", pointRadius:4, borderWidth:2.5 }]
      },
      options:{ responsive:true, maintainAspectRatio:false, scales:{ y:{min:0,max:100,grid:{color:"#f0eee8"}}, x:{grid:{display:false}} }, plugins:{legend:{display:false}} }
    });
  }

  // ── Stagger card animations ──────────────────────────────────
  document.querySelectorAll(".stat-card,.chart-card,.table-card").forEach((el,i) => {
    el.style.animationDelay = (i*55)+"ms";
  });

  // ── WHO Live Data ───────────────────────────────────────────
  loadWHOData();
});


async function loadWHOData() {
  const badge   = document.getElementById("whoBadge");
  const credit  = document.getElementById("whoCredit");

  try {
    const res  = await fetch("/api/who-data");
    const data = await res.json();

    badge.innerHTML = `<span class="who-dot live"></span> Live WHO GHO Data`;
    badge.classList.add("live");

    if (credit) {
      document.getElementById("whoSource").textContent  = data.source || "WHO GHO";
      document.getElementById("whoFetched").textContent = data.fetched_at || "";
      credit.style.display = "flex";
    }

    // Regional Bar
    const regionalCtx = document.getElementById("regionalBar");
    if (regionalCtx && data.regional) {
      const sorted  = [...data.regional].sort((a,b) => b.rate - a.rate);
      const palette = ["#d62839","#d97a1f","#e0a83e","#1a9e5c","#3d6b8c","#7c5cbf"];
      new Chart(regionalCtx, {
        type: "bar",
        data: {
          labels:   sorted.map(d => d.region),
          datasets: [{
            label: "NCD Mortality Probability (%)",
            data:  sorted.map(d => d.rate),
            backgroundColor: sorted.map((_,i) => palette[i % palette.length] + "cc"),
            borderColor:     sorted.map((_,i) => palette[i % palette.length]),
            borderWidth: 1.5, borderRadius: 6,
          }]
        },
        options: {
          responsive:true, maintainAspectRatio:false,
          scales:{ y:{grid:{color:"#f0eee8"},ticks:{callback:v=>v+"%"}}, x:{grid:{display:false}} },
          plugins:{ legend:{display:false}, tooltip:{ callbacks:{ label:ctx=>` ${ctx.parsed.y}% probability` } } }
        }
      });
    }

    if (data.india) renderIndiaCharts(data.india);

    // Top Countries
    const topCtx = document.getElementById("topCountries");
    if (topCtx && data.top_countries) {
      const sorted2 = [...data.top_countries].sort((a,b) => b.rate - a.rate);
      new Chart(topCtx, {
        type: "bar",
        data: {
          labels:   sorted2.map(d => d.country),
          datasets: [{ label: "NCD Mortality %", data: sorted2.map(d => d.rate), backgroundColor: "rgba(214,40,57,0.75)", borderColor: "#d62839", borderWidth: 1, borderRadius: 4 }]
        },
        options:{
          indexAxis: "y", responsive:true, maintainAspectRatio:false,
          scales:{ x:{ grid:{color:"#f0eee8"}, ticks:{callback:v=>v+"%"} }, y:{ grid:{display:false}, ticks:{font:{size:11}} } },
          plugins:{ legend:{display:false}, tooltip:{ callbacks:{ label:ctx=>` ${ctx.parsed.x}%` } } }
        }
      });
    }

    // Global Trend Line
    const trendLineCtx = document.getElementById("trendLine");
    if (trendLineCtx && data.trend) {
      new Chart(trendLineCtx, {
        type: "line",
        data: {
          labels: data.trend.map(d => d.year),
          datasets:[{ label: "CVD Death Rate", data: data.trend.map(d => d.rate), borderColor: "#3d6b8c", backgroundColor: "rgba(61,107,140,0.07)", tension: 0.4, fill: true, pointBackgroundColor: "#3d6b8c", pointRadius: 4, borderWidth: 2.5 }]
        },
        options:{
          responsive:true, maintainAspectRatio:false,
          scales:{ y:{ grid:{color:"#f0eee8"}, ticks:{callback:v=>v+"%"} }, x:{grid:{display:false}} },
          plugins:{ legend:{display:false}, tooltip:{ callbacks:{ label:ctx=>` ${ctx.parsed.y}% mortality` } } }
        }
      });
    }

  } catch (err) {
    console.error("WHO data fetch failed:", err);
    badge.innerHTML = `<span class="who-dot error"></span> WHO data unavailable`;
    badge.classList.add("error");
    ["regionalBar","trendLine","topCountries"].forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      el.parentElement.innerHTML = `<div class="empty-chart">${EMPTY_ICON_CHART}<div>WHO data unavailable — check connection</div></div>`;
    });
  }
}

function renderIndiaCharts(india) {
  const rateEl = document.getElementById("indiaRate");
  const yearEl = document.getElementById("indiaYear");
  const badge  = document.getElementById("indiaBadge");
  const ctxTxt = document.getElementById("indiaContextText");

  if (rateEl) rateEl.textContent = india.latest_rate + "%";
  if (yearEl) yearEl.textContent = `age 30–70, both sexes (${india.latest_year})`;
  if (badge)  { badge.innerHTML = `<span class="who-dot live"></span> WHO GHO Data`; badge.classList.add("live"); }
  if (ctxTxt) ctxTxt.textContent = india.rank_context;

  const indiaTrendCtx = document.getElementById("indiaTrend");
  if (indiaTrendCtx && india.trend) {
    new Chart(indiaTrendCtx, {
      type: "line",
      data: {
        labels: india.trend.map(d => d.year),
        datasets: [{ label: "India CVD Mortality %", data: india.trend.map(d => d.rate), borderColor: "#d97a1f", backgroundColor: "rgba(217,122,31,0.08)", tension: 0.4, fill: true, pointBackgroundColor: "#d97a1f", pointRadius: 5, borderWidth: 2.5 }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: { y: { grid: { color: "#f0eee8" }, ticks: { callback: v => v + "%" } }, x: { grid: { display: false } } },
        plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y}% mortality probability` } } }
      }
    });
  }

  const indiaRFCtx = document.getElementById("indiaRiskFactors");
  if (indiaRFCtx) {
    new Chart(indiaRFCtx, {
      type: "bar",
      data: {
        labels: ["Hypertension", "Diabetes", "Tobacco Use", "Obesity", "Air Pollution", "Inactivity", "High Cholesterol"],
        datasets: [{
          label: "Prevalence (%)", data: [67, 42, 38, 31, 28, 55, 44],
          backgroundColor: ["rgba(214,38,57,0.75)","rgba(217,122,31,0.75)","rgba(184,134,11,0.75)","rgba(101,163,13,0.75)","rgba(8,145,178,0.75)","rgba(79,70,229,0.75)","rgba(168,85,247,0.75)"],
          borderRadius: 5,
        }]
      },
      options: {
        indexAxis: "y", responsive: true, maintainAspectRatio: false,
        scales: { x: { grid: { color: "#f0eee8" }, ticks: { callback: v => v + "%" }, max: 100 }, y: { grid: { display: false }, ticks: { font: { size: 11 } } } },
        plugins: { legend: { display: false } }
      }
    });
  }
}
