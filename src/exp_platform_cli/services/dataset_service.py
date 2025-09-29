"""Loading and persisting datasets for experimentation."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable

import pandas as pd
import yaml

from ..constants import PROJECT_ROOT
from ..models import DataModelRow, ExperimentConfig


class DatasetService:
    """Handle dataset retrieval and artifact persistence."""

    def __init__(self, dataset_root: Path | None = None) -> None:
        if dataset_root:
            self._dataset_root = Path(dataset_root)
        else:
            # Get dataset root from environment or use new unified location
            dataset_root_env = os.getenv("EXP_CLI_DATASET_ROOT")
            if dataset_root_env:
                self._dataset_root = Path(dataset_root_env).expanduser().resolve()
            else:
                # Default to unified data structure
                self._dataset_root = PROJECT_ROOT / "data" / "datasets"

    def load_dataframe(self, name: str, version: str) -> pd.DataFrame:
        """Load a dataset stored as JSONL under the dataset root."""
        dataset_dir = self._dataset_root / name / version
        if not dataset_dir.exists():
            raise FileNotFoundError(
                f"Dataset '{name}' version '{version}' not found at {dataset_dir}"
            )
        records = []
        for file in sorted(dataset_dir.glob("*.jsonl")):
            with file.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        records.append(json.loads(line))
        return pd.DataFrame(records)

    def write_local_results(
        self,
        *,
        name: str,
        version: str,
        experiment_id: str,
        rows: Iterable[DataModelRow],
        config: ExperimentConfig,
    ) -> Path:
        """Persist scored rows locally and return the directory path."""
        # Use configured output path if available, otherwise fallback to environment/default
        if config.output_path:
            artifact_root = Path(config.output_path).expanduser().resolve()
        else:
            artifact_root_env = os.getenv("EXP_CLI_ARTIFACT_ROOT")
            if artifact_root_env:
                artifact_root = Path(artifact_root_env).expanduser().resolve()
            else:
                # Default to unified data structure
                artifact_root = PROJECT_ROOT / "data" / "experiments"
        
        # Structure: output_path/dataset_name/dataset_version/experiment_id
        output_dir = artifact_root / name / version / experiment_id
        output_dir.mkdir(parents=True, exist_ok=True)

        rows_path = output_dir / "data.jsonl"
        with rows_path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(row.model_dump_json() + "\n")

        # Save config in both JSON and YAML formats
        config_json_path = output_dir / "config.json"
        config_json_path.write_text(
            config.model_dump_json(indent=2),
            encoding="utf-8",
        )
        
        config_yaml_path = output_dir / "config.yaml"
        config_yaml_path.write_text(
            yaml.dump(config.model_dump(), default_flow_style=False, indent=2),
            encoding="utf-8",
        )
        return output_dir
