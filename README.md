# 🧪 Experimentation Platform CLI

A robust, production-ready experimentation platform with comprehensive support for:

- **🏠 Local & ☁️ Cloud Evaluation** - Seamless switching between local and Azure AI Projects evaluation
- **🔧 Multiple Evaluator Types** - Platform-native and foundry-style evaluators with `flow.flex.yaml` support  
- **📊 Configurable Output Paths** - Flexible result storage with per-dataset organization
- **🛡️ Comprehensive Resilience** - Retry logic, error handling, and graceful degradation
- **📈 Progress Tracking** - Real-time execution monitoring and detailed logging

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (when published)
pip install exp-platform-cli

# Or install from source
git clone <repository-url>
cd exp-platform-cli
pip install -e .
```

### Basic Usage

```bash
# Get help and see all available commands
exp-cli --help

# Try the simplest example first
exp-cli run examples/quick-start/config.yaml --dataset-root examples/quick-start/data/datasets

# Run a math computation example  
exp-cli run examples/sample/config.yaml --dataset-root examples/datasets

# Validate configuration without execution
exp-cli validate examples/quick-start/config.yaml

# View platform information and available evaluators
exp-cli info

# Run with verbose logging
exp-cli -vv run examples/quick-start/config.yaml --dataset-root examples/quick-start/data/datasets
```

### Development Setup

```bash
# Clone and setup development environment
git clone <repository-url>
cd exp-platform-cli
pip install -e ".[dev]"

# Run tests
pytest

# Format and lint code
ruff format .
ruff check .
```

## 📋 Configuration

### Basic Experiment Configuration

Experiment files use YAML (or JSON) following the `ExperimentConfig` schema:

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
    data_mapping:
      response: data_output
      ground_truth: expected_output
local_mode: true
output_path: /custom/results/path  # Optional: override default output location
```

## 📚 Examples

The `examples/` directory contains working demonstrations:

- **`examples/quick-start/`** - Simplest possible example with echo processor
- **`examples/sample/`** - Math computation evaluation  
- **`examples/notebooks/`** - Jupyter interfaces and advanced patterns
- **`tutorials/`** - Step-by-step guided learning experiences

Each example includes its own README with specific usage instructions.

### Advanced Features

- **📁 Flexible Dataset Discovery**: Datasets discovered under `EXP_CLI_ARTIFACT_ROOT` or `--dataset-root`
- **🔄 Automatic Retries**: Configurable retry attempts with exponential backoff
- **📊 Progress Tracking**: Real-time execution monitoring with success/failure rates
- **🛡️ Error Isolation**: Per-row error handling prevents total experiment failure
- **📈 Comprehensive Logging**: Multiple verbosity levels with structured output

### Cloud Evaluation Setup

For cloud evaluation, set these environment variables:

```bash
export SUBSCRIPTION_NAME="your-subscription"
export RESOURCE_GROUP_NAME="your-resource-group"
export WORKSPACE_NAME="your-workspace"
export FOUNDRY_PROJECT_ENDPOINT="https://your-project.cognitiveservices.azure.com"
export AZURE_FOUNDRY_CONNECTION_STRING="your-connection-string"
```

## 🎯 Key Features

### Resilient Execution
- **Retry Logic**: Configurable retry attempts for both dataset loading and execution
- **Error Handling**: Comprehensive error categorization and graceful degradation  
- **Progress Monitoring**: Real-time progress tracking with success/failure metrics
- **Timeout Management**: Configurable timeouts for long-running operations

### Evaluation Ecosystem
- **Platform Evaluators**: Built-in evaluators with row-by-row processing
- **Foundry Evaluators**: Support for `flow.flex.yaml` foundry-style evaluators
- **Data Mapping**: Flexible field mapping between platform and foundry formats
- **Cloud Integration**: Azure AI Projects evaluation with local fallback

### Production Features
- **Configurable Storage**: Custom output paths with per-dataset organization
- **Environment Management**: Support for multiple environments and configurations
- **Comprehensive Logging**: Structured logging with configurable verbosity
- **CLI Interface**: Modern Click-based CLI with comprehensive help and validation

## 📚 Documentation

- [Foundry Evaluator Integration](FOUNDRY_EVALUATORS.md) - Detailed guide for foundry evaluators
- [Examples](examples/) - Complete working examples
- [API Documentation](src/exp_platform_cli/) - Full API reference

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `pip install -e ".[dev]"`
4. Make your changes with tests
5. Run tests: `pytest`
6. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

### Logging

The CLI ships with a Rich-powered logger that renders colorful banners, levels, and success messages. If you want to integrate the logger in additional modules, import `get_logger()` from `exp_platform_cli` and reuse its `banner`, `info`, `success`, and other helper methods.

### Evaluators

Built-in evaluators live under `src/exp_platform_cli/evaluators/`. They register themselves with the registry so that an experiment config can reference them by name (for example `equivalent`). Add new evaluators by creating a class that extends `BaseEvaluator` and decorating it with `@register_evaluator("your-name")`.

### Examples

The `examples/` directory contains complete working examples:

- **`semantic_kernel_plugin/`** - A Semantic Kernel math plugin that demonstrates:
  - Creating reusable Semantic Kernel plugins with mathematical operations
  - Integration with the experimentation platform for evaluation
  - Standalone CLI demo and comprehensive tests
  - Custom evaluators for structured output comparison
  
See the [plugin README](examples/semantic_kernel_plugin/README.md) for setup and usage instructions.

## Development Tasks

```bash
uv run python -m pytest            # Run the test suite
uv run ruff check src tests        # Lint with Ruff
uv run ruff format src tests       # Format with Ruff formatter
```

## Dev Container

A dev container (`.devcontainer/devcontainer.json`) is provided with Python 3.11 and installs `uv` automatically. It runs `uv sync` on creation so the environment is ready to go.
