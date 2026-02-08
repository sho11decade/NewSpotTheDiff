"""Flask application factory."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from flask import Flask

from src.config import config
from src.database import init_db
from src.routes import register_blueprints
from src.services.segmentation import SegmentationService
from src.services.saliency import SaliencyService
from src.services.inpainting import InpaintingService
from src.services.color_changer import ColorChanger
from src.services.object_duplicator import ObjectDuplicator
from src.services.answer_visualizer import AnswerVisualizer
from src.services.a4_layout_composer import A4LayoutComposer
from src.services.difference_generator import DifferenceGenerator
from src.services.job_manager import JobManager
from src.utils.file_manager import ensure_directories


def create_app(config_name=None) -> Flask:
    """Create and configure Flask application.

    Args:
        config_name: Configuration name ('development', 'production', or None for auto-detect)
    """
    # Set Ultralytics environment variables before any imports
    # This prevents "Read-only file system" errors in deployment
    os.environ.setdefault('YOLO_CONFIG_DIR', '/tmp/.config/Ultralytics')
    os.environ.setdefault('TORCH_HOME', '/tmp/.cache/torch')

    if config_name is None:
        # Auto-detect environment
        config_name = os.environ.get("FLASK_ENV", "development")
        if config_name not in config:
            config_name = "development"

    config_class = config[config_name]

    app = Flask(
        __name__,
        static_folder=str(Path(__file__).parent / "static"),
        template_folder=str(Path(__file__).parent / "templates"),
    )
    app.config.from_object(config_class)

    _setup_logging(app)
    _ensure_dirs(app)
    _init_security(app)
    init_db(app.config["DATABASE_PATH"])
    _init_services(app)
    register_blueprints(app)

    return app


def _setup_logging(app: Flask) -> None:
    level = logging.DEBUG if app.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _ensure_dirs(app: Flask) -> None:
    ensure_directories(
        app.config["UPLOAD_FOLDER"],
        app.config["OUTPUT_FOLDER"],
        app.config["MODEL_FOLDER"],
    )


def _init_security(app: Flask) -> None:
    """Initialize security headers and rate limiting."""
    try:
        from flask_talisman import Talisman
    except ImportError:
        logging.warning("Flask-Talisman not installed. Security headers disabled.")
    else:
        sec_config = app.config.get("SECURITY_HEADERS", {})
        Talisman(
            app,
            force_https=sec_config.get("force_https", False),
            strict_transport_security=sec_config.get("strict_transport_security", True),
            strict_transport_security_max_age=sec_config.get(
                "strict_transport_security_max_age", 31536000
            ),
            content_security_policy=sec_config.get("content_security_policy"),
            content_security_policy_nonce_in=["script-src", "style-src"],
            x_content_type_options=sec_config.get("x_content_type_options", True),
            frame_options=sec_config.get("x_frame_options", "SAMEORIGIN"),
            force_file_save=False,
        )
        logging.info("Security headers initialized with Flask-Talisman")

    if app.config.get("RATELIMIT_ENABLED", True):
        try:
            from flask_limiter import Limiter
            from flask_limiter.util import get_remote_address
        except ImportError:
            logging.warning("Flask-Limiter not installed. Rate limiting disabled.")
        else:
            limiter = Limiter(
                get_remote_address,
                app=app,
                default_limits=[app.config.get("RATELIMIT_DEFAULT", "100 per hour")],
                storage_uri=app.config.get("RATELIMIT_STORAGE_URI", "memory://"),
            )
            app.extensions["limiter"] = limiter
            logging.info("Rate limiting initialized with Flask-Limiter")


def _init_services(app: Flask) -> None:
    model_path = os.path.join(
        app.config["MODEL_FOLDER"], app.config["FASTSAM_MODEL"]
    )

    segmentation = SegmentationService(
        model_path=model_path,
        conf=app.config["FASTSAM_CONF"],
        iou=app.config["FASTSAM_IOU"],
        imgsz=app.config["PROCESSING_IMAGE_SIZE"],
    )

    # Pre-load FastSAM model at startup to avoid first-request timeout
    # This takes ~30-60 seconds but prevents WORKER TIMEOUT on first request
    # Only pre-load if model file exists (skips on first deployment)
    from pathlib import Path
    model_file = Path(model_path)
    if model_file.exists():
        logging.info("Pre-loading FastSAM model at startup...")
        segmentation._ensure_model()
        logging.info("FastSAM model pre-loaded successfully")
    else:
        logging.warning(
            "FastSAM model not found at startup. Model will be loaded on first request. "
            "Consider downloading model before deployment: python scripts/download_model.py"
        )

    saliency = SaliencyService()
    inpainting = InpaintingService(radius=app.config["INPAINT_RADIUS"])
    color_changer = ColorChanger()
    duplicator = ObjectDuplicator()
    answer_visualizer = AnswerVisualizer()
    a4_composer = A4LayoutComposer()

    generator = DifferenceGenerator(
        segmentation=segmentation,
        saliency=saliency,
        inpainting=inpainting,
        color_changer=color_changer,
        object_duplicator=duplicator,
        difficulty_config=app.config["DIFFICULTY_CONFIG"],
        segment_min_area_ratio=app.config["SEGMENT_MIN_AREA_RATIO"],
        segment_max_area_ratio=app.config["SEGMENT_MAX_AREA_RATIO"],
    )

    job_manager = JobManager(
        generator=generator,
        answer_visualizer=answer_visualizer,
        a4_composer=a4_composer,
        output_folder=app.config["OUTPUT_FOLDER"],
        database_path=app.config["DATABASE_PATH"],
        max_workers=app.config["MAX_WORKERS"],
    )

    app.extensions["job_manager"] = job_manager
