"""Download the FastSAM model weights.

Usage:
    python scripts/download_model.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import Config


def main() -> None:
    model_dir = Path(Config.MODEL_FOLDER)
    model_dir.mkdir(parents=True, exist_ok=True)

    model_name = Config.FASTSAM_MODEL
    model_path = model_dir / model_name

    if model_path.exists():
        print(f"Model already exists: {model_path}")
        return

    print(f"Downloading {model_name} ...")

    try:
        from ultralytics import FastSAM
    except ImportError:
        print("Error: ultralytics is not installed.")
        print("Run: pip install ultralytics")
        sys.exit(1)

    # FastSAM auto-downloads from Ultralytics hub when model file is not found
    model = FastSAM(model_name)

    # Move the downloaded file to our model directory if it's elsewhere
    default_path = Path(model_name)
    if default_path.exists() and not model_path.exists():
        default_path.rename(model_path)
        print(f"Moved model to: {model_path}")
    elif model_path.exists():
        # Clean up the default location copy if both exist
        if default_path.exists():
            default_path.unlink()
        print(f"Model saved to: {model_path}")
    else:
        print(f"Model loaded. Ensure it's placed at: {model_path}")

    print("Done.")


if __name__ == "__main__":
    main()
