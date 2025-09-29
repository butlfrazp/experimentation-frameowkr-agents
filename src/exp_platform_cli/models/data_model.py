"""Canonical in-memory representations of experimental datasets and rows."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .data_types import DataType


class AgentFramework(str, Enum):
    """Supported agent frameworks."""

    SEMANTIC_KERNEL = "semantic_kernel"
    LANGCHAIN = "langchain"
    AUTOGEN = "autogen"
    UNKNOWN = "unknown"


class ToolCallStatus(str, Enum):
    """Status of a tool call execution."""

    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class AgentRole(str, Enum):
    """Role of an agent in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    FUNCTION = "function"


class DataModelRowError(BaseModel):
    """Describe a structured error encountered while processing a row."""

    message: str
    code: int = 0


class ToolCallDetails(BaseModel):
    """Details of a tool/function call made by an agent."""

    tool_name: str
    function_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: Any = None
    status: ToolCallStatus = ToolCallStatus.SUCCESS
    execution_time_ms: float | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentMessage(BaseModel):
    """A single message in an agent conversation."""

    role: AgentRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str | None = None
    tool_calls: list[ToolCallDetails] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SemanticKernelTrace(BaseModel):
    """Semantic Kernel specific execution trace."""

    kernel_id: str | None = None
    plugin_name: str | None = None
    function_name: str | None = None
    invocation_id: str | None = None
    execution_settings: dict[str, Any] = Field(default_factory=dict)
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    model_name: str | None = None
    temperature: float | None = None
    filters_applied: list[str] = Field(default_factory=list)
    planners_used: list[str] = Field(default_factory=list)


class AgentInteraction(BaseModel):
    """Complete agent interaction including messages, tool calls, and framework data."""

    interaction_id: str
    framework: AgentFramework = AgentFramework.UNKNOWN
    messages: list[AgentMessage] = Field(default_factory=list)
    total_tokens: int | None = None
    total_cost: float | None = None
    duration_ms: float | None = None
    semantic_kernel_trace: SemanticKernelTrace | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DatasetModel(BaseModel):
    """Identify a dataset used during experimentation."""

    name: str
    version: str
    type: DataType = DataType.UNKNOWN


class EvaluationResult(BaseModel):
    """Capture the score emitted by an evaluator for a row."""

    metric_name: str
    metric_value: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class DataModelRow(BaseModel):
    """A single piece of input data alongside outputs and metadata."""

    id: str
    data_input: dict[str, Any] = Field(default_factory=dict)
    expected_output: Any | None = None
    data_output: Any | None = None
    error: DataModelRowError | None = None
    evaluation_results: dict[str, EvaluationResult] = Field(default_factory=dict)
    # Agent evaluation fields
    agent_interaction: AgentInteraction | None = None
    tool_calls: list[ToolCallDetails] = Field(default_factory=list)
    conversation_history: list[AgentMessage] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DataModel(BaseModel):
    """Container for all rows tied to a specific dataset."""

    dataset: DatasetModel
    rows: list[DataModelRow]
    metadata: dict[str, Any] = Field(default_factory=dict)
