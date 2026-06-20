// dashboard.js — Your prediction charts + live WHO GHO data charts

document.addEventListener("DOMContentLoaded", () => {
  Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";
  Chart.defaults.color       = "#64748b";

  // ── 1. Your predictions: Donut ──────────────────────────────
  const donutCtx = document.getElementById("donutChart");
  if (donutCtx) {
    new Chart(donutCtx, {
      type: "doughnut",
      data: {
        labels: ["Low Risk", "Moderate Risk", "High Risk"],
        datasets: [{ data:[LOW,MODERATE,HIGH], backgroundColor:["#16a34a","#ea580c","#dc2626"], borderWidth:2, borderColor:"#fff", hoverOffset:6 }]
      },
      options: { responsive:true, maintainAspectRatio:false, cutout:"65%", plugins:{ legend:{ position:"bottom", labels:{padding:16,font:{size:12}} } } }
    });
  }

  // ── 2. Your predictions: Trend ──────────────────────────────
  const trendCtx = document.getElementById("trendChart");
  if (trendCtx) {
    new Chart(trendCtx, {
      type: "line",
      data: {
        labels: SCORES.map((_,i) => "#"+(i+1)),
        datasets:[{ label:"Risk Score (%)", data:SCORES, borderColor:"#e63946", backgroundColor:"rgba(230,57,70,0.08)", tension:0.4, fill:true, pointBackgroundColor:"#e63946", pointRadius:4 }]
      },
      options:{ responsive:true, maintainAspectRatio:false, scales:{ y:{min:0,max:100,grid:{color:"#f1f5f9"}}, x:{grid:{display:false}} }, plugins:{legend:{display:false}} }
    });
  }

  // ── Stagger card animations ──────────────────────────────────
  document.querySelectorAll(".stat-card,.chart-card,.table-card").forEach((el,i) => {
    el.style.animationDelay = (i*60)+"ms";
  });

  // ── 3-5. WHO Live Data ───────────────────────────────────────
  loadWHOData();
});


async function loadWHOData() {
  const badge   = document.getElementById("whoBadge");
  const credit  = document.getElementById("whoCredit");

  try {
    const res  = await fetch("/api/who-data");
    const data = await res.json();

    // Update badge
    badge.innerHTML = '<span class="who-dot live"></span> Live WHO GHO Data';
    badge.classList.add("live");

    // Show credit
    if (credit) {
      document.getElementById("whoSource").textContent  = data.source || "WHO GHO";
      document.getElementById("whoFetched").textContent = data.fetched_at || "";
      credit.style.display = "block";
    }

    // ── 3. Regional Bar ────────────────────────────────────────
    const regionalCtx = document.getElementById("regionalBar");
    if (regionalCtx && data.regional) {
      const sorted  = [...data.regional].sort((a,b) => b.rate - a.rate);
      const palette = ["#dc2626","#ea580c","#f59e0b","#16a34a","#2563eb","#7c3aed"];
      new Chart(regionalCtx, {
        type: "bar",
        data: {
          labels:   sorted.map(d => d.region),
          datasets: [{
            label: "NCD Mortality Probability (%)",
            data:  sorted.map(d => d.rate),
            backgroundColor: sorted.map((_,i) => palette[i % palette.length] + "cc"),
            borderColor:     sorted.map((_,i) => palette[i % palette.length]),
            borderWidth: 1.5,
            borderRadius: 6,
          }]
        },
        options: {
          responsive:true, maintainAspectRatio:false,
          scales:{ y:{grid:{color:"#f1f5f9"},ticks:{callback:v=>v+"%"}}, x:{grid:{display:false}} },
          plugins:{ legend:{display:false}, tooltip:{ callbacks:{ label:ctx=>` ${ctx.parsed.y}% probability` } } }
        }
      });
    }

    // ── 4. Global Trend Line ───────────────────────────────────
    const trendLineCtx = document.getElementById("trendLine");
    if (trendLineCtx && data.trend) {
      new Chart(trendLineCtx, {
        type: "line",
        data: {
          labels: data.trend.map(d => d.year),
          datasets:[{
            label: "CVD Death Rate",
            data:  data.trend.map(d => d.rate),
            borderColor: "#2563eb",
            backgroundColor: "rgba(37,99,235,0.07)",
            tension: 0.4, fill: true,
            pointBackgroundColor: "#2563eb", pointRadius: 4,
          }]
        },
        options:{
          responsive:true, maintainAspectRatio:false,
          scales:{ y:{ grid:{color:"#f1f5f9"}, ticks:{callback:v=>v+"%"} }, x:{grid:{display:false}} },
          plugins:{ legend:{display:false}, tooltip:{ callbacks:{ label:ctx=>` ${ctx.parsed.y}% mortality` } } }
        }
      });
    }

    // ── India Charts ───────────────────────────────────────────
    if (data.india) renderIndiaCharts(data.india);

    // ── 5. Top Countries Horizontal Bar ───────────────────────
    const topCtx = document.getElementById("topCountries");
    if (topCtx && data.top_countries) {
      const sorted2 = [...data.top_countries].sort((a,b) => b.rate - a.rate);
      new Chart(topCtx, {
        type: "bar",
        data: {
          labels:   sorted2.map(d => d.country),
          datasets: [{
            label: "NCD Mortality %",
            data:  sorted2.map(d => d.rate),
            backgroundColor: "rgba(220,38,38,0.75)",
            borderColor: "#dc2626",
            borderWidth: 1,
            borderRadius: 4,
          }]
        },
        options:{
          indexAxis: "y",
          responsive:true, maintainAspectRatio:false,
          scales:{
            x:{ grid:{color:"#f1f5f9"}, ticks:{callback:v=>v+"%"} },
            y:{ grid:{display:false}, ticks:{font:{size:11}} }
          },
          plugins:{ legend:{display:false}, tooltip:{ callbacks:{ label:ctx=>` ${ctx.parsed.x}%` } } }
        }
      });
    }

  } catch (err) {
    console.error("WHO data fetch failed:", err);
    badge.innerHTML = '<span class="who-dot error"></span> WHO data unavailable (offline fallback shown)';
    badge.classList.add("error");
    // Charts will still render using fallback data from the Flask route
    loadWHOData_fallback();
  }
}

