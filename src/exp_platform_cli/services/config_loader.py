"""Utilities for loading experiment configuration files."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from ..models import ExperimentConfig

log = logging.getLogger(__name__)


class ConfigLoader:
    """Load ``ExperimentConfig`` instances from YAML files."""

    @staticmethod
    def load_config(path: str | Path) -> ExperimentConfig:
        path = Path(path)
        log.info("Loading experiment configuration from %s", path)
        with path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)
        log.debug("Parsed experiment configuration: %s", payload)
        config = ExperimentConfig(**payload)
        log.info(
            "Configured dataset %s:%s",
            config.dataset.name,
            config.dataset.version,
        )
        return config
