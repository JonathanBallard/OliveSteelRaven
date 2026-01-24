// recipes/static/recipes/js/recipe_form/tags.js
(function () {
    const MAX = 3;

    // Select by name so we don't need Django-rendered IDs
    const tagsSelect = document.querySelector('select[name="tags"]');
    const tag1 = document.querySelector('input[name="tag_1"]');
    const tag2 = document.querySelector('input[name="tag_2"]');
    const tag3 = document.querySelector('input[name="tag_3"]');

    const counterEl = document.getElementById("tagCounter");
    const msgEl = document.getElementById("tagLimitMsg");

    // Bail quietly if this form doesn't have tags UI for some reason
    if (!tagsSelect || !tag1 || !tag2 || !tag3 || !counterEl || !msgEl) return;

    let lastSelectedValues = Array.from(tagsSelect.selectedOptions).map((o) => o.value);

    function countSelected() {
        return Array.from(tagsSelect.selectedOptions).length;
    }

    function countNew() {
        const vals = [tag1.value, tag2.value, tag3.value]
        .map((v) => (v || "").trim())
        .filter((v) => v.length > 0);
        // Backend is source of truth; don't dedupe here
        return vals.length;
    }

    function updateUI() {
        const selectedCount = countSelected();
        const remaining = MAX - selectedCount;

        const inputs = [tag1, tag2, tag3];
        inputs.forEach((inp, idx) => {
        const shouldEnable = idx < remaining;
        inp.disabled = !shouldEnable;

        // If disabling an input that has text, clear it
        if (!shouldEnable && inp.value.trim()) inp.value = "";
        });

        const totalUsed = selectedCount + countNew();
        counterEl.textContent = String(Math.min(totalUsed, MAX));
        msgEl.classList.toggle("d-none", totalUsed <= MAX);
    }

    tagsSelect.addEventListener("change", function () {
        const selected = Array.from(tagsSelect.selectedOptions).map((o) => o.value);

        if (selected.length > MAX) {
        // revert to previous valid selection
        Array.from(tagsSelect.options).forEach((opt) => {
            opt.selected = lastSelectedValues.includes(opt.value);
        });
        msgEl.classList.remove("d-none");
        } else {
        lastSelectedValues = selected;
        }

        updateUI();
    });

    [tag1, tag2, tag3].forEach((inp) => inp.addEventListener("input", updateUI));

    // Initial sync (important for edit pages)
    updateUI();
})();
