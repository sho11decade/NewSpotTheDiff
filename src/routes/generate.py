"""Generation API endpoints: submit, status, result."""

import json
import uuid
from pathlib import Path

from flask import Blueprint, request, jsonify, current_app

from src.models.job import JobState
from src.utils.validation import validate_difficulty
from src.exceptions import ValidationError

bp = Blueprint("generate", __name__, url_prefix="/api")


def _get_limiter():
    """Get limiter from app extensions if available."""
    return current_app.extensions.get("limiter")


@bp.route("/generate", methods=["POST"])
def generate():
    # Apply rate limiting if available
    limiter = _get_limiter()
    if limiter:
        limiter.limit(current_app.config.get("RATELIMIT_GENERATE", "5 per minute"))(
            lambda: None
        )()

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "JSON body required"}), 400

    file_id = data.get("file_id")
    if not file_id:
        return jsonify({"error": "file_id is required"}), 400

    try:
        difficulty = validate_difficulty(data.get("difficulty", "medium"))
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    # Find the uploaded file
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    matches = list(upload_dir.glob(f"{file_id}.*"))
    if not matches:
        return jsonify({"error": "アップロードされた画像が見つかりません"}), 404

    image_path = str(matches[0])
    job_id = f"job_{uuid.uuid4().hex[:12]}"

    job_manager = current_app.extensions["job_manager"]
    job_manager.submit(job_id, image_path, difficulty)

    return jsonify({
        "success": True,
        "job_id": job_id,
        "status": "queued",
    })


@bp.route("/status/<job_id>", methods=["GET"])
def get_status(job_id: str):
    job_manager = current_app.extensions["job_manager"]
    status = job_manager.get_status(job_id)
    if status is None:
        return jsonify({"error": "ジョブが見つかりません"}), 404
    return jsonify(status.to_dict())


@bp.route("/result/<job_id>", methods=["GET"])
def get_result(job_id: str):
    job_manager = current_app.extensions["job_manager"]
    status = job_manager.get_status(job_id)
    if status is None:
        return jsonify({"error": "ジョブが見つかりません"}), 404

    if status.status != JobState.COMPLETED:
        return jsonify({"error": "ジョブが完了していません", "status": status.status.value}), 400

    # Load metadata
    out_dir = Path(status.result_path)
    metadata_path = out_dir / "metadata.json"
    metadata = {}
    if metadata_path.exists():
        with open(metadata_path, encoding="utf-8") as f:
            metadata = json.load(f)

    return jsonify({
        "success": True,
        "job_id": job_id,
        "original_image_url": f"/outputs/{job_id}/original.png",
        "modified_image_url": f"/outputs/{job_id}/modified.png",
        "original_with_answers_url": f"/outputs/{job_id}/original_with_answers.png",
        "modified_with_answers_url": f"/outputs/{job_id}/modified_with_answers.png",
        "a4_layout_url": f"/outputs/{job_id}/a4_layout.png",
        "a4_layout_with_answers_url": f"/outputs/{job_id}/a4_layout_with_answers.png",
        "metadata": metadata,
    })
