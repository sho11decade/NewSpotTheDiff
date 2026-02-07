"""File upload validation utilities."""

from __future__ import annotations

import uuid
from pathlib import Path

from PIL import Image

from src.exceptions import ValidationError


# Magic bytes for allowed image formats
_MAGIC_BYTES = {
    b"\xff\xd8\xff": "jpg",
    b"\x89PNG": "png",
}

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def validate_upload_file(
    file,
    max_size: int = 10 * 1024 * 1024,
    min_dim: int = 512,
    max_dim: int = 4096,
) -> dict:
    """Validate an uploaded image file.

    Returns a dict with file info on success:
        {"extension": str, "width": int, "height": int, "size": int}
    Raises ValidationError on failure.
    """
    if file is None or file.filename == "":
        raise ValidationError("ファイルが選択されていません")

    # Check extension
    ext = _get_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"対応していないファイル形式です。PNG/JPEG のみ対応しています。")

    # Check file size
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > max_size:
        mb = max_size // (1024 * 1024)
        raise ValidationError(f"ファイルサイズが大きすぎます（上限: {mb}MB）")
    if size == 0:
        raise ValidationError("空のファイルです")

    # Check magic bytes
    header = file.read(8)
    file.seek(0)
    if not any(header.startswith(magic) for magic in _MAGIC_BYTES):
        raise ValidationError("ファイルの内容が画像形式と一致しません")

    # Verify as valid image and check dimensions
    try:
        img = Image.open(file)
        img.verify()
        file.seek(0)
        img = Image.open(file)
        width, height = img.size
        file.seek(0)
    except Exception:
        raise ValidationError("画像ファイルを読み込めません")

    if width < min_dim or height < min_dim:
        raise ValidationError(f"画像が小さすぎます（最小: {min_dim}x{min_dim}px）")
    if width > max_dim or height > max_dim:
        raise ValidationError(f"画像が大きすぎます（最大: {max_dim}x{max_dim}px）")

    return {"extension": ext, "width": width, "height": height, "size": size}


def generate_safe_filename(extension: str) -> str:
    """Generate a UUID-based safe filename."""
    return f"{uuid.uuid4().hex}.{extension}"


def validate_difficulty(value: str) -> str:
    """Validate difficulty parameter. Returns normalised value."""
    valid = {"easy", "medium", "hard"}
    normalised = value.strip().lower()
    if normalised not in valid:
        raise ValidationError(f"無効な難易度です。選択可能: {', '.join(sorted(valid))}")
    return normalised


def _get_extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[1].lower()
