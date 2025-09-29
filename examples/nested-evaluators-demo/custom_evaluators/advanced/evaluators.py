"""
Advanced evaluators in a nested subdirectory.
"""

import re
import statistics

from exp_platform_cli import BaseEvaluator, EvaluatorOutput, register_evaluator
from exp_platform_cli.models import DataModelRow


@register_evaluator("advanced_quality")
class AdvancedQualityEvaluator(BaseEvaluator):
    """Advanced quality assessment evaluator."""

    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Evaluate response quality with multiple metrics."""
        per_row_scores = {}
        quality_scores = []

        for row in rows:
            output_text = str(row.data_output) if row.data_output else ""

            # Multiple quality metrics
            word_count = len(output_text.split())
            sentence_count = len(re.findall(r"[.!?]+", output_text))
            has_numbers = bool(re.search(r"\d+", output_text))
            proper_capitalization = output_text and output_text[0].isupper()

            # Calculate quality score (0-1)
            quality_score = sum(
                [
                    min(word_count / 10, 1.0) * 0.3,  # Word count contribution
                    min(sentence_count / 3, 1.0) * 0.2,  # Sentence structure
                    0.2 if has_numbers else 0.0,  # Contains numbers
                    0.3 if proper_capitalization else 0.0,  # Proper formatting
                ]
            )

            quality_scores.append(quality_score)

            per_row_scores[row.id] = {
                "quality_score": quality_score,
                "word_count": float(word_count),
                "sentence_count": float(sentence_count),
                "has_numbers": 1.0 if has_numbers else 0.0,
                "proper_capitalization": 1.0 if proper_capitalization else 0.0,
            }

        summary = {
            "average_quality": statistics.mean(quality_scores) if quality_scores else 0.0,
            "min_quality": min(quality_scores) if quality_scores else 0.0,
            "max_quality": max(quality_scores) if quality_scores else 0.0,
            "quality_std": statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0.0,
        }

        return EvaluatorOutput(name=self.config.name, summary=summary, per_row=per_row_scores)


@register_evaluator("advanced_coherence")
class AdvancedCoherenceEvaluator(BaseEvaluator):
    """Evaluate response coherence and structure."""

    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Evaluate response coherence."""
        per_row_scores = {}
        coherence_scores = []

        keywords_positive = {"correct", "accurate", "good", "right", "proper", "valid"}
        keywords_negative = {"wrong", "incorrect", "error", "bad", "invalid", "false"}

        for row in rows:
            output_text = str(row.data_output).lower() if row.data_output else ""

            # Coherence metrics
            positive_indicators = sum(1 for word in keywords_positive if word in output_text)
            negative_indicators = sum(1 for word in keywords_negative if word in output_text)

            # Check for logical structure
            has_logical_flow = bool(
                re.search(r"\b(first|then|next|finally|therefore|because|since)\b", output_text)
            )
            consistent_tone = not bool(
                re.search(r"[.!?]\s*[a-z]", output_text)
            )  # Consistent capitalization

            # Calculate coherence score
            coherence_score = sum(
                [
                    0.3 if positive_indicators > negative_indicators else 0.1,
                    0.3 if has_logical_flow else 0.0,
                    0.4 if consistent_tone else 0.2,
                ]
            )

            coherence_scores.append(coherence_score)

            per_row_scores[row.id] = {
                "coherence_score": coherence_score,
                "positive_indicators": float(positive_indicators),
                "negative_indicators": float(negative_indicators),
                "has_logical_flow": 1.0 if has_logical_flow else 0.0,
                "consistent_tone": 1.0 if consistent_tone else 0.0,
            }

        summary = {
            "average_coherence": statistics.mean(coherence_scores) if coherence_scores else 0.0,
            "coherent_responses": sum(1 for s in coherence_scores if s > 0.5),
            "total_responses": len(coherence_scores),
        }

        return EvaluatorOutput(name=self.config.name, summary=summary, per_row=per_row_scores)
