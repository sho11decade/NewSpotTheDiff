/**
 * Processing page: polls job status and updates the progress bar.
 */
(function () {
    "use strict";

    var POLL_INTERVAL = 2000; // ms

    var progressFill = document.getElementById("progressFill");
    var progressText = document.getElementById("progressText");
    var stepText = document.getElementById("stepText");

    var jobId = sessionStorage.getItem("job_id");

    if (!jobId) {
        stepText.textContent = "ジョブ情報が見つかりません";
        window.location.href = "/";
        return;
    }

    var timer = setInterval(pollStatus, POLL_INTERVAL);
    pollStatus(); // immediate first call

    function pollStatus() {
        fetch("/api/status/" + encodeURIComponent(jobId))
            .then(function (res) { return res.json(); })
            .then(function (data) {
                var progress = data.progress || 0;
                var step = data.step || "";

                progressFill.style.width = progress + "%";
                progressText.textContent = progress + "%";
                stepText.textContent = step || "処理中...";

                if (data.status === "completed") {
                    clearInterval(timer);
                    progressFill.style.width = "100%";
                    progressText.textContent = "100%";
                    stepText.textContent = "完了！リダイレクトしています...";
                    setTimeout(function () {
                        window.location.href = "/result/" + encodeURIComponent(jobId);
                    }, 500);
                } else if (data.status === "failed") {
                    clearInterval(timer);
                    stepText.textContent = "エラーが発生しました: " + (data.error || "不明なエラー");
                    progressFill.style.background = "#dc2626";
                }
            })
            .catch(function () {
                // Transient network error — keep polling
                stepText.textContent = "接続を再試行しています...";
            });
    }
})();
