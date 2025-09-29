"""
Deep nested evaluator that can be loaded via python_path configuration.
"""

from exp_platform_cli import BaseEvaluator, EvaluatorOutput, register_evaluator
from exp_platform_cli.models import DataModelRow
from typing import Dict, Mapping


@register_evaluator("deep_nested_evaluator")
class DeepNestedEvaluator(BaseEvaluator):
    """Evaluator from deeply nested directory structure."""
    
    def evaluate(self, row: DataModelRow) -> EvaluatorOutput:
        """Evaluate response complexity from deep nested location."""
        response = row.data_output or ""
        
        # Count different complexity metrics
        word_count = len(response.split())
        char_count = len(response)
        sentence_count = response.count('.') + response.count('!') + response.count('?')
        
        # Calculate complexity score
        complexity_score = (word_count * 0.3 + char_count * 0.01 + sentence_count * 0.5) / 10
        complexity_score = min(complexity_score, 1.0)  # Cap at 1.0
        
        metrics = {
            "complexity_score": complexity_score,
            "word_count": word_count,
            "character_count": char_count,
            "sentence_count": sentence_count
        }
        
        return EvaluatorOutput(
            evaluator_id=self.evaluator_id,
            row_id=row.id,
            metrics=metrics,
            score=complexity_score,
            passed=complexity_score > 0.3
        )