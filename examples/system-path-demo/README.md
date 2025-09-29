# System Path Demo

This example demonstrates the new **python_path** functionality that allows loading modules from custom nested directories during experiment execution.

## 📁 Directory Structure

```
system-path-demo/
├── config.yaml                    # Experiment config with python_path
├── main_processor.py               # Main executable module  
├── data/datasets/system-path-test/1.0/
│   └── dataset.json                # Test dataset
├── nested/deep/evaluators/         # Deep nested evaluators
│   └── complex_evaluator.py        # DeepNestedEvaluator
├── utils/helpers/                  # Utility evaluators  
│   └── utility_eval.py             # UtilityEvaluator
└── shared/common/                  # Shared utility functions
    └── text_utils.py               # Text processing utilities
```

## 🔧 New python_path Configuration

The `config.yaml` includes a new `python_path` field:

```yaml
executable:
  type: "module"
  path: "main_processor"
  processor: "run"
  python_path:                    # 🆕 New feature!
    - "nested/deep/evaluators"    # Deep nested directory
    - "utils/helpers"             # Utility modules  
    - "shared/common"             # Shared components
  config: {}
```

## ✨ How It Works

1. **Path Addition**: Before loading the main module, the platform adds all `python_path` directories to `sys.path`
2. **Module Loading**: Your module can now import directly from nested directories:
   ```python
   import complex_evaluator        # from nested/deep/evaluators/
   import utility_eval            # from utils/helpers/
   from text_utils import helper  # from shared/common/
   ```
3. **Path Cleanup**: After module loading, the original `sys.path` is restored

## 🎯 Benefits

- **Organized Code**: Keep evaluators in logical nested directories
- **Shared Components**: Import common utilities from any nested location
- **No Path Hacking**: No need for manual `sys.path.insert()` in your code
- **Clean Configuration**: Declarative path management in YAML config

## 🚀 Usage

```bash
# Run the system path demo
cd examples/system-path-demo
exp-cli run config.yaml --dataset-root data/datasets
```

## 📊 Expected Results

The experiment will:
1. ✅ Load evaluators from nested directories via `python_path`
2. ✅ Import shared utilities across modules  
3. ✅ Process 4 test samples with nested evaluators
4. ✅ Generate metrics from deeply nested evaluator modules

## 💡 Use Cases

Perfect for:
- **Large Projects**: Organize evaluators in team/project specific folders
- **Shared Libraries**: Import common utilities from centralized locations  
- **Legacy Code**: Integrate existing modules without restructuring
- **Plugin Architecture**: Load evaluators from configurable plugin directories

This feature makes the experimentation platform much more flexible for complex, real-world project structures!