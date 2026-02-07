"""Initialize the SQLite database.

Usage:
    python scripts/init_db.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import Config
from src.database import init_db


def main() -> None:
    db_path = Config.DATABASE_PATH
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    print(f"Initializing database at: {db_path}")
    init_db(db_path)
    print("Database initialized successfully.")


if __name__ == "__main__":
    main()
