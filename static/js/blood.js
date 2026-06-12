document.addEventListener("DOMContentLoaded", () => {
  const dropZone  = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");
  const preview   = document.getElementById("filePreview");
  const fpName    = document.getElementById("fpName");
  const fpSize    = document.getElementById("fpSize");
  const uploadBtn = document.getElementById("uploadBtn");

  if (!dropZone) return;

  // Drag events
  dropZone.addEventListener("dragover",  e => { e.preventDefault(); dropZone.classList.add("drag-over"); });
  dropZone.addEventListener("dragleave", ()=> dropZone.classList.remove("drag-over"));
  dropZone.addEventListener("drop", e => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    if (e.dataTransfer.files[0]) {
      fileInput.files = e.dataTransfer.files;
      showPreview(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) showPreview(fileInput.files[0]);
  });

  function showPreview(file) {
    fpName.textContent = file.name;
    fpSize.textContent = (file.size / 1024).toFixed(1) + " KB";
    preview.style.display = "flex";
    dropZone.querySelector(".dz-text").textContent = "File selected ✓";
  }

  document.getElementById("uploadForm")?.addEventListener("submit", () => {
    if (uploadBtn) {
      uploadBtn.textContent = "⏳ Analysing with Gemini...";
      uploadBtn.disabled = true;
    }
  });
});
