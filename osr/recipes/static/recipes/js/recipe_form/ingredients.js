// recipes/static/recipes/js/recipe_form/ingredients.js
(function () {
  const addBtn = document.getElementById("add-ingredient-btn");
  const container = document.getElementById("ingredient-forms");
  const template = document.getElementById("empty-ingredient-form-template");

  // Prefix must match your view: prefix="ingredients"
  const totalFormsInput = document.getElementById("id_ingredients-TOTAL_FORMS");

  if (!addBtn || !container || !template || !totalFormsInput) return;

  function wireRemoveButton(formEl) {
    const removeBtn = formEl.querySelector(".remove-ingredient-btn");
    const deleteField = formEl.querySelector('input[type="checkbox"][name$="-DELETE"]');

    if (!removeBtn) return;

    removeBtn.addEventListener("click", () => {
      // Prevent double-click weirdness while animating
      if (formEl.classList.contains("ingredient-removing")) return;

      // Respect reduced motion: skip animation and do the action immediately
      const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

      const finalizeRemoval = () => {
        // Existing line: mark DELETE + hide
        if (deleteField) {
          deleteField.checked = true;
          formEl.style.display = "none";
        } else {
          // New unsaved line: remove DOM node
          formEl.remove();
        }
      };

      if (prefersReduced) {
        finalizeRemoval();
        return;
      }

      // Animate out, then finalize
      formEl.classList.add("ingredient-removing");
      formEl.addEventListener("animationend", finalizeRemoval, { once: true });
    });
  }

  // Wire existing rows
  container.querySelectorAll(".ingredient-form").forEach(wireRemoveButton);

  addBtn.addEventListener("click", () => {
    const formIndex = parseInt(totalFormsInput.value, 10);

    // Clone template HTML and replace __prefix__ with index
    const html = template.innerHTML.replaceAll("__prefix__", String(formIndex));

    const wrapper = document.createElement("div");
    wrapper.innerHTML = html.trim();
    const newFormEl = wrapper.firstElementChild;
    if (!newFormEl) return;

    container.appendChild(newFormEl);
    wireRemoveButton(newFormEl);

    // Animate in
    newFormEl.classList.add("ingredient-just-added");
    newFormEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
    newFormEl.addEventListener(
      "animationend",
      () => newFormEl.classList.remove("ingredient-just-added"),
      { once: true }
    );

    // Increment TOTAL_FORMS
    totalFormsInput.value = String(formIndex + 1);
  });
})();
