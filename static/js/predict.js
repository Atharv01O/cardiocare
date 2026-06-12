document.addEventListener("DOMContentLoaded", () => {
  const form      = document.getElementById("predictForm");
  const submitBtn = document.getElementById("submitBtn");
  const btnText   = document.getElementById("btnText");

  if (!form) return;

  form.addEventListener("submit", (e) => {
    let valid = true;
    form.querySelectorAll("input, select").forEach(el => {
      el.classList.remove("invalid");
      if (!el.value && el.value !== "0") {
        el.classList.add("invalid");
        valid = false;
      }
    });
    if (!valid) {
      e.preventDefault();
      alert("Please fill in all fields before submitting.");
      return;
    }
    btnText.textContent = "⏳ Analysing...";
    submitBtn.disabled = true;
  });

  // Live range hints on number inputs
  form.querySelectorAll("input[type=number]").forEach(inp => {
    inp.addEventListener("input", () => {
      const min = parseFloat(inp.min), max = parseFloat(inp.max), val = parseFloat(inp.value);
      if (!isNaN(min) && !isNaN(max) && (val < min || val > max)) {
        inp.classList.add("invalid");
      } else {
        inp.classList.remove("invalid");
      }
    });
  });
});
