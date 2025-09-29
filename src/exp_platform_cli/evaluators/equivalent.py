"""Simple equivalence evaluator for local experimentation."""

from __future__ import annotations

from typing import Dict

from ..logger import get_logger
from ..models import DataModelRow
from .base import BaseEvaluator, EvaluatorOutput
from .registry import register_evaluator

log = get_logger(__name__)


@register_evaluator("equivalent")
class EquivalentEvaluator(BaseEvaluator):
    """Compare ``data_output`` and ``expected_output`` for each row."""

    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Evaluate each row individually for equivalence."""
        per_row: Dict[str, Dict[str, float]] = {}
        total_matches = 0
        
        for row in rows:
            row_result = self._evaluate_single_row(row)
            per_row[row.id] = row_result
            total_matches += row_result.get("match", 0.0)

        # Calculate summary metrics
        accuracy = (total_matches / len(rows)) if rows else 0.0
        log.debug(
            "EquivalentEvaluator summary accuracy=%s for %s rows",
            accuracy,
            len(rows),
        )
        
        return EvaluatorOutput(
            name=self.config.name,
            summary={"accuracy": accuracy, "match_rate": accuracy},
            per_row=per_row,
        )
    
    def _evaluate_single_row(self, row: DataModelRow) -> Dict[str, float]:
        """Evaluate a single row for equivalence - row-by-row processing."""
        expected = row.expected_output
        actual = row.data_output
        
        # Handle different data types consistently
        if expected is None and actual is None:
            match = 1.0
        elif expected is None or actual is None:
            match = 0.0
        else:
            # Convert to strings for comparison to handle mixed types
            expected_str = str(expected).strip().lower()
            actual_str = str(actual).strip().lower()
            match = float(1.0 if expected_str == actual_str else 0.0)
        
        return {
            "match": match,
            "score": match,  # Provide score for consistency with foundry evaluators
        }
