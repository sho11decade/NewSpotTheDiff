"""Data model definitions."""

from src.models.segment import Segment
from src.models.difference import Difference, GenerationResult
from src.models.job import JobStatus

__all__ = ["Segment", "Difference", "GenerationResult", "JobStatus"]
