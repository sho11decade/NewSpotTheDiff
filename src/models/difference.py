"""Difference and generation result data models."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

import numpy as np


@dataclass
class Difference:
    """A single difference applied to the image."""

    id: int
    type: str  # "deletion", "color_change", "addition"
    bbox: list[int]  # [x1, y1, x2, y2]
    saliency_score: float
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GenerationResult:
    """Result of the spot-the-difference generation pipeline."""

    original_image: np.ndarray
    modified_image: np.ndarray
    differences: list[Difference]
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_metadata_with_differences(self) -> dict[str, Any]:
        return {
            **self.metadata,
            "differences": [d.to_dict() for d in self.differences],
            "total_differences": len(self.differences),
        }
