"""Base evaluator interfaces used by the experimentation CLI."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Mapping

from ..models import DataModelRow, EvaluatorConfig


@dataclass(slots=True)
class EvaluatorOutput:
    """Aggregated result produced by an evaluator."""

    name: str
    summary: Mapping[str, float]
    per_row: Dict[str, Mapping[str, float]] = field(default_factory=dict)


class BaseEvaluator(ABC):
    """Abstract base class for evaluators."""

    def __init__(self, config: EvaluatorConfig) -> None:
        self.config = config

    @abstractmethod
    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Evaluate the provided rows and return aggregated metrics."""