"""
Custom evaluators for demonstrating the experimentation platform.
This module shows how to create and register your own evaluators.
"""

from exp_platform_cli import BaseEvaluator, EvaluatorOutput, register_evaluator
from exp_platform_cli.models import DataModelRow
import re
import statistics
from typing import Dict, Mapping


@register_evaluator("response_length")
class ResponseLengthEvaluator(BaseEvaluator):
    """Evaluates the length of responses."""
    
    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Evaluate response lengths and provide statistics."""
        lengths = []
        per_row_scores = {}
        
        for row in rows:
            output_text = str(row.data_output) if row.data_output else ""
            length = len(output_text)
            lengths.append(length)
            
            # Score based on reasonable length (1-500 characters gets full score)
            if 1 <= length <= 500:
                score = 1.0
            elif length == 0:
                score = 0.0
            else:
                # Penalize overly long responses
                score = max(0.1, 1.0 - (length - 500) / 1000)
            
            per_row_scores[row.id] = {
                "length": float(length),
                "length_score": score
            }
        
        # Calculate aggregate statistics
        summary = {
            "average_length": statistics.mean(lengths) if lengths else 0.0,
            "median_length": statistics.median(lengths) if lengths else 0.0,
            "min_length": float(min(lengths)) if lengths else 0.0,
            "max_length": float(max(lengths)) if lengths else 0.0,
            "average_length_score": statistics.mean([s["length_score"] for s in per_row_scores.values()]) if per_row_scores else 0.0
        }
        
        return EvaluatorOutput(
            name=self.config.name,
            summary=summary,
            per_row=per_row_scores
        )


@register_evaluator("accuracy_checker")
class AccuracyEvaluator(BaseEvaluator):
    """Evaluates accuracy by comparing output to expected values."""
    
    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Check accuracy against expected outputs."""
        per_row_scores = {}
        correct_count = 0
        total_count = 0
        
        for row in rows:
            output_text = str(row.data_output).strip() if row.data_output else ""
            expected = row.data_input.get("expected", "") if row.data_input else ""
            expected = str(expected).strip()
            
            # Simple exact match
            is_correct = output_text.lower() == expected.lower()
            
            # For math problems, also try to extract numbers
            if not is_correct and expected:
                output_numbers = self._extract_numbers(output_text)
                expected_numbers = self._extract_numbers(expected)
                if output_numbers and expected_numbers:
                    is_correct = output_numbers[0] == expected_numbers[0]
            
            score = 1.0 if is_correct else 0.0
            per_row_scores[row.id] = {
                "exact_match": score,
                "output": output_text,
                "expected": expected
            }
            
            if is_correct:
                correct_count += 1
            total_count += 1
        
        accuracy = correct_count / total_count if total_count > 0 else 0.0
        
        summary = {
            "accuracy": accuracy,
            "correct_count": float(correct_count),
            "total_count": float(total_count)
        }
        
        return EvaluatorOutput(
            name=self.config.name,
            summary=summary,
            per_row=per_row_scores
        )
    
    def _extract_numbers(self, text: str) -> list[float]:
        """Extract numbers from text."""
        numbers = re.findall(r'-?\d+\.?\d*', text)
        return [float(n) for n in numbers if n]


@register_evaluator("sentiment_evaluator")
class SentimentEvaluator(BaseEvaluator):
    """Basic sentiment analysis evaluator."""
    
    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Evaluate sentiment of responses."""
        per_row_scores = {}
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        
        # Simple keyword-based sentiment (in real use, you'd use ML models)
        positive_words = {"good", "great", "excellent", "helpful", "correct", "yes", "right"}
        negative_words = {"bad", "wrong", "error", "incorrect", "no", "fail", "cannot"}
        
        for row in rows:
            output_text = str(row.data_output).lower() if row.data_output else ""
            
            pos_count = sum(1 for word in positive_words if word in output_text)
            neg_count = sum(1 for word in negative_words if word in output_text)
            
            if pos_count > neg_count:
                sentiment = "positive"
                sentiment_score = min(1.0, pos_count / 3)
            elif neg_count > pos_count:
                sentiment = "negative"  
                sentiment_score = max(0.0, 1.0 - neg_count / 3)
            else:
                sentiment = "neutral"
                sentiment_score = 0.5
            
            sentiment_counts[sentiment] += 1
            
            per_row_scores[row.id] = {
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "positive_words": pos_count,
                "negative_words": neg_count
            }
        
        total = len(rows)
        summary = {
            "average_sentiment_score": statistics.mean([s["sentiment_score"] for s in per_row_scores.values()]) if per_row_scores else 0.0,
            "positive_ratio": sentiment_counts["positive"] / total if total > 0 else 0.0,
            "negative_ratio": sentiment_counts["negative"] / total if total > 0 else 0.0,
            "neutral_ratio": sentiment_counts["neutral"] / total if total > 0 else 0.0
        }

        return EvaluatorOutput(
            name=self.config.name,
            summary=summary,
            per_row=per_row_scores
        )
