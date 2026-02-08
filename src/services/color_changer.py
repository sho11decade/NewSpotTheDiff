"""Object colour changing via intelligent HSV manipulation."""

from __future__ import annotations

import random

import cv2
import numpy as np


class ColorChanger:
    """Changes the colour of masked regions with intelligent color selection."""

    def change_hue(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        hue_shift: int | None = None,
    ) -> tuple[np.ndarray, int]:
        """Shift the hue of masked pixels in a BGR image with intelligent selection.

        Args:
            image: BGR image (H, W, 3) uint8.
            mask: Boolean or uint8 mask (H, W).
            hue_shift: Hue shift in [30, 150]. Random if None.

        Returns:
            (modified_image, actual_hue_shift).
        """
        bool_mask = mask.astype(bool)
        result = image.copy()

        # Analyze original color to avoid similar hues
        if hue_shift is None:
            hue_shift = self._intelligent_hue_selection(image, bool_mask)

        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)

        # Apply hue shift with slight saturation and value adjustments
        hsv[:, :, 0][bool_mask] = (hsv[:, :, 0][bool_mask] + hue_shift) % 180

        # Slightly adjust saturation to make color more vibrant (but not oversaturated)
        sat_factor = random.uniform(1.05, 1.15)
        hsv[:, :, 1][bool_mask] = np.clip(hsv[:, :, 1][bool_mask] * sat_factor, 0, 255)

        # Slight value adjustment to maintain visibility
        val_factor = random.uniform(0.95, 1.05)
        hsv[:, :, 2][bool_mask] = np.clip(hsv[:, :, 2][bool_mask] * val_factor, 0, 255)

        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        # Blend edges for smoother transition
        result = self._blend_edges(image, result, bool_mask)
        return result, hue_shift

    def _intelligent_hue_selection(
        self,
        image: np.ndarray,
        mask: np.ndarray,
    ) -> int:
        """Select a hue shift that is visibly different from the original.

        Args:
            image: BGR image.
            mask: Boolean mask of region to change.

        Returns:
            Hue shift value.
        """
        # Get average hue of masked region
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        masked_hues = hsv[:, :, 0][mask]

        if len(masked_hues) == 0:
            return random.randint(60, 120)

        avg_hue = np.median(masked_hues)

        # Generate candidate hue shifts that are visibly different
        # Avoid shifts too close to original (within 30 degrees)
        # and avoid shifts that result in similar colors
        candidates = []

        # Prefer complementary or triadic colors
        for base in [90, 120, 150]:  # Complementary and triadic
            for offset in [-30, -15, 0, 15, 30]:
                shift = base + offset
                new_hue = (avg_hue + shift) % 180
                # Check if sufficiently different
                hue_diff = min(abs(new_hue - avg_hue), 180 - abs(new_hue - avg_hue))
                if hue_diff >= 40:  # At least 40 degrees difference
                    candidates.append(shift)

        if candidates:
            return random.choice(candidates)
        else:
            # Fallback to large shift
            return random.choice([90, 100, 110, 120])

    def _blend_edges(
        self,
        original: np.ndarray,
        modified: np.ndarray,
        mask: np.ndarray,
    ) -> np.ndarray:
        """Feather the edges of the modified region for a smooth transition."""
        mask_u8 = mask.astype(np.uint8) * 255

        # Create a more sophisticated edge blending
        # Use distance transform for smoother gradient
        dist_transform = cv2.distanceTransform(mask_u8, cv2.DIST_L2, 3)
        dist_transform = np.clip(dist_transform, 0, 5)
        dist_transform = dist_transform / 5.0  # Normalize to [0, 1]

        # Apply Gaussian blur for smoother transition
        blurred = cv2.GaussianBlur((dist_transform * 255).astype(np.uint8), (7, 7), 2)
        blurred = blurred.astype(np.float32) / 255.0
        blurred = blurred[:, :, np.newaxis]

        result = (modified.astype(np.float32) * blurred +
                  original.astype(np.float32) * (1 - blurred))
        return result.astype(np.uint8)
