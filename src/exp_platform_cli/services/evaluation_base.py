"""Abstract interface for evaluation implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Sequence

from ..models import DataModelRow, EvaluatorConfig, ExperimentConfig


class EvaluationService(ABC):  # pragma: no cover - interface only
    """Define the contract for running evaluations against row outputs."""

    @abstractmethod
    def evaluate(
        self,
        *,
        experiment_id: str,
        dataset_name: str,
        dataset_version: str,
        data_id: str | None,
        config: ExperimentConfig,
        evaluators: Sequence[EvaluatorConfig],
        rows: Iterable[DataModelRow] | None = None,
    ) -> None:
        """Evaluate execution results.

        ``data_id`` references a remote dataset when available. Local
        implementations may ignore it and instead use ``rows``.
        """
