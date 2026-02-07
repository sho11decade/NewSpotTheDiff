"""Asynchronous job management with ThreadPoolExecutor."""

from __future__ import annotations

import gc
import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from src.models.job import JobStatus, JobState
from src.services.difference_generator import DifferenceGenerator
from src.utils.image_io import load_image, save_image

logger = logging.getLogger(__name__)


class JobManager:
    """Manages background generation jobs."""

    def __init__(
        self,
        generator: DifferenceGenerator,
        output_folder: str,
        max_workers: int = 2,
    ) -> None:
        self._generator = generator
        self._output_folder = output_folder
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._jobs: dict[str, JobStatus] = {}
        self._lock = threading.Lock()

    def submit(self, job_id: str, image_path: str, difficulty: str) -> JobStatus:
        """Submit a new generation job to the background pool."""
        status = JobStatus(job_id=job_id, status=JobState.QUEUED, current_step="待機中")
        with self._lock:
            self._jobs[job_id] = status

        self._executor.submit(self._process, job_id, image_path, difficulty)
        return status

    def get_status(self, job_id: str) -> JobStatus | None:
        """Get current status of a job (thread-safe)."""
        with self._lock:
            return self._jobs.get(job_id)

    def _process(self, job_id: str, image_path: str, difficulty: str) -> None:
        """Background processing function."""
        try:
            self._update(job_id, status=JobState.PROCESSING, progress=5, current_step="画像を読み込み中...")

            image = load_image(image_path)

            def on_progress(percent: int, step: str) -> None:
                self._update(job_id, progress=percent, current_step=step)

            result = self._generator.generate(image, difficulty, progress=on_progress)

            # Save outputs
            out_dir = Path(self._output_folder) / job_id
            out_dir.mkdir(parents=True, exist_ok=True)

            save_image(result.original_image, out_dir / "original.png")
            save_image(result.modified_image, out_dir / "modified.png")

            metadata = result.get_metadata_with_differences()
            with open(out_dir / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            self._update(
                job_id,
                status=JobState.COMPLETED,
                progress=100,
                current_step="完了",
                result_path=str(out_dir),
            )
            logger.info("Job %s completed successfully.", job_id)

        except Exception as e:
            logger.exception("Job %s failed: %s", job_id, e)
            self._update(
                job_id,
                status=JobState.FAILED,
                error=str(e),
                current_step="エラー",
            )
        finally:
            gc.collect()

    def _update(self, job_id: str, **kwargs) -> None:
        """Thread-safe status update."""
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            for key, value in kwargs.items():
                setattr(job, key, value)
