# Installation Test

Simple test to verify the package can be installed and basic functionality works.

## Test Installation

```bash
# Install in development mode
pip install -e .

# Test basic CLI functionality
exp-cli --help
exp-cli info
```

## Create Test Configuration

```bash
# Create a simple test dataset
mkdir -p artifacts/datasets/test/1.0
echo '{"input": "test", "expected": "result"}' > artifacts/datasets/test/1.0/data.jsonl

# Create test configuration
cat > test_install.yaml << EOF
dataset:
  name: test
  version: "1.0"
  config:
    expected_output_field: expected
executable:
  type: module
  path: /workspaces/agent-experiment/examples/semantic_kernel/simple_examples/01_basic_math.py
  processor: process_row
evaluation: []
local_mode: true
EOF

# Test experiment execution
exp-cli validate test_install.yaml
exp-cli run test_install.yaml --dry-run
```