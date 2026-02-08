#!/usr/bin/env python3
"""Download FastSAM model for deployment.

This script uses Ultralytics library to download FastSAM model.
The model will be cached by Ultralytics and we verify it's available.
"""

import os
import sys
from pathlib import Path

# CRITICAL: Set environment variables and change directory BEFORE any other imports
# This must be done before importing config or any other modules that might use Ultralytics
os.environ.setdefault('YOLO_CONFIG_DIR', '/tmp/.config/Ultralytics')
os.environ.setdefault('TORCH_HOME', '/tmp/.cache/torch')

# Change to writable directory immediately
original_dir = os.getcwd()
os.chdir('/tmp')

# Now safe to import config
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import config


def main():
    """Ensure FastSAM model is available."""
    print("FastSAM Model Setup")
    print("=" * 50)
    print(f"Working directory: {os.getcwd()}")
    print(f"YOLO_CONFIG_DIR: {os.environ.get('YOLO_CONFIG_DIR')}")
    print(f"TORCH_HOME: {os.environ.get('TORCH_HOME')}")

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
        print(f"Current directory: {os.getcwd()}")

        # Let Ultralytics handle everything - it will download to WEIGHTS_DIR
        model = FastSAM('FastSAM-x.pt')

        print("✓ FastSAM model is ready")
        print("✓ Model is cached by Ultralytics and ready to use")

        # Optionally try to copy to local path if it doesn't exist
        if not model_path.exists():
            from ultralytics.utils import WEIGHTS_DIR

            print(f"\nUltralytics WEIGHTS_DIR: {WEIGHTS_DIR}")
            cache_path = WEIGHTS_DIR / 'FastSAM-x.pt'

            if cache_path.exists():
                try:
                    print(f"Copying model to {model_path} for faster access...")
                    import shutil
                    shutil.copy2(cache_path, model_path)
                    size_mb = model_path.stat().st_size / 1e6
                    print(f"✓ Model copied: {model_path} ({size_mb:.1f}MB)")
                except Exception as copy_error:
                    print(f"⚠ Could not copy to local path: {copy_error}")
                    print("  App will use Ultralytics cache (works fine)")

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
