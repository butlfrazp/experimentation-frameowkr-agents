# Examples

This directory contains example datasets, experiments, and configurations to demonstrate how to use the Experimentation Platform CLI.

## Structure

- `datasets/` - Sample datasets for experimentation
- `experiments/` - Previous experiment results (for reference)
- `notebooks/` - Jupyter notebook examples (symlinked from main notebooks directory)
- `quick-start/` - Simple getting started example with echo processor
- `sample/` - Math computation example
- `custom-evaluators/` - Custom evaluator development and demonstration
- `semantic_kernel/` - Semantic Kernel integration examples

## Quick Start

To run the sample experiments:

```bash
# Install the platform
pip install -e .

# Run the simplest example (echo processor)
exp-cli run examples/quick-start/config.yaml --dataset-root examples/quick-start/data/datasets

# Run the math computation example
exp-cli run examples/sample/config.yaml --dataset-root examples/datasets

# Demonstrate custom evaluators (execution + standalone demo)
cd examples/custom-evaluators && python demo_evaluators.py

# Run from within example directories (shorter commands)
cd examples/quick-start && exp-cli run config.yaml --dataset-root data/datasets
cd examples/sample && exp-cli run config.yaml --dataset-root ../datasets
cd examples/custom-evaluators && python demo_evaluators.py
```

## Dataset Examples

### Quick Start Dataset
Located in `quick-start/data/datasets/hello-world/1.0/`, contains simple conversation examples for testing.

### Sample Dataset
Located in `datasets/sample/0.1/`, contains basic math questions for computational evaluation.

## Working Examples

### Quick Start Example
Located in `quick-start/`, demonstrates the simplest possible usage with an echo processor.

### Sample Math Example
Located in `sample/`, shows how to evaluate mathematical computation capabilities.

### Custom Evaluators Example
Located in `custom-evaluators/`, shows how to define, register, and use custom evaluators with comprehensive metrics.

### Historical Results
The `experiments/` directory contains results from previous test runs for reference.

## Integration with Tutorials

The `tutorials/` directory at the root level contains step-by-step guided tutorials, while this `examples/` directory provides reference implementations and datasets that can be used independently.