"""Minimal local evaluation implementation for offline experiments."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, Sequence

from ..evaluators import load_evaluators
from ..models import (
    DataModelRow,
    EvaluationResult,
    EvaluatorConfig,
    ExperimentConfig,
)
from ..constants import PROJECT_ROOT
from ..utils import ensure_directories
from .evaluation_base import EvaluationService


class LocalEvaluationService(EvaluationService):
    """Persist execution results locally for later inspection."""

    def evaluate(
        self,
        *,
        experiment_id: str,
        dataset_name: str,
        dataset_version: str,
        data_id: str | None,
        config: ExperimentConfig,
        evaluators: Sequence[EvaluatorConfig],
        rows: Iterable[DataModelRow] | None = None,
    ) -> None:
        ensure_directories()
        
        # Use configured output path if available, otherwise fallback to environment/default
        if config.output_path:
            artifact_root = Path(config.output_path).expanduser().resolve()
        else:
            artifact_root_env = os.getenv("EXP_CLI_ARTIFACT_ROOT")
            if artifact_root_env:
                artifact_root = Path(artifact_root_env).expanduser().resolve()
            else:
                artifact_root = PROJECT_ROOT / "artifacts"
        
        # Structure: output_path/dataset_name/dataset_version/experiment_id
        output_dir = artifact_root / dataset_name / dataset_version / experiment_id
        output_dir.mkdir(parents=True, exist_ok=True)

        if rows is None:
            rows = []
        rows_list = list(rows)

        evaluator_instances = load_evaluators(evaluators)
        metrics_summary: dict[str, dict[str, float]] = {}

        for evaluator in evaluator_instances:
            result = evaluator.evaluate(rows_list)
            metrics_summary[result.name] = dict(result.summary)
            for row in rows_list:
                metrics = result.per_row.get(row.id)
                if not metrics:
                    continue
                for metric_name, metric_value in metrics.items():
                    key = f"{result.name}:{metric_name}"
                    row.evaluation_results[key] = EvaluationResult(
                        metric_name=key,
                        metric_value=float(metric_value),
                        metadata={"evaluator": result.name},
                    )

        results_path = output_dir / "rows.jsonl"
        with results_path.open("w", encoding="utf-8") as handle:
            for row in rows_list:
                handle.write(row.model_dump_json() + "\n")

        metadata_path = output_dir / "experiment_config.json"
        metadata_path.write_text(
            config.model_dump_json(indent=2),
            encoding="utf-8",
        )

        evaluators_path = output_dir / "evaluators.json"
        evaluators_path.write_text(
            json.dumps([ev.model_dump() for ev in evaluators], indent=2),
            encoding="utf-8",
        )

        metrics_path = output_dir / "local_metrics_summary.json"
        metrics_path.write_text(
            json.dumps(metrics_summary, indent=2),
            encoding="utf-8",
        )
