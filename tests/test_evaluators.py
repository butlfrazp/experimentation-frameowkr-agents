from __future__ import annotations

import json
from pathlib import Path

import pytest

from exp_platform_cli.evaluators import load_evaluators
from exp_platform_cli.models import (
    DataModelRow,
    DatasetConfig,
    DatasetConfigDetails,
    EvaluatorConfig,
    ExperimentConfig,
    ModuleExecutableConfig,
)
from exp_platform_cli.services.local_evaluation import LocalEvaluationService


def _make_rows() -> list[DataModelRow]:
    row_ok = DataModelRow(
        id="row-ok",
        data_input={"value": 1},
        expected_output={"value": 1},
        data_output={"value": 1},
    )
    row_bad = DataModelRow(
        id="row-bad",
        data_input={"value": 2},
        expected_output={"value": 4},
        data_output={"value": 3},
    )
    return [row_ok, row_bad]


def test_equivalent_evaluator_outputs_accuracy() -> None:
    config = EvaluatorConfig(id="equivalent", name="equivalent", data_mapping={})
    evaluator = load_evaluators([config])[0]

    rows = _make_rows()
    result = evaluator.evaluate(rows)

    assert pytest.approx(result.summary["accuracy"]) == 0.5
    assert result.per_row["row-ok"]["match"] == 1.0
    assert result.per_row["row-bad"]["match"] == 0.0


def test_local_evaluation_writes_metrics(tmp_path: Path, monkeypatch) -> None:
    output_path = tmp_path / "experiments"
    
    experiment_cfg = ExperimentConfig(
        dataset=DatasetConfig(name="sample", version="0.1"),
        executable=ModuleExecutableConfig(path="sample", processor="run"),
        output_path=str(output_path)  # Set the output path in the config
    )
    evaluator_cfg = EvaluatorConfig(id="equiv", name="equivalent")
    rows = _make_rows()

    service = LocalEvaluationService()
    service.evaluate(
        experiment_id="exp123",
        dataset_name="sample",
        dataset_version="0.1",
        data_id=None,
        config=experiment_cfg,
        evaluators=[evaluator_cfg],
        rows=rows,
    )

    # Updated path structure: output_path/dataset_name/dataset_version/experiment_id
    metrics_file = output_path / "sample" / "0.1" / "exp123" / "local_metrics_summary.json"
    assert metrics_file.exists()

    summary = json.loads(metrics_file.read_text())
    assert pytest.approx(summary["equivalent"]["accuracy"]) == 0.5

    assert "equivalent:match" in rows[0].evaluation_results
    assert rows[0].evaluation_results["equivalent:match"].metric_value == 1.0
    assert rows[1].evaluation_results["equivalent:match"].metric_value == 0.0
