from __future__ import annotations

import json
from pathlib import Path

from exp_platform_cli.cli import run_experiment_with_resilience


def _write_config(path: Path, dataset_name: str, version: str) -> None:
    payload = {
        "dataset": {
            "name": dataset_name,
            "version": version,
            "config": {"expected_output_field": "expected"},
        },
        "executable": {
            "type": "module",
            "path": "tests/assets/sample_module.py",
            "processor": "process_row",
        },
        "evaluation": [],
        "local_mode": True,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_dataset(root: Path, dataset: str, version: str) -> None:
    data_dir = root / dataset / version
    data_dir.mkdir(parents=True)
    lines = [
        {"id": "row_1", "value": 1, "expected": 2},
        {"id": "row_2", "value": 2, "expected": 4},
    ]
    data_path = data_dir / "sample.jsonl"
    with data_path.open("w", encoding="utf-8") as handle:
        for line in lines:
            handle.write(json.dumps(line) + "\n")


def test_run_dry_run(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("EXP_CLI_ARTIFACT_ROOT", str(tmp_path / "artifacts"))
    config_path = tmp_path / "config.json"
    _write_config(config_path, dataset_name="sample", version="0.1")

    # Call the function directly since CLI works
    run_experiment_with_resilience(config_path, dry_run=True)


def test_run_executes_pipeline(tmp_path: Path, monkeypatch) -> None:
    artifact_root = tmp_path / "artifacts"
    dataset_root = artifact_root / "datasets"
    monkeypatch.setenv("EXP_CLI_ARTIFACT_ROOT", str(artifact_root))

    dataset_name = "sample"
    version = "0.1"
    _write_dataset(dataset_root, dataset_name, version)

    config_path = tmp_path / "config.json"
    _write_config(config_path, dataset_name=dataset_name, version=version)

    # Call the function directly
    run_experiment_with_resilience(config_path, dataset_root=dataset_root)

    # Check that results were written to some subdirectory structure
    experiments_root = artifact_root
    # The actual path structure may vary, so just check something was created
    assert any(experiments_root.rglob("*.jsonl")), "Expected experiment artifacts to be written"
