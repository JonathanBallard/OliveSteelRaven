// recipes/static/recipes/js/recipe_form/ingredients.js
(function () {
  const addBtn = document.getElementById("add-ingredient-btn");
  const container = document.getElementById("ingredient-forms");
  const template = document.getElementById("empty-ingredient-form-template");
  const totalFormsInput = document.getElementById("id_ingredients-TOTAL_FORMS");
  const formEl = container?.closest("form");

  if (!addBtn || !container || !template || !totalFormsInput) return;

  function getDeleteField(row) {
    return row.querySelector('input[name$="-DELETE"]');
  }

  function isMarkedForDelete(row) {
    const del = getDeleteField(row);
    if (!del) return false;

    if (del.type === "checkbox") return !!del.checked;

    const v = (del.value || "").toString().trim().toLowerCase();
    return v === "on" || v === "true" || v === "1" || v === "yes";
  }

  function markForDelete(row) {
    const del = getDeleteField(row);
    if (!del) return false;

    if (del.type === "checkbox") del.checked = true;
    else del.value = "on";

    return true;
  }

  function isExistingRow(row) {
    const idField = row.querySelector('input[name$="-id"]');
    return !!(idField && idField.value);
  }

  // Optional UI-only numbering (does NOT touch line_order field)
  function updateOrderDisplay() {
    let n = 1;
    container.querySelectorAll(".ingredient-form").forEach((row) => {
      if (row.style.display === "none") return;
      if (isMarkedForDelete(row)) return;

      const display = row.querySelector(".ingredient-order-display");
      if (display) display.textContent = String(n);
      n += 1;
    });
  }

  function wireRemoveButton(row) {
    const removeBtn = row.querySelector(".remove-ingredient-btn");
    if (!removeBtn) return;

    removeBtn.addEventListener("click", () => {
      if (row.classList.contains("ingredient-removing")) return;

      const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

      const finalizeRemoval = () => {
        if (isExistingRow(row)) {
          const ok = markForDelete(row);
          if (!ok) {
            console.warn("Existing ingredient row has no DELETE field; refusing to remove from DOM.");
            row.classList.remove("ingredient-removing");
            return;
          }

          // Keep it so id + DELETE still post
          row.style.display = "none";
          row.setAttribute("aria-hidden", "true");
        } else {
          // New unsaved row can be removed
          row.remove();
        }

        updateOrderDisplay();
      };

      if (prefersReduced) return finalizeRemoval();

      row.classList.add("ingredient-removing");
      row.addEventListener("animationend", finalizeRemoval, { once: true });
    });
  }

  // Wire existing rows
  container.querySelectorAll(".ingredient-form").forEach(wireRemoveButton);

  updateOrderDisplay();

  // Safety pass: ensure deletes are applied before submit (no ordering manipulation)
  if (formEl) {
    formEl.addEventListener("submit", () => updateOrderDisplay());
  }

  addBtn.addEventListener("click", () => {
    const formIndex = parseInt(totalFormsInput.value, 10);
    const html = template.innerHTML.replaceAll("__prefix__", String(formIndex));

    const wrapper = document.createElement("div");
    wrapper.innerHTML = html.trim();
    const newRow = wrapper.firstElementChild;
    if (!newRow) return;

    container.appendChild(newRow);
    wireRemoveButton(newRow);

    totalFormsInput.value = String(formIndex + 1);

    updateOrderDisplay();

    newRow.classList.add("ingredient-just-added");
    newRow.scrollIntoView({ behavior: "smooth", block: "nearest" });
    newRow.addEventListener(
      "animationend",
      () => newRow.classList.remove("ingredient-just-added"),
      { once: true }
    );
  });
})();
