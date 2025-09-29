"""
Basic evaluators in a nested subdirectory.
"""

import statistics

from exp_platform_cli import BaseEvaluator, EvaluatorOutput, register_evaluator
from exp_platform_cli.models import DataModelRow


@register_evaluator("basic_length")
class BasicLengthEvaluator(BaseEvaluator):
    """Simple length evaluator from nested location."""

    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Evaluate basic response lengths."""
        lengths = []
        per_row_scores = {}

        for row in rows:
            output_text = str(row.data_output) if row.data_output else ""
            length = len(output_text)
            lengths.append(length)

            per_row_scores[row.id] = {
                "length": float(length),
                "is_reasonable": 1.0 if 5 <= length <= 200 else 0.0,
            }

        summary = {
            "average_length": statistics.mean(lengths) if lengths else 0.0,
            "total_responses": float(len(rows)),
        }

        return EvaluatorOutput(name=self.config.name, summary=summary, per_row=per_row_scores)


@register_evaluator("basic_completeness")
class BasicCompletenessEvaluator(BaseEvaluator):
    """Check if responses are complete."""

    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Evaluate response completeness."""
        per_row_scores = {}
        complete_count = 0

        for row in rows:
            output_text = str(row.data_output) if row.data_output else ""

            # Simple completeness check
            is_complete = bool(output_text and len(output_text.strip()) > 0)
            if is_complete:
                complete_count += 1

            per_row_scores[row.id] = {
                "is_complete": 1.0 if is_complete else 0.0,
                "has_content": 1.0 if output_text.strip() else 0.0,
            }

        summary = {
            "completeness_rate": complete_count / len(rows) if rows else 0.0,
            "complete_count": float(complete_count),
            "total_count": float(len(rows)),
        }

        return EvaluatorOutput(name=self.config.name, summary=summary, per_row=per_row_scores)
