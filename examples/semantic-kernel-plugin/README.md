# Semantic Kernel Plugin Example

This example demonstrates how to create and use Semantic Kernel plugins with the experimentation platform, featuring a math plugin that performs arithmetic operations.

## Files

- `config.yaml` - Experiment configuration for SK plugin testing
- `semantic_kernel_math_module.py` - Semantic Kernel math plugin implementation
- `data/datasets/sk-math/1.0/data.jsonl` - Test dataset with math operations
- `requirements.txt` - Dependencies for Semantic Kernel
- `README.md` - This file

## Semantic Kernel Math Plugin

### Plugin Functions

The `MathPlugin` class provides three kernel functions:

1. **`add_numbers`** - Adds two numbers together
2. **`multiply_numbers`** - Multiplies two numbers  
3. **`square_number`** - Calculates the square of a number

### Function Signatures

```python
@kernel_function(description="Add two numbers together", name="add_numbers")
def add_numbers(
    self, 
    first_number: Annotated[float, "The first number to add"] = 0,
    second_number: Annotated[float, "The second number to add"] = 0
) -> Annotated[str, "The sum of the two numbers"]:
```

### Integration with Experimentation Platform

The module provides a `run(**kwargs)` function that:
1. Extracts math operation requests from the dataset
2. Creates a Semantic Kernel instance with the math plugin
3. Invokes the appropriate plugin function
4. Returns formatted results

## Dataset Format

Each row contains:
- `request`: Natural language description of the operation
- `operation_data`: JSON string with operation details
- `expected_output`: Expected result string

Example:
```json
{
  "request": "Add 15 and 25",
  "operation_data": "{\"operation\": \"add\", \"first_number\": 15, \"second_number\": 25}",
  "expected_output": "The sum of 15.0 and 25.0 is 40.0"
}
```

## Usage

### Prerequisites

Install Semantic Kernel:
```bash
pip install semantic-kernel
```

### Run the Plugin Demo

```bash
# Test the plugin directly
cd examples/semantic-kernel-plugin
python semantic_kernel_math_module.py
```

### Run the Experiment

```bash
# Run the full experiment
cd examples/semantic-kernel-plugin
exp-cli run config.yaml --dataset-root data/datasets

# With dry run validation
exp-cli run config.yaml --dataset-root data/datasets --dry-run
```

## Expected Output

The experiment will process 5 math operations:
1. **Addition**: 15 + 25 = 40
2. **Multiplication**: 7 × 8 = 56  
3. **Square**: 9² = 81
4. **Addition**: 100 + 200 = 300
5. **Multiplication**: 12 × 5 = 60

Each operation is processed through:
1. **Semantic Kernel Setup** - Creates kernel with math plugin
2. **Plugin Invocation** - Calls appropriate kernel function
3. **Result Formatting** - Returns structured response
4. **Evaluation** - Accuracy and response length analysis

## Features Demonstrated

- **Semantic Kernel Plugin Creation** - Full plugin with multiple functions
- **Function Annotations** - Proper type hints and descriptions for SK
- **Async Processing** - Handles async Semantic Kernel operations  
- **Error Handling** - Robust error handling for plugin failures
- **JSON Data Processing** - Parses complex operation parameters
- **Integration Testing** - Works seamlessly with experimentation platform

This example shows how to build production-ready Semantic Kernel plugins that integrate with comprehensive experimentation and evaluation workflows!