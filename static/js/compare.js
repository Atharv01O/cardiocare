document.addEventListener("DOMContentLoaded", () => {
  const ctx = document.getElementById("scoreBar");
  if (!ctx) return;

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Past Report\n" + OLD_DATE, "New Report\n" + NEW_DATE],
      datasets: [{
        label: "Risk Score (%)",
        data: [OLD_SCORE, NEW_SCORE],
        backgroundColor: [
          "rgba(100, 116, 139, 0.7)",
          NEW_SCORE < OLD_SCORE ? "rgba(22, 163, 74, 0.75)" :
          NEW_SCORE > OLD_SCORE ? "rgba(220, 38, 38, 0.75)" :
                                  "rgba(69, 123, 157, 0.75)"
        ],
        borderColor: [
          "#64748b",
          NEW_SCORE < OLD_SCORE ? "#16a34a" :
          NEW_SCORE > OLD_SCORE ? "#dc2626" : "#457b9d"
        ],
        borderWidth: 2,
        borderRadius: 8,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        y: { min: 0, max: 100, grid: { color: "#f1f5f9" }, ticks: { callback: v => v + "%" } },
        x: { grid: { display: false } }
      },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` Score: ${ctx.parsed.y}%` } }
      }
    }
  });

  // stagger rows
  document.querySelectorAll(".fade-row").forEach((el, i) => {
    el.style.animationDelay = `${i * 40}ms`;
  });
});
