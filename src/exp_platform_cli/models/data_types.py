"""Enumerations describing dataset categories used by the CLI."""

from __future__ import annotations

from enum import Enum


class DataType(str, Enum):
    """Identify the high-level shape or origin of a dataset."""

    JSON = "json"
    CSV = "csv"
    UNKNOWN = "unknown"
