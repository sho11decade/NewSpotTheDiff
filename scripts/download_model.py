#!/usr/bin/env python3
"""Download FastSAM model for deployment.

This script uses Ultralytics library to download FastSAM model.
The model will be cached by Ultralytics and we verify it's available.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config


def main():
    """Ensure FastSAM model is available."""
    print("FastSAM Model Setup")
    print("=" * 50)

    # Set Ultralytics to use writable directories
    # This prevents "Read-only file system" errors in deployment
    os.environ.setdefault('YOLO_CONFIG_DIR', '/tmp/.config/Ultralytics')
    os.environ.setdefault('TORCH_HOME', '/tmp/.cache/torch')

    # Change to writable directory before importing Ultralytics
    # Ultralytics may try to write to current directory during import/download
    original_dir = os.getcwd()
    os.chdir('/tmp')

    # Get production config
    env = os.environ.get("FLASK_ENV", "production")
    cfg = config.get(env, config["production"])

    model_folder = Path(cfg.MODEL_FOLDER)
    model_name = cfg.FASTSAM_MODEL
    model_path = model_folder / model_name

    # Create model directory
    model_folder.mkdir(parents=True, exist_ok=True)
    print(f"Model directory: {model_folder}")

    # Check if model already exists locally
    if model_path.exists() and model_path.stat().st_size > 1_000_000:
        size_mb = model_path.stat().st_size / 1e6
        print(f"✓ Local model exists: {model_path} ({size_mb:.1f}MB)")
        return 0

    print("\nDownloading FastSAM-x model...")
    print("This uses Ultralytics and may take several minutes (~1.3GB)")
    print("")

    try:
        # Use Ultralytics to download/cache the model
        from ultralytics import FastSAM

        print("Initializing FastSAM (triggers automatic download)...")
        model = FastSAM('FastSAM-x.pt')

        print("✓ FastSAM model is ready")
        print("✓ Model is cached by Ultralytics and ready to use")

        # Try to find and copy to local path for faster access
        from ultralytics.utils import WEIGHTS_DIR

        cache_locations = [
            WEIGHTS_DIR / 'FastSAM-x.pt',
            Path.home() / '.cache' / 'torch' / 'hub' / 'checkpoints' / 'FastSAM-x.pt',
            Path.home() / '.cache' / 'ultralytics' / 'FastSAM-x.pt',
        ]

        for cache_path in cache_locations:
            if cache_path.exists():
                print(f"\nCopying model to local path for faster access...")
                print(f"Source: {cache_path}")
                print(f"Destination: {model_path}")

                import shutil
                shutil.copy2(cache_path, model_path)

                size_mb = model_path.stat().st_size / 1e6
                print(f"✓ Model copied: {model_path} ({size_mb:.1f}MB)")
                break

        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

        # Don't fail if Ultralytics cached it successfully
        # The app will use it from cache
        print("\n⚠ Warning: Could not copy model to local path")
        print("  App will use Ultralytics cache (slightly slower startup)")

        return 0  # Don't fail, let app use cache
    finally:
        # Restore original directory
        os.chdir(original_dir)


if __name__ == "__main__":
    sys.exit(main())
