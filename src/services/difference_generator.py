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
from src.services.quality_evaluator import QualityEvaluator

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
        self._quality = QualityEvaluator()
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
        """Pick segments based on difficulty settings with quality filtering."""
        config = self._difficulty_config[difficulty]
        num_changes = config["num_changes"]
        max_saliency = config["max_saliency"]

        # First, filter by quality
        quality_filtered = []
        for seg in ranked:
            is_acceptable, quality_score, reason = self._quality.evaluate_segment_quality(
                np.zeros((seg.mask.shape[0], seg.mask.shape[1], 3), dtype=np.uint8),
                seg,
            )
            if is_acceptable:
                seg.quality_score = quality_score  # Store for reference
                quality_filtered.append(seg)
            else:
                logger.debug(f"Segment {seg.id} rejected: {reason}")

        logger.info(f"Quality filtered: {len(quality_filtered)} / {len(ranked)} segments passed")

        # Then filter by saliency
        candidates = [s for s in quality_filtered if s.saliency_score <= max_saliency]

        # If not enough candidates below threshold, relax and take from full quality list
        if len(candidates) < num_changes:
            candidates = quality_filtered.copy()

        # If still not enough, take from ranked list (without quality filter)
        if len(candidates) < num_changes:
            logger.warning(f"Not enough high-quality segments, relaxing quality requirements")
            candidates = ranked.copy()

        n = min(num_changes, len(candidates))
        return random.sample(candidates, n)

    def _apply_changes(
        self,
        image: np.ndarray,
        segments: list[Segment],
        progress: ProgressCallback,
    ) -> tuple[np.ndarray, list[Difference]]:
        """Apply a random change to each selected segment with quality checking."""
        modified = image.copy()
        differences: list[Difference] = []

        total = len(segments)
        successful_changes = 0
        max_retries = 2

        for i, seg in enumerate(segments):
            pct = 55 + int((i / max(total, 1)) * 35)
            change_type = self._decide_change_type(seg)

            _notify(progress, pct, f"変更を適用中 ({i + 1}/{total}): {change_type}")

            # Try to apply change with quality check
            for attempt in range(max_retries):
                temp_modified = modified.copy()
                x1, y1, x2, y2 = seg.bbox
                original_region = image[y1:y2, x1:x2].copy()
                new_bbox_result = None

                # Apply the change
                if change_type == "deletion":
                    temp_modified = self._inp.inpaint(temp_modified, seg.mask)
                elif change_type == "color_change":
                    temp_modified, _ = self._col.change_hue(temp_modified, seg.mask)
                elif change_type == "addition":
                    temp_modified, new_bbox_result = self._dup.duplicate(temp_modified, seg)
                    if new_bbox_result is None:
                        logger.debug(f"Addition failed for segment {seg.id}, trying different type")
                        change_type = random.choice(["deletion", "color_change"])
                        continue

                # Check quality of the modification
                modified_region = temp_modified[y1:y2, x1:x2]
                local_mask = seg.mask[y1:y2, x1:x2]

                is_acceptable, quality_score, reason = self._quality.evaluate_modification_quality(
                    original_region,
                    modified_region,
                    local_mask,
                    change_type,
                )

                if is_acceptable or attempt == max_retries - 1:
                    # Accept this modification
                    modified = temp_modified
                    diff = self._apply_single_change(modified, seg, change_type, successful_changes + 1)

                    if diff is not None:
                        if change_type == "addition" and new_bbox_result is not None:
                            diff.bbox = new_bbox_result
                        differences.append(diff)
                        successful_changes += 1

                    if not is_acceptable:
                        logger.warning(f"Accepting lower quality change ({reason}) after {max_retries} attempts")
                    else:
                        logger.debug(f"Change accepted with quality score: {quality_score:.2f}")
                    break
                else:
                    logger.debug(f"Modification rejected ({reason}), retrying with different parameters...")
                    # Try a different change type on retry
                    if change_type == "color_change":
                        change_type = random.choice(["deletion", "addition"])
                    elif change_type == "addition":
                        change_type = "color_change"

        logger.info(f"Successfully applied {successful_changes} / {total} changes")
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
