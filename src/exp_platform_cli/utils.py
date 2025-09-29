"""General utilities shared across the experimentation CLI."""

from __future__ import annotations

from pathlib import Path

from .constants import DATASET_ROOT, EXPERIMENT_ROOT, refresh_paths


def ensure_directories() -> None:
    """Ensure that the dataset and experiment directories exist."""
    refresh_paths()
    for path in (DATASET_ROOT, EXPERIMENT_ROOT):
        Path(path).mkdir(parents=True, exist_ok=True)
