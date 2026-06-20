// Universal count-up animation for stat numbers
// Usage: add class="count-up" and data-target="123" to any element

function animateCountUp(el, target, duration = 900, decimals = 0) {
  const start = 0;
  const startTime = performance.now();

  function tick(now) {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    const value = start + (target - start) * eased;
    el.textContent = decimals > 0 ? value.toFixed(decimals) : Math.round(value);
    if (progress < 1) requestAnimationFrame(tick);
    else el.textContent = decimals > 0 ? target.toFixed(decimals) : target;
  }
  requestAnimationFrame(tick);
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".count-up[data-target]").forEach(el => {
    const target   = parseFloat(el.dataset.target);
    const decimals = parseInt(el.dataset.decimals || "0");
    animateCountUp(el, target, 900, decimals);
  });
});
