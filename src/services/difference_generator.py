"""Main pipeline: orchestrates segmentation, saliency, and modifications."""

from __future__ import annotations

import logging
import random
import time
from typing import Callable

import cv2
import numpy as np

from src.models.segment import Segment
from src.models.difference import Difference, GenerationResult
from src.services.segmentation import SegmentationService
from src.services.saliency import SaliencyService
from src.services.inpainting import InpaintingService
from src.services.color_changer import ColorChanger
from src.services.object_duplicator import ObjectDuplicator

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, str], None] | None


class DifferenceGenerator:
    """Generates spot-the-difference images from a single input image."""

    def __init__(
        self,
        segmentation: SegmentationService,
        saliency: SaliencyService,
        inpainting: InpaintingService,
        color_changer: ColorChanger,
        object_duplicator: ObjectDuplicator,
        difficulty_config: dict,
        segment_min_area_ratio: float = 0.002,
        segment_max_area_ratio: float = 0.15,
    ) -> None:
        self._seg = segmentation
        self._sal = saliency
        self._inp = inpainting
        self._col = color_changer
        self._dup = object_duplicator
        self._difficulty_config = difficulty_config
        self._min_area_ratio = segment_min_area_ratio
        self._max_area_ratio = segment_max_area_ratio

    def generate(
        self,
        image: np.ndarray,
        difficulty: str = "medium",
        progress: ProgressCallback = None,
    ) -> GenerationResult:
        """Run the full generation pipeline.

        Args:
            image: BGR image (H, W, 3) uint8.
            difficulty: "easy", "medium", or "hard".
            progress: Optional callback(percent, step_name).

        Returns:
            GenerationResult with original, modified image, and difference metadata.
        """
        timings: dict[str, float] = {}
        _notify(progress, 5, "セグメンテーション開始...")

        # 1. Segmentation
        t0 = time.time()
        segments = self._seg.segment(
            image,
            min_area_ratio=self._min_area_ratio,
            max_area_ratio=self._max_area_ratio,
        )
        timings["segmentation"] = time.time() - t0
        _notify(progress, 40, f"セグメンテーション完了 ({len(segments)}個検出)")

        if len(segments) < 2:
            logger.warning("Too few segments (%d) to generate differences.", len(segments))
            return GenerationResult(
                original_image=image,
                modified_image=image.copy(),
                differences=[],
                metadata={"error": "検出されたオブジェクトが少なすぎます"},
            )

        # 2. Saliency analysis
        t0 = time.time()
        saliency_map = self._sal.compute_map(image)
        ranked = self._sal.rank_segments(segments, saliency_map)
        timings["saliency"] = time.time() - t0
        _notify(progress, 50, "顕著性解析完了")

        # 3. Select segments based on difficulty
        selected = self._select_segments(ranked, difficulty)
        _notify(progress, 55, f"{len(selected)}個のオブジェクトを変更します")

        # 4. Apply changes
        t0 = time.time()
        modified, differences = self._apply_changes(image, selected, progress)
        timings["changes"] = time.time() - t0

        total_time = sum(timings.values())
        timings["total"] = total_time

        _notify(progress, 95, "メタデータを生成中...")

        metadata = {
            "difficulty": difficulty,
            "processing_times": {k: round(v, 2) for k, v in timings.items()},
            "segments_detected": len(segments),
            "model_versions": {
                "segmentation": "FastSAM-x",
                "saliency": "OpenCV SpectralResidual",
                "inpainting": "OpenCV Navier-Stokes",
            },
        }

        _notify(progress, 100, "完了")

        return GenerationResult(
            original_image=image,
            modified_image=modified,
            differences=differences,
            metadata=metadata,
        )

    def _select_segments(
        self, ranked: list[Segment], difficulty: str
    ) -> list[Segment]:
        """Pick segments based on difficulty settings."""
        config = self._difficulty_config[difficulty]
        num_changes = config["num_changes"]
        max_saliency = config["max_saliency"]

        candidates = [s for s in ranked if s.saliency_score <= max_saliency]

        # If not enough candidates below threshold, relax and take from full list
        if len(candidates) < num_changes:
            candidates = ranked.copy()

        n = min(num_changes, len(candidates))
        return random.sample(candidates, n)

    def _apply_changes(
        self,
        image: np.ndarray,
        segments: list[Segment],
        progress: ProgressCallback,
    ) -> tuple[np.ndarray, list[Difference]]:
        """Apply a random change to each selected segment."""
        modified = image.copy()
        differences: list[Difference] = []

        total = len(segments)
        for i, seg in enumerate(segments):
            pct = 55 + int((i / max(total, 1)) * 35)
            change_type = self._decide_change_type(seg)

            _notify(progress, pct, f"変更を適用中 ({i + 1}/{total}): {change_type}")

            diff = self._apply_single_change(modified, seg, change_type, i + 1)
            if diff is not None:
                differences.append(diff)
                # Update modified in-place reference is fine since services return new arrays
                if change_type == "deletion":
                    modified = self._inp.inpaint(modified, seg.mask)
                elif change_type == "color_change":
                    modified, _ = self._col.change_hue(modified, seg.mask)
                elif change_type == "addition":
                    modified, new_bbox = self._dup.duplicate(modified, seg)
                    if new_bbox:
                        diff.bbox = new_bbox

        return modified, differences

    def _apply_single_change(
        self,
        image: np.ndarray,
        seg: Segment,
        change_type: str,
        diff_id: int,
    ) -> Difference | None:
        """Create a Difference record. Actual mutation happens in _apply_changes."""
        descriptions = {
            "deletion": "オブジェクトを削除",
            "color_change": "色を変更",
            "addition": "オブジェクトを追加",
        }
        return Difference(
            id=diff_id,
            type=change_type,
            bbox=seg.bbox,
            saliency_score=seg.saliency_score,
            description=descriptions.get(change_type, ""),
        )

    def _decide_change_type(self, seg: Segment) -> str:
        """Choose change type, preferring colour/addition for large objects."""
        image_area_ratio = seg.area / max(seg.mask.size, 1)
        if image_area_ratio > 0.08:
            # Large object — inpainting quality degrades, avoid deletion
            return random.choice(["color_change", "addition"])
        return random.choice(["deletion", "color_change", "addition"])


def _notify(cb: ProgressCallback, percent: int, step: str) -> None:
    if cb is not None:
        cb(percent, step)
