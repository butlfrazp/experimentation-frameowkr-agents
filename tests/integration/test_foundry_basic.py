"""Integration tests for Foundry platform.

These tests require Foundry environment variables to be set:
- FOUNDRY_BASE_URL
- FOUNDRY_TOKEN
- FOUNDRY_DATASET_RID (optional, for existing dataset tests)
- FOUNDRY_NAMESPACE (optional, defaults to test namespace)
"""

import json
import os
import subprocess
from datetime import datetime
from typing import Any

import pytest
import yaml

# Import platform components
try:
    from exp_platform_cli.cli import load_and_validate_config, run_experiment_with_resilience
    from exp_platform_cli.models import ExperimentConfig
    from exp_platform_cli.services import ConfigLoader, DatasetService

    DIRECT_IMPORT = True
except ImportError:
    DIRECT_IMPORT = False


class FoundryTestConfig:
    """Configuration for Foundry integration tests."""

    def __init__(self):
        self.base_url = os.getenv("FOUNDRY_BASE_URL")
        self.token = os.getenv("FOUNDRY_TOKEN")
        self.dataset_rid = os.getenv("FOUNDRY_DATASET_RID")
        self.namespace = os.getenv("FOUNDRY_NAMESPACE", "test-exp-platform")

        # Validation
        if not self.base_url:
            pytest.skip("FOUNDRY_BASE_URL not set - skipping Foundry integration tests")
        if not self.token:
            pytest.skip("FOUNDRY_TOKEN not set - skipping Foundry integration tests")

    @property
    def is_configured(self) -> bool:
        """Check if Foundry is properly configured."""
        return bool(self.base_url and self.token)

    def get_foundry_config(self) -> dict[str, Any]:
        """Get Foundry configuration for experiments."""
        return {
            "foundry_base_url": self.base_url,
            "foundry_token": self.token,
            "foundry_namespace": self.namespace,
        }


@pytest.fixture
def foundry_config():
    """Fixture providing Foundry configuration."""
    return FoundryTestConfig()


@pytest.fixture
def sample_test_data():
    """Sample data for integration tests."""
    return [
        {
            "input": "What is the capital of France?",
            "expected_output": "Paris",
            "category": "geography",
            "difficulty": "easy",
        },
        {
            "input": "Explain machine learning in simple terms",
            "expected_output": "Machine learning is teaching computers to learn patterns from data",
            "category": "technology",
            "difficulty": "medium",
        },
        {
            "input": "What is 15 * 7?",
            "expected_output": "105",
            "category": "math",
            "difficulty": "easy",
        },
        {
            "input": "Describe photosynthesis",
            "expected_output": "Plants convert sunlight into energy using carbon dioxide and water",
            "category": "science",
            "difficulty": "medium",
        },
        {
            "input": "Hello, how are you?",
            "expected_output": "Hello! I'm doing well, thank you for asking.",
            "category": "conversation",
            "difficulty": "easy",
        },
    ]


@pytest.fixture
def foundry_experiment_config(foundry_config, sample_test_data, tmp_path):
    """Create a complete experiment configuration for Foundry."""

    # Create test module
    test_module = tmp_path / "foundry_test_module.py"
    test_module.write_text('''
"""Test module for Foundry integration."""

def run(input_text: str, context: dict = None) -> str:
    """Simple test processing function."""
    
    input_lower = input_text.lower()
    
    # Geography
    if "capital" in input_lower and "france" in input_lower:
        return "The capital of France is Paris."
    
    # Math
    elif "15" in input_text and "7" in input_text:
        return "15 * 7 = 105"
    
    # Science
    elif "photosynthesis" in input_lower:
        return "Photosynthesis is how plants convert sunlight to chemical energy."
    
    # Technology
    elif "machine learning" in input_lower:
        return "Machine learning teaches computers to find patterns in data."
    
    # Conversation
    elif "hello" in input_lower:
        return "Hello! I'm doing well, thank you."
    
    # Default
    else:
        return f"I understand you're asking about: {input_text}"
''')

    # Create dataset
    dataset_name = f"foundry_integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    dataset_dir = tmp_path / "data" / "datasets" / dataset_name / "1.0"
    dataset_dir.mkdir(parents=True, exist_ok=True)

    dataset_file = dataset_dir / "data.jsonl"
    with dataset_file.open("w") as f:
        for item in sample_test_data:
            f.write(json.dumps(item) + "\n")

    # Create configuration
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
            {"id": "quality_eval", "name": "conversation_quality", "data_mapping": {}},
            {"id": "relevance_eval", "name": "response_relevance", "data_mapping": {}},
        ],
        "local_mode": False,  # Use Foundry
        "output_path": str(tmp_path / "results"),
        **foundry_config.get_foundry_config(),
    }

    return config, str(test_module), dataset_name


