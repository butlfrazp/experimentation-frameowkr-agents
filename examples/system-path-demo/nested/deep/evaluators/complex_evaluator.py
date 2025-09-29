"""
Deep nested evaluator that can be loaded via python_path configuration.
"""

from exp_platform_cli import BaseEvaluator, EvaluatorOutput, register_evaluator
from exp_platform_cli.models import DataModelRow
from typing import Dict, Mapping


@register_evaluator("deep_nested_evaluator")
class DeepNestedEvaluator(BaseEvaluator):
    """Evaluator from deeply nested directory structure."""
    
    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Evaluate response complexity from deep nested location."""
        per_row = {}
        all_scores = []
        
        for row in rows:
            response = row.data_output or ""
            
            # Count different complexity metrics
            word_count = len(response.split())
            char_count = len(response)
            sentence_count = response.count('.') + response.count('!') + response.count('?')
            
            # Calculate complexity score
            complexity_score = (word_count * 0.3 + char_count * 0.01 + sentence_count * 0.5) / 10
            complexity_score = min(complexity_score, 1.0)  # Cap at 1.0
            
            per_row[row.id] = {
                "complexity_score": complexity_score,
                "word_count": word_count,
                "character_count": char_count,
                "sentence_count": sentence_count
            }
            all_scores.append(complexity_score)
        
        # Calculate summary metrics
        import statistics
        summary = {
            "average_complexity": statistics.mean(all_scores) if all_scores else 0.0,
            "max_complexity": max(all_scores) if all_scores else 0.0,
            "min_complexity": min(all_scores) if all_scores else 0.0,
            "complexity_std": statistics.stdev(all_scores) if len(all_scores) > 1 else 0.0
        }
        
        return EvaluatorOutput(
            name=self.config.name,
            summary=summary,
            per_row=per_row
        )