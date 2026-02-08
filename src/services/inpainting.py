"""Image inpainting using OpenCV methods with quality comparison."""

from __future__ import annotations

import cv2
import numpy as np


class InpaintingService:
    """Removes objects from images by inpainting masked regions."""

    def __init__(self, radius: int = 5, method: str = "auto") -> None:
        """Initialize inpainting service.

        Args:
            radius: Base inpaint radius.
            method: "ns", "telea", or "auto" (tries both and picks best).
        """
        self._base_radius = radius
        self._method = method

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

        if self._method == "auto":
            # Try both methods and pick the one with better quality
            result_ns = cv2.inpaint(image, mask_u8, radius, cv2.INPAINT_NS)
            result_telea = cv2.inpaint(image, mask_u8, radius, cv2.INPAINT_TELEA)

            # Evaluate quality based on smoothness around edges
            quality_ns = self._evaluate_quality(result_ns, mask_u8)
            quality_telea = self._evaluate_quality(result_telea, mask_u8)

            result = result_ns if quality_ns > quality_telea else result_telea
        elif self._method == "telea":
            result = cv2.inpaint(image, mask_u8, radius, cv2.INPAINT_TELEA)
        else:
            result = cv2.inpaint(image, mask_u8, radius, cv2.INPAINT_NS)

        # Post-process to reduce artifacts
        result = self._post_process(result, mask_u8)
        return result

    def _prepare_mask(self, mask: np.ndarray) -> np.ndarray:
        """Ensure mask is uint8 with values 0 or 255, and slightly dilated."""
        m = mask.astype(np.uint8)
        if m.max() == 1:
            m = m * 255
        # Dilate mask slightly to cover edge artefacts
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        m = cv2.dilate(m, kernel, iterations=2)
        return m

    def _adaptive_radius(self, mask_u8: np.ndarray) -> int:
        """Choose inpaint radius based on mask size."""
        mask_pixels = np.count_nonzero(mask_u8)
        total_pixels = mask_u8.shape[0] * mask_u8.shape[1]
        ratio = mask_pixels / total_pixels

        if ratio < 0.01:
            return max(self._base_radius, 5)
        elif ratio < 0.05:
            return max(self._base_radius, 10)
        else:
            return max(self._base_radius, 15)

    def _evaluate_quality(self, image: np.ndarray, mask: np.ndarray) -> float:
        """Evaluate inpainting quality based on edge smoothness.

        Args:
            image: Inpainted image.
            mask: Binary mask of inpainted region.

        Returns:
            Quality score (higher is better).
        """
        # Create a border region around the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dilated = cv2.dilate(mask, kernel, iterations=2)
        border = dilated - mask

        if np.count_nonzero(border) == 0:
            return 0.0

        # Calculate gradient magnitude in border region
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient = np.sqrt(grad_x**2 + grad_y**2)

        # Lower gradient in border means smoother transition
        border_gradient = gradient[border > 0].mean()

        # Return inverse of gradient (smoother = higher quality)
        return 1.0 / (border_gradient + 1.0)

    def _post_process(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Apply post-processing to reduce artifacts.

        Args:
            image: Inpainted image.
            mask: Binary mask of inpainted region.

        Returns:
            Post-processed image.
        """
        result = image.copy()

        # Apply gentle bilateral filter to inpainted region
        mask_bool = mask > 0
        if np.count_nonzero(mask_bool) > 0:
            # Create eroded mask for core region
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            eroded = cv2.erode(mask, kernel, iterations=1)
            core_bool = eroded > 0

            if np.count_nonzero(core_bool) > 0:
                # Apply bilateral filter to smooth while preserving edges
                filtered = cv2.bilateralFilter(result, d=9, sigmaColor=75, sigmaSpace=75)
                result[core_bool] = filtered[core_bool]

        return result
