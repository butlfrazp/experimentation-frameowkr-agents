# 📚 Experimentation Platform Tutorials

Welcome to the comprehensive tutorial series for the Experimentation Platform CLI! These tutorials will guide you through all aspects of the platform, from basic usage to advanced evaluation scenarios.

## 🎯 Tutorial Structure

### 📖 Getting Started
- **[01-quickstart](01-quickstart/)** - Your first experiment in 5 minutes
- **[02-installation](02-installation/)** - Complete installation and setup guide
- **[03-basic-concepts](03-basic-concepts/)** - Core concepts and terminology

### 🏃 Basic Usage  
- **[04-simple-experiment](04-simple-experiment/)** - Create and run your first experiment
- **[05-configuration](05-configuration/)** - Understanding YAML configuration files
- **[06-evaluators](06-evaluators/)** - Working with built-in evaluators

### 🔧 Advanced Features
- **[07-foundry-evaluators](07-foundry-evaluators/)** - Using foundry-style evaluators
- **[08-cloud-evaluation](08-cloud-evaluation/)** - Setting up cloud evaluation
- **[09-directory-execution](09-directory-execution/)** - Running multiple experiments
- **[10-custom-modules](10-custom-modules/)** - Creating custom execution modules

### 🎨 Real-World Examples
- **[11-agent-evaluation](11-agent-evaluation/)** - Evaluating AI agents and tool calls
- **[12-semantic-kernel](12-semantic-kernel/)** - Semantic Kernel integration examples
- **[13-batch-processing](13-batch-processing/)** - Processing large datasets
- **[14-continuous-evaluation](14-continuous-evaluation/)** - CI/CD integration

### 🚀 Production Usage
- **[15-best-practices](15-best-practices/)** - Production deployment patterns
- **[16-monitoring](16-monitoring/)** - Monitoring and observability
- **[17-troubleshooting](17-troubleshooting/)** - Common issues and solutions

## 🚀 Quick Start

If you're new to the platform, start with the quickstart tutorial:

```bash
cd tutorials/01-quickstart
exp-cli run-directory . --install-deps
```

## 📋 Prerequisites

- Python 3.11+
- Experimentation Platform CLI installed (`pip install -e .`)
- Basic understanding of YAML configuration

## 🎓 Learning Path

### Beginner Path
1. 01-quickstart → 02-installation → 03-basic-concepts → 04-simple-experiment

### Intermediate Path  
2. 05-configuration → 06-evaluators → 07-foundry-evaluators → 09-directory-execution

### Advanced Path
3. 08-cloud-evaluation → 11-agent-evaluation → 12-semantic-kernel → 15-best-practices

## 🔗 Additional Resources

- [API Documentation](../docs/api/)
- [Configuration Reference](../docs/configuration.md)
- [Evaluator Guide](../docs/evaluators.md)
- [Examples Repository](../examples/)

## 🤝 Contributing

Found an issue or want to improve a tutorial? Please see our [Contributing Guide](../CONTRIBUTING.md).

---

**💡 Tip**: Each tutorial is self-contained and includes all necessary files to run independently!