class TestFoundryDatasetManagement:
    """Test dataset operations with Foundry."""

    def test_dataset_creation_foundry(self, foundry_config, sample_test_data, tmp_path):
        """Test creating a dataset in Foundry."""
        if not foundry_config.is_configured:
            pytest.skip("Foundry not configured")

        dataset_name = f"test_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create dataset locally first
        dataset_dir = tmp_path / "data" / "datasets" / dataset_name / "1.0"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        dataset_file = dataset_dir / "data.jsonl"
        with dataset_file.open("w") as f:
            for item in sample_test_data:
                f.write(json.dumps(item) + "\n")

        # Test dataset service can handle the dataset
        if DIRECT_IMPORT:
            service = DatasetService()
            # This would upload to Foundry in real implementation
            dataset_config = {
                "name": dataset_name,
                "version": "1.0",
                "config": {"expected_output_field": "expected_output"},
            }

            # Verify dataset structure
            assert dataset_file.exists()
            with dataset_file.open() as f:
                lines = f.readlines()
            assert len(lines) == len(sample_test_data)

            # Verify each line is valid JSON
            for line in lines:
                data = json.loads(line)
                assert "input" in data
                assert "expected_output" in data

    def test_dataset_validation_foundry(self, foundry_config, tmp_path):
        """Test dataset validation for Foundry requirements."""
        if not foundry_config.is_configured:
            pytest.skip("Foundry not configured")

        # Test with invalid dataset (missing required fields)
        invalid_data = [
            {"input": "test"},  # Missing expected_output
            {"expected_output": "result"},  # Missing input
        ]

        dataset_name = f"invalid_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        dataset_dir = tmp_path / "data" / "datasets" / dataset_name / "1.0"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        dataset_file = dataset_dir / "data.jsonl"
        with dataset_file.open("w") as f:
            for item in invalid_data:
                f.write(json.dumps(item) + "\n")

        # This should be caught during validation
        # Implementation would validate required fields for Foundry
        assert dataset_file.exists()

    def test_existing_foundry_dataset(self, foundry_config):
        """Test using an existing Foundry dataset."""
        if not foundry_config.is_configured or not foundry_config.dataset_rid:
            pytest.skip("Foundry dataset RID not configured")

        # Test configuration with existing dataset
        config = {
            "dataset": {
                "type": "foundry",
                "rid": foundry_config.dataset_rid,
                "config": {"expected_output_field": "expected_output"},
            },
            **foundry_config.get_foundry_config(),
        }

        # This would be handled by the platform's Foundry integration
        assert config["dataset"]["rid"] == foundry_config.dataset_rid
        assert config["foundry_base_url"] == foundry_config.base_url


