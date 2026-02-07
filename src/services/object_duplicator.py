"""Object duplication / addition by copying segments to new positions."""

from __future__ import annotations

import random

import cv2
import numpy as np

from src.models.segment import Segment


class ObjectDuplicator:
    """Copies a segmented object to another location in the image."""

    def duplicate(
        self,
        image: np.ndarray,
        segment: Segment,
    ) -> tuple[np.ndarray, list[int] | None]:
        """Duplicate the segment's object to a new location.

        Args:
            image: BGR image (H, W, 3) uint8.
            segment: The Segment to duplicate.

        Returns:
            (modified_image, new_bbox) or (original_image, None) on failure.
        """
        placement = self._find_placement(image.shape, segment)
        if placement is None:
            return image, None

        dx, dy = placement
        x1, y1, x2, y2 = segment.bbox
        obj_h, obj_w = y2 - y1, x2 - x1

        new_x1, new_y1 = x1 + dx, y1 + dy
        new_x2, new_y2 = new_x1 + obj_w, new_y1 + obj_h

        # Extract object pixels and its local mask
        local_mask = segment.mask[y1:y2, x1:x2].astype(bool)
        obj_pixels = image[y1:y2, x1:x2].copy()

        result = image.copy()

        # Paste with alpha blending at the edges
        target_region = result[new_y1:new_y2, new_x1:new_x2]

        # Create feathered mask for blending
        mask_u8 = local_mask.astype(np.uint8) * 255
        blurred = cv2.GaussianBlur(mask_u8, (3, 3), 1).astype(np.float32) / 255.0
        blurred = blurred[:, :, np.newaxis]

        blended = (obj_pixels.astype(np.float32) * blurred +
                   target_region.astype(np.float32) * (1 - blurred))
        result[new_y1:new_y2, new_x1:new_x2] = blended.astype(np.uint8)

        new_bbox = [new_x1, new_y1, new_x2, new_y2]
        return result, new_bbox

    def _find_placement(
        self,
        image_shape: tuple,
        segment: Segment,
        max_attempts: int = 20,
    ) -> tuple[int, int] | None:
        """Find a non-overlapping placement offset (dx, dy).

        Returns None if no valid placement is found.
        """
        h, w = image_shape[:2]
        x1, y1, x2, y2 = segment.bbox
        obj_w, obj_h = x2 - x1, y2 - y1

        margin = 20  # minimum gap from original

        for _ in range(max_attempts):
            # Try random offset
            dx = random.randint(-w // 3, w // 3)
            dy = random.randint(-h // 3, h // 3)

            # Skip if too close to original
            if abs(dx) < obj_w + margin and abs(dy) < obj_h + margin:
                continue

            new_x1, new_y1 = x1 + dx, y1 + dy
            new_x2, new_y2 = new_x1 + obj_w, new_y1 + obj_h

            # Check bounds
            if new_x1 < 0 or new_y1 < 0 or new_x2 > w or new_y2 > h:
                continue

            return dx, dy

        return None
