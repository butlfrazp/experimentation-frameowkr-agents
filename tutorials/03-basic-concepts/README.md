# 🔧 Core Concepts Guide

Understanding the fundamental concepts of the Experimentation Platform.

## 🏗️ Architecture Overview

The platform is built around four core components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   📝 Dataset    │───▶│  🏃 Execution   │───▶│  📊 Evaluation  │
│                 │    │     Module      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ ⚙️ Configuration │    │  💾 Results     │
                       │                 │    │                 │
                       └─────────────────┘    └─────────────────┘
```

## 📝 Dataset

Your **data** that drives the experiments:

### Types
- **Inline**: Data defined directly in YAML
- **File**: CSV, JSON, or other file formats  
- **Dynamic**: Generated programmatically

### Structure
```yaml
dataset:
  type: inline
  data:
    - input: "Question 1"
      expected_output: "Answer 1"
      context: "additional_info"
```

## 🏃 Execution Module

The **code** that processes your data:

### Requirements
- Must have a `run()` function
- Takes input data as parameters
- Returns results for evaluation

### Example
```python
def run(input_data: str, context: str = None) -> str:
    # Your processing logic here
    return processed_result
```

## 📊 Evaluators

The **metrics** that measure performance:

### Platform Evaluators
Built-in evaluators for common tasks:
- `conversation_quality` - Chat/dialogue quality
- `tool_call_accuracy` - API/tool usage correctness
- `response_relevance` - Answer relevance scoring

### Foundry Evaluators  
Custom evaluators using the foundry pattern:
- Row-by-row processing
- Flexible input/output handling
- Custom scoring logic

## ⚙️ Configuration

The **YAML file** that ties everything together:

### Key Sections
```yaml
name: experiment_name
description: "What this experiment does"

dataset: # Your data source
evaluators: # How to measure success  
execution: # How to run the code
output: # Where to save results
```

## 💾 Results

The **output** of your experiments:

### What's Saved
- **Raw Results**: Individual evaluation scores
- **Aggregated Metrics**: Summary statistics
- **Execution Logs**: Detailed run information
- **Configuration**: Resolved experiment setup

### File Structure
```
data/experiments/
└── experiment_name_20241215_143052/
    ├── results.json
    ├── execution.log
    └── config.yaml
```

## 🔄 Execution Flow

1. **Load Configuration** - Parse YAML file
2. **Prepare Dataset** - Load and validate data
3. **Initialize Evaluators** - Set up measurement tools
4. **Execute Module** - Run processing logic
5. **Evaluate Results** - Calculate metrics
6. **Save Output** - Store results and logs

## 🎯 Best Practices

### Configuration
- ✅ Use descriptive names and descriptions
- ✅ Set appropriate timeouts
- ✅ Include metadata for tracking

### Modules
- ✅ Handle errors gracefully
- ✅ Return consistent data types
- ✅ Include logging for debugging

### Evaluation
- ✅ Choose appropriate evaluators
- ✅ Set realistic thresholds
- ✅ Document scoring criteria

## 🔗 Next Steps

Ready to build your first experiment?

- **[Simple Experiment](../04-simple-experiment/)** - Build from scratch
- **[Configuration Guide](../05-configuration/)** - Master YAML configs
- **[Evaluator Guide](../06-evaluators/)** - Understand evaluation metrics

---

**💡 Key Takeaway**: The platform provides a structured way to run **reproducible experiments** with **consistent evaluation** across different **execution contexts**.