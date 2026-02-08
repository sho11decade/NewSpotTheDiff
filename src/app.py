"""Flask application factory."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from flask import Flask

from src.config import Config
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


def create_app(config_class=Config) -> Flask:
    app = Flask(
        __name__,
        static_folder=str(Path(__file__).parent / "static"),
        template_folder=str(Path(__file__).parent / "templates"),
    )
    app.config.from_object(config_class)

    _setup_logging(app)
    _ensure_dirs(app)
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
        max_workers=app.config["MAX_WORKERS"],
    )

    app.extensions["job_manager"] = job_manager
