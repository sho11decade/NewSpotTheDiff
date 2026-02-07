"""Saliency map computation using OpenCV Spectral Residual."""

from __future__ import annotations

import cv2
import numpy as np

from src.models.segment import Segment


class SaliencyService:
    """Computes saliency maps and scores segments by visual attention."""

    def __init__(self) -> None:
        self._detector = cv2.saliency.StaticSaliencySpectralResidual_create()

    def compute_map(self, image: np.ndarray) -> np.ndarray:
        """Compute a normalised saliency map from a BGR image.

        Returns a float32 array of shape (H, W) with values in [0.0, 1.0].
        """
        success, saliency_map = self._detector.computeSaliency(image)
        if not success:
            raise RuntimeError("Saliency computation failed")

        saliency_map = cv2.GaussianBlur(saliency_map, (25, 25), 0)
        saliency_map = cv2.normalize(
            saliency_map, None, 0.0, 1.0, cv2.NORM_MINMAX, dtype=cv2.CV_32F
        )
        return saliency_map

    def score_segment(self, saliency_map: np.ndarray, segment: Segment) -> float:
        """Compute the mean saliency score for a segment's mask region."""
        mask = segment.mask.astype(bool)
        if not mask.any():
            return 0.0
        return float(np.mean(saliency_map[mask]))

    def rank_segments(
        self, segments: list[Segment], saliency_map: np.ndarray
    ) -> list[Segment]:
        """Score all segments and return them sorted by saliency (ascending).

        Low-saliency segments come first (harder to notice).
        """
        for seg in segments:
            seg.saliency_score = self.score_segment(saliency_map, seg)
        return sorted(segments, key=lambda s: s.saliency_score)
