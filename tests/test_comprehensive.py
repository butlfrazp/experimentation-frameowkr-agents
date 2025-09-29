"""Comprehensive test suite for the experimentation platform CLI."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml
from exp_platform_cli.cli import (
    discover_config_files,
    install_directory_dependencies,
    load_and_validate_config,
    setup_module_path,
    validate_config_file,
    validate_dataset_root,
)
from exp_platform_cli.models import ExperimentConfig
from exp_platform_cli.services import DatasetService


class TestConfigValidation:
    """Test configuration validation functions."""

    def test_validate_config_file_exists(self, tmp_path: Path):
        """Test config file validation when file exists."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("name: test")

        # Should not raise an exception
        validate_config_file(config_file)

    def test_validate_config_file_missing(self, tmp_path: Path):
        """Test config file validation when file is missing."""
        from exp_platform_cli.cli import ConfigurationError

        config_file = tmp_path / "missing.yaml"

        with pytest.raises(ConfigurationError):
            validate_config_file(config_file)

    def test_validate_dataset_root_valid(self, tmp_path: Path):
        """Test dataset root validation with valid directory."""
        result = validate_dataset_root(tmp_path)
        assert result == tmp_path

    def test_validate_dataset_root_none(self):
        """Test dataset root validation with None."""
        result = validate_dataset_root(None)
        assert result is None

    def test_validate_dataset_root_creates_missing(self, tmp_path: Path):
        """Test dataset root validation creates missing directories."""
        missing_path = tmp_path / "nonexistent"

        result = validate_dataset_root(missing_path)
        assert result == missing_path
        assert missing_path.exists()


