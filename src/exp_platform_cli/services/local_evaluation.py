"""Minimal local evaluation implementation for offline experiments."""

from __future__ import annotations

import json
import os
import traceback
from pathlib import Path
from typing import Iterable, Sequence, Any, Dict, Union

from ..evaluators import load_evaluators
from ..models import (
    DataModelRow,
    EvaluationResult,
    EvaluatorConfig,
    ExperimentConfig,
)
from ..constants import PROJECT_ROOT
from ..utils import ensure_directories
from ..logger import get_logger
from .evaluation_base import EvaluationService

logger = get_logger(__name__)


class LocalEvaluationService(EvaluationService):
    """Persist execution results locally for later inspection."""

    def evaluate(
        self,
        *,
        experiment_id: str,
        dataset_name: str,
        dataset_version: str,
        data_id: str | None,
        config: ExperimentConfig,
        evaluators: Sequence[EvaluatorConfig],
        rows: Iterable[DataModelRow] | None = None,
    ) -> None:
        ensure_directories()
        
        # Use configured output path if available, otherwise fallback to environment/default
        if config.output_path:
            artifact_root = Path(config.output_path).expanduser().resolve()
        else:
            artifact_root_env = os.getenv("EXP_CLI_ARTIFACT_ROOT")
            if artifact_root_env:
                artifact_root = Path(artifact_root_env).expanduser().resolve()
            else:
                artifact_root = PROJECT_ROOT / "artifacts"
        
        # Structure: output_path/dataset_name/dataset_version/experiment_id
        output_dir = artifact_root / dataset_name / dataset_version / experiment_id
        output_dir.mkdir(parents=True, exist_ok=True)

        if rows is None:
            rows = []
        rows_list = list(rows)

        evaluator_instances = load_evaluators(evaluators)
        metrics_summary: dict[str, dict[str, float]] = {}
        evaluation_errors: dict[str, dict[str, Any]] = {}
        non_numeric_metrics: dict[str, dict[str, Any]] = {}

        for evaluator in evaluator_instances:
            evaluator_name = evaluator.config.name
            logger.debug(f"Running evaluator: {evaluator_name}")
            
            try:
                result = evaluator.evaluate(rows_list)
                logger.debug(f"Evaluator {evaluator_name} completed successfully")
                
                # Process summary metrics with error handling
                summary_metrics = {}
                for metric_name, metric_value in result.summary.items():
                    numeric_value, error = self._convert_to_numeric(
                        metric_value, f"{evaluator_name}.summary.{metric_name}"
                    )
                    if error:
                        evaluation_errors.setdefault(evaluator_name, {}).setdefault("summary_errors", {})[metric_name] = error
                        # Store non-numeric summary in separate bucket
                        non_numeric_metrics.setdefault(evaluator_name, {}).setdefault("summary", {})[metric_name] = metric_value
                    else:
                        summary_metrics[metric_name] = numeric_value
                
                metrics_summary[result.name] = summary_metrics
                
                # Process per-row metrics with comprehensive error handling
                for row in rows_list:
                    metrics = result.per_row.get(row.id)
                    if not metrics:
                        continue
                        
                    for metric_name, metric_value in metrics.items():
                        key = f"{result.name}:{metric_name}"
                        
                        # Convert to numeric with detailed error tracking
                        numeric_value, error = self._convert_to_numeric(
                            metric_value, f"{evaluator_name}.{row.id}.{metric_name}"
                        )
                        
                        if error:
                            # Track conversion errors
                            evaluation_errors.setdefault(evaluator_name, {}).setdefault("per_row_errors", {}).setdefault(row.id, {})[metric_name] = error
                            
                            # Store non-numeric metrics in row metadata under evaluator namespace
                            mm = row.metadata.setdefault("non_numeric_metrics", {})
                            ev_bucket = mm.setdefault(result.name, {})
                            ev_bucket[metric_name] = metric_value
                            logger.debug(f"Stored non-numeric metric {key}: {metric_value} ({type(metric_value).__name__})")
                        else:
                            # Store numeric metric as evaluation result
                            row.evaluation_results[key] = EvaluationResult(
                                metric_name=key,
                                metric_value=numeric_value,
                                metadata={"evaluator": result.name},
                            )
                            logger.debug(f"Stored numeric metric {key}: {numeric_value}")
            
            except Exception as e:
                # Catch and log evaluator execution failures
                error_msg = f"Evaluator '{evaluator_name}' failed: {str(e)}"
                logger.error(error_msg)
                logger.debug(f"Full traceback for {evaluator_name}: {traceback.format_exc()}")
                
                evaluation_errors.setdefault(evaluator_name, {})["execution_error"] = {
                    "error": str(e),
                    "type": type(e).__name__,
                    "traceback": traceback.format_exc()
                }
                
                # Add empty summary to maintain consistency
                metrics_summary[evaluator_name] = {}
        
        # Log evaluation summary
        successful_evaluators = len(evaluator_instances) - len([e for e in evaluation_errors.values() if "execution_error" in e])
        logger.info(f"Evaluation completed: {successful_evaluators}/{len(evaluator_instances)} evaluators successful")
        
        if evaluation_errors:
            logger.warning(f"Evaluation issues found: {len(evaluation_errors)} evaluators had errors")
            for evaluator_name, errors in evaluation_errors.items():
                if "execution_error" in errors:
                    logger.error(f"  {evaluator_name}: Execution failed - {errors['execution_error']['error']}")
                if "summary_errors" in errors:
                    logger.debug(f"  {evaluator_name}: {len(errors['summary_errors'])} summary metric conversion errors")
                if "per_row_errors" in errors:
                    total_row_errors = sum(len(row_errors) for row_errors in errors["per_row_errors"].values())
                    logger.debug(f"  {evaluator_name}: {total_row_errors} per-row metric conversion errors")

        results_path = output_dir / "rows.jsonl"
        with results_path.open("w", encoding="utf-8") as handle:
            for row in rows_list:
                handle.write(row.model_dump_json() + "\n")

        metadata_path = output_dir / "experiment_config.json"
        metadata_path.write_text(
            config.model_dump_json(indent=2),
            encoding="utf-8",
        )

        evaluators_path = output_dir / "evaluators.json"
        evaluators_path.write_text(
            json.dumps([ev.model_dump() for ev in evaluators], indent=2),
            encoding="utf-8",
        )

        metrics_path = output_dir / "local_metrics_summary.json"
        metrics_path.write_text(
            json.dumps(metrics_summary, indent=2),
            encoding="utf-8",
        )
        
        # Save evaluation errors and non-numeric metrics for debugging
        if evaluation_errors:
            errors_path = output_dir / "evaluation_errors.json"
            errors_path.write_text(
                json.dumps(evaluation_errors, indent=2),
                encoding="utf-8",
            )
            logger.debug(f"Evaluation errors saved to: {errors_path}")
        
        if non_numeric_metrics:
            non_numeric_path = output_dir / "non_numeric_metrics.json"
            non_numeric_path.write_text(
                json.dumps(non_numeric_metrics, indent=2),
                encoding="utf-8",
            )
            logger.debug(f"Non-numeric metrics saved to: {non_numeric_path}")

    def _convert_to_numeric(self, value: Any, context: str) -> tuple[float, str | None]:
        """
        Convert a value to numeric (float) with comprehensive error handling.
        
        Args:
            value: The value to convert
            context: Description of where this value came from (for error reporting)
            
        Returns:
            Tuple of (numeric_value, error_message). If conversion succeeds,
            error_message is None. If conversion fails, numeric_value is 0.0.
        """
        # Handle None values
        if value is None:
            return 0.0, f"None value converted to 0.0 in {context}"
        
        # Handle already numeric values
        if isinstance(value, (int, float)):
            if isinstance(value, bool):  # bool is subclass of int, handle specially
                return float(value), f"Boolean {value} converted to {float(value)} in {context}"
            return float(value), None
        
        # Handle string values
        if isinstance(value, str):
            # Handle empty strings
            if not value.strip():
                return 0.0, f"Empty string converted to 0.0 in {context}"
            
            # Try to convert string to float
            try:
                return float(value), None
            except (ValueError, TypeError) as e:
                return 0.0, f"String '{value}' could not be converted to float in {context}: {e}"
        
        # Handle boolean values explicitly (in case not caught above)
        if isinstance(value, bool):
            return float(value), f"Boolean {value} converted to {float(value)} in {context}"
        
        # Handle other types
        try:
            numeric_val = float(value)
            return numeric_val, f"Value {value} ({type(value).__name__}) converted to {numeric_val} in {context}"
        except (TypeError, ValueError) as e:
            return 0.0, f"Value {value} ({type(value).__name__}) could not be converted to float in {context}: {e}"
