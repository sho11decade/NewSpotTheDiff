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
from src.services.answer_visualizer import AnswerVisualizer
from src.services.a4_layout_composer import A4LayoutComposer
from src.utils.image_io import load_image, save_image

logger = logging.getLogger(__name__)


class JobManager:
    """Manages background generation jobs."""

    def __init__(
        self,
        generator: DifferenceGenerator,
        answer_visualizer: AnswerVisualizer,
        a4_composer: A4LayoutComposer,
        output_folder: str,
        max_workers: int = 2,
    ) -> None:
        self._generator = generator
        self._answer_visualizer = answer_visualizer
        self._a4_composer = a4_composer
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

            # Generate and save answer images
            self._update(job_id, progress=92, current_step="答え画像を生成中...")
            original_with_answers, modified_with_answers = self._answer_visualizer.create_answer_overlay(
                result.original_image,
                result.modified_image,
                result.differences,
            )
            save_image(original_with_answers, out_dir / "original_with_answers.png")
            save_image(modified_with_answers, out_dir / "modified_with_answers.png")

            # Generate and save A4 layout
            self._update(job_id, progress=96, current_step="A4レイアウトを生成中...")
            a4_layout = self._a4_composer.compose_side_by_side(
                result.original_image,
                result.modified_image,
                left_title="元の画像",
                right_title="間違い探し",
                title="間違い探しパズル",
            )
            save_image(a4_layout, out_dir / "a4_layout.png")

            # Also create A4 layout with answers
            a4_layout_with_answers = self._a4_composer.compose_side_by_side(
                original_with_answers,
                modified_with_answers,
                left_title="元の画像（答え）",
                right_title="間違い探し（答え）",
                title="間違い探しパズル - 答え",
            )
            save_image(a4_layout_with_answers, out_dir / "a4_layout_with_answers.png")

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
            # Aggressive memory cleanup for 4GB hosting environment
            # Explicitly delete local variables to free memory immediately
            try:
                del image
                del result
                del original_with_answers
                del modified_with_answers
                del a4_layout
                del a4_layout_with_answers
            except (NameError, UnboundLocalError):
                # Variables may not be defined if error occurred early
                pass

            # Force garbage collection
            gc.collect()

            # Additional numpy/opencv cleanup
            if hasattr(np, 'clear_memo'):
                np.clear_memo()  # Clear numpy memo cache if available

    def _update(self, job_id: str, **kwargs) -> None:
        """Thread-safe status update."""
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            for key, value in kwargs.items():
                setattr(job, key, value)
