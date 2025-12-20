(() => {
  const valueEl = document.getElementById("dialValue");
  const inputEl = document.getElementById("dialInput");
  const grid = document.getElementById("dialGrid");
  const back = document.getElementById("backspace");
  if (!valueEl || !inputEl || !grid || !back) return;

  const setVal = (v) => { valueEl.textContent = v; inputEl.value = v; };

  grid.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-key]");
    if (!btn) return;
    const k = btn.dataset.key;
    setVal(inputEl.value + k);
  });

  back.addEventListener("click", () => {
    const v = inputEl.value;
    setVal(v.length > 0 ? v.slice(0, -1) : v);
  });
})();
