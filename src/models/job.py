"""Job status tracking data model."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class JobState(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class JobStatus:
    """Tracks the status of an async generation job."""

    job_id: str
    status: JobState = JobState.QUEUED
    progress: int = 0
    current_step: str = ""
    error: str | None = None
    result_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d
