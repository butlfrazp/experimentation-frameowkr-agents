# Sample Math Example

This example demonstrates basic mathematical computation evaluation.

## Files

- `config.yaml` - Experiment configuration for math evaluation
- `simple_math_module.py` - Math processing module
- `README.md` - This file

## Dataset

Uses the dataset at `examples/datasets/sample/0.1/test_data.jsonl` which contains basic math questions.

## Usage

```bash
# Run from the example directory
cd examples/sample
exp-cli run config.yaml --dataset-root ../datasets

# Or run from project root
exp-cli run examples/sample/config.yaml --dataset-root examples/datasets
```

## What This Example Does

1. Loads math questions from the dataset
2. Processes each question through a simple math parser
3. Evaluates the results against expected answers
4. Outputs detailed results and metrics

This demonstrates how to create domain-specific processors and evaluations.