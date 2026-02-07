"""Main page routes."""

from flask import Blueprint, render_template, current_app, abort, send_from_directory
from pathlib import Path

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/processing")
def processing():
    return render_template("processing.html")


@bp.route("/result/<job_id>")
def result(job_id: str):
    job_manager = current_app.extensions["job_manager"]
    status = job_manager.get_status(job_id)
    if status is None:
        abort(404)
    return render_template("result.html", job_id=job_id)


@bp.route("/outputs/<job_id>/<filename>")
def serve_output(job_id: str, filename: str):
    """Serve generated images from the output directory."""
    output_dir = Path(current_app.config["OUTPUT_FOLDER"]) / job_id
    if not output_dir.exists():
        abort(404)
    return send_from_directory(str(output_dir), filename)
