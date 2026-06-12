document.addEventListener("DOMContentLoaded", () => {

  // ── Gauge (semi-circle) ──────────────────────────────────────
  const gaugeCtx = document.getElementById("gaugeChart");
  if (!gaugeCtx) return;

  const score     = RISK_SCORE;
  const colorMap  = { green: "#16a34a", orange: "#ea580c", red: "#dc2626" };
  const fillColor = colorMap[RISK_COLOR] || "#e63946";

  new Chart(gaugeCtx, {
    type: "doughnut",
    data: {
      datasets: [{
        data: [score, 100 - score],
        backgroundColor: [fillColor, "#f1f5f9"],
        borderWidth: 0,
        circumference: 180,
        rotation: 270,
      }]
    },
    options: {
      responsive: false,
      cutout: "72%",
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false },
      }
    },
    plugins: [{
      id: "gaugeText",
      afterDraw(chart) {
        const { ctx, chartArea: { left, right, top, bottom } } = chart;
        const cx = (left + right) / 2;
        const cy = bottom - 10;
        ctx.save();
        ctx.font = "bold 28px 'Segoe UI'";
        ctx.fillStyle = fillColor;
        ctx.textAlign = "center";
        ctx.fillText(score.toFixed(1) + "%", cx, cy);
        ctx.font = "12px 'Segoe UI'";
        ctx.fillStyle = "#94a3b8";
        ctx.fillText("Risk Score", cx, cy + 20);
        ctx.restore();
      }
    }]
  });

  // ── Animate result cards ─────────────────────────────────────
  document.querySelectorAll(".result-card,.summary-card,.gauge-card").forEach((el, i) => {
    el.style.opacity = "0";
    el.style.transform = "translateY(16px)";
    setTimeout(() => {
      el.style.transition = "0.45s ease";
      el.style.opacity = "1";
      el.style.transform = "translateY(0)";
    }, 150 + i * 100);
  });
});
