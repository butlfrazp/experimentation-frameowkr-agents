# Jupyter Notebooks for Experimentation Platform

This directory contains interactive Jupyter notebooks that provide a data scientist-friendly interface for the Experimentation Platform.

## 📚 Available Notebooks

### 🚀 [data_scientist_interface.ipynb](data_scientist_interface.ipynb)
**Main Interactive Interface** - Perfect for beginners and visual learners

- **🎛️ Interactive Widget Interface**: Visual forms for experiment design
- **⚙️ Configuration Editor**: Edit and validate YAML configs visually  
- **📊 Results Viewer**: Browse and analyze experiment results
- **📚 Tutorial Runner**: Execute built-in tutorials interactively
- **🔧 Quick Experiment API**: Programmatic interface for simple experiments

**Best for**: First-time users, visual workflow preference, quick prototyping

### 🔬 [advanced_patterns.ipynb](advanced_patterns.ipynb)  
**Advanced Experimentation Patterns** - For experienced data scientists

- **📊 Parameter Sweep Experiments**: Systematic testing across configurations
- **📈 Results Analysis & Visualization**: Statistical analysis with pandas/matplotlib
- **🎯 A/B Testing Framework**: Compare different approaches statistically
- **🔧 Custom Evaluation Metrics**: Build domain-specific evaluation functions
- **💡 Performance Optimization**: Data-driven recommendations

**Best for**: Experienced users, research workflows, optimization projects

## 🛠️ Supporting Files

### [experiment_interface.py](experiment_interface.py)
Core widget interface implementation with:
- `ExperimentPlatformWidget`: Main interactive interface class
- `quick_experiment()`: Simplified API for running experiments
- `load_results()`: Utility for loading and analyzing results
- `create_experiment_interface()`: Factory function for widget creation

### [advanced_example.py](advanced_example.py)
Sophisticated example module demonstrating:
- Context-aware processing with different modes (concise, helpful, detailed)
- Temperature-based response variation
- Multi-domain question handling (geography, math, science)
- Structured response generation

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install ipywidgets pyyaml pandas matplotlib seaborn scipy numpy
   ```

2. **Start with the Basic Interface**:
   - Open `data_scientist_interface.ipynb`
   - Run the setup cells
   - Use the interactive widget interface

3. **Explore Advanced Patterns**:
   - Open `advanced_patterns.ipynb` after basic familiarity
   - Run parameter sweeps and custom analyses

## 💡 Key Features

### 🎯 For Data Scientists
- **No Command Line Required**: Full visual interface for all operations
- **Integrated Analysis**: Built-in visualization and statistical analysis
- **Flexible APIs**: Both visual and programmatic interfaces available
- **Research-Friendly**: Advanced patterns for systematic experimentation

### 🔧 For Developers  
- **Extensible Widget System**: Easy to add new interface components
- **Custom Evaluators**: Framework for domain-specific metrics
- **Configuration Management**: Visual editing with validation
- **Result Export**: Multiple formats for downstream analysis

### 📊 For Researchers
- **Parameter Sweeps**: Systematic exploration of configuration space
- **Statistical Analysis**: A/B testing and significance testing
- **Custom Metrics**: Domain-specific evaluation functions
- **Reproducible Workflows**: Save and replay experimental configurations

## 🎨 Interface Overview

The main interface provides four key tabs:

1. **🚀 Experiment Designer**: Visual form for creating experiments
2. **⚙️ Config Editor**: YAML configuration editing with validation
3. **📊 Results**: Browse and analyze experiment outputs  
4. **📚 Tutorials**: Interactive tutorial execution

## 📈 Example Workflows

### Quick Experiment
```python
from experiment_interface import quick_experiment

result = quick_experiment(
    module_path="my_module.py",
    data=[{"input": "Hello", "expected_output": "Hi!"}],
    evaluators=["conversation_quality"],
    dataset_name="my_test"
)
```

### Parameter Sweep
```python
# See advanced_patterns.ipynb for full implementation
for mode in ['concise', 'helpful', 'detailed']:
    for temp in [0.2, 0.5, 0.8]:
        # Run experiment with parameters
        # Collect and analyze results
```

### Custom Analysis
```python
from experiment_interface import load_results

results = load_results("data/experiments/exp_001/")
# Perform custom analysis on results['rows']
```

## 🎯 Tips for Success

### 🚀 Getting Started
- Start with simple examples in the basic interface
- Use the tutorial runner to learn platform concepts
- Try the example modules before building custom ones

### 📊 Advanced Usage
- Run parameter sweeps to find optimal configurations
- Create custom evaluation metrics for your domain
- Use statistical analysis to validate improvements
- Save successful configurations for reuse

### 🔧 Development
- Build on the provided widget examples
- Extend evaluation functions for specific needs
- Create domain-specific interfaces using the base components

---

**Ready to start experimenting? Open `data_scientist_interface.ipynb` and begin your journey! 🧪✨**