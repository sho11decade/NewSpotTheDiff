"""Quality evaluation for segments and modifications."""

from __future__ import annotations

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

from src.models.segment import Segment


class QualityEvaluator:
    """Evaluates the quality of segments and image modifications."""

    def __init__(
        self,
        min_edge_smoothness: float = 0.6,
        min_mask_completeness: float = 0.85,
        min_ssim_score: float = 0.7,
    ):
        """Initialize quality evaluator.

        Args:
            min_edge_smoothness: Minimum edge smoothness score (0-1).
            min_mask_completeness: Minimum mask completeness ratio.
            min_ssim_score: Minimum SSIM score for modifications.
        """
        self._min_edge_smoothness = min_edge_smoothness
        self._min_mask_completeness = min_mask_completeness
        self._min_ssim_score = min_ssim_score

    def evaluate_segment_quality(
        self,
        image: np.ndarray,
        segment: Segment,
    ) -> tuple[bool, float, str]:
        """Evaluate the quality of a segment.

        Args:
            image: Original BGR image.
            segment: Segment to evaluate.

        Returns:
            Tuple of (is_acceptable, quality_score, reason).
        """
        x1, y1, x2, y2 = segment.bbox
        mask = segment.mask[y1:y2, x1:x2]

        # Check 1: Edge smoothness
        edge_score = self._evaluate_edge_smoothness(mask)
        if edge_score < self._min_edge_smoothness:
            return False, edge_score, f"エッジが荒い (score: {edge_score:.2f})"

        # Check 2: Mask completeness
        completeness = self._evaluate_mask_completeness(mask, segment.bbox)
        if completeness < self._min_mask_completeness:
            return False, completeness, f"マスクが不完全 (score: {completeness:.2f})"

        # Check 3: Shape complexity (avoid overly complex shapes)
        complexity = self._evaluate_shape_complexity(mask)
        if complexity > 0.8:  # Too complex
            return False, 1.0 - complexity, "形状が複雑すぎる"

        # Check 4: Contour quality
        if not self._has_valid_contour(mask):
            return False, 0.0, "有効な輪郭がない"

        # Calculate overall quality score
        overall_score = (edge_score + completeness + (1.0 - complexity)) / 3.0

        return True, overall_score, "合格"

    def evaluate_modification_quality(
        self,
        original_region: np.ndarray,
        modified_region: np.ndarray,
        mask: np.ndarray,
        modification_type: str,
    ) -> tuple[bool, float, str]:
        """Evaluate the quality of a modification.

        Args:
            original_region: Original image region.
            modified_region: Modified image region.
            mask: Binary mask of modification area.
            modification_type: Type of modification.

        Returns:
            Tuple of (is_acceptable, quality_score, reason).
        """
        # Check 1: SSIM score (structural similarity)
        # We want high similarity in non-modified areas
        mask_inv = ~mask.astype(bool)
        if np.count_nonzero(mask_inv) > 100:
            # Check similarity in surrounding area
            orig_gray = cv2.cvtColor(original_region, cv2.COLOR_BGR2GRAY)
            mod_gray = cv2.cvtColor(modified_region, cv2.COLOR_BGR2GRAY)

            # Compute SSIM on entire region
            score, _ = ssim(orig_gray, mod_gray, full=True)

            # For modifications, we expect some difference
            # But surrounding areas should be very similar
            if modification_type == "deletion":
                # Deletion should look natural
                if score < 0.5:  # Too different
                    return False, score, "削除が不自然 (SSIM低い)"
            elif modification_type == "color_change":
                # Color change should preserve structure
                if score < 0.7:  # Structure changed too much
                    return False, score, "構造が変わりすぎている"

        # Check 2: Edge artifacts
        artifact_score = self._detect_edge_artifacts(original_region, modified_region, mask)
        if artifact_score > 0.3:  # Too many artifacts
            return False, 1.0 - artifact_score, f"エッジにアーティファクト (score: {artifact_score:.2f})"

        # Check 3: Color naturalness
        if modification_type == "color_change":
            color_score = self._evaluate_color_naturalness(modified_region, mask)
            if color_score < 0.5:
                return False, color_score, "色が不自然"

        # Check 4: Continuity (for additions)
        if modification_type == "addition":
            continuity_score = self._evaluate_addition_continuity(modified_region, mask)
            if continuity_score < 0.6:
                return False, continuity_score, "追加が不自然"

        return True, 0.9, "合格"

    def _evaluate_edge_smoothness(self, mask: np.ndarray) -> float:
        """Evaluate how smooth the edges of a mask are.

        Args:
            mask: Binary mask.

        Returns:
            Smoothness score (0-1, higher is smoother).
        """
        mask_u8 = mask.astype(np.uint8) * 255

        # Find contours
        contours, _ = cv2.findContours(mask_u8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if not contours:
            return 0.0

        # Get the largest contour
        contour = max(contours, key=cv2.contourArea)

        # Calculate perimeter and area
        perimeter = cv2.arcLength(contour, True)
        area = cv2.contourArea(contour)

        if area == 0:
            return 0.0

        # Circularity: 4π * area / perimeter²
        # Perfect circle = 1.0
        # More irregular shapes have lower values
        circularity = 4 * np.pi * area / (perimeter * perimeter + 1e-6)

        # Approximate the contour to measure smoothness
        epsilon = 0.02 * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Smoothness: fewer points after approximation = smoother
        smoothness = 1.0 - min(len(approx) / (perimeter / 10), 1.0)

        # Combine circularity and smoothness
        return (circularity * 0.6 + smoothness * 0.4)

    def _evaluate_mask_completeness(
        self,
        mask: np.ndarray,
        bbox: list[int],
    ) -> float:
        """Evaluate how complete a mask is within its bounding box.

        Args:
            mask: Binary mask (local coordinates).
            bbox: Bounding box [x1, y1, x2, y2].

        Returns:
            Completeness score (0-1).
        """
        x1, y1, x2, y2 = bbox
        bbox_area = (x2 - x1) * (y2 - y1)
        mask_area = np.count_nonzero(mask)

        if bbox_area == 0:
            return 0.0

        # Ratio of mask area to bounding box area
        ratio = mask_area / bbox_area

        # Good segments should have 0.5-0.9 ratio
        # (not too sparse, not filling entire bbox)
        if ratio < 0.3:
            return ratio / 0.3  # Penalize very sparse masks
        elif ratio > 0.95:
            return max(0.0, 1.0 - (ratio - 0.95) * 20)  # Penalize masks that fill bbox
        else:
            return 1.0

    def _evaluate_shape_complexity(self, mask: np.ndarray) -> float:
        """Evaluate the complexity of a shape.

        Args:
            mask: Binary mask.

        Returns:
            Complexity score (0-1, higher is more complex).
        """
        mask_u8 = mask.astype(np.uint8) * 255

        # Find contours
        contours, _ = cv2.findContours(mask_u8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return 1.0

        contour = max(contours, key=cv2.contourArea)

        # Number of vertices in simplified contour
        perimeter = cv2.arcLength(contour, True)
        epsilon = 0.01 * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Complexity based on number of vertices
        # Simple shapes: 3-8 vertices
        # Complex shapes: >15 vertices
        num_vertices = len(approx)
        if num_vertices <= 8:
            return 0.2
        elif num_vertices <= 12:
            return 0.5
        else:
            return min(1.0, 0.5 + (num_vertices - 12) * 0.05)

    def _has_valid_contour(self, mask: np.ndarray) -> bool:
        """Check if mask has a valid contour.

        Args:
            mask: Binary mask.

        Returns:
            True if valid contour exists.
        """
        mask_u8 = mask.astype(np.uint8) * 255

        contours, _ = cv2.findContours(mask_u8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return False

        # Check if largest contour has reasonable area
        contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(contour)

        return area > 100  # Minimum 100 pixels

    def _detect_edge_artifacts(
        self,
        original: np.ndarray,
        modified: np.ndarray,
        mask: np.ndarray,
    ) -> float:
        """Detect artifacts around edges of modification.

        Args:
            original: Original region.
            modified: Modified region.
            mask: Binary mask.

        Returns:
            Artifact score (0-1, higher means more artifacts).
        """
        # Create edge region (border of mask)
        mask_u8 = mask.astype(np.uint8) * 255
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dilated = cv2.dilate(mask_u8, kernel, iterations=2)
        eroded = cv2.erode(mask_u8, kernel, iterations=2)
        edge_region = (dilated > 0) & (eroded == 0)

        if np.count_nonzero(edge_region) == 0:
            return 0.0

        # Calculate gradient magnitude in edge region
        orig_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        mod_gray = cv2.cvtColor(modified, cv2.COLOR_BGR2GRAY)

        orig_grad = cv2.Sobel(orig_gray, cv2.CV_64F, 1, 1, ksize=3)
        mod_grad = cv2.Sobel(mod_gray, cv2.CV_64F, 1, 1, ksize=3)

        # Compare gradients in edge region
        orig_edge_grad = np.abs(orig_grad[edge_region]).mean()
        mod_edge_grad = np.abs(mod_grad[edge_region]).mean()

        # High increase in gradient = artifacts
        if orig_edge_grad < 1.0:
            orig_edge_grad = 1.0

        gradient_increase = (mod_edge_grad - orig_edge_grad) / orig_edge_grad

        # Normalize to 0-1
        artifact_score = min(1.0, max(0.0, gradient_increase / 2.0))

        return artifact_score

    def _evaluate_color_naturalness(
        self,
        image: np.ndarray,
        mask: np.ndarray,
    ) -> float:
        """Evaluate if colors in the modified region look natural.

        Args:
            image: Modified image region.
            mask: Binary mask of modified area.

        Returns:
            Naturalness score (0-1).
        """
        masked_region = image[mask.astype(bool)]

        if len(masked_region) == 0:
            return 1.0

        # Convert to HSV
        hsv_region = cv2.cvtColor(
            masked_region.reshape(-1, 1, 3),
            cv2.COLOR_BGR2HSV
        ).reshape(-1, 3)

        # Check saturation distribution
        saturations = hsv_region[:, 1]
        mean_sat = np.mean(saturations)
        std_sat = np.std(saturations)

        # Unnatural: overly saturated or no variation
        if mean_sat > 220:  # Too saturated
            return 0.3
        if std_sat < 5:  # No variation (might be flat color)
            return 0.5

        # Check for extreme values
        values = hsv_region[:, 2]
        if np.mean(values) > 250 or np.mean(values) < 20:
            return 0.4  # Too bright or too dark

        return 0.9

    def _evaluate_addition_continuity(
        self,
        image: np.ndarray,
        mask: np.ndarray,
    ) -> float:
        """Evaluate continuity of added object with surroundings.

        Args:
            image: Image region with added object.
            mask: Binary mask of added object.

        Returns:
            Continuity score (0-1).
        """
        mask_u8 = mask.astype(np.uint8) * 255

        # Get border region
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dilated = cv2.dilate(mask_u8, kernel, iterations=2)
        border = (dilated > 0) & (mask_u8 == 0)

        if np.count_nonzero(border) == 0:
            return 1.0

        # Calculate color difference at border
        object_pixels = image[mask.astype(bool)]
        border_pixels = image[border]

        if len(object_pixels) == 0 or len(border_pixels) == 0:
            return 1.0

        # Mean color difference
        object_color = np.mean(object_pixels, axis=0)
        border_color = np.mean(border_pixels, axis=0)

        color_diff = np.linalg.norm(object_color - border_color)

        # Normalize (0-255 range -> 0-1)
        continuity = 1.0 - min(1.0, color_diff / 150.0)

        return continuity
