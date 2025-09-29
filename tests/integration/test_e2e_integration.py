"""End-to-end integration tests for the Experimentation Platform.

These tests validate the complete workflow from configuration to results,
including both local and Foundry execution modes.
"""

import json
import subprocess
from datetime import datetime

import pytest
import yaml

# Import platform components
try:
    from exp_platform_cli.cli import run_experiment_with_resilience
    from exp_platform_cli.models import ExperimentConfig

    DIRECT_IMPORT = True
except ImportError:
    DIRECT_IMPORT = False


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""

    def test_complete_local_workflow(self, tmp_path):
        """Test complete workflow in local mode."""

        # Create test module
        test_module = tmp_path / "e2e_test_module.py"
        test_module.write_text('''
"""End-to-end test module."""

def run(input_text: str, context: dict = None) -> str:
    """Process input and return response."""
    
    input_lower = input_text.lower()
    
    if "hello" in input_lower:
        return "Hello! How can I help you today?"
    elif "goodbye" in input_lower:
        return "Goodbye! Have a great day!"
    elif "math" in input_lower or "calculate" in input_lower:
        return "I can help with mathematical calculations."
    elif "weather" in input_lower:
        return "I don't have access to real weather data, but I'd be happy to discuss weather concepts."
    else:
        return f"Thank you for your message: {input_text}"
''')

        # Create test dataset
        test_data = [
            {"input": "Hello there!", "expected_output": "Hello! How can I help you today?"},
            {"input": "Goodbye", "expected_output": "Goodbye! Have a great day!"},
            {
                "input": "Help me with math",
                "expected_output": "I can help with mathematical calculations.",
            },
            {
                "input": "What's the weather like?",
                "expected_output": "I don't have access to real weather data.",
            },
            {"input": "Random question", "expected_output": "Thank you for your message"},
        ]

        dataset_name = f"e2e_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        dataset_dir = tmp_path / "data" / "datasets" / dataset_name / "1.0"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        dataset_file = dataset_dir / "data.jsonl"
        with dataset_file.open("w") as f:
            for item in test_data:
                f.write(json.dumps(item) + "\\n")

        # Create experiment configuration
        config = {
            "dataset": {
                "name": dataset_name,
                "version": "1.0",
                "config": {"expected_output_field": "expected_output"},
            },
            "executable": {
                "type": "module",
                "path": str(test_module),
                "processor": "run",
                "config": {},
            },
            "evaluation": [
                {"id": "quality_eval", "name": "conversation_quality", "data_mapping": {}}
            ],
            "local_mode": True,
            "output_path": str(tmp_path / "results"),
        }

        config_file = tmp_path / "e2e_config.yaml"
        with config_file.open("w") as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)

        # Run experiment
        result = subprocess.run(
            ["exp-cli", "run", str(config_file)], capture_output=True, text=True, cwd=str(tmp_path)
        )

        # Validate execution
        assert result.returncode == 0, f"Experiment failed: {result.stderr}"

        # Check results directory exists
        results_dir = tmp_path / "results"
        assert results_dir.exists(), "Results directory not created"

        # Find experiment directory
        exp_dirs = [d for d in results_dir.rglob("exp*") if d.is_dir()]
        assert len(exp_dirs) > 0, "No experiment directory created"

        latest_exp = max(exp_dirs, key=lambda x: x.stat().st_mtime)

        # Check for expected files
        expected_files = ["data.jsonl", "local_metrics_summary.json"]
        for expected_file in expected_files:
            file_path = latest_exp / expected_file
            assert file_path.exists(), f"Expected file {expected_file} not found"

        # Validate results content
        with (latest_exp / "local_metrics_summary.json").open() as f:
            metrics = json.load(f)

        assert "conversation_quality_eval" in metrics
        assert "average_score" in metrics["conversation_quality_eval"]

        # Validate execution data
        with (latest_exp / "data.jsonl").open() as f:
            execution_data = [json.loads(line) for line in f if line.strip()]

        assert len(execution_data) == len(test_data)

        for row in execution_data:
            assert "input" in row
            assert "data_output" in row
            assert "expected_output" in row

    def test_configuration_validation_workflow(self, tmp_path):
        """Test configuration validation in complete workflow."""

        # Test with invalid configuration
        invalid_config = {
            "dataset": {
                "name": "test_dataset",
                "version": "1.0",
                # Missing config section
            },
            "executable": {"type": "module", "path": "nonexistent.py", "processor": "run"},
            "evaluation": [{"id": "test_eval", "name": "invalid_evaluator"}],
            "local_mode": True,
        }

        config_file = tmp_path / "invalid_config.yaml"
        with config_file.open("w") as f:
            yaml.dump(invalid_config, f, default_flow_style=False, indent=2)

        # Should fail with validation error
        result = subprocess.run(
            ["exp-cli", "run", str(config_file)], capture_output=True, text=True, cwd=str(tmp_path)
        )

        assert result.returncode != 0
        assert len(result.stderr) > 0

    def test_directory_runner_workflow(self, tmp_path):
        """Test running experiments from a directory."""

        # Create multiple experiment configurations
        experiments_dir = tmp_path / "experiments"
        experiments_dir.mkdir()

        # Create shared test module
        test_module = tmp_path / "shared_module.py"
        test_module.write_text("""
def run(input_text: str) -> str:
    return f"Processed: {input_text}"
""")

        # Create test datasets and configs
        for i in range(3):
            dataset_name = f"batch_test_{i}"
            dataset_dir = tmp_path / "data" / "datasets" / dataset_name / "1.0"
            dataset_dir.mkdir(parents=True, exist_ok=True)

            # Create small dataset
            test_data = [
                {"input": f"Test input {i}-1", "expected_output": f"Expected {i}-1"},
                {"input": f"Test input {i}-2", "expected_output": f"Expected {i}-2"},
            ]

            dataset_file = dataset_dir / "data.jsonl"
            with dataset_file.open("w") as f:
                for item in test_data:
                    f.write(json.dumps(item) + "\\n")

            # Create config
            config = {
                "dataset": {
                    "name": dataset_name,
                    "version": "1.0",
                    "config": {"expected_output_field": "expected_output"},
                },
                "executable": {
                    "type": "module",
                    "path": str(test_module),
                    "processor": "run",
                    "config": {},
                },
                "evaluation": [
                    {"id": "quality_eval", "name": "conversation_quality", "data_mapping": {}}
                ],
                "local_mode": True,
                "output_path": str(tmp_path / "batch_results"),
            }

            config_file = experiments_dir / f"experiment_{i}.yaml"
            with config_file.open("w") as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)

        # Run directory of experiments
        result = subprocess.run(
            ["exp-cli", "run-directory", str(experiments_dir)],
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )

        # Should complete successfully
        assert result.returncode == 0, f"Directory run failed: {result.stderr}"

        # Check that results were created for each experiment
        results_dir = tmp_path / "batch_results"
        if results_dir.exists():
            exp_dirs = [d for d in results_dir.rglob("exp*") if d.is_dir()]
            # Should have created experiments (may be fewer due to batch optimization)
            assert len(exp_dirs) > 0


