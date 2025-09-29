# Nested Custom Evaluators Demo

This example demonstrates how to organize and load custom evaluators from nested directories and different folder structures.

## 📁 Directory Structure

```
nested-evaluators-demo/
├── config.yaml                          # Experiment configuration
├── nested_evaluator_loader.py           # Main module with 3 loading methods
├── data/datasets/nested-test/1.0/       # Test dataset
└── custom_evaluators/                   # Nested evaluator packages
    ├── __init__.py
    ├── basic/                            # Basic evaluators subfolder
    │   ├── __init__.py
    │   └── evaluators.py                 # BasicLengthEvaluator, BasicCompletenessEvaluator
    └── advanced/                         # Advanced evaluators subfolder
        ├── __init__.py
        └── evaluators.py                 # AdvancedQualityEvaluator, AdvancedCoherenceEvaluator
```

## 🔧 Three Methods for Loading Nested Evaluators

### Method 1: sys.path Manipulation
```python
# Add nested directories to Python path
current_dir = Path(__file__).parent
basic_path = current_dir / "custom_evaluators" / "basic"
advanced_path = current_dir / "custom_evaluators" / "advanced"

sys.path.insert(0, str(basic_path))
sys.path.insert(0, str(advanced_path))

# Then import normally
import evaluators as basic_evaluators
```

### Method 2: Package Structure Imports
```python
# Use proper Python package imports
from custom_evaluators.basic.evaluators import BasicLengthEvaluator
from custom_evaluators.advanced.evaluators import AdvancedQualityEvaluator
```

### Method 3: Dynamic Loading with importlib
```python
# Load modules dynamically from file paths
import importlib.util
spec = importlib.util.spec_from_file_location("basic_evaluators", path_to_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
```

## 📊 Custom Evaluators in This Demo

### Basic Evaluators (`custom_evaluators/basic/`)
- **BasicLengthEvaluator** (`basic_length`) - Response length analysis
- **BasicCompletenessEvaluator** (`basic_completeness`) - Response completeness check

### Advanced Evaluators (`custom_evaluators/advanced/`)  
- **AdvancedQualityEvaluator** (`advanced_quality`) - Multi-metric quality assessment
- **AdvancedCoherenceEvaluator** (`advanced_coherence`) - Coherence and structure evaluation

## ✅ Requirements for Nested Evaluators

1. **Python Package Structure** - Use `__init__.py` files to make directories proper packages
2. **Proper Imports** - Import evaluators before the platform tries to use them
3. **Path Management** - Ensure Python can find your nested modules
4. **Registration** - Use `@register_evaluator("name")` in each evaluator class

## 🚀 Usage

```bash
# Run the nested evaluators demo
cd examples/nested-evaluators-demo
exp-cli run config.yaml --dataset-root data/datasets

# Test the loading methods directly
python nested_evaluator_loader.py
```

## 🎯 Key Benefits

- **Organization** - Keep related evaluators grouped in logical folders
- **Modularity** - Separate basic and advanced functionality  
- **Reusability** - Easy to import evaluators across different experiments
- **Scalability** - Support for complex evaluator hierarchies
- **Flexibility** - Multiple loading strategies for different use cases

## 💡 Best Practices

1. **Use Package Structure** - Create proper Python packages with `__init__.py`
2. **Clear Naming** - Use descriptive folder and module names
3. **Path Handling** - Use `pathlib.Path` for cross-platform compatibility
4. **Error Handling** - Implement fallback loading strategies
5. **Documentation** - Document your evaluator organization clearly

This approach allows you to organize evaluators in any nested structure you need while maintaining full compatibility with the experimentation platform!