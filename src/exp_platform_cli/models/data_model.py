"""Canonical in-memory representations of experimental datasets and rows."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

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
    arguments: Dict[str, Any] = Field(default_factory=dict)
    result: Any = None
    status: ToolCallStatus = ToolCallStatus.SUCCESS
    execution_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentMessage(BaseModel):
    """A single message in an agent conversation."""
    
    role: AgentRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: Optional[str] = None
    tool_calls: List[ToolCallDetails] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SemanticKernelTrace(BaseModel):
    """Semantic Kernel specific execution trace."""
    
    kernel_id: Optional[str] = None
    plugin_name: Optional[str] = None
    function_name: Optional[str] = None
    invocation_id: Optional[str] = None
    execution_settings: Dict[str, Any] = Field(default_factory=dict)
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    filters_applied: List[str] = Field(default_factory=list)
    planners_used: List[str] = Field(default_factory=list)


class AgentInteraction(BaseModel):
    """Complete agent interaction including messages, tool calls, and framework data."""
    
    interaction_id: str
    framework: AgentFramework = AgentFramework.UNKNOWN
    messages: List[AgentMessage] = Field(default_factory=list)
    total_tokens: Optional[int] = None
    total_cost: Optional[float] = None
    duration_ms: Optional[float] = None
    semantic_kernel_trace: Optional[SemanticKernelTrace] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DatasetModel(BaseModel):
    """Identify a dataset used during experimentation."""

    name: str
    version: str
    type: DataType = DataType.UNKNOWN


class EvaluationResult(BaseModel):
    """Capture the score emitted by an evaluator for a row."""

    metric_name: str
    metric_value: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DataModelRow(BaseModel):
    """A single piece of input data alongside outputs and metadata."""

    id: str
    data_input: Dict[str, Any] = Field(default_factory=dict)
    expected_output: Any | None = None
    data_output: Any | None = None
    error: DataModelRowError | None = None
    evaluation_results: Dict[str, EvaluationResult] = Field(
        default_factory=dict
    )
    # Agent evaluation fields
    agent_interaction: Optional[AgentInteraction] = None
    tool_calls: List[ToolCallDetails] = Field(default_factory=list)
    conversation_history: List[AgentMessage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DataModel(BaseModel):
    """Container for all rows tied to a specific dataset."""

    dataset: DatasetModel
    rows: List[DataModelRow]
    metadata: Dict[str, Any] = Field(default_factory=dict)
