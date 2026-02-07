"""Image I/O and resizing utilities."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def load_image(path: str | Path) -> np.ndarray:
    """Load an image as a BGR numpy array.

    Raises FileNotFoundError if the path does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Failed to decode image: {path}")
    return img


def save_image(image: np.ndarray, path: str | Path) -> None:
    """Save a BGR numpy array as an image file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    success = cv2.imwrite(str(path), image)
    if not success:
        raise IOError(f"Failed to save image: {path}")


def resize_for_processing(image: np.ndarray, max_size: int = 1024) -> tuple[np.ndarray, float]:
    """Resize image so the longest side is at most max_size.

    Returns (resized_image, scale_factor).
    scale_factor is 1.0 if no resize was needed.
    """
    h, w = image.shape[:2]
    scale = min(max_size / max(h, w), 1.0)
    if scale < 1.0:
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return resized, scale
    return image, 1.0


def scale_up_result(
    processed: np.ndarray,
    original: np.ndarray,
    scale: float,
) -> np.ndarray:
    """Scale the processed image back to the original dimensions.

    Blends the processed result into the original where changes were applied.
    """
    if scale >= 1.0:
        return processed
    h, w = original.shape[:2]
    return cv2.resize(processed, (w, h), interpolation=cv2.INTER_LANCZOS4)


def get_image_dimensions(path: str | Path) -> tuple[int, int]:
    """Return (width, height) of the image at path without fully loading it."""
    with Image.open(path) as img:
        return img.size
