"""
Test evaluator with various problematic metric types to test error handling.
"""

from exp_platform_cli import BaseEvaluator, EvaluatorOutput, register_evaluator
from exp_platform_cli.models import DataModelRow
from typing import Dict, Mapping


@register_evaluator("problematic_evaluator")
class ProblematicEvaluator(BaseEvaluator):
    """Evaluator that produces various problematic metric types for testing."""
    
    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Return metrics with various problematic types."""
        per_row = {}
        
        for i, row in enumerate(rows):
            per_row[row.id] = {
                "valid_float": 0.85,
                "valid_int": 42,
                "string_number": "0.75",
                "string_text": "high_quality",
                "boolean_true": True,
                "boolean_false": False,
                "none_value": None,
                "empty_string": "",
                "whitespace_string": "   ",
                "list_value": [1, 2, 3],
                "dict_value": {"score": 0.9},
                "infinity": float('inf'),
                "nan": float('nan'),
            }
        
        # Summary with similar problematic types
        summary = {
            "average_score": 0.78,
            "total_processed": len(rows),
            "status": "completed",
            "has_errors": False,
            "error_rate": None,
            "categories": ["good", "bad", "ugly"],
            "config": {"threshold": 0.5},
        }
        
        return EvaluatorOutput(
            name=self.config.name,
            summary=summary,
            per_row=per_row
        )