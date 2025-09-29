"""Pydantic models describing experiment configuration files."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Dict, List, Literal, Union

from pydantic import BaseModel, Field
from pydantic import ConfigDict
from pydantic.functional_validators import field_validator


class ExecutableType(str, Enum):
    """Supported execution backends for running dataset rows."""

    MODULE = "module"
    UNKNOWN = "unknown"


class EvaluatorConfig(BaseModel):
    """Describe an evaluator to run after execution."""

    id: str
    name: str
    data_mapping: Dict[str, str] = Field(default_factory=dict)


class DatasetConfigDetails(BaseModel):
    """Dataset specific metadata used when loading rows."""

    expected_output_field: str | None = None


class DatasetConfig(BaseModel):
    """Describe which dataset should be loaded for an experiment."""

    name: str
    version: str
    config: DatasetConfigDetails = Field(default_factory=DatasetConfigDetails)


class BaseExecutableConfig(BaseModel):
    """Base configuration shared by all executable variants."""

    type: ExecutableType

    def run_descriptor(self) -> str:  # pragma: no cover - simple formatting
        return f"Executable(type={self.type})"


class ModuleExecutableConfig(BaseExecutableConfig):
    """Load and execute a Python callable from a module or package."""

    type: Literal["module"] = "module"
    path: str
    processor: str
    config: Dict[str, Union[str, int, float, bool]] = Field(
        default_factory=dict
    )
    python_path: List[str] = Field(
        default_factory=list,
        description="Additional directories to add to sys.path for module loading"
    )

    def run_descriptor(self) -> str:  # pragma: no cover - simple formatting
        return f"Module(path={self.path}, processor={self.processor})"


class UnknownExecutableConfig(BaseExecutableConfig):
    """Fallback when the configuration references an unknown type."""

    type: Literal["unknown"] = "unknown"


ExecutableConfig = Annotated[
    Union[ModuleExecutableConfig, UnknownExecutableConfig],
    Field(discriminator="type"),
]


class ExperimentConfig(BaseModel):
    """Top-level configuration for an experiment run."""

    model_config = ConfigDict(populate_by_name=True)

    dataset: DatasetConfig
    executable: ExecutableConfig
    evaluators: List[EvaluatorConfig] = Field(
        default_factory=list, alias="evaluation"
    )
    local_mode: bool = False
    output_path: str | None = Field(
        default=None, 
        description="Directory path where experiment results will be stored. "
                   "Results are organized by dataset name and version within this path."
    )

    @property
    def evaluation(self) -> List[EvaluatorConfig]:  # pragma: no cover
        return self.evaluators

    @field_validator("executable", mode="before")
    @classmethod
    def _coerce_executable(cls, value):  # pragma: no cover - simple coercion
        if isinstance(value, dict) and "type" not in value:
            value = {**value, "type": ExecutableType.UNKNOWN.value}
        return value

    def describe(self) -> str:  # pragma: no cover - string formatting helper
        return (
            "Experiment(dataset="
            f"{self.dataset.name}:{self.dataset.version}, "
            f"exec={self.executable.run_descriptor()})"
        )
