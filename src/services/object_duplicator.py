"""Object duplication with intelligent placement and blending."""

from __future__ import annotations

import random

import cv2
import numpy as np

from src.models.segment import Segment


class ObjectDuplicator:
    """Copies a segmented object to another location with intelligent placement."""

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
        placement = self._find_placement(image, segment)
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

        # Paste with advanced alpha blending
        target_region = result[new_y1:new_y2, new_x1:new_x2].copy()

        # Create feathered mask with distance transform for better blending
        mask_u8 = local_mask.astype(np.uint8) * 255
        dist_transform = cv2.distanceTransform(mask_u8, cv2.DIST_L2, 3)
        dist_transform = np.clip(dist_transform, 0, 5)
        alpha = (dist_transform / 5.0).astype(np.float32)

        # Apply Gaussian blur for smoother edges
        alpha = cv2.GaussianBlur((alpha * 255).astype(np.uint8), (5, 5), 1.5)
        alpha = alpha.astype(np.float32) / 255.0
        alpha = alpha[:, :, np.newaxis]

        # Color adaptation: slightly adjust object color to match target background
        adapted_obj = self._adapt_colors(obj_pixels, target_region, local_mask)

        # Blend with alpha
        blended = (adapted_obj.astype(np.float32) * alpha +
                   target_region.astype(np.float32) * (1 - alpha))
        result[new_y1:new_y2, new_x1:new_x2] = blended.astype(np.uint8)

        # Post-process to reduce artifacts
        result = self._post_process_addition(result, new_x1, new_y1, new_x2, new_y2, local_mask)

        new_bbox = [new_x1, new_y1, new_x2, new_y2]
        return result, new_bbox

    def _find_placement(
        self,
        image: np.ndarray,
        segment: Segment,
        max_attempts: int = 30,
    ) -> tuple[int, int] | None:
        """Find a non-overlapping placement with similar background.

        Returns None if no valid placement is found.
        """
        h, w = image.shape[:2]
        x1, y1, x2, y2 = segment.bbox
        obj_w, obj_h = x2 - x1, y2 - y1

        margin = 30  # minimum gap from original

        # Sample background color around original object
        orig_bg_color = self._sample_background_color(image, segment)

        best_placement = None
        best_score = float('inf')

        for _ in range(max_attempts):
            # Try random offset
            dx = random.randint(-w // 2, w // 2)
            dy = random.randint(-h // 2, h // 2)

            # Skip if too close to original
            if abs(dx) < obj_w + margin and abs(dy) < obj_h + margin:
                continue

            new_x1, new_y1 = x1 + dx, y1 + dy
            new_x2, new_y2 = new_x1 + obj_w, new_y1 + obj_h

            # Check bounds
            if new_x1 < 0 or new_y1 < 0 or new_x2 > w or new_y2 > h:
                continue

            # Sample target background color
            target_bg_color = self._sample_region_color(
                image,
                new_x1,
                new_y1,
                new_x2,
                new_y2,
            )

            # Calculate color similarity (lower is better)
            color_diff = np.linalg.norm(orig_bg_color - target_bg_color)

            if color_diff < best_score:
                best_score = color_diff
                best_placement = (dx, dy)

        return best_placement

    def _sample_background_color(
        self,
        image: np.ndarray,
        segment: Segment,
    ) -> np.ndarray:
        """Sample the average background color around a segment.

        Args:
            image: BGR image.
            segment: Segment to sample around.

        Returns:
            Average BGR color as float array.
        """
        x1, y1, x2, y2 = segment.bbox
        local_mask = segment.mask[y1:y2, x1:x2]

        # Invert mask to get background pixels
        bg_mask = ~local_mask.astype(bool)

        if np.count_nonzero(bg_mask) == 0:
            return np.array([128, 128, 128], dtype=np.float32)

        bg_pixels = image[y1:y2, x1:x2][bg_mask]
        return np.mean(bg_pixels, axis=0).astype(np.float32)

    def _sample_region_color(
        self,
        image: np.ndarray,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
    ) -> np.ndarray:
        """Sample the average color of a region.

        Args:
            image: BGR image.
            x1, y1, x2, y2: Region bounds.

        Returns:
            Average BGR color as float array.
        """
        region = image[y1:y2, x1:x2]
        return np.mean(region.reshape(-1, 3), axis=0).astype(np.float32)

    def _adapt_colors(
        self,
        obj_pixels: np.ndarray,
        target_bg: np.ndarray,
        mask: np.ndarray,
    ) -> np.ndarray:
        """Adapt object colors to match target background lighting.

        Args:
            obj_pixels: Object pixel values.
            target_bg: Target background pixels.
            mask: Object mask.

        Returns:
            Color-adapted object pixels.
        """
        # Calculate average brightness difference
        obj_brightness = np.mean(cv2.cvtColor(obj_pixels, cv2.COLOR_BGR2GRAY))
        bg_brightness = np.mean(cv2.cvtColor(target_bg, cv2.COLOR_BGR2GRAY))

        brightness_ratio = bg_brightness / max(obj_brightness, 1)

        # Limit adjustment to avoid overexposure
        brightness_ratio = np.clip(brightness_ratio, 0.85, 1.15)

        # Apply subtle brightness adjustment
        adapted = obj_pixels.astype(np.float32) * brightness_ratio
        adapted = np.clip(adapted, 0, 255).astype(np.uint8)

        return adapted

    def _post_process_addition(
        self,
        image: np.ndarray,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        mask: np.ndarray,
    ) -> np.ndarray:
        """Apply post-processing to reduce artifacts around added object.

        Args:
            image: Image with added object.
            x1, y1, x2, y2: Bounding box of added object.
            mask: Local mask of object.

        Returns:
            Post-processed image.
        """
        result = image.copy()

        # Apply gentle bilateral filter to edge region
        mask_u8 = mask.astype(np.uint8) * 255
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dilated = cv2.dilate(mask_u8, kernel, iterations=2)
        eroded = cv2.erode(mask_u8, kernel, iterations=1)
        edge_mask = (dilated > 0) & (eroded == 0)

        if np.count_nonzero(edge_mask) > 0:
            region = result[y1:y2, x1:x2]
            filtered = cv2.bilateralFilter(region, d=7, sigmaColor=50, sigmaSpace=50)
            region[edge_mask] = filtered[edge_mask]
            result[y1:y2, x1:x2] = region

        return result
