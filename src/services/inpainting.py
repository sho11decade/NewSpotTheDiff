"""Image inpainting using OpenCV Navier-Stokes method."""

from __future__ import annotations

import cv2
import numpy as np


class InpaintingService:
    """Removes objects from images by inpainting masked regions."""

    def __init__(self, radius: int = 5, method: str = "ns") -> None:
        self._base_radius = radius
        self._flag = cv2.INPAINT_NS if method == "ns" else cv2.INPAINT_TELEA

    def inpaint(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Inpaint the masked region of a BGR image.

        Args:
            image: BGR image (H, W, 3) uint8.
            mask: Binary mask (H, W). Non-zero pixels are inpainted.

        Returns:
            Inpainted BGR image.
        """
        mask_u8 = self._prepare_mask(mask)
        radius = self._adaptive_radius(mask_u8)
        result = cv2.inpaint(image, mask_u8, radius, self._flag)
        return result

    def _prepare_mask(self, mask: np.ndarray) -> np.ndarray:
        """Ensure mask is uint8 with values 0 or 255, and slightly dilated."""
        m = mask.astype(np.uint8)
        if m.max() == 1:
            m = m * 255
        # Dilate mask slightly to cover edge artefacts
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        m = cv2.dilate(m, kernel, iterations=1)
        return m

    def _adaptive_radius(self, mask_u8: np.ndarray) -> int:
        """Choose inpaint radius based on mask size."""
        mask_pixels = np.count_nonzero(mask_u8)
        total_pixels = mask_u8.shape[0] * mask_u8.shape[1]
        ratio = mask_pixels / total_pixels

        if ratio < 0.01:
            return max(self._base_radius, 3)
        elif ratio < 0.05:
            return max(self._base_radius, 7)
        else:
            return max(self._base_radius, 12)