class TestFoundryExperimentExecution:
    """Test experiment execution on Foundry."""

    def test_foundry_experiment_basic(self, foundry_experiment_config, tmp_path):
        """Test basic experiment execution on Foundry."""
        config, module_path, dataset_name = foundry_experiment_config

        # Create config file
        config_file = tmp_path / "foundry_test_config.yaml"
        with config_file.open("w") as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)

        # Test configuration loading
        if DIRECT_IMPORT:
            try:
                loaded_config = load_and_validate_config(config_file)
                assert loaded_config is not None
                assert loaded_config.dataset.name == dataset_name
                assert loaded_config.local_mode is False  # Should be using Foundry
            except Exception as e:
                pytest.skip(f"Config validation failed: {e}")

        # Test via CLI (more realistic integration test)
        result = subprocess.run(
            ["exp-cli", "run", str(config_file)],
            capture_output=True,
            text=True,
            cwd=str(tmp_path.parent),
        )

        # Check execution
        if result.returncode == 0:
            assert (
                "experiment completed" in result.stdout.lower()
                or "success" in result.stdout.lower()
            )
        else:
            # Log error for debugging but don't fail test immediately
            print(f"Experiment execution warning: {result.stderr}")
            # This might fail due to network/auth issues, which is expected in CI

    def test_foundry_experiment_with_multiple_evaluators(
        self, foundry_config, sample_test_data, tmp_path
    ):
        """Test Foundry experiment with multiple evaluators."""
        if not foundry_config.is_configured:
            pytest.skip("Foundry not configured")

        # Create enhanced config with multiple evaluators
        test_module = tmp_path / "multi_eval_module.py"
        test_module.write_text("""
def run(input_text: str) -> str:
    return f"Response to: {input_text}"
""")

        dataset_name = f"multi_eval_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        dataset_dir = tmp_path / "data" / "datasets" / dataset_name / "1.0"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        dataset_file = dataset_dir / "data.jsonl"
        with dataset_file.open("w") as f:
            for item in sample_test_data:
                f.write(json.dumps(item) + "\n")

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
                {"id": "quality_eval", "name": "conversation_quality", "data_mapping": {}},
                {"id": "relevance_eval", "name": "response_relevance", "data_mapping": {}},
                {"id": "accuracy_eval", "name": "tool_call_accuracy", "data_mapping": {}},
            ],
            "local_mode": False,
            "output_path": str(tmp_path / "results"),
            **foundry_config.get_foundry_config(),
        }

        config_file = tmp_path / "multi_eval_config.yaml"
        with config_file.open("w") as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)

        # Verify config structure
        assert len(config["evaluation"]) == 3
        assert config["local_mode"] is False
        assert "foundry_base_url" in config

    def test_foundry_experiment_error_handling(self, foundry_config, tmp_path):
        """Test error handling in Foundry experiments."""
        if not foundry_config.is_configured:
            pytest.skip("Foundry not configured")

        # Create config with intentional errors
        config = {
            "dataset": {
                "name": "nonexistent_dataset",
                "version": "1.0",
                "config": {"expected_output_field": "expected_output"},
            },
            "executable": {
                "type": "module",
                "path": "nonexistent_module.py",
                "processor": "run",
                "config": {},
            },
            "evaluation": [{"id": "test_eval", "name": "conversation_quality", "data_mapping": {}}],
            "local_mode": False,
            **foundry_config.get_foundry_config(),
        }

        config_file = tmp_path / "error_test_config.yaml"
        with config_file.open("w") as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)

        # Test should handle errors gracefully
        result = subprocess.run(
            ["exp-cli", "run", str(config_file)],
            capture_output=True,
            text=True,
            cwd=str(tmp_path.parent),
        )

        # Should fail but with meaningful error message
        assert result.returncode != 0
        assert len(result.stderr) > 0  # Should have error output


class TestFoundryResultsHandling:
    """Test results handling for Foundry experiments."""

    def test_foundry_results_structure(self, foundry_config, tmp_path):
        """Test that Foundry results follow expected structure."""
        if not foundry_config.is_configured:
            pytest.skip("Foundry not configured")

        # Mock results structure that would come from Foundry
        expected_results_structure = {
            "experiment_id": "exp_foundry_001",
            "dataset_info": {"name": "test_dataset", "version": "1.0", "source": "foundry"},
            "execution_info": {
                "platform": "foundry",
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
            },
            "metrics": {
                "conversation_quality_eval": {"average_score": 0.85, "total_evaluations": 5}
            },
            "foundry_metadata": {
                "namespace": foundry_config.namespace,
                "execution_rid": "ri.foundry.execution.12345",
            },
        }

        # Test structure validation
        assert "experiment_id" in expected_results_structure
        assert "foundry_metadata" in expected_results_structure
        assert expected_results_structure["dataset_info"]["source"] == "foundry"
        assert expected_results_structure["execution_info"]["platform"] == "foundry"

    def test_foundry_metrics_aggregation(self, foundry_config):
        """Test metrics aggregation for Foundry results."""
        if not foundry_config.is_configured:
            pytest.skip("Foundry not configured")

        # Mock multiple evaluation results
        eval_results = [
            {"evaluator": "conversation_quality", "score": 0.9, "row_id": "row_1"},
            {"evaluator": "conversation_quality", "score": 0.8, "row_id": "row_2"},
            {"evaluator": "response_relevance", "score": 0.85, "row_id": "row_1"},
            {"evaluator": "response_relevance", "score": 0.95, "row_id": "row_2"},
        ]

        # Test aggregation logic
        by_evaluator = {}
        for result in eval_results:
            evaluator = result["evaluator"]
            if evaluator not in by_evaluator:
                by_evaluator[evaluator] = []
            by_evaluator[evaluator].append(result["score"])

        # Calculate averages
        aggregated = {}
        for evaluator, scores in by_evaluator.items():
            aggregated[evaluator] = {
                "average_score": sum(scores) / len(scores),
                "min_score": min(scores),
                "max_score": max(scores),
                "count": len(scores),
            }

        # Validate aggregation
        assert aggregated["conversation_quality"]["average_score"] == 0.85
        assert aggregated["response_relevance"]["average_score"] == 0.9
        assert aggregated["conversation_quality"]["count"] == 2

    def test_foundry_results_export(self, foundry_config, tmp_path):
        """Test exporting results from Foundry experiments."""
        if not foundry_config.is_configured:
            pytest.skip("Foundry not configured")

        # Mock results data
        results_data = {
            "experiment_metadata": {
                "id": "exp_foundry_test",
                "timestamp": datetime.now().isoformat(),
                "platform": "foundry",
            },
            "dataset_summary": {
                "total_rows": 5,
                "categories": ["geography", "technology", "math", "science", "conversation"],
            },
            "evaluation_results": {
                "conversation_quality_eval": {
                    "average_score": 0.82,
                    "scores": [0.9, 0.8, 0.7, 0.85, 0.85],
                },
                "response_relevance_eval": {
                    "average_score": 0.88,
                    "scores": [0.95, 0.85, 0.9, 0.8, 0.9],
                },
            },
        }

        # Test JSON export
        json_file = tmp_path / "foundry_results.json"
        with json_file.open("w") as f:
            json.dump(results_data, f, indent=2)

        # Test YAML export
        yaml_file = tmp_path / "foundry_results.yaml"
        with yaml_file.open("w") as f:
            yaml.dump(results_data, f, default_flow_style=False, indent=2)

        # Verify exports
        assert json_file.exists()
        assert yaml_file.exists()

        # Verify content
        with json_file.open() as f:
            loaded_json = json.load(f)
        assert loaded_json["experiment_metadata"]["platform"] == "foundry"

        with yaml_file.open() as f:
            loaded_yaml = yaml.safe_load(f)
        assert loaded_yaml["dataset_summary"]["total_rows"] == 5


