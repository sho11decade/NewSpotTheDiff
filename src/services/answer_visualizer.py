"""Answer visualization: draws red circles on differences."""

from __future__ import annotations

import cv2
import numpy as np

from src.models.difference import Difference


class AnswerVisualizer:
    """Visualizes answers by drawing red circles around differences."""

    def __init__(self, circle_color: tuple[int, int, int] = (0, 0, 255), thickness: int = 3):
        """Initialize the answer visualizer.

        Args:
            circle_color: BGR color for circles (default: red).
            thickness: Circle line thickness.
        """
        self._color = circle_color
        self._thickness = thickness

    def draw_answers(
        self,
        image: np.ndarray,
        differences: list[Difference],
        padding_ratio: float = 0.15,
    ) -> np.ndarray:
        """Draw red circles around each difference on the image.

        Args:
            image: BGR image (H, W, 3) uint8.
            differences: List of differences to mark.
            padding_ratio: Extra padding around bbox as ratio of bbox size.

        Returns:
            Image with red circles drawn around differences.
        """
        result = image.copy()

        for diff in differences:
            x1, y1, x2, y2 = diff.bbox

            # Calculate center and radius
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            # Calculate radius as diagonal distance from center to corner, plus padding
            width = x2 - x1
            height = y2 - y1
            radius = int(np.sqrt(width**2 + height**2) / 2 * (1 + padding_ratio))

            # Ensure radius is at least visible
            radius = max(radius, 20)

            # Draw circle
            cv2.circle(result, (center_x, center_y), radius, self._color, self._thickness)

            # Optionally draw a smaller filled circle at center for emphasis
            cv2.circle(result, (center_x, center_y), 5, self._color, -1)

        return result

    def create_answer_overlay(
        self,
        original: np.ndarray,
        modified: np.ndarray,
        differences: list[Difference],
    ) -> tuple[np.ndarray, np.ndarray]:
        """Create answer overlays for both original and modified images.

        Args:
            original: Original image.
            modified: Modified image with differences.
            differences: List of differences.

        Returns:
            Tuple of (original_with_answers, modified_with_answers).
        """
        original_marked = self.draw_answers(original, differences)
        modified_marked = self.draw_answers(modified, differences)

        return original_marked, modified_marked
