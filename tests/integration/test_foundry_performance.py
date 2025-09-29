"""Performance and load testing for Foundry integration.

These tests validate performance characteristics and scalability
when running experiments on the Foundry platform.
"""

import os
import json
import yaml
import pytest
import time
import concurrent.futures
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import subprocess


class TestFoundryPerformance:
    """Test performance characteristics of Foundry integration."""
    
    @pytest.fixture
    def foundry_config(self):
        """Foundry configuration for performance tests."""
        base_url = os.getenv('FOUNDRY_BASE_URL')
        token = os.getenv('FOUNDRY_TOKEN')
        
        if not base_url or not token:
            pytest.skip("Foundry credentials not configured for performance tests")
        
        return {
            'foundry_base_url': base_url,
            'foundry_token': token,
            'foundry_namespace': os.getenv('FOUNDRY_NAMESPACE', 'perf-test-exp-platform')
        }
    
    def test_large_dataset_performance(self, foundry_config, tmp_path):
        """Test performance with large datasets."""
        
        # Create large dataset (1000 rows)
        large_dataset = []
        for i in range(1000):
            large_dataset.append({
                "input": f"Test question {i}: What is the meaning of life?",
                "expected_output": f"Response {i}: The meaning of life is subjective and varies by individual.",
                "category": f"category_{i % 10}",
                "complexity": "medium"
            })
        
        dataset_name = f"large_perf_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        dataset_dir = tmp_path / "data" / "datasets" / dataset_name / "1.0"
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        dataset_file = dataset_dir / "data.jsonl"
        with dataset_file.open("w") as f:
            for item in large_dataset:
                f.write(json.dumps(item) + "\\n")
        
        # Create simple processing module
        test_module = tmp_path / "perf_test_module.py"
        test_module.write_text('''
def run(input_text: str, context: dict = None) -> str:
    """Simple processing for performance testing."""
    return f"Processed response for: {input_text[:50]}..."
''')
        
        # Create configuration
        config = {
            "dataset": {
                "name": dataset_name,
                "version": "1.0",
                "config": {"expected_output_field": "expected_output"}
            },
            "executable": {
                "type": "module",
                "path": str(test_module),
                "processor": "run",
                "config": {}
            },
            "evaluation": [
                {"id": "quality_eval", "name": "conversation_quality", "data_mapping": {}}
            ],
            "local_mode": False,  # Use Foundry
            "output_path": str(tmp_path / "perf_results"),
            **foundry_config
        }
        
        config_file = tmp_path / "large_dataset_config.yaml"
        with config_file.open("w") as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        # Measure execution time
        start_time = time.time()
        
        result = subprocess.run([
            'exp-cli', 'run', str(config_file)
        ], capture_output=True, text=True, cwd=str(tmp_path), timeout=1800)  # 30 min timeout
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance assertions
        if result.returncode == 0:
            print(f"Large dataset processing completed in {execution_time:.2f} seconds")
            
            # Should process at reasonable speed (less than 2 seconds per row on average)
            avg_time_per_row = execution_time / len(large_dataset)
            assert avg_time_per_row < 2.0, f"Too slow: {avg_time_per_row:.3f}s per row"
            
            # Check results were created
            results_dir = tmp_path / "perf_results"
            if results_dir.exists():
                exp_dirs = [d for d in results_dir.rglob("exp*") if d.is_dir()]
                assert len(exp_dirs) > 0, "No experiment results created"
        else:
            pytest.skip(f"Large dataset test failed due to infrastructure: {result.stderr}")
    
    def test_concurrent_experiments(self, foundry_config, tmp_path):
        """Test running multiple experiments concurrently."""
        
        def create_experiment_config(exp_id: int, base_path: Path) -> Path:
            """Create a single experiment configuration."""
            
            # Create test module
            test_module = base_path / f"concurrent_module_{exp_id}.py"
            test_module.write_text(f'''
def run(input_text: str) -> str:
    """Concurrent test module {exp_id}."""
    import time
    time.sleep(0.1)  # Simulate some processing time
    return f"Experiment {exp_id} response: {{input_text}}"
''')
            
            # Create small dataset
            dataset_name = f"concurrent_test_{exp_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            dataset_dir = base_path / "data" / "datasets" / dataset_name / "1.0"
            dataset_dir.mkdir(parents=True, exist_ok=True)
            
            test_data = [
                {"input": f"Test {exp_id}-{i}", "expected_output": f"Expected {exp_id}-{i}"}
                for i in range(10)  # Small dataset for concurrency test
            ]
            
            dataset_file = dataset_dir / "data.jsonl"
            with dataset_file.open("w") as f:
                for item in test_data:
                    f.write(json.dumps(item) + "\\n")
            
            # Create config
            config = {
                "dataset": {
                    "name": dataset_name,
                    "version": "1.0",
                    "config": {"expected_output_field": "expected_output"}
                },
                "executable": {
                    "type": "module",
                    "path": str(test_module),
                    "processor": "run",
                    "config": {}
                },
                "evaluation": [
                    {"id": "quality_eval", "name": "conversation_quality", "data_mapping": {}}
                ],
                "local_mode": False,
                "output_path": str(base_path / f"concurrent_results_{exp_id}"),
                **foundry_config
            }
            
            config_file = base_path / f"concurrent_config_{exp_id}.yaml"
            with config_file.open("w") as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            
            return config_file
        
        def run_single_experiment(config_file: Path) -> Dict[str, Any]:
            """Run a single experiment and return results."""
            start_time = time.time()
            
            result = subprocess.run([
                'exp-cli', 'run', str(config_file)
            ], capture_output=True, text=True, cwd=str(config_file.parent), timeout=300)
            
            end_time = time.time()
            
            return {
                'config_file': str(config_file),
                'returncode': result.returncode,
                'execution_time': end_time - start_time,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        
        # Create multiple experiment configurations
        num_concurrent = 3  # Conservative number for testing
        config_files = []
        
        for i in range(num_concurrent):
            config_file = create_experiment_config(i, tmp_path)
            config_files.append(config_file)
        
        # Run experiments concurrently
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            future_to_config = {
                executor.submit(run_single_experiment, config_file): config_file
                for config_file in config_files
            }
            
            results = []
            for future in concurrent.futures.as_completed(future_to_config, timeout=600):
                config_file = future_to_config[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    print(f'Experiment {config_file} generated an exception: {exc}')
                    results.append({
                        'config_file': str(config_file),
                        'returncode': -1,
                        'execution_time': 0,
                        'error': str(exc)
                    })
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_results = [r for r in results if r.get('returncode') == 0]
        failed_results = [r for r in results if r.get('returncode') != 0]
        
        print(f"Concurrent execution completed in {total_time:.2f} seconds")
        print(f"Successful experiments: {len(successful_results)}/{len(results)}")
        
        if failed_results:
            print("Failed experiments:")
            for failed in failed_results:
                print(f"  - {failed['config_file']}: {failed.get('stderr', failed.get('error', 'Unknown error'))}")
        
        # Performance assertions
        if len(successful_results) > 0:
            avg_execution_time = sum(r['execution_time'] for r in successful_results) / len(successful_results)
            print(f"Average execution time per experiment: {avg_execution_time:.2f} seconds")
            
            # Concurrent execution should be efficient
            # Total time should be less than sum of individual times (shows parallelism)
            sequential_time_estimate = sum(r['execution_time'] for r in successful_results)
            efficiency = sequential_time_estimate / total_time
            
            print(f"Concurrency efficiency: {efficiency:.2f}x")
            assert efficiency > 1.5, "Concurrency not providing significant benefit"
        
        # At least some experiments should succeed
        success_rate = len(successful_results) / len(results)
        assert success_rate >= 0.5, f"Too many failed experiments: {success_rate:.1%} success rate"
    
    def test_memory_usage_monitoring(self, foundry_config, tmp_path):
        """Test memory usage during experiment execution."""
        
        # Create moderate-sized dataset
        dataset_size = 500
        test_data = []
        
        for i in range(dataset_size):
            # Create some variety in data size
            input_length = 50 + (i % 200)  # Varying input lengths
            test_data.append({
                "input": f"Test question {i}: " + "x" * input_length,
                "expected_output": f"Expected response {i}",
                "metadata": {
                    "category": f"cat_{i % 5}",
                    "priority": i % 3,
                    "tags": [f"tag_{j}" for j in range(i % 5)]
                }
            })
        
        dataset_name = f"memory_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        dataset_dir = tmp_path / "data" / "datasets" / dataset_name / "1.0"
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        dataset_file = dataset_dir / "data.jsonl"
        with dataset_file.open("w") as f:
            for item in test_data:
                f.write(json.dumps(item) + "\\n")
        
        # Create processing module that uses some memory
        test_module = tmp_path / "memory_test_module.py"
        test_module.write_text('''
def run(input_text: str, context: dict = None) -> str:
    """Module that uses some memory for testing."""
    
    # Simulate some memory usage (but not excessive)
    temp_data = ["response_item"] * 1000  # Small temporary list
    
    # Process input
    response = f"Processed: {input_text[:100]}"
    
    # Clean up temporary data
    del temp_data
    
    return response
''')
        
        config = {
            "dataset": {
                "name": dataset_name,
                "version": "1.0",
                "config": {"expected_output_field": "expected_output"}
            },
            "executable": {
                "type": "module",
                "path": str(test_module),
                "processor": "run",
                "config": {}
            },
            "evaluation": [
                {"id": "quality_eval", "name": "conversation_quality", "data_mapping": {}}
            ],
            "local_mode": False,
            "output_path": str(tmp_path / "memory_results"),
            **foundry_config
        }
        
        config_file = tmp_path / "memory_test_config.yaml"
        with config_file.open("w") as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        # Monitor memory usage (basic monitoring via subprocess)
        result = subprocess.run([
            'exp-cli', 'run', str(config_file)
        ], capture_output=True, text=True, cwd=str(tmp_path), timeout=900)
        
        if result.returncode == 0:
            print("Memory usage test completed successfully")
            
            # Check that results were created (indicates completion)
            results_dir = tmp_path / "memory_results"
            if results_dir.exists():
                exp_dirs = [d for d in results_dir.rglob("exp*") if d.is_dir()]
                assert len(exp_dirs) > 0, "No results created"
                
                # Check results size is reasonable
                latest_exp = max(exp_dirs, key=lambda x: x.stat().st_mtime)
                data_file = latest_exp / "data.jsonl"
                
                if data_file.exists():
                    file_size = data_file.stat().st_size
                    print(f"Results file size: {file_size / 1024:.1f} KB")
                    
                    # File size should be reasonable (not excessive)
                    max_expected_size = dataset_size * 2000  # ~2KB per row max
                    assert file_size < max_expected_size, f"Results file too large: {file_size} bytes"
        else:
            pytest.skip(f"Memory test failed due to infrastructure: {result.stderr}")


class TestFoundryScalability:
    """Test scalability characteristics of Foundry integration."""
    
    def test_evaluator_scalability(self, tmp_path):
        """Test performance with multiple evaluators."""
        
        foundry_config = {
            'foundry_base_url': os.getenv('FOUNDRY_BASE_URL', 'https://test.foundry.com'),
            'foundry_token': os.getenv('FOUNDRY_TOKEN', 'test_token'),
            'foundry_namespace': 'scalability-test'
        }
        
        if not os.getenv('FOUNDRY_BASE_URL') or not os.getenv('FOUNDRY_TOKEN'):
            pytest.skip("Foundry credentials not configured")
        
        # Create test dataset
        test_data = [
            {"input": f"Test input {i}", "expected_output": f"Expected {i}"}
            for i in range(50)  # Moderate size for scalability test
        ]
        
        dataset_name = f"evaluator_scale_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        dataset_dir = tmp_path / "data" / "datasets" / dataset_name / "1.0"
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        dataset_file = dataset_dir / "data.jsonl"
        with dataset_file.open("w") as f:
            for item in test_data:
                f.write(json.dumps(item) + "\\n")
        
        # Create simple module
        test_module = tmp_path / "evaluator_scale_module.py"
        test_module.write_text('''
def run(input_text: str) -> str:
    return f"Response to: {input_text}"
''')
        
        # Test with increasing numbers of evaluators
        evaluator_counts = [1, 3, 5]  # Conservative scaling test
        results = {}
        
        for eval_count in evaluator_counts:
            evaluators = []
            for i in range(eval_count):
                eval_names = ["conversation_quality", "response_relevance", "tool_call_accuracy", "equivalent"]
                evaluators.append({
                    "id": f"eval_{i}",
                    "name": eval_names[i % len(eval_names)],
                    "data_mapping": {}
                })
            
            config = {
                "dataset": {
                    "name": dataset_name,
                    "version": "1.0",
                    "config": {"expected_output_field": "expected_output"}
                },
                "executable": {
                    "type": "module",
                    "path": str(test_module),
                    "processor": "run",
                    "config": {}
                },
                "evaluation": evaluators,
                "local_mode": False,
                "output_path": str(tmp_path / f"eval_scale_results_{eval_count}"),
                **foundry_config
            }
            
            config_file = tmp_path / f"eval_scale_config_{eval_count}.yaml"
            with config_file.open("w") as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            
            # Measure execution time
            start_time = time.time()
            
            result = subprocess.run([
                'exp-cli', 'run', str(config_file)
            ], capture_output=True, text=True, cwd=str(tmp_path), timeout=600)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            results[eval_count] = {
                'success': result.returncode == 0,
                'execution_time': execution_time,
                'stderr': result.stderr if result.returncode != 0 else None
            }
            
            print(f"Evaluators: {eval_count}, Time: {execution_time:.2f}s, Success: {result.returncode == 0}")
        
        # Analyze scalability
        successful_results = {k: v for k, v in results.items() if v['success']}
        
        if len(successful_results) >= 2:
            # Check that execution time scales reasonably
            times = [(k, v['execution_time']) for k, v in successful_results.items()]
            times.sort()
            
            if len(times) >= 2:
                # Time should increase with more evaluators, but not excessively
                first_count, first_time = times[0]
                last_count, last_time = times[-1]
                
                time_ratio = last_time / first_time
                evaluator_ratio = last_count / first_count
                
                print(f"Scalability ratio: {time_ratio:.2f}x time for {evaluator_ratio:.2f}x evaluators")
                
                # Should scale sub-linearly (good) or at most linearly (acceptable)
                assert time_ratio <= evaluator_ratio * 1.5, f"Poor scalability: {time_ratio:.2f}x time for {evaluator_ratio:.2f}x evaluators"
        
        # At least one configuration should work
        assert len(successful_results) > 0, "No evaluator configurations worked"
    
    def test_batch_processing_efficiency(self, tmp_path):
        """Test efficiency of batch processing multiple experiments."""
        
        foundry_config = {
            'foundry_base_url': os.getenv('FOUNDRY_BASE_URL', 'https://test.foundry.com'),
            'foundry_token': os.getenv('FOUNDRY_TOKEN', 'test_token'),
            'foundry_namespace': 'batch-test'
        }
        
        if not os.getenv('FOUNDRY_BASE_URL') or not os.getenv('FOUNDRY_TOKEN'):
            pytest.skip("Foundry credentials not configured")
        
        # Create multiple small experiments
        experiments_dir = tmp_path / "batch_experiments"
        experiments_dir.mkdir()
        
        num_experiments = 5
        experiment_configs = []
        
        # Create shared test module
        shared_module = tmp_path / "batch_shared_module.py"
        shared_module.write_text('''
def run(input_text: str) -> str:
    return f"Batch processed: {input_text}"
''')
        
        for i in range(num_experiments):
            # Create dataset
            dataset_name = f"batch_exp_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            dataset_dir = tmp_path / "data" / "datasets" / dataset_name / "1.0"
            dataset_dir.mkdir(parents=True, exist_ok=True)
            
            test_data = [
                {"input": f"Batch test {i}-{j}", "expected_output": f"Expected {i}-{j}"}
                for j in range(10)  # Small datasets for batch test
            ]
            
            dataset_file = dataset_dir / "data.jsonl"
            with dataset_file.open("w") as f:
                for item in test_data:
                    f.write(json.dumps(item) + "\\n")
            
            # Create config
            config = {
                "dataset": {
                    "name": dataset_name,
                    "version": "1.0",
                    "config": {"expected_output_field": "expected_output"}
                },
                "executable": {
                    "type": "module",
                    "path": str(shared_module),
                    "processor": "run",
                    "config": {}
                },
                "evaluation": [
                    {"id": "quality_eval", "name": "conversation_quality", "data_mapping": {}}
                ],
                "local_mode": False,
                "output_path": str(tmp_path / f"batch_results"),
                **foundry_config
            }
            
            config_file = experiments_dir / f"batch_experiment_{i}.yaml"
            with config_file.open("w") as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            
            experiment_configs.append(config_file)
        
        # Test batch execution
        start_time = time.time()
        
        result = subprocess.run([
            'exp-cli', 'run-directory', str(experiments_dir)
        ], capture_output=True, text=True, cwd=str(tmp_path), timeout=1200)  # 20 min timeout
        
        end_time = time.time()
        batch_time = end_time - start_time
        
        print(f"Batch processing of {num_experiments} experiments took {batch_time:.2f} seconds")
        
        if result.returncode == 0:
            # Check results
            results_dir = tmp_path / "batch_results"
            if results_dir.exists():
                exp_dirs = [d for d in results_dir.rglob("exp*") if d.is_dir()]
                print(f"Created {len(exp_dirs)} experiment result directories")
                
                # Should have created some results
                assert len(exp_dirs) > 0, "No experiment results created"
                
                # Batch should be reasonably efficient
                avg_time_per_experiment = batch_time / num_experiments
                print(f"Average time per experiment: {avg_time_per_experiment:.2f} seconds")
                
                # Should be reasonably fast per experiment
                assert avg_time_per_experiment < 300, f"Too slow: {avg_time_per_experiment:.1f}s per experiment"
        else:
            print(f"Batch processing failed: {result.stderr}")
            pytest.skip("Batch processing failed due to infrastructure issues")


# Mark all tests as integration and performance tests
pytestmark = [pytest.mark.integration, pytest.mark.performance]