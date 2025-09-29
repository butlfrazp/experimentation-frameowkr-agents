# 🚀 5-Minute Quickstart

Get up and running with the Experimentation Platform in just 5 minutes!

## What You'll Learn

- How to install the platform
- How to run your first experiment
- How to view results

## Step 1: Installation

```bash
# Install the platform
pip install -e .

# Verify installation
exp-cli --version
```

## Step 2: Run Your First Experiment

```bash
# Navigate to this tutorial
cd tutorials/01-quickstart

# Run the experiment
exp-cli run-directory . --install-deps
```

This will:
- 📦 Install any missing dependencies
- 🔍 Discover the experiment configuration
- 🏃 Run the evaluation
- 📊 Generate results

## Step 3: View Results

Check the `data/experiments/` directory for your results:

```bash
ls -la data/experiments/
```

You'll see:
- 📈 **Results JSON**: Detailed evaluation metrics
- 📝 **Execution Log**: Step-by-step execution details
- ⚙️ **Configuration**: The resolved experiment setup

## What Just Happened?

You ran a simple **conversation quality** evaluation that:

1. 🤖 Simulated AI agent responses
2. 📏 Evaluated response quality using multiple metrics
3. 💾 Saved comprehensive results and logs

## Next Steps

🎯 **Ready for more?** Try these tutorials:

- **[Basic Concepts](../03-basic-concepts/)** - Understanding the platform
- **[Simple Experiment](../04-simple-experiment/)** - Build from scratch  
- **[Configuration Guide](../05-configuration/)** - Master YAML configs

## Troubleshooting

### Command Not Found
```bash
# If exp-cli command not found, try:
python -m exp_platform_cli --version
```

### Permission Issues  
```bash
# Install in development mode:
pip install -e . --user
```

### Dependencies Missing
```bash
# Install with all dependencies:
pip install -e .[all]
```

---

**🎉 Congratulations!** You've successfully run your first experiment with the Experimentation Platform!