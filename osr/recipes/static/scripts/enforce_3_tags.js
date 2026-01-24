
// Max 3 Tags Existing + New
(function () {
    const MAX = 3;

    const tagsSelect = document.getElementById("{{ form.tags.id_for_label }}");
    const tag1 = document.getElementById("{{ form.tag_1.id_for_label }}");
    const tag2 = document.getElementById("{{ form.tag_2.id_for_label }}");
    const tag3 = document.getElementById("{{ form.tag_3.id_for_label }}");

    const counterEl = document.getElementById("tagCounter");
    const msgEl = document.getElementById("tagLimitMsg");

    // Safety: if elements aren't present, bail quietly
    if (!tagsSelect || !tag1 || !tag2 || !tag3 || !counterEl || !msgEl) return;

    let lastSelectedValues = Array.from(tagsSelect.selectedOptions).map(o => o.value);

    function countSelected() {
        return Array.from(tagsSelect.selectedOptions).length;
    }

    function countNew() {
        const vals = [tag1.value, tag2.value, tag3.value]
        .map(v => (v || "").trim())
        .filter(v => v.length > 0);
        // Not normalizing/deduping here; backend is source of truth.
        return vals.length;
    }

    function updateUI() {
        const selectedCount = countSelected();
        const remaining = MAX - selectedCount;

        // Enable only the number of new-tag inputs that can still be used
        const inputs = [tag1, tag2, tag3];
        inputs.forEach((inp, idx) => {
        const shouldEnable = idx < remaining;
        inp.disabled = !shouldEnable;

        // If disabling an input that has text, clear it to avoid confusion
        if (!shouldEnable && inp.value.trim()) {
            inp.value = "";
        }
        });

        const totalUsed = selectedCount + countNew();
        counterEl.textContent = String(Math.min(totalUsed, MAX));
        msgEl.classList.toggle("d-none", totalUsed <= MAX);
    }

    // Enforce max 3 selections in the multi-select
    tagsSelect.addEventListener("change", function () {
        const selected = Array.from(tagsSelect.selectedOptions).map(o => o.value);

        if (selected.length > MAX) {
        // Revert to previous valid selection set
        Array.from(tagsSelect.options).forEach(opt => {
            opt.selected = lastSelectedValues.includes(opt.value);
        });
        msgEl.classList.remove("d-none");
        } else {
        lastSelectedValues = selected;
        }

        updateUI();
    });

    // Keep UI in sync as user types new tags
    [tag1, tag2, tag3].forEach(inp => inp.addEventListener("input", updateUI));

    // Initial sync (important on edit pages)
    updateUI();
})();