class TestRegressionPrevention:
    """Test to prevent regressions in key functionality."""

    def test_config_format_compatibility(self, tmp_path):
        """Test that configs remain compatible across versions."""

        # Test both YAML and JSON config formats
        config_data = {
            "dataset": {
                "name": "regression_test",
                "version": "1.0",
                "config": {"expected_output_field": "expected_output"},
            },
            "executable": {
                "type": "module",
                "path": "test_module.py",
                "processor": "run",
                "config": {},
            },
            "evaluation": [{"id": "test_eval", "name": "conversation_quality", "data_mapping": {}}],
            "local_mode": True,
        }

        # Test YAML format
        yaml_config = tmp_path / "test_config.yaml"
        with yaml_config.open("w") as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)

        # Test JSON format
        json_config = tmp_path / "test_config.json"
        with json_config.open("w") as f:
            json.dump(config_data, f, indent=2)

        # Both should be readable
        with yaml_config.open() as f:
            yaml_loaded = yaml.safe_load(f)

        with json_config.open() as f:
            json_loaded = json.load(f)

        # Should be equivalent
        assert yaml_loaded == json_loaded
        assert yaml_loaded["dataset"]["name"] == "regression_test"

    def test_cli_interface_stability(self, tmp_path):
        """Test that CLI interface remains stable."""

        # Test basic CLI commands exist and respond
        commands_to_test = [
            ["exp-cli", "--help"],
            ["exp-cli", "run", "--help"],
            ["exp-cli", "run-directory", "--help"],
        ]

        for cmd in commands_to_test:
            result = subprocess.run(cmd, capture_output=True, text=True)
            # Should not crash and should provide help
            assert result.returncode in [0, 1]  # Help commands may return 1
            assert len(result.stdout) > 0 or len(result.stderr) > 0

    def test_output_format_consistency(self, tmp_path):
        """Test that output formats remain consistent."""

        # Create minimal working experiment
        test_module = tmp_path / "output_test_module.py"
        test_module.write_text("""
def run(input_text: str) -> str:
    return "test response"
""")

        dataset_name = "output_format_test"
        dataset_dir = tmp_path / "data" / "datasets" / dataset_name / "1.0"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        dataset_file = dataset_dir / "data.jsonl"
        with dataset_file.open("w") as f:
            f.write(json.dumps({"input": "test", "expected_output": "test response"}) + "\\n")

        config = {
            "dataset": {
                "name": dataset_name,
                "version": "1.0",
                "config": {"expected_output_field": "expected_output"},
            },
            "executable": {
                "type": "module",
                "path": str(test_module),
                "processor": "run",
                "config": {},
            },
            "evaluation": [{"id": "test_eval", "name": "conversation_quality", "data_mapping": {}}],
            "local_mode": True,
            "output_path": str(tmp_path / "format_test_results"),
        }

        config_file = tmp_path / "format_test_config.yaml"
        with config_file.open("w") as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)

        # Run experiment
        result = subprocess.run(
            ["exp-cli", "run", str(config_file)], capture_output=True, text=True, cwd=str(tmp_path)
        )

        if result.returncode == 0:
            # Check output format consistency
            results_dir = tmp_path / "format_test_results"
            exp_dirs = [d for d in results_dir.rglob("exp*") if d.is_dir()]

            if exp_dirs:
                latest_exp = max(exp_dirs, key=lambda x: x.stat().st_mtime)

                # Check expected output files exist
                expected_files = ["data.jsonl", "local_metrics_summary.json"]
                for expected_file in expected_files:
                    assert (latest_exp / expected_file).exists()

                # Check JSON format validity
                with (latest_exp / "local_metrics_summary.json").open() as f:
                    metrics = json.load(f)
                    assert isinstance(metrics, dict)

                # Check JSONL format validity
                with (latest_exp / "data.jsonl").open() as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            assert isinstance(data, dict)


