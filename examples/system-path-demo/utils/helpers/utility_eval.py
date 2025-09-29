"""
Utility evaluator from utils/helpers directory.
"""

from exp_platform_cli import BaseEvaluator, EvaluatorOutput, register_evaluator
from exp_platform_cli.models import DataModelRow
from typing import Dict, Mapping


@register_evaluator("utility_evaluator")
class UtilityEvaluator(BaseEvaluator):
    """Utility evaluator from utils directory."""
    
    def evaluate(self, row: DataModelRow) -> EvaluatorOutput:
        """Evaluate utility/usefulness of the response."""
        response = row.data_output or ""
        input_text = row.data_input.get("input", "")
        
        # Simple utility metrics
        has_question_response = "?" in input_text and len(response) > 0
        has_greeting_response = any(word in input_text.lower() for word in ["hello", "hi", "hey"]) and \
                               any(word in response.lower() for word in ["hello", "hi", "hey"])
        
        # Calculate utility score
        utility_score = 0.0
        if has_question_response:
            utility_score += 0.5
        if has_greeting_response:
            utility_score += 0.3
        if len(response) > 10:  # Non-trivial response
            utility_score += 0.2
            
        utility_score = min(utility_score, 1.0)
        
        metrics = {
            "utility_score": utility_score,
            "has_question_response": has_question_response,
            "has_greeting_response": has_greeting_response,
            "response_length": len(response)
        }
        
        return EvaluatorOutput(
            evaluator_id=self.evaluator_id,
            row_id=row.id,
            metrics=metrics,
            score=utility_score,
            passed=utility_score > 0.4
        )