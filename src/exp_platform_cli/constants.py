"""Shared filesystem locations for datasets and experiment artifacts."""

from __future__ import annotations

import os
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent


def _resolve_artifact_root() -> Path:
    env_value = os.getenv("EXP_CLI_ARTIFACT_ROOT")
    if env_value:
        return Path(env_value).expanduser().resolve()
    return PROJECT_ROOT / "artifacts"


def refresh_paths() -> None:
    """Recompute filesystem roots from the current environment."""

    global ARTIFACT_ROOT, DATASET_ROOT, EXPERIMENT_ROOT
    ARTIFACT_ROOT = _resolve_artifact_root()
    DATASET_ROOT = ARTIFACT_ROOT / "datasets"
    EXPERIMENT_ROOT = ARTIFACT_ROOT / "experiments"


# Initialize module-level paths on import.
refresh_paths()

__all__ = [
    "PACKAGE_ROOT",
    "PROJECT_ROOT",
    "ARTIFACT_ROOT",
    "DATASET_ROOT",
    "EXPERIMENT_ROOT",
    "refresh_paths",
]
