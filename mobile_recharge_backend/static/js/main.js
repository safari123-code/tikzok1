(() => {
  const btn = document.getElementById("menuBtn");
  const menu = document.getElementById("navMenu");
  if (!btn || !menu) return;

  btn.addEventListener("click", () => {
    menu.classList.toggle("is-open");
  });
})();
