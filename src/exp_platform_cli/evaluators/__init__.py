"""Evaluator collection used by the experimentation CLI."""

from .base import BaseEvaluator, EvaluatorOutput
from .registry import register_evaluator, registry
from .enhanced_registry import load_evaluators, enhanced_registry

# Import built-in evaluators so they register themselves.
from . import equivalent  # noqa: F401
from . import agent_evaluators  # noqa: F401

# Import agent evaluators for direct access
from .agent_evaluators import (
    ToolCallAccuracyEvaluator,
    ConversationQualityEvaluator,
    SemanticKernelPerformanceEvaluator,
    AgentToAgentCommunicationEvaluator,
)

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
