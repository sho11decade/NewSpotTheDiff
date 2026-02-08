/**
 * Result page: load images, metadata, download, show answers.
 */
(function () {
    "use strict";

    var originalImage = document.getElementById("originalImage");
    var modifiedImage = document.getElementById("modifiedImage");
    var originalWithAnswers = document.getElementById("originalWithAnswers");
    var modifiedWithAnswers = document.getElementById("modifiedWithAnswers");
    var a4LayoutImage = document.getElementById("a4LayoutImage");
    var resultInfo = document.getElementById("resultInfo");
    var difficultyBadge = document.getElementById("difficultyBadge");
    var countBadge = document.getElementById("countBadge");
    var timeBadge = document.getElementById("timeBadge");
    var downloadOriginal = document.getElementById("downloadOriginal");
    var downloadModified = document.getElementById("downloadModified");
    var downloadA4Layout = document.getElementById("downloadA4Layout");
    var downloadA4WithAnswers = document.getElementById("downloadA4WithAnswers");
    var downloadAnswerImage = document.getElementById("downloadAnswerImage");
    var toggleAnswersBtn = document.getElementById("toggleAnswers");
    var toggleA4ViewBtn = document.getElementById("toggleA4View");
    var answersSection = document.getElementById("answersSection");
    var a4Section = document.getElementById("a4Section");
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
            originalWithAnswers.src = data.original_with_answers_url;
            modifiedWithAnswers.src = data.modified_with_answers_url;
            a4LayoutImage.src = data.a4_layout_url;

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

    downloadA4Layout.addEventListener("click", function () {
        if (resultData) {
            downloadImage(resultData.a4_layout_url, "spot_the_difference_a4.png");
        }
    });

    downloadA4WithAnswers.addEventListener("click", function () {
        if (resultData) {
            downloadImage(resultData.a4_layout_with_answers_url, "spot_the_difference_a4_answers.png");
        }
    });

    downloadAnswerImage.addEventListener("click", function () {
        if (resultData) {
            downloadImage(resultData.modified_with_answers_url, "answer.png");
        }
    });

    // Toggle answers
    toggleAnswersBtn.addEventListener("click", function () {
        var showing = !answersSection.hidden;
        answersSection.hidden = showing;
        toggleAnswersBtn.textContent = showing ? "答えを見る" : "答えを隠す";
    });

    // Toggle A4 view
    toggleA4ViewBtn.addEventListener("click", function () {
        var showing = !a4Section.hidden;
        a4Section.hidden = showing;
        toggleA4ViewBtn.textContent = showing ? "A4表示に切替" : "通常表示に戻る";
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