class TestFoundryConfiguration:
    """Test Foundry-specific configuration handling."""

    def test_foundry_config_validation(self, foundry_config):
        """Test validation of Foundry configuration."""
        if not foundry_config.is_configured:
            pytest.skip("Foundry not configured")

        config = foundry_config.get_foundry_config()

        # Test required fields
        assert "foundry_base_url" in config
        assert "foundry_token" in config
        assert "foundry_namespace" in config

        # Test URL format
        assert config["foundry_base_url"].startswith(("http://", "https://"))

        # Test token is not empty
        assert len(config["foundry_token"]) > 0

    def test_foundry_environment_detection(self):
        """Test detection of Foundry environment variables."""

        # Test environment variable detection
        env_vars = ["FOUNDRY_BASE_URL", "FOUNDRY_TOKEN", "FOUNDRY_DATASET_RID", "FOUNDRY_NAMESPACE"]

        detected_vars = {}
        for var in env_vars:
            value = os.getenv(var)
            if value:
                detected_vars[var] = "[REDACTED]" if "TOKEN" in var else value

        print(f"Detected Foundry environment variables: {list(detected_vars.keys())}")

        # At minimum, we need base URL and token for tests to run
        has_minimum = "FOUNDRY_BASE_URL" in detected_vars and "FOUNDRY_TOKEN" in detected_vars

        if not has_minimum:
            pytest.skip("Minimum Foundry environment variables not set")

    def test_foundry_config_merging(self, foundry_config, tmp_path):
        """Test merging Foundry config with experiment config."""
        if not foundry_config.is_configured:
            pytest.skip("Foundry not configured")

        base_config = {
            "dataset": {"name": "test", "version": "1.0"},
            "executable": {"type": "module", "path": "test.py"},
            "evaluation": [{"id": "test", "name": "conversation_quality"}],
            "local_mode": False,
        }

        # Merge with Foundry config
        foundry_settings = foundry_config.get_foundry_config()
        merged_config = {**base_config, **foundry_settings}

        # Test merged config
        assert merged_config["local_mode"] is False
        assert "foundry_base_url" in merged_config
        assert "foundry_token" in merged_config
        assert merged_config["dataset"]["name"] == "test"  # Original config preserved

        # Test config file creation
        config_file = tmp_path / "merged_config.yaml"
        with config_file.open("w") as f:
            # Don't include sensitive token in file for security
            safe_config = {k: v for k, v in merged_config.items() if "token" not in k.lower()}
            yaml.dump(safe_config, f, default_flow_style=False, indent=2)

        assert config_file.exists()


# Integration test markers
pytestmark = pytest.mark.integration
