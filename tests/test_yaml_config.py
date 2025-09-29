"""Test YAML configuration roundtrip functionality."""

from __future__ import annotations

from pathlib import Path

import yaml

from exp_platform_cli.services import ConfigLoader
from exp_platform_cli.models import ExperimentConfig


def test_yaml_config_roundtrip(tmp_path: Path):
    """Test that YAML configs can be saved and loaded back correctly."""
    
    # Sample YAML config content
    yaml_content = """
dataset:
  name: test_dataset
  version: "1.0"
  config:
    expected_output_field: expected_output

executable:
  type: module
  path: test_module
  processor: run
  config: {}

evaluation:
  - id: test_eval
    name: conversation_quality
    data_mapping: {}

local_mode: true
output_path: data/experiments
"""
    
    # Write YAML config file
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(yaml_content.strip())
    
    # Load using ConfigLoader
    loader = ConfigLoader()
    loaded_config = loader.load_config(config_file)
    
    # Verify it's a valid ExperimentConfig
    assert isinstance(loaded_config, ExperimentConfig)
    assert loaded_config.dataset.name == "test_dataset"
    assert loaded_config.dataset.version == "1.0"
    assert loaded_config.executable.type == "module"
    assert loaded_config.executable.path == "test_module"
    assert loaded_config.executable.processor == "run"
    assert len(loaded_config.evaluators) == 1
    assert loaded_config.evaluators[0].name == "conversation_quality"
    assert loaded_config.local_mode is True
    assert loaded_config.output_path == "data/experiments"


def test_yaml_config_equivalence_with_json(tmp_path: Path):
    """Test that YAML and JSON configs produce equivalent results."""
    
    config_data = {
        "dataset": {
            "name": "equivalence_test",
            "version": "1.0",
            "config": {"expected_output_field": "expected"}
        },
        "executable": {
            "type": "module",
            "path": "test_module",
            "processor": "run",
            "config": {}
        },
        "evaluation": [
            {
                "id": "test_eval",
                "name": "response_relevance",
                "data_mapping": {}
            }
        ],
        "local_mode": False,
        "output_path": "experiments"
    }
    
    # Create JSON config
    json_file = tmp_path / "config.json"
    import json
    json_file.write_text(json.dumps(config_data, indent=2))
    
    # Create YAML config
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml.dump(config_data, default_flow_style=False, indent=2))
    
    # Load both configs
    loader = ConfigLoader()
    json_config = loader.load_config(json_file)
    yaml_config = loader.load_config(yaml_file)
    
    # Verify they're equivalent
    assert json_config.model_dump() == yaml_config.model_dump()
    assert json_config.dataset.name == yaml_config.dataset.name
    assert json_config.executable.path == yaml_config.executable.path
    assert len(json_config.evaluators) == len(yaml_config.evaluators)
    assert json_config.local_mode == yaml_config.local_mode
    assert json_config.output_path == yaml_config.output_path