/**
 * Upload page: drag-and-drop, preview, difficulty selection, generate request.
 */
(function () {
    "use strict";

    // DOM elements
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const uploadSection = document.getElementById("uploadSection");
    const previewSection = document.getElementById("previewSection");
    const previewImage = document.getElementById("previewImage");
    const difficultyButtons = document.getElementById("difficultyButtons");
    const generateBtn = document.getElementById("generateBtn");
    const resetBtn = document.getElementById("resetBtn");
    const uploadError = document.getElementById("uploadError");

    let currentFileId = null;
    let currentDifficulty = "medium";

    // ─── Drag & Drop ──────────────────────────
    dropZone.addEventListener("dragover", function (e) {
        e.preventDefault();
        dropZone.classList.add("drop-zone--hover");
    });

    dropZone.addEventListener("dragleave", function () {
        dropZone.classList.remove("drop-zone--hover");
    });

    dropZone.addEventListener("drop", function (e) {
        e.preventDefault();
        dropZone.classList.remove("drop-zone--hover");
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener("change", function () {
        if (fileInput.files.length > 0) {
            handleFile(fileInput.files[0]);
        }
    });

    // ─── Difficulty Buttons ───────────────────
    difficultyButtons.addEventListener("click", function (e) {
        const btn = e.target.closest(".diff-btn");
        if (!btn) return;

        difficultyButtons.querySelectorAll(".diff-btn").forEach(function (b) {
            b.classList.remove("diff-btn--active");
        });
        btn.classList.add("diff-btn--active");
        currentDifficulty = btn.dataset.value;
    });

    // ─── Reset ────────────────────────────────
    resetBtn.addEventListener("click", function () {
        currentFileId = null;
        fileInput.value = "";
        previewSection.hidden = true;
        uploadSection.hidden = false;
        hideError();
    });

    // ─── Generate ─────────────────────────────
    generateBtn.addEventListener("click", function () {
        if (!currentFileId) return;
        generateBtn.disabled = true;
        generateBtn.textContent = "送信中...";
        hideError();

        fetch("/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                file_id: currentFileId,
                difficulty: currentDifficulty,
            }),
        })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (data.success) {
                    // Store job info and redirect to processing page
                    sessionStorage.setItem("job_id", data.job_id);
                    sessionStorage.setItem("difficulty", currentDifficulty);
                    window.location.href = "/processing";
                } else {
                    showError(data.error || "生成リクエストに失敗しました");
                    generateBtn.disabled = false;
                    generateBtn.textContent = "間違い探しを生成";
                }
            })
            .catch(function () {
                showError("サーバーとの通信に失敗しました");
                generateBtn.disabled = false;
                generateBtn.textContent = "間違い探しを生成";
            });
    });

    // ─── File Handling ────────────────────────
    function handleFile(file) {
        hideError();

        // Client-side checks
        var validTypes = ["image/jpeg", "image/png"];
        if (validTypes.indexOf(file.type) === -1) {
            showError("JPEGまたはPNG画像を選択してください");
            return;
        }
        if (file.size > 10 * 1024 * 1024) {
            showError("ファイルサイズは10MB以下にしてください");
            return;
        }

        // Show preview immediately
        var reader = new FileReader();
        reader.onload = function (e) {
            previewImage.src = e.target.result;
            uploadSection.hidden = true;
            previewSection.hidden = false;
        };
        reader.readAsDataURL(file);

        // Upload
        uploadFile(file);
    }

    function uploadFile(file) {
        generateBtn.disabled = true;
        generateBtn.textContent = "アップロード中...";

        var formData = new FormData();
        formData.append("file", file);

        fetch("/api/upload", {
            method: "POST",
            body: formData,
        })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (data.success) {
                    currentFileId = data.file_id;
                    generateBtn.disabled = false;
                    generateBtn.textContent = "間違い探しを生成";
                } else {
                    showError(data.error || "アップロードに失敗しました");
                    generateBtn.textContent = "間違い探しを生成";
                }
            })
            .catch(function () {
                showError("アップロード中にエラーが発生しました");
                generateBtn.textContent = "間違い探しを生成";
            });
    }

    // ─── Helpers ──────────────────────────────
    function showError(msg) {
        uploadError.textContent = msg;
        uploadError.hidden = false;
    }

    function hideError() {
        uploadError.hidden = true;
    }
})();
