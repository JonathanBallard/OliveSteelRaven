// recipes/static/recipes/js/recipe_form/ingredients.js
(function () {
  const addBtn = document.getElementById("add-ingredient-btn");
  const container = document.getElementById("ingredient-forms");
  const template = document.getElementById("empty-ingredient-form-template");

  // Prefix must match your view: prefix="ingredients"
  const totalFormsInput = document.getElementById("id_ingredients-TOTAL_FORMS");

  // Optional: renumber right before submit
  const formEl = container?.closest("form");

  if (!addBtn || !container || !template || !totalFormsInput) return;

  /**
   * Renumber line_order for all ACTIVE (non-deleted, visible) ingredient forms
   * based on their current DOM order.
   *
   * - Skips forms marked DELETE (checked)
   * - Skips forms that are display:none
   * - Sets line_order to 1..N
   */
  function updateLineOrders() {
    let order = 1;

    container.querySelectorAll(".ingredient-form").forEach((row) => {
      // If hidden, skip
      if (row.style.display === "none") return;

      // If marked for deletion, skip
      const deleteField = row.querySelector('input[name$="-DELETE"]');
      if (deleteField && deleteField.checked) return;

      // Find the line_order input
      const lineOrderInput = row.querySelector('input[name$="-line_order"]');
      if (lineOrderInput) {
        lineOrderInput.value = String(order);
      }

      // Update visible display (if present)
      const orderDisplay = row.querySelector(".ingredient-order-display");
      if (orderDisplay) {
        orderDisplay.textContent = String(order);
      }

      order += 1;
    });
  }

  function wireRemoveButton(row) {
    const removeBtn = row.querySelector(".remove-ingredient-btn");
    const deleteField = row.querySelector('input[name$="-DELETE"]');

    if (!removeBtn) return;

    removeBtn.addEventListener("click", () => {
      // Prevent double-click weirdness while animating
      if (row.classList.contains("ingredient-removing")) return;

      // Respect reduced motion: skip animation and do the action immediately
      const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

      const finalizeRemoval = () => {
        // Existing line: mark DELETE + hide
        if (deleteField) {
          // Mark DELETE immediately, regardless of widget type
          if (deleteField.type === "checkbox") {
            deleteField.checked = true;
          } else {
            // Hidden input or non-checkbox DELETE field
            deleteField.value = "on";
          }

          // Hide but DO NOT remove existing forms from DOM
          row.style.display = "none";
        } else {
          // Only remove brand-new, unsaved rows
          const idField = row.querySelector('input[name$="-id"]');
          if (idField && idField.value) {
            console.warn("Refusing to remove existing ingredient row without DELETE field");
            return;
          }
          row.remove();
        }

        // ✅ Keep line_order consistent after removal
        updateLineOrders();
      };

      if (prefersReduced) {
        finalizeRemoval();
        return;
      }

      // Animate out, then finalize
      row.classList.add("ingredient-removing");
      row.addEventListener("animationend", finalizeRemoval, { once: true });
    });
  }

  // Wire existing rows
  container.querySelectorAll(".ingredient-form").forEach(wireRemoveButton);

  // ✅ Initial numbering on load (important for edit pages)
  updateLineOrders();

  // ✅ Final safety pass on submit (covers odd cases)
  if (formEl) {
    formEl.addEventListener("submit", () => updateLineOrders());
  }

  addBtn.addEventListener("click", () => {
    const formIndex = parseInt(totalFormsInput.value, 10);

    // Clone template HTML and replace __prefix__ with index
    const html = template.innerHTML.replaceAll("__prefix__", String(formIndex));

    const wrapper = document.createElement("div");
    wrapper.innerHTML = html.trim();
    const newRow = wrapper.firstElementChild;
    if (!newRow) return;

    container.appendChild(newRow);
    wireRemoveButton(newRow);

    // Increment TOTAL_FORMS
    totalFormsInput.value = String(formIndex + 1);

    // ✅ Renumber after add so the new row gets the correct order
    updateLineOrders();

    // Animate in
    newRow.classList.add("ingredient-just-added");
    newRow.scrollIntoView({ behavior: "smooth", block: "nearest" });
    newRow.addEventListener(
      "animationend",
      () => newRow.classList.remove("ingredient-just-added"),
      { once: true }
    );
  });
})();
