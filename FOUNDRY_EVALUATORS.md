# Foundry-Style Evaluator Integration & Cloud Evaluation

The exp-platform-cli now supports:
- **Platform-native evaluators** and **foundry-style evaluators** with `flow.flex.yaml` configuration files
- **Local and cloud evaluation** modes for flexible deployment
- **Configurable output paths** for experiment result storage

## Evaluator Types

### Platform Evaluators
Built-in evaluators that inherit from `BaseEvaluator` and are registered using the `@register_evaluator` decorator.

**Example:**
```python
@register_evaluator("platform_equivalent")
class PlatformEquivalentEvaluator(BaseEvaluator):
    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        # Platform-specific evaluation logic
        return EvaluatorOutput(name="platform_equivalent", ...)
```

### Foundry-Style Evaluators
Evaluators that follow the foundry evaluation format with:
- `flow.flex.yaml` configuration file
- Callable evaluator classes that accept keyword arguments
- Return dictionaries with metrics

**Directory Structure:**
```
evaluators/
├── equivalent/
│   ├── flow.flex.yaml
│   ├── equivalent.py
│   └── requirements.txt
```

**flow.flex.yaml:**
```yaml
inputs:
  metrics:
    type: string
entry: equivalent:EquivalentEvaluator
environment:
  python_requirements_txt: requirements.txt
```

**Evaluator Class:**
```python
class EquivalentEvaluator:
    def __call__(self, *, response: Any, ground_truth: Any, **kwargs) -> Dict[str, Any]:
        # Foundry-style evaluation logic - called once per row
        # This is true row-by-row processing as foundry intended
        return {
            "score": 0.85,
            "exact": True, 
            "notes": "Evaluation details for this specific row..."
        }
```

**Row-by-Row Processing:**
- ✅ **True foundry behavior**: Each evaluator call processes exactly one row
- ✅ **Individual row context**: Full access to row inputs, outputs, and metadata
- ✅ **Per-row error handling**: Evaluation failures isolated to individual rows
- ✅ **Flexible data mapping**: Row-specific field mapping for complex datasets

## Configuration

### Experiment YAML Configuration

```yaml
dataset:
  name: sample
  version: "0.1"
  config:
    expected_output_field: expected
executable:
  type: module
  path: /path/to/processor.py
  processor: process_row
evaluation:
  - id: equivalent
    name: equivalent
    data_mapping:  # Triggers foundry-style evaluator preference
      response: data_output
      ground_truth: expected_output
local_mode: true
output_path: /custom/results/path  # Configurable output directory
```

## Evaluator Selection Priority

1. **Foundry-style evaluators** are preferred when `data_mapping` is specified in the configuration
2. **Platform evaluators** are used as fallback or when no data mapping is provided
3. The enhanced registry automatically detects and loads both types

## Output Path Configuration

Results are stored in the directory structure:
```
{output_path}/{dataset_name}/{dataset_version}/{experiment_id}/
├── data.jsonl                    # Execution results
├── config.json                   # Experiment configuration  
├── rows.jsonl                    # Evaluation results
├── local_metrics_summary.json    # Aggregated metrics
├── evaluators.json              # Evaluator configurations
└── experiment_config.json       # Full experiment config
```

The `output_path` field in the YAML configuration overrides the default `EXP_CLI_ARTIFACT_ROOT` environment variable.

## Available Evaluators

Run the following to see all available evaluators:
```python
from exp_platform_cli.evaluators import enhanced_registry
print(list(enhanced_registry.available()))
```

## Testing Foundry Integration

Use the provided test configuration:
```bash
python -c "from exp_platform_cli.cli import run_experiment; run_experiment('test_foundry_evaluator.yaml')"
```

## Local vs Cloud Evaluation

### Local Evaluation
Set `local_mode: true` in your experiment configuration:
```yaml
local_mode: true
```
- Uses `LocalEvaluationService`
- Runs evaluators locally using enhanced registry
- Supports both platform and foundry-style evaluators
- Results stored locally in configured output path

### Cloud Evaluation  
Set `local_mode: false` and configure Azure environment variables:
```yaml
local_mode: false
```

**Required Environment Variables:**
```bash
export SUBSCRIPTION_NAME="your-subscription"
export RESOURCE_GROUP_NAME="your-resource-group"  
export WORKSPACE_NAME="your-workspace"
export FOUNDRY_PROJECT_ENDPOINT="https://your-project.cognitiveservices.azure.com"
export AZURE_FOUNDRY_CONNECTION_STRING="your-connection-string"
```

- Uses `CloudEvaluationService` with Azure AI Projects
- Uploads datasets to cloud for evaluation
- Runs evaluations using Azure AI evaluation services
- Downloads and stores results locally
- **Graceful fallback**: Automatically falls back to local evaluation if cloud credentials are missing

## Testing Both Modes

### Local Evaluation Test:
```bash
python -c "from exp_platform_cli.cli import run_experiment; run_experiment('test_foundry_evaluator.yaml')"
```

### Cloud Evaluation Test:
```bash
python -c "from exp_platform_cli.cli import run_experiment; run_experiment('test_cloud_evaluator.yaml')"
```

This will demonstrate:
- Foundry-style evaluator usage (produces `score`, `exact` metrics)
- Custom output path configuration  
- Data field mapping between platform and foundry formats
- Cloud evaluation with graceful fallback to local mode