# Custom Evaluators Example

This example demonstrates how to create and register custom evaluators in the experimentation platform.

## Files

- `config.yaml` - Experiment configuration using custom evaluators
- `custom_evaluators.py` - Custom evaluator implementations
- `simple_echo_module.py` - Module that imports custom evaluators
- `data/` - Sample dataset
- `README.md` - This file

## Custom Evaluators Demonstrated

### 1. ResponseLengthEvaluator (`response_length`)
- **Purpose**: Evaluates the length of responses 
- **Metrics**: Average, median, min/max length, plus length-based scoring
- **Scoring**: Responses 1-500 chars get full score, longer ones are penalized

### 2. AccuracyEvaluator (`accuracy_checker`)  
- **Purpose**: Compares outputs to expected values
- **Features**: Exact match and number extraction for math problems
- **Metrics**: Accuracy percentage, correct/total counts

### 3. SentimentEvaluator (`sentiment_evaluator`)
- **Purpose**: Basic sentiment analysis of responses
- **Method**: Keyword-based sentiment classification
- **Metrics**: Sentiment distribution, average sentiment score

## How Custom Evaluators Work

### 1. Define Your Evaluator Class
```python
from exp_platform_cli import BaseEvaluator, EvaluatorOutput, register_evaluator

@register_evaluator("my_evaluator_name")
class MyCustomEvaluator(BaseEvaluator):
    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        # Your evaluation logic here
        return EvaluatorOutput(name="my_eval", summary={...}, per_row={...})
```

### 2. Import in Your Module
```python
import custom_evaluators  # This registers the evaluators
```

### 3. Reference in Configuration
```yaml
evaluators:
  - id: "my_eval_id"
    name: "my_evaluator_name"  # Must match registered name
    data_mapping: {}
```

## Usage

```bash
# Run from the example directory
cd examples/custom-evaluators
exp-cli run config.yaml --dataset-root data/datasets

# Or from project root
exp-cli run examples/custom-evaluators/config.yaml --dataset-root examples/custom-evaluators/data/datasets
```

## Expected Output

The experiment will process 5 conversation samples through:
1. **Response Length Evaluation** - Length statistics and scoring
2. **Accuracy Evaluation** - Comparison against expected outputs  
3. **Sentiment Evaluation** - Sentiment analysis of responses

## Extending the System

You can easily add more evaluators by:
1. Creating new classes inheriting from `BaseEvaluator`
2. Decorating with `@register_evaluator("name")`
3. Implementing the `evaluate()` method
4. Importing the module to register evaluators
5. Adding to your experiment configuration

The platform supports unlimited custom evaluators with full metrics tracking and reporting!