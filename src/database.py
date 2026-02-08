"""SQLite database for generation history."""

from __future__ import annotations

import json
import sqlite3
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS generation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL UNIQUE,
    session_id TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    original_path TEXT NOT NULL,
    output_path TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    num_differences INTEGER NOT NULL,
    processing_time REAL NOT NULL,
    metadata TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_job_id ON generation_history(job_id);
CREATE INDEX IF NOT EXISTS idx_expires_at ON generation_history(expires_at);
"""


def init_db(db_path: str) -> None:
    """Create the database and tables if they don't exist.

    Raises OSError if the database directory cannot be created.
    """
    db_file = Path(db_path)

    try:
        # Create parent directory if needed
        db_file.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Database directory ensured: {db_file.parent}")
    except OSError as e:
        logger.error(f"Failed to create database directory {db_file.parent}: {e}")
        raise OSError(
            f"Cannot create database directory {db_file.parent}. "
            f"Please ensure FLASK_ENV=production is set for deployment."
        ) from e

    try:
        # Create database and schema
        with sqlite3.connect(db_path) as conn:
            conn.executescript(_SCHEMA)
        logger.info(f"Database initialized: {db_path}")
    except sqlite3.Error as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def save_generation(
    db_path: str,
    job_id: str,
    session_id: str,
    original_filename: str,
    original_path: str,
    output_path: str,
    difficulty: str,
    num_differences: int,
    processing_time: float,
    metadata: dict,
    expiry_hours: int = 24,
) -> int:
    """Save a generation record. Returns the row id."""
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=expiry_hours)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            """INSERT INTO generation_history
               (job_id, session_id, original_filename, original_path,
                output_path, difficulty, num_differences, processing_time,
                metadata, created_at, expires_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                job_id,
                session_id,
                original_filename,
                original_path,
                output_path,
                difficulty,
                num_differences,
                processing_time,
                json.dumps(metadata, ensure_ascii=False),
                now.isoformat(),
                expires.isoformat(),
            ),
        )
        return cursor.lastrowid


def get_generation(db_path: str, job_id: str) -> dict | None:
    """Retrieve a generation record by job_id."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM generation_history WHERE job_id = ?", (job_id,)
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["metadata"] = json.loads(d["metadata"])
        return d


def cleanup_expired(db_path: str) -> int:
    """Delete expired records. Returns count of deleted rows."""
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "DELETE FROM generation_history WHERE expires_at < ?", (now,)
        )
        return cursor.rowcount
