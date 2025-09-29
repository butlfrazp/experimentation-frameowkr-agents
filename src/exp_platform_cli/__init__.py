"""Experimentation platform CLI package."""

from importlib import metadata

from .evaluators import BaseEvaluator, EvaluatorOutput, load_evaluators, register_evaluator
from .logger import SUCCESS_LEVEL, ExperimentLogger, get_logger
from .models import (
    DataModel,
    DataModelRow,
    DataModelRowError,
    DatasetModel,
    DataType,
    EvaluatorConfig,
    ExperimentConfig,
    ModuleExecutableConfig,
)
from .orchestrator import Orchestrator
from .services import (
    CloudEvaluationService,
    ConfigLoader,
    DatasetService,
    EvaluationService,
    LocalEvaluationService,
)

__all__ = [
    "__version__",
    "ExperimentLogger",
    "get_logger",
    "SUCCESS_LEVEL",
    "BaseEvaluator",
    "EvaluatorOutput",
    "load_evaluators",
    "register_evaluator",
    "Orchestrator",
    "ConfigLoader",
    "DatasetService",
    "EvaluationService",
    "LocalEvaluationService",
    "CloudEvaluationService",
    "DataModel",
    "DataModelRow",
    "DataModelRowError",
    "DatasetModel",
    "DataType",
    "EvaluatorConfig",
    "ExperimentConfig",
    "ModuleExecutableConfig",
    "load_evaluators",
    "register_evaluator",
    "BaseEvaluator",
    "EvaluatorOutput",
]


def _load_version() -> str:
    try:
        return metadata.version("exp-platform-cli")
    except metadata.PackageNotFoundError:
        return "0.0.0"


__version__ = _load_version()
