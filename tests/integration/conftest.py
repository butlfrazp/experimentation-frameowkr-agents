"""Test configuration and documentation for Foundry integration tests.

This module provides pytest configuration, test utilities, and documentation
for running integration tests against Foundry environments.
"""

import os
from pathlib import Path

import pytest


def pytest_configure(config):
    """Configure pytest for integration tests."""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "foundry: mark test as requiring Foundry environment")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle integration test markers."""

    # Auto-mark integration tests
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Mark Foundry-specific tests
        if "foundry" in str(item.fspath).lower():
            item.add_marker(pytest.mark.foundry)


@pytest.fixture(scope="session")
def foundry_environment_check():
    """Check if Foundry environment is properly configured."""

    required_vars = ["FOUNDRY_BASE_URL", "FOUNDRY_TOKEN"]
    optional_vars = ["FOUNDRY_DATASET_RID", "FOUNDRY_NAMESPACE"]

    env_status = {"configured": True, "missing_required": [], "available_optional": []}

    # Check required variables
    for var in required_vars:
        if not os.getenv(var):
            env_status["configured"] = False
            env_status["missing_required"].append(var)

    # Check optional variables
    for var in optional_vars:
        if os.getenv(var):
            env_status["available_optional"].append(var)

    return env_status


@pytest.fixture
def skip_if_no_foundry(foundry_environment_check):
    """Skip test if Foundry environment is not configured."""
    if not foundry_environment_check["configured"]:
        missing = ", ".join(foundry_environment_check["missing_required"])
        pytest.skip(f"Foundry environment not configured. Missing: {missing}")


def pytest_report_header(config):
    """Add custom header information to pytest report."""

    foundry_status = "Not Configured"
    if os.getenv("FOUNDRY_BASE_URL") and os.getenv("FOUNDRY_TOKEN"):
        base_url = os.getenv("FOUNDRY_BASE_URL")
        namespace = os.getenv("FOUNDRY_NAMESPACE", "default")
        foundry_status = f"Configured (URL: {base_url}, Namespace: {namespace})"

    return [
        f"Foundry Integration: {foundry_status}",
        f"Test Environment: {os.getenv('TEST_ENV', 'local')}",
        f"Integration Tests Directory: {Path(__file__).parent}",
    ]


class FoundryTestHelpers:
    """Helper utilities for Foundry integration tests."""

    @staticmethod
    def get_test_config_template():
        """Get a template configuration for Foundry tests."""
        return {
            "dataset": {
                "name": "integration_test_dataset",
                "version": "1.0",
                "config": {"expected_output_field": "expected_output"},
            },
            "executable": {
                "type": "module",
                "path": "test_module.py",
                "processor": "run",
                "config": {},
            },
            "evaluation": [
                {"id": "quality_eval", "name": "conversation_quality", "data_mapping": {}}
            ],
            "local_mode": False,
            "output_path": "test_results",
        }

    @staticmethod
    def get_sample_test_data(size=5):
        """Get sample test data for integration tests."""
        return [
            {
                "input": f"Test question {i}: What is the capital of France?",
                "expected_output": f"Test answer {i}: Paris is the capital of France.",
                "category": "geography",
                "test_id": f"test_{i}",
            }
            for i in range(size)
        ]

    @staticmethod
    def create_test_module_content(module_name="test_module"):
        """Create content for a test processing module."""
        return f'''
"""Test module for {module_name} integration testing."""

def run(input_text: str, context: dict = None) -> str:
    """Process input text and return response."""
    
    # Simple processing logic for testing
    input_lower = input_text.lower()
    
    if "capital" in input_lower and "france" in input_lower:
        return "Paris is the capital of France."
    elif "hello" in input_lower:
        return "Hello! How can I help you today?"
    elif "math" in input_lower or "calculate" in input_lower:
        return "I can help with mathematical calculations."
    else:
        return f"Thank you for your question: {{input_text}}"

if __name__ == "__main__":
    # Test the module locally
    test_inputs = [
        "What is the capital of France?",
        "Hello there!",
        "Help me with math"
    ]
    
    for test_input in test_inputs:
        result = run(test_input)
        print(f"Input: {{test_input}}")
        print(f"Output: {{result}}")
        print("-" * 40)
'''

    @staticmethod
    def validate_foundry_results_structure(results_data):
        """Validate that results follow expected Foundry structure."""

        required_fields = ["experiment_id", "execution_info", "dataset_info", "metrics"]

        for field in required_fields:
            if field not in results_data:
                raise AssertionError(f"Missing required field in results: {field}")

        # Validate execution info
        execution_info = results_data["execution_info"]
        if execution_info.get("platform") != "foundry":
            raise AssertionError("Results should indicate Foundry platform")

        # Validate metrics structure
        metrics = results_data["metrics"]
        if not isinstance(metrics, dict):
            raise AssertionError("Metrics should be a dictionary")

        return True


@pytest.fixture
def foundry_helpers():
    """Provide Foundry test helper utilities."""
    return FoundryTestHelpers()


# Custom pytest marks for different test categories
pytestmark = [
    pytest.mark.integration,
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.filterwarnings("ignore::PendingDeprecationWarning"),
]
