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
    INPAINT_METHOD = "auto"  # auto | ns | telea

    # Segment filtering - more conservative for better quality
    SEGMENT_MIN_AREA_RATIO = 0.003   # min 0.3% of image area (increased from 0.2%)
    SEGMENT_MAX_AREA_RATIO = 0.12    # max 12% of image area (decreased from 15%)

    # Quality thresholds
    MIN_EDGE_SMOOTHNESS = 0.6
    MIN_MASK_COMPLETENESS = 0.85
    MIN_MODIFICATION_SSIM = 0.7

    # Difficulty presets - adjusted for higher quality standards
    DIFFICULTY_CONFIG = {
        "easy": {
            "num_changes": 3,
            "max_saliency": 0.65,  # Slightly more conservative
        },
        "medium": {
            "num_changes": 5,
            "max_saliency": 0.45,  # More conservative
        },
        "hard": {
            "num_changes": 7,  # Reduced from 8 for better quality
            "max_saliency": 0.25,  # More conservative
        },
    }

    # Security settings
    SECURITY_HEADERS = {
        "force_https": False,  # Set to True in production
        "strict_transport_security": True,
        "strict_transport_security_max_age": 31536000,
        "content_security_policy": {
            "default-src": "'self'",
            "script-src": "'self' 'unsafe-inline'",
            "style-src": "'self' 'unsafe-inline'",
            "img-src": "'self' data: blob:",
        },
        "x_content_type_options": True,
        "x_frame_options": "SAMEORIGIN",
        "x_xss_protection": True,
    }

    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_UPLOAD = "10 per minute"
    RATELIMIT_GENERATE = "5 per minute"
