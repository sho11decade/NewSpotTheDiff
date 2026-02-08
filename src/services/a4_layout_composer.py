"""A4 layout composer: creates side-by-side comparison in A4 landscape format."""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


class A4LayoutComposer:
    """Composes two images side-by-side in A4 landscape format."""

    # A4 landscape at 300 DPI: 3508 x 2480 pixels
    A4_WIDTH = 3508
    A4_HEIGHT = 2480

    def __init__(
        self,
        dpi: int = 300,
        margin: int = 100,
        gap: int = 80,
        bg_color: tuple[int, int, int] = (255, 255, 255),
    ):
        """Initialize the A4 layout composer.

        Args:
            dpi: DPI for A4 size calculation (default: 300).
            margin: Margin around edges in pixels.
            gap: Gap between images in pixels.
            bg_color: Background color (RGB).
        """
        self._dpi = dpi
        self._margin = margin
        self._gap = gap
        self._bg_color = bg_color

        # Calculate A4 dimensions based on DPI
        # A4 = 297mm x 210mm
        if dpi != 300:
            self.A4_WIDTH = int(297 * dpi / 25.4)
            self.A4_HEIGHT = int(210 * dpi / 25.4)

    def compose_side_by_side(
        self,
        left_image: np.ndarray,
        right_image: np.ndarray,
        left_title: str = "元の画像",
        right_title: str = "間違い探し",
        title: str = "間違い探しパズル",
    ) -> np.ndarray:
        """Create a side-by-side comparison in A4 landscape format.

        Args:
            left_image: Left image (BGR).
            right_image: Right image (BGR).
            left_title: Title for left image.
            right_title: Title for right image.
            title: Main title at the top.

        Returns:
            A4 landscape image with side-by-side comparison.
        """
        # Convert BGR to RGB for PIL
        left_rgb = cv2.cvtColor(left_image, cv2.COLOR_BGR2RGB)
        right_rgb = cv2.cvtColor(right_image, cv2.COLOR_BGR2RGB)

        # Create A4 canvas
        canvas = Image.new("RGB", (self.A4_WIDTH, self.A4_HEIGHT), self._bg_color)
        draw = ImageDraw.Draw(canvas)

        # Calculate available space for images
        title_height = 150
        available_width = self.A4_WIDTH - 2 * self._margin - self._gap
        available_height = self.A4_HEIGHT - 2 * self._margin - title_height
        image_width = available_width // 2
        image_height = available_height - 60  # Reserve space for labels

        # Resize images to fit
        left_resized = self._resize_to_fit(left_rgb, image_width, image_height)
        right_resized = self._resize_to_fit(right_rgb, image_width, image_height)

        # Calculate positions
        left_x = self._margin
        right_x = self._margin + image_width + self._gap
        image_y = self._margin + title_height + 60

        # Draw main title
        try:
            # Try to use a Japanese font if available
            title_font = self._get_japanese_font(60)
        except Exception:
            title_font = None

        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.A4_WIDTH - title_width) // 2
        draw.text((title_x, self._margin + 20), title, fill=(0, 0, 0), font=title_font)

        # Draw labels
        try:
            label_font = self._get_japanese_font(40)
        except Exception:
            label_font = None

        label_y = self._margin + title_height
        left_bbox = draw.textbbox((0, 0), left_title, font=label_font)
        left_label_width = left_bbox[2] - left_bbox[0]
        left_label_x = left_x + (image_width - left_label_width) // 2

        right_bbox = draw.textbbox((0, 0), right_title, font=label_font)
        right_label_width = right_bbox[2] - right_bbox[0]
        right_label_x = right_x + (image_width - right_label_width) // 2

        draw.text((left_label_x, label_y), left_title, fill=(0, 0, 0), font=label_font)
        draw.text((right_label_x, label_y), right_title, fill=(0, 0, 0), font=label_font)

        # Paste images
        left_pil = Image.fromarray(left_resized)
        right_pil = Image.fromarray(right_resized)

        # Center images horizontally in their sections
        left_img_x = left_x + (image_width - left_pil.width) // 2
        right_img_x = right_x + (image_width - right_pil.width) // 2

        canvas.paste(left_pil, (left_img_x, image_y))
        canvas.paste(right_pil, (right_img_x, image_y))

        # Draw border around images
        draw.rectangle(
            [left_img_x - 2, image_y - 2, left_img_x + left_pil.width + 2, image_y + left_pil.height + 2],
            outline=(200, 200, 200),
            width=2,
        )
        draw.rectangle(
            [right_img_x - 2, image_y - 2, right_img_x + right_pil.width + 2, image_y + right_pil.height + 2],
            outline=(200, 200, 200),
            width=2,
        )

        # Convert back to BGR for OpenCV
        result = cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)
        return result

    def _resize_to_fit(self, image: np.ndarray, max_width: int, max_height: int) -> np.ndarray:
        """Resize image to fit within max dimensions while preserving aspect ratio.

        Args:
            image: RGB image array.
            max_width: Maximum width.
            max_height: Maximum height.

        Returns:
            Resized RGB image.
        """
        h, w = image.shape[:2]
        scale = min(max_width / w, max_height / h)

        if scale < 1:
            new_w = int(w * scale)
            new_h = int(h * scale)
            pil_img = Image.fromarray(image)
            pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            return np.array(pil_img)

        return image

    def _get_japanese_font(self, size: int) -> ImageFont.FreeTypeFont | None:
        """Try to load a Japanese font.

        Args:
            size: Font size.

        Returns:
            Font object or None if not found.
        """
        font_paths = [
            # Windows fonts
            "C:/Windows/Fonts/msgothic.ttc",  # MS Gothic
            "C:/Windows/Fonts/meiryo.ttc",  # Meiryo
            "C:/Windows/Fonts/YuGothM.ttc",  # Yu Gothic Medium
            # Mac fonts
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",  # Hiragino
            "/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            # Linux fonts (Debian/Ubuntu)
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Noto Sans CJK
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",  # IPA Gothic
            "/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf",  # Takao Gothic
        ]

        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except (OSError, IOError):
                continue

        # Fallback to default font (will not display Japanese correctly)
        return ImageFont.load_default()