async function loadWHOData_fallback() {
  // If fetch itself failed (e.g. Flask not running), show empty state gracefully
  ["regionalBar","trendLine","topCountries"].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    const parent = el.parentElement;
    parent.innerHTML = '<div style="height:100%;display:flex;align-items:center;justify-content:center;color:#94a3b8;font-size:0.85rem;">WHO data unavailable — check your connection</div>';
  });
}

function renderIndiaCharts(india) {
  // Update stat cards
  const rateEl = document.getElementById("indiaRate");
  const yearEl = document.getElementById("indiaYear");
  const badge  = document.getElementById("indiaBadge");
  const ctxTxt = document.getElementById("indiaContextText");

  if (rateEl) rateEl.textContent = india.latest_rate + "%";
  if (yearEl) yearEl.textContent = `age 30–70, both sexes (${india.latest_year})`;
  if (badge)  {
    badge.innerHTML = `<span class="who-dot live"></span> WHO GHO Data`;
    badge.classList.add("live");
  }
  if (ctxTxt) ctxTxt.textContent = india.rank_context;

  // India Trend Line
  const indiaTrendCtx = document.getElementById("indiaTrend");
  if (indiaTrendCtx && india.trend) {
    new Chart(indiaTrendCtx, {
      type: "line",
      data: {
        labels: india.trend.map(d => d.year),
        datasets: [{
          label: "India CVD Mortality %",
          data:  india.trend.map(d => d.rate),
          borderColor: "#f97316",
          backgroundColor: "rgba(249,115,22,0.08)",
          tension: 0.4, fill: true,
          pointBackgroundColor: "#f97316", pointRadius: 5,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: {
          y: { grid: { color: "#f1f5f9" }, ticks: { callback: v => v + "%" } },
          x: { grid: { display: false } }
        },
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y}% mortality probability` } }
        }
      }
    });
  }

  // India Risk Factors horizontal bar
  const indiaRFCtx = document.getElementById("indiaRiskFactors");
  if (indiaRFCtx) {
    new Chart(indiaRFCtx, {
      type: "bar",
      data: {
        labels: ["Hypertension", "Diabetes", "Tobacco Use", "Obesity", "Air Pollution", "Physical Inactivity", "High Cholesterol"],
        datasets: [{
          label: "Prevalence among CVD patients (%)",
          data: [67, 42, 38, 31, 28, 55, 44],
          backgroundColor: [
            "rgba(220,38,38,0.75)", "rgba(234,88,12,0.75)", "rgba(161,98,7,0.75)",
            "rgba(101,163,13,0.75)", "rgba(8,145,178,0.75)", "rgba(79,70,229,0.75)",
            "rgba(168,85,247,0.75)"
          ],
          borderRadius: 5,
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true, maintainAspectRatio: false,
        scales: {
          x: { grid: { color: "#f1f5f9" }, ticks: { callback: v => v + "%" }, max: 100 },
          y: { grid: { display: false }, ticks: { font: { size: 11 } } }
        },
        plugins: { legend: { display: false } }
      }
    });
  }
}