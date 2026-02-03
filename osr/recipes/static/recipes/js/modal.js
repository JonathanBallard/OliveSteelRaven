document.addEventListener("DOMContentLoaded", function () {
    const modalEl = document.getElementById("confirmDeleteModal");
    if (!modalEl) return;

    const titleEl = document.getElementById("deleteRecipeTitle");
    const formEl = document.getElementById("confirmDeleteForm");

    modalEl.addEventListener("show.bs.modal", function (event) {
        const trigger = event.relatedTarget;
        if (!trigger) return;

        const deleteUrl = trigger.getAttribute("data-delete-url");
        const recipeTitle = trigger.getAttribute("data-recipe-title") || "this recipe";

        formEl.action = deleteUrl;
        if (titleEl) titleEl.textContent = recipeTitle;
        });
    });