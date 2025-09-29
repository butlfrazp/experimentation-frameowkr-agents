"""Base class for user-defined processors executed per dataset row."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

from ..models import DataModelRow

ConfigT = TypeVar("ConfigT", bound=BaseModel | dict)


class BaseProcessor(ABC, Generic[ConfigT]):
    """Lightweight base class for processors executed via the CLI."""

    def __init__(self, config: Optional[ConfigT] = None) -> None:
        self.config = config

    @abstractmethod
    def run(self, data_model_row: DataModelRow, **kwargs) -> DataModelRow:
        """Process a row and return the updated ``DataModelRow``."""
