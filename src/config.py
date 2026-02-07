"""Application configuration."""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

    # File upload
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    UPLOAD_FOLDER = str(INSTANCE_DIR / "uploads")
    OUTPUT_FOLDER = str(INSTANCE_DIR / "outputs")
    MODEL_FOLDER = str(INSTANCE_DIR / "models")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

    # Image constraints
    MIN_IMAGE_DIMENSION = 512
    MAX_IMAGE_DIMENSION = 4096
    PROCESSING_IMAGE_SIZE = 1024

    # Database
    DATABASE_PATH = str(INSTANCE_DIR / "spotdiff.db")

    # Job processing
    MAX_WORKERS = 2
    SESSION_EXPIRY_HOURS = 24

    # FastSAM
    FASTSAM_MODEL = "FastSAM-x.pt"
    FASTSAM_CONF = 0.4
    FASTSAM_IOU = 0.9

    # Inpainting
    INPAINT_RADIUS = 5

    # Segment filtering
    SEGMENT_MIN_AREA_RATIO = 0.002   # min 0.2% of image area
    SEGMENT_MAX_AREA_RATIO = 0.15    # max 15% of image area

    # Difficulty presets
    DIFFICULTY_CONFIG = {
        "easy": {"num_changes": 3, "max_saliency": 0.7},
        "medium": {"num_changes": 5, "max_saliency": 0.5},
        "hard": {"num_changes": 8, "max_saliency": 0.3},
    }
