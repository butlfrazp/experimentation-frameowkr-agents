# Foundry Integration Tests

This directory contains comprehensive integration tests for the Experimentation Platform's Foundry integration. These tests validate the platform's ability to run experiments on the Foundry cloud platform.

## 🔧 Setup Requirements

### Environment Variables

Set these environment variables to run Foundry integration tests:

```bash
# Required
export FOUNDRY_BASE_URL="https://your-foundry-instance.palantirfoundry.com"
export FOUNDRY_TOKEN="your-foundry-api-token"

# Optional
export FOUNDRY_DATASET_RID="ri.foundry.dataset.12345"  # For existing dataset tests
export FOUNDRY_NAMESPACE="your-test-namespace"         # Default: test-exp-platform
```

### Installation

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-timeout pytest-xdist

# Install platform in development mode
pip install -e .
```

## 📋 Test Modules

### `test_foundry_basic.py`
**Core Foundry Integration Tests**
- Dataset creation and management
- Basic experiment execution
- Configuration validation
- Results handling and export
- Error handling and recovery

### `test_foundry_performance.py`
**Performance and Load Tests**
- Large dataset processing (1000+ rows)
- Concurrent experiment execution
- Memory usage monitoring
- Evaluator scalability
- Batch processing efficiency

### `test_e2e_integration.py`
**End-to-End Workflow Tests**
- Complete workflow validation
- Configuration format compatibility
- CLI interface stability
- Output format consistency
- Error recovery mechanisms

### `conftest.py`
**Test Configuration and Utilities**
- Pytest configuration and markers
- Foundry environment validation
- Test helper utilities
- Fixtures and common setup

## 🚀 Running Tests

### Run All Integration Tests
```bash
# Run all integration tests (local + Foundry)
pytest tests/integration/ -v

# Run only if Foundry is configured
pytest tests/integration/ -v -m "not foundry or (foundry and integration)"
```

### Run Foundry-Specific Tests
```bash
# Run only Foundry tests
pytest tests/integration/ -v -m foundry

# Run with specific patterns
pytest tests/integration/test_foundry_*.py -v

# Run basic Foundry tests only
pytest tests/integration/test_foundry_basic.py -v
```

### Run Performance Tests
```bash
# Run performance tests (longer duration)
pytest tests/integration/test_foundry_performance.py -v --timeout=1800

# Run with parallelization
pytest tests/integration/ -v -n auto
```

### Run with Different Verbosity
```bash
# Detailed output
pytest tests/integration/ -v -s --tb=short

# Minimal output
pytest tests/integration/ -q

# Show local variables on failure
pytest tests/integration/ -v -l
```

## 📊 Test Categories

### Integration Tests (`@pytest.mark.integration`)
- Test complete workflows end-to-end
- Validate integration between components
- Test real environment interactions

### Performance Tests (`@pytest.mark.performance`)
- Validate performance characteristics
- Test scalability limits
- Monitor resource usage

### Foundry Tests (`@pytest.mark.foundry`)
- Require Foundry environment setup
- Test cloud platform specific features
- Validate Foundry API interactions

## 🔍 Test Structure

### Test Classes
```python
class TestFoundryDatasetManagement:
    """Test dataset operations with Foundry."""
    
class TestFoundryExperimentExecution:
    """Test experiment execution on Foundry."""
    
class TestFoundryResultsHandling:
    """Test results handling for Foundry experiments."""
    
class TestFoundryConfiguration:
    """Test Foundry-specific configuration handling."""
```

### Fixtures
- `foundry_config`: Foundry connection configuration
- `sample_test_data`: Test datasets for experiments
- `foundry_experiment_config`: Complete experiment setup
- `foundry_helpers`: Utility functions for tests

## 🎯 Test Scenarios

### Basic Functionality
- ✅ Dataset creation and upload to Foundry
- ✅ Experiment configuration validation
- ✅ Module execution on Foundry platform
- ✅ Results retrieval and parsing
- ✅ Error handling and resilience

### Advanced Scenarios
- ✅ Large dataset processing (1000+ rows)
- ✅ Multiple evaluator configurations
- ✅ Concurrent experiment execution
- ✅ Batch experiment processing
- ✅ Performance monitoring

### Error Handling
- ✅ Network connectivity issues
- ✅ Authentication failures
- ✅ Invalid configurations
- ✅ Module execution errors
- ✅ Timeout handling

## 📈 Performance Benchmarks

### Expected Performance Characteristics
- **Small datasets** (≤50 rows): < 60 seconds
- **Medium datasets** (51-500 rows): < 300 seconds  
- **Large datasets** (501-1000 rows): < 900 seconds
- **Concurrent experiments**: 1.5x+ efficiency gain
- **Memory usage**: Linear scaling with dataset size

### Performance Test Metrics
- Execution time per experiment
- Throughput (rows processed per second)
- Memory usage patterns
- Concurrency efficiency ratios
- Error rates under load

## 🛠️ Troubleshooting

### Common Issues

**Tests Skip with "Foundry not configured"**
```bash
# Check environment variables
echo $FOUNDRY_BASE_URL
echo $FOUNDRY_TOKEN

# Set if missing
export FOUNDRY_BASE_URL="https://your-instance.palantirfoundry.com"
export FOUNDRY_TOKEN="your-token"
```

**Authentication Errors**
- Verify token has required permissions
- Check token expiration
- Validate base URL format

**Network Timeouts**
- Check network connectivity to Foundry
- Increase timeout values for slow networks
- Run tests with `--timeout=1800` for extended timeout

**Performance Test Failures**
- Adjust performance thresholds for your environment
- Run with `--timeout=3600` for very large datasets
- Check system resources (CPU, memory, network)

### Debug Mode
```bash
# Run with maximum verbosity
pytest tests/integration/ -v -s --tb=long --capture=no

# Run single test with debugging
pytest tests/integration/test_foundry_basic.py::TestFoundryDatasetManagement::test_dataset_creation_foundry -v -s
```

## 📝 Adding New Tests

### Test Template
```python
def test_new_foundry_feature(self, foundry_config, tmp_path):
    """Test description."""
    if not foundry_config.is_configured:
        pytest.skip("Foundry not configured")
    
    # Test setup
    # ...
    
    # Execute test
    # ...
    
    # Validate results
    assert result.returncode == 0
    # ...
```

### Best Practices
1. **Always check Foundry configuration** before test execution
2. **Use unique names** for datasets and experiments
3. **Include cleanup** in test teardown when possible
4. **Handle network errors gracefully** with meaningful messages
5. **Add performance assertions** for scalability tests
6. **Use descriptive test names** and docstrings

## 📊 Continuous Integration

### CI Configuration
The integration tests are designed to work in CI environments:
- Skip Foundry tests if credentials not available
- Fail gracefully on network issues
- Provide detailed error reporting
- Support parallel execution

### Environment Setup in CI
```yaml
env:
  FOUNDRY_BASE_URL: ${{ secrets.FOUNDRY_BASE_URL }}
  FOUNDRY_TOKEN: ${{ secrets.FOUNDRY_TOKEN }}
  FOUNDRY_NAMESPACE: "ci-testing"
```

---

**Ready to test your Foundry integration? Start with the basic tests and work your way up to performance testing! 🚀**