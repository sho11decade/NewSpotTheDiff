/**
 * Processing page: polls job status and updates the progress bar with detailed steps.
 */
(function () {
    "use strict";

    var POLL_INTERVAL = 1500; // ms
    var ESTIMATED_TIME = 15; // seconds (increased for new steps)

    var progressFill = document.getElementById("progressFill");
    var progressText = document.getElementById("progressText");
    var stepText = document.getElementById("stepText");
    var estimatedTime = document.getElementById("estimatedTime");

    var startTime = Date.now();

    var jobId = sessionStorage.getItem("job_id");

    if (!jobId) {
        stepText.textContent = "ジョブ情報が見つかりません";
        setTimeout(function () {
            window.location.href = "/";
        }, 2000);
        return;
    }

    var timer = setInterval(pollStatus, POLL_INTERVAL);
    pollStatus(); // immediate first call

    function pollStatus() {
        fetch("/api/status/" + encodeURIComponent(jobId))
            .then(function (res) { return res.json(); })
            .then(function (data) {
                var progress = data.progress || 0;
                var step = data.current_step || data.step || "";

                progressFill.style.width = progress + "%";
                progressText.textContent = Math.round(progress) + "%";
                stepText.textContent = step || "処理中...";

                // Update step visualization
                updateSteps(progress, step);

                // Update estimated time with adaptive calculation
                var elapsed = (Date.now() - startTime) / 1000;
                if (progress > 5 && progress < 100) {
                    var estimatedTotal = elapsed / (progress / 100);
                    var remaining = Math.max(0, estimatedTotal - elapsed);
                    if (remaining > 0 && data.status !== "completed") {
                        estimatedTime.textContent = "残り約 " + Math.ceil(remaining) + " 秒";
                    }
                } else if (data.status !== "completed") {
                    estimatedTime.textContent = "推定 " + ESTIMATED_TIME + " 秒";
                }

                if (data.status === "completed") {
                    clearInterval(timer);
                    progressFill.style.width = "100%";
                    progressText.textContent = "100%";
                    stepText.textContent = "完了！リダイレクトしています...";
                    estimatedTime.textContent = "";
                    markStepComplete("step-finalize");
                    setTimeout(function () {
                        window.location.href = "/result/" + encodeURIComponent(jobId);
                    }, 500);
                } else if (data.status === "failed") {
                    clearInterval(timer);
                    stepText.textContent = "エラーが発生しました: " + (data.error || "不明なエラー");
                    progressFill.style.background = "#dc2626";
                    estimatedTime.textContent = "";
                }
            })
            .catch(function () {
                // Transient network error — keep polling
                stepText.textContent = "接続を再試行しています...";
            });
    }

    function updateSteps(progress, stepText) {
        // Map progress to steps based on job_manager progress updates
        // 5%: Image load
        // 40%: Segmentation complete
        // 50%: Saliency complete
        // 55-92%: Changes being applied
        // 92-96%: Generating answer images
        // 96-100%: Generating A4 layout & completion

        if (progress >= 5 && progress < 40) {
            markStepInProgress("step-load");
        } else if (progress >= 40) {
            markStepComplete("step-load");
        }

        if (progress >= 10 && progress < 50) {
            markStepInProgress("step-segment");
        } else if (progress >= 50) {
            markStepComplete("step-segment");
        }

        if (progress >= 50 && progress < 55) {
            markStepInProgress("step-saliency");
        } else if (progress >= 55) {
            markStepComplete("step-saliency");
        }

        if (progress >= 55 && progress < 92) {
            markStepInProgress("step-modify");
        } else if (progress >= 92) {
            markStepComplete("step-modify");
        }

        if (progress >= 92 && progress < 100) {
            markStepInProgress("step-finalize");
        }
    }

    function markStepInProgress(stepId) {
        var step = document.getElementById(stepId);
        if (step && !step.classList.contains("complete")) {
            step.classList.add("in-progress");
            var status = step.querySelector(".step-status");
            if (status) {
                status.textContent = "処理中...";
            }
        }
    }

    function markStepComplete(stepId) {
        var step = document.getElementById(stepId);
        if (step) {
            step.classList.remove("in-progress");
            step.classList.add("complete");
            var status = step.querySelector(".step-status");
            if (status) {
                status.textContent = "✓ 完了";
            }
        }
    }
})();
