"""Abstract executable wrapper used to run processors for each row."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import DataModelRow


class BaseExecutable(ABC):
    """Execute a configured workload for a single ``DataModelRow``."""

    def __init__(self, row: DataModelRow, config):
        self._row = row
        self._config = config

    @abstractmethod
    def execute(self, **kwargs) -> DataModelRow:
        """Run the executable and return the resulting row."""
