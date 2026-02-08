#!/usr/bin/env python3
"""Download FastSAM model for deployment.

This script downloads the FastSAM-x.pt model from the official source
and saves it to the configured model directory.
"""

import os
import sys
from pathlib import Path
from urllib.request import urlretrieve

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config


def download_progress(block_num, block_size, total_size):
    """Display download progress."""
    downloaded = block_num * block_size
    if total_size > 0:
        percent = min(100, downloaded * 100 / total_size)
        bar_length = 50
        filled_length = int(bar_length * downloaded / total_size)
        bar = '=' * filled_length + '-' * (bar_length - filled_length)
        print(f'\rDownloading: [{bar}] {percent:.1f}% ({downloaded / 1e6:.1f}MB / {total_size / 1e6:.1f}MB)', end='', flush=True)
    else:
        print(f'\rDownloading: {downloaded / 1e6:.1f}MB', end='', flush=True)


def main():
    """Download FastSAM model if not already present."""
    # Get production config
    env = os.environ.get("FLASK_ENV", "production")
    cfg = config.get(env, config["production"])

    model_folder = cfg.MODEL_FOLDER
    model_name = cfg.FASTSAM_MODEL
    model_path = Path(model_folder) / model_name

    # Create model directory if needed
    model_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Model directory: {model_path.parent}")

    # Check if model already exists
    if model_path.exists():
        size_mb = model_path.stat().st_size / 1e6
        print(f"✓ Model already exists: {model_path} ({size_mb:.1f}MB)")
        return 0

    # Download model
    # FastSAM-x.pt from official repository
    model_url = "https://github.com/CASIA-IVA-Lab/FastSAM/releases/download/v0.1.0/FastSAM-x.pt"

    print(f"Downloading FastSAM model from: {model_url}")
    print(f"Destination: {model_path}")
    print("This may take several minutes (~1.3GB)...\n")

    try:
        urlretrieve(model_url, model_path, reporthook=download_progress)
        print("\n✓ Download complete!")

        # Verify file size
        size_mb = model_path.stat().st_size / 1e6
        print(f"✓ Model saved: {model_path} ({size_mb:.1f}MB)")

        if size_mb < 100:
            print("⚠ Warning: Model file seems too small. Download may have failed.")
            return 1

        return 0

    except Exception as e:
        print(f"\n✗ Error downloading model: {e}")
        if model_path.exists():
            model_path.unlink()  # Remove partial download
        return 1


if __name__ == "__main__":
    sys.exit(main())
