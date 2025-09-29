# Quick Start Example

This is the simplest possible example to get started with the Experimentation Platform CLI.

## Files

- `config.yaml` - Basic experiment configuration
- `data/hello-world.jsonl` - Simple test dataset with 3 conversations
- `README.md` - This file

## Usage

From the root of the project:

```bash
# Run the quick start example
cd examples/quick-start
exp-cli run config.yaml

# Or run from anywhere
exp-cli run examples/quick-start/config.yaml
```

## What This Example Does

1. Loads a simple dataset with 3 conversation pairs
2. Processes each input through an echo processor (simulated agent)
3. Evaluates the responses using basic length checks
4. Outputs results in JSON format

This example demonstrates the core workflow without complex configurations or large datasets.

## Next Steps

After running this example, try:
- The full tutorials in `tutorials/01-quickstart/`
- More complex examples in `examples/experiments/`
- The Jupyter notebook interface in `notebooks/`