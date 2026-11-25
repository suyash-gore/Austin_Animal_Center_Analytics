/* Austin Animal Center — presentation controller (no dependencies).
   Keys: → / Space / PageDown = next · ← / PageUp = previous · Home / End · F = full screen · N = presenter notes
   URL hash #1…#10 opens a specific slide. */
(function () {
  "use strict";
  const BASE_W = 1600, BASE_H = 900, BAR_H = 64;
  const stage = document.querySelector(".stage");
  const slides = Array.from(document.querySelectorAll(".slide"));
  const counter = document.getElementById("counter");
  const progress = document.getElementById("progress");
  const titleNow = document.getElementById("title-now");
  const dots = document.getElementById("dots");
  const notes = document.getElementById("notes");
  const notesBody = document.getElementById("notes-body");
  let current = 0;

  slides.forEach((s, i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.setAttribute("aria-label", "Go to slide " + (i + 1) + ": " + (s.dataset.title || ""));
    b.addEventListener("click", () => show(i));
    dots.appendChild(b);
  });

  function pad(n) { return String(n).padStart(2, "0"); }

  function show(i, fromHash) {
    current = Math.max(0, Math.min(slides.length - 1, i));
    slides.forEach((s, j) => {
      s.classList.toggle("active", j === current);
      s.classList.toggle("before", j < current);
      s.setAttribute("aria-hidden", j === current ? "false" : "true");
    });
    Array.from(dots.children).forEach((b, j) => b.classList.toggle("active", j === current));
    counter.textContent = pad(current + 1) + " / " + pad(slides.length);
    progress.style.width = ((current + 1) / slides.length * 100) + "%";
    titleNow.textContent = slides[current].dataset.title || "";
    const n = slides[current].querySelector(".speaker");
    notesBody.innerHTML = n ? n.innerHTML : "";
    slides[current].scrollTop = 0;
    if (!fromHash && location.hash !== "#" + (current + 1)) history.replaceState(null, "", "#" + (current + 1));
  }

  function fit() {
    if (window.innerWidth <= 900) { stage.style.transform = "none"; return; }
    const scale = Math.min(window.innerWidth / (BASE_W + 48), (window.innerHeight - BAR_H) / (BASE_H + 36));
    stage.style.transform = "scale(" + scale + ")";
  }

  function toggleFullscreen() {
    if (!document.fullscreenElement) document.documentElement.requestFullscreen && document.documentElement.requestFullscreen();
    else document.exitFullscreen && document.exitFullscreen();
  }

  document.addEventListener("keydown", (e) => {
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    const k = e.key;
    if (k === "ArrowRight" || k === " " || k === "PageDown") { e.preventDefault(); show(current + 1); }
    else if (k === "ArrowLeft" || k === "PageUp") { e.preventDefault(); show(current - 1); }
    else if (k === "Home") { e.preventDefault(); show(0); }
    else if (k === "End") { e.preventDefault(); show(slides.length - 1); }
    else if (k === "f" || k === "F") { toggleFullscreen(); }
    else if (k === "n" || k === "N") { notes.classList.toggle("open"); }
  });

  document.getElementById("prev").addEventListener("click", () => show(current - 1));
  document.getElementById("next").addEventListener("click", () => show(current + 1));
  document.getElementById("fs").addEventListener("click", toggleFullscreen);
  document.getElementById("notes-btn").addEventListener("click", () => notes.classList.toggle("open"));

  // swipe on touch screens
  let x0 = null;
  document.addEventListener("touchstart", (e) => { x0 = e.touches[0].clientX; }, { passive: true });
  document.addEventListener("touchend", (e) => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 60) show(current + (dx < 0 ? 1 : -1));
    x0 = null;
  }, { passive: true });

  window.addEventListener("resize", fit);
  window.addEventListener("hashchange", () => {
    const n = parseInt(location.hash.slice(1), 10);
    if (!isNaN(n)) show(n - 1, true);
  });

  fit();
  const start = parseInt(location.hash.slice(1), 10);
  show(isNaN(start) ? 0 : start - 1, true);
})();
