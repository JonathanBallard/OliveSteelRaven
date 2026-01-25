document.addEventListener("DOMContentLoaded", function () {
  const tagSelect = document.querySelector("select[multiple][name='tags']");
  if (!tagSelect || typeof TomSelect === "undefined") return;

  const counter = document.getElementById("tagCounter");
  const limitMsg = document.getElementById("tagLimitMsg");

  const newTagInputs = [
    document.getElementById("id_tag_1"),
    document.getElementById("id_tag_2"),
    document.getElementById("id_tag_3"),
  ].filter(Boolean);

  const updateCounter = (selectedValues) => {
    const existingCount = selectedValues.length;
    const newCount = newTagInputs.filter(
      input => input.value.trim() !== ""
    ).length;

    const total = existingCount + newCount;

    if (counter) counter.textContent = total;
    if (limitMsg) {
      limitMsg.classList.toggle("d-none", total <= 3);
    }
  };

  const ts = new TomSelect(tagSelect, {
    plugins: ["remove_button"],
    maxItems: 3,              // UX guardrail only
    closeAfterSelect: true,
    hideSelected: true,
    onChange(values) {
      updateCounter(values);
    },
  });

  // Watch new-tag inputs too
  newTagInputs.forEach(input => {
    input.addEventListener("input", () => {
      updateCounter(ts.items);
    });
  });

  // Initial state (important for edit form)
  updateCounter(ts.items);
});
