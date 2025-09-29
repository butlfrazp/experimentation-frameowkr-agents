"""Enhanced evaluator registry supporting both platform and foundry evaluators."""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Type, Union

import yaml
from pydantic import BaseModel

from ..models import EvaluatorConfig, DataModelRow
from .base import BaseEvaluator, EvaluatorOutput
from .registry import registry as base_registry


class FlowEvaluatorConfig(BaseModel):
    """Configuration for foundry-style flow evaluators."""
    
    inputs: Dict[str, Any]
    entry: str  # module:ClassName format
    environment: Dict[str, str] = {}


class FlowEvaluatorWrapper(BaseEvaluator):
    """Wrapper to adapt foundry-style evaluators to platform interface."""
    
    def __init__(self, config: EvaluatorConfig, flow_config: FlowEvaluatorConfig, evaluator_instance: Any):
        super().__init__(config)
        self.flow_config = flow_config
        self.evaluator_instance = evaluator_instance
    
    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Process foundry evaluator row-by-row as intended by foundry design."""
        per_row: Dict[str, Dict[str, float]] = {}
        summary_metrics: Dict[str, float] = {}
        
        for row in rows:
            row_result = self._evaluate_single_row(row)
            per_row[row.id] = row_result
            
            # Accumulate metrics for summary
            for key, value in row_result.items():
                if key not in summary_metrics:
                    summary_metrics[key] = 0.0
                summary_metrics[key] += value
        
        # Calculate averages for summary (foundry-style aggregation)
        total_rows = len(rows)
        if total_rows > 0:
            for key in summary_metrics:
                summary_metrics[key] /= total_rows
        
        return EvaluatorOutput(
            name=self.config.name,
            summary=summary_metrics,
            per_row=per_row,
        )
    
    def _evaluate_single_row(self, row: DataModelRow) -> Dict[str, float]:
        """Evaluate a single row using foundry evaluator - true row-by-row processing."""
        try:
            # Build foundry-style inputs for this specific row
            foundry_inputs = self._build_foundry_inputs(row)
            
            # Call foundry evaluator (row-by-row as designed)
            result = self.evaluator_instance(**foundry_inputs)
            
            # Process foundry result into platform metrics
            return self._process_foundry_result(result)
            
        except Exception as e:
            # Graceful error handling per row
            return {
                "error": 1.0, 
                "score": 0.0,
                "evaluation_error": f"Foundry evaluator failed: {str(e)}"
            }
    
    def _build_foundry_inputs(self, row: DataModelRow) -> Dict[str, Any]:
        """Build foundry-compatible inputs for a single row."""
        # Start with core foundry inputs
        foundry_inputs = {
            "response": row.data_output,
            "ground_truth": row.expected_output,
        }
        
        # Add all row input data (foundry evaluators expect access to original inputs)
        foundry_inputs.update(row.data_input)
        
        # Apply explicit data mapping if configured
        if self.config.data_mapping:
            # Create a complete view of available data for mapping
            available_data = {
                "data_output": row.data_output,
                "expected_output": row.expected_output,
                "response": row.data_output,  # Common alias
                "ground_truth": row.expected_output,  # Common alias
                **row.data_input,
            }
            
            # Apply mappings (this allows flexible field mapping)
            for foundry_key, platform_key in self.config.data_mapping.items():
                if platform_key in available_data:
                    foundry_inputs[foundry_key] = available_data[platform_key]
        
        return foundry_inputs
    
    def _process_foundry_result(self, result: Any) -> Dict[str, float]:
        """Convert foundry evaluator result to platform metrics."""
        if not isinstance(result, dict):
            # Handle non-dict results
            return {"score": float(result) if isinstance(result, (int, float, bool)) else 0.0}
        
        # Process foundry result dictionary
        row_metrics = {}
        for key, value in result.items():
            if isinstance(value, (int, float)):
                row_metrics[key] = float(value)
            elif isinstance(value, bool):
                row_metrics[key] = float(value)
            # Skip non-numeric fields (like 'notes', 'response_normalized', etc.)
        
        # Ensure we always have a 'score' metric for consistency
        if "score" not in row_metrics and len(row_metrics) > 0:
            # Use the first numeric metric as score if no explicit score
            row_metrics["score"] = next(iter(row_metrics.values()))
        
        return row_metrics


class EnhancedEvaluatorRegistry:
    """Enhanced registry supporting both platform and foundry evaluators."""
    
    def __init__(self):
        self.base_registry = base_registry
        self._flow_cache: Dict[str, tuple[FlowEvaluatorConfig, Any]] = {}
    
    def _load_flow_evaluator(self, evaluator_path: Path) -> tuple[FlowEvaluatorConfig, Any] | None:
        """Load a foundry-style flow evaluator from directory."""
        flow_file = evaluator_path / "flow.flex.yaml"
        if not flow_file.exists():
            return None
            
        try:
            # Load flow configuration
            with flow_file.open('r') as f:
                flow_data = yaml.safe_load(f)
            
            flow_config = FlowEvaluatorConfig(**flow_data)
            
            # Parse entry point
            if ':' not in flow_config.entry:
                raise ValueError(f"Invalid entry format: {flow_config.entry}. Expected 'module:ClassName'")
            
            module_name, class_name = flow_config.entry.split(':', 1)
            
            # Load the module from the evaluator directory
            module_file = evaluator_path / f"{module_name}.py"
            if not module_file.exists():
                raise FileNotFoundError(f"Module file not found: {module_file}")
            
            spec = importlib.util.spec_from_file_location(module_name, module_file)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load spec for {module_name}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the evaluator class
            evaluator_class = getattr(module, class_name)
            evaluator_instance = evaluator_class()
            
            return flow_config, evaluator_instance
            
        except Exception as e:
            raise ValueError(f"Failed to load flow evaluator from {evaluator_path}: {e}")
    
    def _find_evaluator_paths(self) -> list[Path]:
        """Find all potential evaluator directories."""
        paths = []
        
        # Look in common evaluator directories
        search_dirs = [
            Path.cwd() / "evaluators",
            Path.cwd() / "custom_evaluators",
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for item in search_dir.iterdir():
                    if item.is_dir() and (item / "flow.flex.yaml").exists():
                        paths.append(item)
        
        return paths
    
    def create(self, config: EvaluatorConfig) -> BaseEvaluator | None:
        """Create evaluator instance, trying both registry and flow approaches."""
        
        evaluator_name = config.name or config.id
        if not evaluator_name:
            return None
        
        # If data_mapping is provided, prefer foundry-style evaluators first
        # This indicates the user wants to map data fields, which is foundry-style
        if config.data_mapping:
            # Try foundry evaluator first when data mapping is specified
            foundry_evaluator = self._try_foundry_evaluator(config, evaluator_name)
            if foundry_evaluator is not None:
                return foundry_evaluator
        
        # Try the base registry (platform evaluators)
        evaluator = self.base_registry.create(config)
        if evaluator is not None:
            return evaluator
        
        # If not found in platform registry, try foundry evaluator
        return self._try_foundry_evaluator(config, evaluator_name)
    
    def _try_foundry_evaluator(self, config: EvaluatorConfig, evaluator_name: str) -> BaseEvaluator | None:
        """Try to create a foundry-style evaluator."""
        
        # Check cache first
        cache_key = evaluator_name.lower()
        if cache_key in self._flow_cache:
            flow_config, evaluator_instance = self._flow_cache[cache_key]
            return FlowEvaluatorWrapper(config, flow_config, evaluator_instance)
        
        # Search for flow evaluator
        for evaluator_path in self._find_evaluator_paths():
            if evaluator_path.name.lower() == cache_key:
                try:
                    flow_config, evaluator_instance = self._load_flow_evaluator(evaluator_path)
                    
                    # Cache for future use
                    self._flow_cache[cache_key] = (flow_config, evaluator_instance)
                    
                    return FlowEvaluatorWrapper(config, flow_config, evaluator_instance)
                    
                except Exception:
                    # Continue searching if this evaluator failed to load
                    continue
        
        return None
    
    def available(self) -> Iterable[str]:
        """List all available evaluators (both platform and flow)."""
        # Platform evaluators
        available = list(self.base_registry.available())
        
        # Flow evaluators
        for evaluator_path in self._find_evaluator_paths():
            available.append(evaluator_path.name)
        
        return available


# Create enhanced registry instance
enhanced_registry = EnhancedEvaluatorRegistry()


def load_evaluators(configs: Iterable[EvaluatorConfig]) -> list[BaseEvaluator]:
    """Load evaluators using enhanced registry supporting both formats."""
    instances: list[BaseEvaluator] = []
    for cfg in configs:
        inst = enhanced_registry.create(cfg)
        if inst is not None:
            instances.append(inst)
    return instances