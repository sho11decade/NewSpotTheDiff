/**
 * Result page: load images, metadata, download, show answers.
 */
(function () {
    "use strict";

    var originalImage = document.getElementById("originalImage");
    var modifiedImage = document.getElementById("modifiedImage");
    var resultInfo = document.getElementById("resultInfo");
    var difficultyBadge = document.getElementById("difficultyBadge");
    var countBadge = document.getElementById("countBadge");
    var timeBadge = document.getElementById("timeBadge");
    var downloadOriginal = document.getElementById("downloadOriginal");
    var downloadModified = document.getElementById("downloadModified");
    var showAnswersBtn = document.getElementById("showAnswers");
    var answersSection = document.getElementById("answersSection");
    var answersList = document.getElementById("answersList");

    var jobId = typeof JOB_ID !== "undefined" ? JOB_ID : null;
    if (!jobId) {
        return;
    }

    var resultData = null;

    // Load result
    fetch("/api/result/" + encodeURIComponent(jobId))
        .then(function (res) { return res.json(); })
        .then(function (data) {
            if (!data.success) {
                document.querySelector(".card h2").textContent =
                    "エラー: " + (data.error || "結果を取得できませんでした");
                return;
            }

            resultData = data;

            originalImage.src = data.original_image_url;
            modifiedImage.src = data.modified_image_url;

            // Metadata badges
            var meta = data.metadata || {};
            var diffLabel = {
                easy: "簡単",
                medium: "普通",
                hard: "難しい",
            };
            difficultyBadge.textContent = diffLabel[meta.difficulty] || meta.difficulty || "-";

            var diffCount = meta.differences ? meta.differences.length : meta.num_differences || 0;
            countBadge.textContent = diffCount + "箇所";

            var elapsed = meta.elapsed_seconds;
            if (elapsed != null) {
                timeBadge.textContent = elapsed.toFixed(1) + "秒";
            } else {
                timeBadge.textContent = "";
            }

            resultInfo.hidden = false;

            // Build answers list
            if (meta.differences && meta.differences.length > 0) {
                meta.differences.forEach(function (diff) {
                    var li = document.createElement("li");
                    var typeLabel = {
                        deletion: "削除",
                        color_change: "色変更",
                        addition: "追加",
                    };
                    li.innerHTML =
                        "<strong>" + (typeLabel[diff.change_type] || diff.change_type) + "</strong> " +
                        (diff.description || "");
                    answersList.appendChild(li);
                });
            }
        })
        .catch(function () {
            document.querySelector(".card h2").textContent =
                "結果の読み込みに失敗しました";
        });

    // Download buttons
    downloadOriginal.addEventListener("click", function () {
        if (resultData) {
            downloadImage(resultData.original_image_url, "original.png");
        }
    });

    downloadModified.addEventListener("click", function () {
        if (resultData) {
            downloadImage(resultData.modified_image_url, "modified.png");
        }
    });

    // Show answers toggle
    showAnswersBtn.addEventListener("click", function () {
        var showing = !answersSection.hidden;
        answersSection.hidden = showing;
        showAnswersBtn.textContent = showing ? "答えを見る" : "答えを隠す";
    });

    function downloadImage(url, filename) {
        var a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
})();
