"""Evaluator collection used by the experimentation CLI."""

# Import built-in evaluators so they register themselves.
from . import (
    agent_evaluators,  # noqa: F401
    equivalent,  # noqa: F401
)

# Import agent evaluators for direct access
from .agent_evaluators import (
    AgentToAgentCommunicationEvaluator,
    ConversationQualityEvaluator,
    SemanticKernelPerformanceEvaluator,
    ToolCallAccuracyEvaluator,
)
from .base import BaseEvaluator, EvaluatorOutput
from .enhanced_registry import enhanced_registry, load_evaluators
from .registry import register_evaluator, registry

__all__ = [
    "BaseEvaluator",
    "EvaluatorOutput",
    "load_evaluators",
    "register_evaluator",
    "registry",
    "enhanced_registry",
    "ToolCallAccuracyEvaluator",
    "ConversationQualityEvaluator",
    "SemanticKernelPerformanceEvaluator",
    "AgentToAgentCommunicationEvaluator",
]