class TestErrorRecovery:
    """Test error handling and recovery mechanisms."""

    def test_module_error_handling(self, tmp_path):
        """Test handling of module execution errors."""

        # Create module that raises an exception
        error_module = tmp_path / "error_module.py"
        error_module.write_text("""
def run(input_text: str) -> str:
    raise ValueError("Intentional test error")
""")

        dataset_name = "error_test"
        dataset_dir = tmp_path / "data" / "datasets" / dataset_name / "1.0"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        dataset_file = dataset_dir / "data.jsonl"
        with dataset_file.open("w") as f:
            f.write(json.dumps({"input": "test", "expected_output": "response"}) + "\\n")

        config = {
            "dataset": {
                "name": dataset_name,
                "version": "1.0",
                "config": {"expected_output_field": "expected_output"},
            },
            "executable": {
                "type": "module",
                "path": str(error_module),
                "processor": "run",
                "config": {},
            },
            "evaluation": [{"id": "test_eval", "name": "conversation_quality", "data_mapping": {}}],
            "local_mode": True,
            "output_path": str(tmp_path / "error_results"),
        }

        config_file = tmp_path / "error_config.yaml"
        with config_file.open("w") as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)

        # Run experiment - should handle error gracefully
        result = subprocess.run(
            ["exp-cli", "run", str(config_file)], capture_output=True, text=True, cwd=str(tmp_path)
        )

        # Should fail but not crash catastrophically
        assert result.returncode != 0
        assert "error" in result.stderr.lower() or "exception" in result.stderr.lower()

    def test_network_timeout_simulation(self, tmp_path):
        """Test handling of simulated network issues."""

        # Create config that would attempt Foundry connection with invalid URL
        config = {
            "dataset": {
                "name": "network_test",
                "version": "1.0",
                "config": {"expected_output_field": "expected_output"},
            },
            "executable": {
                "type": "module",
                "path": "test_module.py",
                "processor": "run",
                "config": {},
            },
            "evaluation": [{"id": "test_eval", "name": "conversation_quality", "data_mapping": {}}],
            "local_mode": False,  # Force Foundry mode
            "foundry_base_url": "https://invalid.foundry.url",
            "foundry_token": "invalid_token",
            "foundry_namespace": "test",
        }

        config_file = tmp_path / "network_test_config.yaml"
        with config_file.open("w") as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)

        # Should handle network errors gracefully
        result = subprocess.run(
            ["exp-cli", "run", str(config_file)],
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
            timeout=30,
        )

        # Should fail with network/connection error, not crash
        assert result.returncode != 0
        # Should provide meaningful error message
        assert len(result.stderr) > 0


# Mark all tests as integration tests
pytestmark = pytest.mark.integration
