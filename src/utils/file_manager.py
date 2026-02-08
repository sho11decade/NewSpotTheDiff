"""Temporary file management and cleanup."""

from __future__ import annotations

import shutil
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


def ensure_directories(*dirs: str | Path) -> None:
    """Create directories if they don't exist.

    Logs errors but doesn't raise exceptions to allow app startup
    even if some directories can't be created.
    """
    for d in dirs:
        try:
            Path(d).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {d}")
        except OSError as e:
            logger.warning(f"Failed to create directory {d}: {e}")
            # Don't raise - allow app to start even if some dirs can't be created


def cleanup_expired_files(
    base_dir: str | Path,
    max_age_hours: int = 24,
) -> int:
    """Remove sub-directories older than max_age_hours.

    Returns the number of directories removed.
    """
    base = Path(base_dir)
    if not base.exists():
        return 0

    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    removed = 0

    for entry in base.iterdir():
        if not entry.is_dir():
            continue
        try:
            mtime = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                shutil.rmtree(entry)
                removed += 1
                logger.info("Cleaned up expired directory: %s", entry.name)
        except OSError as e:
            logger.warning("Failed to clean up %s: %s", entry, e)

    return removed


def get_output_dir(base_dir: str | Path, job_id: str) -> Path:
    """Get (and create) the output directory for a job.

    Raises OSError if directory creation fails.
    """
    out = Path(base_dir) / job_id
    try:
        out.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create output directory {out}: {e}")
        raise
    return out
