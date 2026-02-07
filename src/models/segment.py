"""Segment data model for detected objects."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Segment:
    """A detected object segment in an image."""

    id: int
    mask: np.ndarray  # (H, W) boolean mask
    bbox: list[int]  # [x1, y1, x2, y2]
    area: int
    confidence: float = 0.0
    saliency_score: float = 0.0

    @property
    def width(self) -> int:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> int:
        return self.bbox[3] - self.bbox[1]

    @property
    def center(self) -> tuple[int, int]:
        cx = (self.bbox[0] + self.bbox[2]) // 2
        cy = (self.bbox[1] + self.bbox[3]) // 2
        return cx, cy