class TestConfigLoading:
    """Test configuration loading and parsing."""

    def test_load_valid_yaml_config(self, tmp_path: Path):
        """Test loading a valid YAML configuration."""
        config_data = {
            "dataset": {
                "name": "test_dataset",
                "version": "1.0",
                "config": {"expected_output_field": "expected"},
            },
            "executable": {"type": "module", "path": "test_module", "processor": "run"},
            "evaluation": [],
            "local_mode": True,
        }

        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        result = load_and_validate_config(config_file)
        assert isinstance(result, ExperimentConfig)
        assert result.dataset.name == "test_dataset"
        assert result.dataset.version == "1.0"

    def test_load_valid_json_config(self, tmp_path: Path):
        """Test loading a valid JSON configuration."""
        config_data = {
            "dataset": {
                "name": "test_dataset",
                "version": "1.0",
                "config": {"expected_output_field": "expected"},
            },
            "executable": {"type": "module", "path": "test_module", "processor": "run"},
            "evaluation": [],
            "local_mode": True,
        }

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        result = load_and_validate_config(config_file)
        assert isinstance(result, ExperimentConfig)
        assert result.dataset.name == "test_dataset"

    def test_load_invalid_config(self, tmp_path: Path):
        """Test loading an invalid configuration."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content:")

        with pytest.raises(Exception):  # Could be YAML parse error or validation error
            load_and_validate_config(config_file)


class TestDirectoryOperations:
    """Test directory-based operations."""

    def test_discover_config_files_yaml(self, tmp_path: Path):
        """Test discovering YAML config files."""
        # Create test files
        (tmp_path / "config1.yaml").write_text("test")
        (tmp_path / "config2.yml").write_text("test")
        (tmp_path / "other.txt").write_text("test")

        results = discover_config_files(tmp_path, "*.yaml")
        assert len(results) == 1
        assert results[0].name == "config1.yaml"

    def test_discover_config_files_multiple_patterns(self, tmp_path: Path):
        """Test discovering config files with different extensions."""
        # Create test files
        (tmp_path / "config1.yaml").write_text("test")
        (tmp_path / "config2.json").write_text("test")

        yaml_results = discover_config_files(tmp_path, "*.yaml")
        json_results = discover_config_files(tmp_path, "*.json")

        assert len(yaml_results) == 1
        assert len(json_results) == 1

    def test_discover_config_files_empty_directory(self, tmp_path: Path):
        """Test discovering config files in empty directory."""
        results = discover_config_files(tmp_path, "*.yaml")
        assert len(results) == 0

    @patch("subprocess.run")
    def test_install_directory_dependencies_with_requirements(
        self, mock_subprocess, tmp_path: Path
    ):
        """Test installing dependencies when requirements.txt exists."""
        requirements_file = tmp_path / "requirements.txt"
        requirements_file.write_text("numpy==1.21.0\\nrequests>=2.25.0")

        mock_subprocess.return_value = MagicMock(returncode=0)

        install_directory_dependencies(tmp_path)

        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0][0]
        assert "pip" in args
        assert "install" in args

    def test_install_directory_dependencies_no_requirements(self, tmp_path: Path):
        """Test installing dependencies when no requirements.txt exists."""
        # Should not raise an exception
        install_directory_dependencies(tmp_path)

    @patch("sys.path")
    def test_setup_module_path(self, mock_sys_path, tmp_path: Path):
        """Test setting up module path."""
        module_path = str(tmp_path)

        setup_module_path(tmp_path, module_path)

        # Check that path was added to sys.path
        mock_sys_path.insert.assert_called_once_with(0, module_path)


class TestDatasetService:
    """Test dataset service functionality."""

    def test_dataset_service_initialization(self, tmp_path: Path):
        """Test dataset service initialization."""
        service = DatasetService(dataset_root=tmp_path)
        assert service._dataset_root == tmp_path

    def test_dataset_service_default_initialization(self):
        """Test dataset service default initialization."""
        service = DatasetService()
        # Should use default path structure
        assert service._dataset_root is not None

    def test_load_nonexistent_dataset(self, tmp_path: Path):
        """Test loading a dataset that doesn't exist."""
        service = DatasetService(dataset_root=tmp_path)

        with pytest.raises(FileNotFoundError):
            service.load_dataframe("nonexistent", "1.0")

    def test_write_local_results_creates_yaml_config(self, tmp_path: Path):
        """Test that local results include YAML config file."""
        from exp_platform_cli.models import (
            DataModelRow,
            DatasetConfig,
            DatasetConfigDetails,
            ExperimentConfig,
            ModuleExecutableConfig,
        )

        service = DatasetService(dataset_root=tmp_path)

        # Create test configuration
        config = ExperimentConfig(
            dataset=DatasetConfig(
                name="test_dataset", version="1.0", config=DatasetConfigDetails()
            ),
            executable=ModuleExecutableConfig(path="test_module", processor="run"),
            output_path=str(tmp_path / "experiments"),
        )

        # Create test rows
        rows = [
            DataModelRow(
                id="test_row",
                data_input={"input": "test"},
                expected_output={"output": "test"},
                data_output={"output": "result"},
            )
        ]

        # Write results
        result_dir = service.write_local_results(
            name="test_dataset", version="1.0", experiment_id="test_exp", rows=rows, config=config
        )

        # Check that both JSON and YAML config files exist
        assert (result_dir / "config.json").exists()
        assert (result_dir / "config.yaml").exists()

        # Verify YAML content can be loaded
        yaml_content = yaml.safe_load((result_dir / "config.yaml").read_text())
        assert yaml_content["dataset"]["name"] == "test_dataset"


class TestIntegration:
    """Integration tests for the full pipeline."""

    def test_end_to_end_yaml_config_preservation(self, tmp_path: Path):
        """Test that YAML configs are preserved through the pipeline."""
        # This test would require more complex setup but demonstrates
        # the concept of end-to-end testing
        pass

    def test_config_validation_with_real_data(self, tmp_path: Path):
        """Test config validation with realistic data."""
        # Create a realistic config
        config_data = {
            "dataset": {
                "name": "conversation_test",
                "version": "1.0",
                "config": {"expected_output_field": "expected_output"},
            },
            "executable": {
                "type": "module",
                "path": "conversation_module",
                "processor": "run",
                "config": {},
            },
            "evaluation": [
                {"id": "quality_eval", "name": "conversation_quality", "data_mapping": {}}
            ],
            "local_mode": True,
            "output_path": "data/experiments",
        }

        config_file = tmp_path / "realistic_config.yaml"
        config_file.write_text(yaml.dump(config_data, default_flow_style=False))

        # Should load without errors
        result = load_and_validate_config(config_file)
        assert isinstance(result, ExperimentConfig)
        assert result.dataset.name == "conversation_test"
        assert len(result.evaluators) == 1
        assert result.evaluators[0].name == "conversation_quality"


if __name__ == "__main__":
    pytest.main([__file__])
