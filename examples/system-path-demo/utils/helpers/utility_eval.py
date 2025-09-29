"""
Utility evaluator from utils/helpers directory.
"""

from exp_platform_cli import BaseEvaluator, EvaluatorOutput, register_evaluator
from exp_platform_cli.models import DataModelRow
from typing import Dict, Mapping


@register_evaluator("utility_evaluator")
class UtilityEvaluator(BaseEvaluator):
    """Utility evaluator from utils directory."""
    
    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Evaluate utility/usefulness of the response."""
        per_row = {}
        all_scores = []
        total_question_responses = 0
        total_greeting_responses = 0
        
        for row in rows:
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
                total_question_responses += 1
            if has_greeting_response:
                utility_score += 0.3
                total_greeting_responses += 1
            if len(response) > 10:  # Non-trivial response
                utility_score += 0.2
                
            utility_score = min(utility_score, 1.0)
            
            per_row[row.id] = {
                "utility_score": utility_score,
                "has_question_response": 1.0 if has_question_response else 0.0,
                "has_greeting_response": 1.0 if has_greeting_response else 0.0,
                "response_length": len(response)
            }
            all_scores.append(utility_score)
        
        # Calculate summary metrics
        import statistics
        summary = {
            "average_utility": statistics.mean(all_scores) if all_scores else 0.0,
            "question_response_rate": total_question_responses / len(rows) if rows else 0.0,
            "greeting_response_rate": total_greeting_responses / len(rows) if rows else 0.0,
            "total_responses": len(rows)
        }
        
        return EvaluatorOutput(
            name=self.config.name,
            summary=summary,
            per_row=per_row
        )