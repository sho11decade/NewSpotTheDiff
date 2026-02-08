"""Object segmentation using FastSAM."""

from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np

from src.models.segment import Segment

logger = logging.getLogger(__name__)


class SegmentationService:
    """Segments objects in images using FastSAM (CPU-friendly)."""

    def __init__(
        self,
        model_path: str,
        conf: float = 0.4,
        iou: float = 0.9,
        imgsz: int = 1024,
    ) -> None:
        self._model_path = model_path
        self._conf = conf
        self._iou = iou
        self._imgsz = imgsz
        self._model = None  # lazy load

    def _ensure_model(self) -> None:
        """Load the model on first use."""
        if self._model is not None:
            return
        from ultralytics import FastSAM

        path = Path(self._model_path)
        if not path.exists():
            raise FileNotFoundError(
                f"FastSAM model not found: {path}. "
                "Run `python scripts/download_model.py` first."
            )
        logger.info("Loading FastSAM model from %s ...", path)
        self._model = FastSAM(str(path))
        logger.info("FastSAM model loaded successfully.")

    def segment(
        self,
        image: np.ndarray,
        min_area_ratio: float = 0.002,
        max_area_ratio: float = 0.15,
    ) -> list[Segment]:
        """Run FastSAM segmentation on a BGR image.

        Args:
            image: BGR image (H, W, 3) uint8.
            min_area_ratio: Minimum segment area as fraction of image area.
            max_area_ratio: Maximum segment area as fraction of image area.

        Returns:
            List of Segment objects, sorted by area (descending).
        """
        self._ensure_model()

        h, w = image.shape[:2]
        total_pixels = h * w
        min_area = int(total_pixels * min_area_ratio)
        max_area = int(total_pixels * max_area_ratio)

        # FastSAM expects RGB or file path; convert BGR -> RGB
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        results = self._model(
            rgb,
            device="cpu",
            retina_masks=True,
            imgsz=self._imgsz,
            conf=self._conf,
            iou=self._iou,
            verbose=False,
        )

        segments = self._extract_segments(results, h, w, min_area, max_area)
        logger.info(
            "Segmentation complete: %d segments (filtered from raw results)",
            len(segments),
        )
        return segments

    def _extract_segments(
        self,
        results,
        img_h: int,
        img_w: int,
        min_area: int,
        max_area: int,
    ) -> list[Segment]:
        """Extract Segment objects from FastSAM results with improved filtering."""
        segments: list[Segment] = []

        if not results or results[0].masks is None:
            logger.warning("No masks returned by FastSAM.")
            return segments

        masks_data = results[0].masks.data.cpu().numpy()
        boxes = results[0].boxes

        for i in range(len(masks_data)):
            mask = masks_data[i]

            # Resize mask to original image dimensions if needed
            if mask.shape[0] != img_h or mask.shape[1] != img_w:
                mask = cv2.resize(
                    mask.astype(np.float32),
                    (img_w, img_h),
                    interpolation=cv2.INTER_NEAREST,
                )

            mask_bool = mask > 0.5
            area = int(mask_bool.sum())

            # Basic area filtering
            if area < min_area or area > max_area:
                continue

            bbox = self._mask_to_bbox(mask_bool)
            if bbox is None:
                continue

            # Shape quality filtering
            if not self._is_good_shape(mask_bool, bbox):
                continue

            conf = float(boxes.conf[i]) if boxes is not None and i < len(boxes.conf) else 0.0

            segments.append(
                Segment(
                    id=len(segments),
                    mask=mask_bool,
                    bbox=bbox,
                    area=area,
                    confidence=conf,
                )
            )

        # Remove overlapping segments
        segments = self._remove_overlaps(segments)

        # Sort by area descending
        segments.sort(key=lambda s: s.area, reverse=True)
        # Re-assign sequential ids
        for idx, seg in enumerate(segments):
            seg.id = idx

        return segments

    def _is_good_shape(self, mask: np.ndarray, bbox: list[int]) -> bool:
        """Filter out segments with poor shape characteristics.

        Args:
            mask: Boolean mask of the segment.
            bbox: Bounding box [x1, y1, x2, y2].

        Returns:
            True if the segment has acceptable shape characteristics.
        """
        x1, y1, x2, y2 = bbox
        bbox_width = x2 - x1
        bbox_height = y2 - y1

        # Skip very thin segments (likely artifacts or edges)
        if bbox_width < 5 or bbox_height < 5:
            return False

        # Calculate aspect ratio
        aspect_ratio = max(bbox_width, bbox_height) / max(min(bbox_width, bbox_height), 1)

        # Skip extremely elongated segments (likely edges or artifacts)
        if aspect_ratio > 10:
            return False

        # Calculate compactness (area / bbox_area)
        # Good segments should fill their bounding box reasonably
        bbox_area = bbox_width * bbox_height
        mask_area = np.sum(mask)
        compactness = mask_area / max(bbox_area, 1)

        # Skip very sparse segments
        if compactness < 0.15:
            return False

        return True

    def _remove_overlaps(self, segments: list[Segment], iou_threshold: float = 0.7) -> list[Segment]:
        """Remove highly overlapping segments, keeping the one with higher confidence.

        Args:
            segments: List of segments to filter.
            iou_threshold: IoU threshold above which segments are considered overlapping.

        Returns:
            Filtered list of segments with overlaps removed.
        """
        if len(segments) <= 1:
            return segments

        # Sort by confidence (descending) to keep higher confidence segments
        segments_sorted = sorted(segments, key=lambda s: s.confidence, reverse=True)

        keep = []
        for seg in segments_sorted:
            # Check if this segment overlaps significantly with any kept segment
            overlaps = False
            for kept_seg in keep:
                iou = self._calculate_iou(seg.mask, kept_seg.mask)
                if iou > iou_threshold:
                    overlaps = True
                    break

            if not overlaps:
                keep.append(seg)

        return keep

    @staticmethod
    def _calculate_iou(mask1: np.ndarray, mask2: np.ndarray) -> float:
        """Calculate Intersection over Union between two masks."""
        intersection = np.logical_and(mask1, mask2).sum()
        union = np.logical_or(mask1, mask2).sum()

        if union == 0:
            return 0.0

        return float(intersection) / float(union)

    @staticmethod
    def _mask_to_bbox(mask: np.ndarray) -> list[int] | None:
        """Compute bounding box [x1, y1, x2, y2] from a boolean mask."""
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        if not rows.any() or not cols.any():
            return None
        y1, y2 = np.where(rows)[0][[0, -1]]
        x1, x2 = np.where(cols)[0][[0, -1]]
        return [int(x1), int(y1), int(x2 + 1), int(y2 + 1)]
