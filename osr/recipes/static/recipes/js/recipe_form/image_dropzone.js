// recipes/static/recipes/js/recipe_form/image_dropzone.js
(() => {
    const dropzone = document.getElementById("dropzone");
    const input = document.querySelector('input[type="file"][name="recipe_image"]');

    const existingWrap = document.getElementById("existingWrap"); // may be null
    const previewWrap = document.getElementById("previewWrap");
    const previewImg = document.getElementById("previewImg");
    const previewMeta = document.getElementById("previewMeta");
    const clearBtn = document.getElementById("clearImageBtn");

    const dzTitle = document.getElementById("dzTitle");
    const dzSub = document.getElementById("dzSub");

    const MAX_BYTES = 1 * 1024 * 1024; // 1MB
    const MAX_PREVIEW = 300;

    if (!dropzone || !input || !previewWrap || !previewImg || !previewMeta || !clearBtn || !dzTitle || !dzSub) {
        return;
    }

    const setDragActive = (active) => {
        dropzone.classList.toggle("border-primary", active);
        dropzone.classList.toggle("bg-light", active);
    };

    const resetToExisting = () => {
        input.value = "";
        previewWrap.classList.add("d-none");
        previewImg.src = "";
        previewMeta.textContent = "";

        if (existingWrap) existingWrap.classList.remove("d-none");

        dzTitle.textContent = "Drag & drop an image here";
        dzSub.textContent = "or click to choose a file (max 1MB)";
    };

    const renderScaledPreview = (file) => {
        return new Promise((resolve, reject) => {
        const img = new Image();

        img.onload = () => {
            const scale = Math.min(MAX_PREVIEW / img.width, MAX_PREVIEW / img.height, 1);
            const w = Math.round(img.width * scale);
            const h = Math.round(img.height * scale);

            const canvas = document.createElement("canvas");
            canvas.width = w;
            canvas.height = h;

            const ctx = canvas.getContext("2d");
            if (!ctx) return reject(new Error("No canvas context"));
            ctx.drawImage(img, 0, 0, w, h);

            const dataUrl = canvas.toDataURL("image/jpeg", 0.9);
            resolve(dataUrl);
        };

        img.onerror = () => reject(new Error("Could not load image"));

        const objectUrl = URL.createObjectURL(file);
        img.src = objectUrl;

        img.addEventListener("load", () => URL.revokeObjectURL(objectUrl), { once: true });
        img.addEventListener("error", () => URL.revokeObjectURL(objectUrl), { once: true });
        });
    };

    const showNewPreview = async (file) => {
        if (!file) return;

        if (file.size > MAX_BYTES) {
        alert("That image is over 1MB. Please choose a smaller one.");
        resetToExisting();
        return;
        }
        if (!file.type.startsWith("image/")) {
        alert("Please upload an image file.");
        resetToExisting();
        return;
        }

        if (existingWrap) existingWrap.classList.add("d-none");

        try {
        const previewDataUrl = await renderScaledPreview(file);
        previewImg.src = previewDataUrl;
        } catch (err) {
        alert("Could not generate a preview for that image.");
        resetToExisting();
        return;
        }

        const kb = Math.round(file.size / 1024);
        previewMeta.textContent = `${file.name} — ${kb} KB — ${file.type}`;

        previewWrap.classList.remove("d-none");
        dzTitle.textContent = "Drop another image to replace";
        dzSub.textContent = "or click to choose a different file";
    };

    dropzone.addEventListener("click", () => input.click());
    input.addEventListener("change", () => showNewPreview(input.files && input.files[0]));

    ["dragenter", "dragover"].forEach((evt) => {
        dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(true);
        });
    });

    ["dragleave", "drop"].forEach((evt) => {
        dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        });
    });

    dropzone.addEventListener("drop", (e) => {
        const file = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
        if (!file) return;

        const dt = new DataTransfer();
        dt.items.add(file);
        input.files = dt.files;

        showNewPreview(file);
    });

    clearBtn.addEventListener("click", resetToExisting);
})();
