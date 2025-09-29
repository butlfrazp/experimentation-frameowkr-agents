"""Integration tests for Foundry platform.

These tests require Foundry environment variables to be set:
- FOUNDRY_BASE_URL
- FOUNDRY_TOKEN
- FOUNDRY_DATASET_RID (optional, for existing dataset tests)
- FOUNDRY_NAMESPACE (optional, defaults to test namespace)
"""

import os
import json
import yaml
import pytest
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import platform components
try:
    from exp_platform_cli.cli import (
        load_and_validate_config,
        run_experiment_with_resilience
    )
    from exp_platform_cli.models import ExperimentConfig
    from exp_platform_cli.services import ConfigLoader, DatasetService
    DIRECT_IMPORT = True
except ImportError:
    DIRECT_IMPORT = False


class FoundryTestConfig:
    """Configuration for Foundry integration tests."""
    
    def __init__(self):
        self.base_url = os.getenv('FOUNDRY_BASE_URL')
        self.token = os.getenv('FOUNDRY_TOKEN')
        self.dataset_rid = os.getenv('FOUNDRY_DATASET_RID')
        self.namespace = os.getenv('FOUNDRY_NAMESPACE', 'test-exp-platform')
        
        # Validation
        if not self.base_url:
            pytest.skip("FOUNDRY_BASE_URL not set - skipping Foundry integration tests")
        if not self.token:
            pytest.skip("FOUNDRY_TOKEN not set - skipping Foundry integration tests")
    
    @property
    def is_configured(self) -> bool:
        """Check if Foundry is properly configured."""
        return bool(self.base_url and self.token)
    
    def get_foundry_config(self) -> Dict[str, Any]:
        """Get Foundry configuration for experiments."""
        return {
            'foundry_base_url': self.base_url,
            'foundry_token': self.token,
            'foundry_namespace': self.namespace
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
            "difficulty": "easy"
        },
        {
            "input": "Explain machine learning in simple terms",
            "expected_output": "Machine learning is teaching computers to learn patterns from data",
            "category": "technology",
            "difficulty": "medium"
        },
        {
            "input": "What is 15 * 7?",
            "expected_output": "105",
            "category": "math",
            "difficulty": "easy"
        },
        {
            "input": "Describe photosynthesis",
            "expected_output": "Plants convert sunlight into energy using carbon dioxide and water",
            "category": "science",
            "difficulty": "medium"
        },
        {
            "input": "Hello, how are you?",
            "expected_output": "Hello! I'm doing well, thank you for asking.",
            "category": "conversation",
            "difficulty": "easy"
        }
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
            "config": {
                "expected_output_field": "expected_output"
            }
        },
        "executable": {
            "type": "module",
            "path": str(test_module),
            "processor": "run",
            "config": {}
        },
        "evaluation": [
            {
                "id": "quality_eval",
                "name": "conversation_quality",
                "data_mapping": {}
            },
            {
                "id": "relevance_eval",
                "name": "response_relevance",
                "data_mapping": {}
            }
        ],
        "local_mode": False,  # Use Foundry
        "output_path": str(tmp_path / "results"),
        **foundry_config.get_foundry_config()
    }
    
    return config, str(test_module), dataset_name
