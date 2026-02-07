"""Object colour changing via HSV hue shift."""

from __future__ import annotations

import random

import cv2
import numpy as np


class ColorChanger:
    """Changes the colour of masked regions by shifting hue in HSV space."""

    def change_hue(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        hue_shift: int | None = None,
    ) -> tuple[np.ndarray, int]:
        """Shift the hue of masked pixels in a BGR image.

        Args:
            image: BGR image (H, W, 3) uint8.
            mask: Boolean or uint8 mask (H, W).
            hue_shift: Hue shift in [30, 150]. Random if None.

        Returns:
            (modified_image, actual_hue_shift).
        """
        if hue_shift is None:
            hue_shift = random.randint(30, 150)

        bool_mask = mask.astype(bool)
        result = image.copy()

        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.int16)
        hsv[:, :, 0][bool_mask] = (hsv[:, :, 0][bool_mask] + hue_shift) % 180
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        # Blend edges for smoother transition
        result = self._blend_edges(image, result, bool_mask)
        return result, hue_shift

    def _blend_edges(
        self,
        original: np.ndarray,
        modified: np.ndarray,
        mask: np.ndarray,
    ) -> np.ndarray:
        """Feather the edges of the modified region for a smooth transition."""
        mask_u8 = mask.astype(np.uint8) * 255
        # Create a blurred version of the mask for feathering
        blurred = cv2.GaussianBlur(mask_u8, (5, 5), 2).astype(np.float32) / 255.0
        blurred = blurred[:, :, np.newaxis]

        result = (modified.astype(np.float32) * blurred +
                  original.astype(np.float32) * (1 - blurred))
        return result.astype(np.uint8)
