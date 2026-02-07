"""Image upload API endpoint."""

from flask import Blueprint, request, jsonify, current_app
from pathlib import Path

from src.utils.validation import validate_upload_file, generate_safe_filename
from src.exceptions import ValidationError

bp = Blueprint("upload", __name__, url_prefix="/api")


@bp.route("/upload", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "ファイルが提供されていません"}), 400

    file = request.files["file"]

    try:
        info = validate_upload_file(
            file,
            max_size=current_app.config["MAX_CONTENT_LENGTH"],
            min_dim=current_app.config["MIN_IMAGE_DIMENSION"],
            max_dim=current_app.config["MAX_IMAGE_DIMENSION"],
        )
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    filename = generate_safe_filename(info["extension"])
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    filepath = upload_dir / filename

    file.seek(0)
    file.save(str(filepath))

    file_id = filename.rsplit(".", 1)[0]

    return jsonify({
        "success": True,
        "file_id": file_id,
        "filename": file.filename,
        "size": info["size"],
        "dimensions": [info["width"], info["height"]],
    })
