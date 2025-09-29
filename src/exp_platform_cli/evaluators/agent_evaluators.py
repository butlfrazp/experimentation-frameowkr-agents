"""Agent evaluation evaluators for Semantic Kernel interactions."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..models import DataModelRow, EvaluationResult, ToolCallStatus, AgentRole
from .base import BaseEvaluator, EvaluatorOutput


class ToolCallAccuracyEvaluator(BaseEvaluator):
    """Evaluate the accuracy and success rate of tool calls."""

    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Evaluate tool call accuracy across multiple rows."""
        per_row_results = {}
        total_accuracy = 0.0
        total_calls = 0
        successful_calls = 0
        
        for row in rows:
            result = self._evaluate_single_row(row)
            per_row_results[row.id] = {
                "tool_call_accuracy": result.metric_value,
                "total_calls": result.metadata.get("total_calls", 0),
                "successful_calls": result.metadata.get("successful_calls", 0)
            }
            
            total_calls += result.metadata.get("total_calls", 0)
            successful_calls += result.metadata.get("successful_calls", 0)
        
        overall_accuracy = successful_calls / total_calls if total_calls > 0 else 1.0
        
        return EvaluatorOutput(
            name="tool_call_accuracy",
            summary={
                "accuracy": overall_accuracy,
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": total_calls - successful_calls
            },
            per_row=per_row_results
        )

    def _evaluate_single_row(self, row: DataModelRow) -> EvaluationResult:
        """Evaluate tool call accuracy."""
        if not row.tool_calls:
            return EvaluationResult(
                metric_name="tool_call_accuracy",
                metric_value=1.0,  # No tool calls means perfect accuracy
                metadata={"reason": "no_tool_calls", "total_calls": 0}
            )
        
        successful_calls = sum(
            1 for call in row.tool_calls 
            if call.status == ToolCallStatus.SUCCESS
        )
        total_calls = len(row.tool_calls)
        accuracy = successful_calls / total_calls if total_calls > 0 else 1.0
        
        # Calculate additional metrics
        failed_calls = sum(
            1 for call in row.tool_calls
            if call.status == ToolCallStatus.FAILED
        )
        timeout_calls = sum(
            1 for call in row.tool_calls
            if call.status == ToolCallStatus.TIMEOUT
        )
        cancelled_calls = sum(
            1 for call in row.tool_calls
            if call.status == ToolCallStatus.CANCELLED
        )
        
        # Analyze tool usage patterns
        tools_used = set(call.tool_name for call in row.tool_calls)
        functions_used = set(f"{call.tool_name}.{call.function_name}" for call in row.tool_calls)
        
        return EvaluationResult(
            metric_name="tool_call_accuracy",
            metric_value=accuracy,
            metadata={
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": failed_calls,
                "timeout_calls": timeout_calls,
                "cancelled_calls": cancelled_calls,
                "unique_tools": len(tools_used),
                "unique_functions": len(functions_used),
                "tools_used": list(tools_used),
                "functions_used": list(functions_used),
                "average_execution_time_ms": self._calculate_avg_execution_time(row.tool_calls)
            }
        )

    def _calculate_avg_execution_time(self, tool_calls: List) -> Optional[float]:
        """Calculate average execution time for tool calls."""
        times = [
            call.execution_time_ms for call in tool_calls
            if call.execution_time_ms is not None
        ]
        return sum(times) / len(times) if times else None


class ConversationQualityEvaluator(BaseEvaluator):
    """Evaluate the quality of agent conversations."""

    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Evaluate conversation quality across multiple rows."""
        per_row_results = {}
        total_quality = 0.0
        total_messages = 0
        
        for row in rows:
            result = self._evaluate_single_row(row)
            per_row_results[row.id] = {
                "conversation_quality": result.metric_value,
                "message_count": result.metadata.get("total_messages", 0),
                "balance_score": result.metadata.get("balance_score", 0.0)
            }
            
            total_quality += result.metric_value
            total_messages += result.metadata.get("total_messages", 0)
        
        avg_quality = total_quality / len(rows) if rows else 0.0
        
        return EvaluatorOutput(
            name="conversation_quality",
            summary={
                "average_quality": avg_quality,
                "total_conversations": len(rows),
                "total_messages": total_messages,
                "avg_messages_per_conversation": total_messages / len(rows) if rows else 0.0
            },
            per_row=per_row_results
        )

    def _evaluate_single_row(self, row: DataModelRow) -> EvaluationResult:
        """Evaluate conversation quality."""
        if not row.conversation_history:
            return EvaluationResult(
                metric_name="conversation_quality",
                metric_value=0.0,
                metadata={"reason": "no_conversation", "message_count": 0}
            )
        
        messages = row.conversation_history
        
        # Basic conversation metrics
        total_messages = len(messages)
        user_messages = sum(1 for msg in messages if msg.role == AgentRole.USER)
        assistant_messages = sum(1 for msg in messages if msg.role == AgentRole.ASSISTANT)
        system_messages = sum(1 for msg in messages if msg.role == AgentRole.SYSTEM)
        
        # Calculate conversation balance
        balance_score = self._calculate_balance_score(user_messages, assistant_messages)
        
        # Calculate response quality indicators
        avg_response_length = self._calculate_avg_response_length(messages)
        tool_usage_score = self._calculate_tool_usage_score(messages)
        
        # Calculate overall quality score (0-1)
        quality_score = (balance_score + tool_usage_score) / 2
        
        return EvaluationResult(
            metric_name="conversation_quality",
            metric_value=quality_score,
            metadata={
                "total_messages": total_messages,
                "user_messages": user_messages,
                "assistant_messages": assistant_messages,
                "system_messages": system_messages,
                "balance_score": balance_score,
                "tool_usage_score": tool_usage_score,
                "avg_response_length": avg_response_length,
                "conversation_turns": (user_messages + assistant_messages) // 2,
                "unique_agents": len(set(msg.agent_id for msg in messages if msg.agent_id))
            }
        )

    def _calculate_balance_score(self, user_messages: int, assistant_messages: int) -> float:
        """Calculate conversation balance score."""
        if user_messages == 0 and assistant_messages == 0:
            return 0.0
        
        total = user_messages + assistant_messages
        if total == 0:
            return 0.0
        
        # Ideal ratio is close to 1:1 for user:assistant
        ratio = min(user_messages, assistant_messages) / max(user_messages, assistant_messages)
        return ratio

    def _calculate_avg_response_length(self, messages: List) -> float:
        """Calculate average response length."""
        lengths = [len(msg.content) for msg in messages if msg.content]
        return sum(lengths) / len(lengths) if lengths else 0.0

    def _calculate_tool_usage_score(self, messages: List) -> float:
        """Calculate tool usage effectiveness score."""
        messages_with_tools = sum(1 for msg in messages if msg.tool_calls)
        total_messages = len(messages)
        
        if total_messages == 0:
            return 0.0
        
        # Score based on appropriate tool usage (not too much, not too little)
        tool_usage_ratio = messages_with_tools / total_messages
        
        # Optimal range is 10-30% of messages having tool calls
        if 0.1 <= tool_usage_ratio <= 0.3:
            return 1.0
        elif tool_usage_ratio < 0.1:
            return tool_usage_ratio / 0.1  # Scale up from 0
        else:
            return max(0.0, (0.6 - tool_usage_ratio) / 0.3)  # Scale down after 30%


class SemanticKernelPerformanceEvaluator(BaseEvaluator):
    """Evaluate Semantic Kernel specific performance metrics."""

    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Evaluate Semantic Kernel performance across multiple rows."""
        per_row_results = {}
        total_performance = 0.0
        total_tokens = 0
        total_duration = 0.0
        
        for row in rows:
            result = self._evaluate_single_row(row)
            per_row_results[row.id] = {
                "sk_performance": result.metric_value,
                "token_efficiency": result.metadata.get("token_efficiency", 0.0),
                "execution_efficiency": result.metadata.get("execution_efficiency", 0.0),
                "duration_ms": result.metadata.get("duration_ms", 0.0)
            }
            
            total_performance += result.metric_value
            total_tokens += result.metadata.get("total_tokens", 0)
            total_duration += result.metadata.get("duration_ms", 0.0)
        
        avg_performance = total_performance / len(rows) if rows else 0.0
        
        return EvaluatorOutput(
            name="sk_performance",
            summary={
                "average_performance": avg_performance,
                "total_experiments": len(rows),
                "total_tokens": total_tokens,
                "avg_tokens_per_experiment": total_tokens / len(rows) if rows else 0.0,
                "total_duration_ms": total_duration,
                "avg_duration_ms": total_duration / len(rows) if rows else 0.0
            },
            per_row=per_row_results
        )

    def _evaluate_single_row(self, row: DataModelRow) -> EvaluationResult:
        """Evaluate Semantic Kernel performance."""
        if not row.agent_interaction or not row.agent_interaction.semantic_kernel_trace:
            return EvaluationResult(
                metric_name="sk_performance",
                metric_value=0.0,
                metadata={"reason": "no_sk_trace"}
            )
        
        trace = row.agent_interaction.semantic_kernel_trace
        interaction = row.agent_interaction
        
        # Calculate performance metrics
        token_efficiency = self._calculate_token_efficiency(trace)
        execution_efficiency = self._calculate_execution_efficiency(interaction)
        resource_usage = self._calculate_resource_usage(trace, interaction)
        
        # Calculate overall performance score
        performance_score = (token_efficiency + execution_efficiency + resource_usage) / 3
        
        return EvaluationResult(
            metric_name="sk_performance",
            metric_value=performance_score,
            metadata={
                "token_efficiency": token_efficiency,
                "execution_efficiency": execution_efficiency,
                "resource_usage": resource_usage,
                "total_tokens": trace.total_tokens,
                "duration_ms": interaction.duration_ms,
                "cost": interaction.total_cost,
                "model_name": trace.model_name,
                "plugins_used": len(row.tool_calls) if row.tool_calls else 0,
                "filters_applied": len(trace.filters_applied) if trace.filters_applied else 0,
                "planners_used": len(trace.planners_used) if trace.planners_used else 0
            }
        )

    def _calculate_token_efficiency(self, trace) -> float:
        """Calculate token usage efficiency."""
        if not trace.total_tokens:
            return 1.0  # No token usage is perfectly efficient
        
        # Efficiency based on token usage patterns
        prompt_tokens = trace.prompt_tokens or 0
        completion_tokens = trace.completion_tokens or 0
        total_tokens = trace.total_tokens or (prompt_tokens + completion_tokens)
        
        if total_tokens == 0:
            return 1.0
        
        # Good efficiency if completion tokens are reasonable relative to prompt
        if prompt_tokens > 0:
            completion_ratio = completion_tokens / total_tokens
            # Optimal completion ratio is 20-60%
            if 0.2 <= completion_ratio <= 0.6:
                return 1.0
            elif completion_ratio < 0.2:
                return completion_ratio / 0.2
            else:
                return max(0.0, (1.0 - completion_ratio) / 0.4)
        
        # Penalize very high token usage
        if total_tokens > 4000:  # Assuming GPT-4 context
            return max(0.1, 4000 / total_tokens)
        
        return 1.0

    def _calculate_execution_efficiency(self, interaction) -> float:
        """Calculate execution time efficiency."""
        if not interaction.duration_ms:
            return 1.0
        
        # Efficiency based on execution time
        duration_seconds = interaction.duration_ms / 1000
        
        # Good performance thresholds
        if duration_seconds <= 1.0:  # Very fast
            return 1.0
        elif duration_seconds <= 5.0:  # Acceptable
            return 1.0 - (duration_seconds - 1.0) / 4.0 * 0.2
        elif duration_seconds <= 15.0:  # Slow but acceptable
            return 0.8 - (duration_seconds - 5.0) / 10.0 * 0.4
        else:  # Too slow
            return max(0.1, 0.4 - (duration_seconds - 15.0) / 30.0 * 0.3)

    def _calculate_resource_usage(self, trace, interaction) -> float:
        """Calculate resource usage efficiency."""
        score = 1.0
        
        # Factor in cost if available
        if interaction.total_cost:
            # Penalize high costs (assuming reasonable cost thresholds)
            if interaction.total_cost > 0.10:  # $0.10
                score *= max(0.1, 0.10 / interaction.total_cost)
        
        # Factor in model efficiency
        if trace.model_name:
            model_name = trace.model_name.lower()
            if "gpt-4" in model_name:
                score *= 0.8  # GPT-4 is expensive but high quality
            elif "gpt-3.5" in model_name or "gpt-35" in model_name:
                score *= 1.0  # Good balance
            elif "text-" in model_name:
                score *= 0.9  # Older models
        
        return min(1.0, score)


class AgentToAgentCommunicationEvaluator(BaseEvaluator):
    """Evaluate agent-to-agent communication effectiveness."""

    def evaluate(self, rows: list[DataModelRow]) -> EvaluatorOutput:
        """Evaluate agent communication across multiple rows."""
        per_row_results = {}
        total_communication = 0.0
        multi_agent_conversations = 0
        
        for row in rows:
            result = self._evaluate_single_row(row)
            per_row_results[row.id] = {
                "agent_communication": result.metric_value,
                "unique_agents": result.metadata.get("unique_agents", 0),
                "multi_agent_turns": result.metadata.get("multi_agent_turns", 0)
            }
            
            total_communication += result.metric_value
            if result.metadata.get("unique_agents", 0) > 1:
                multi_agent_conversations += 1
        
        avg_communication = total_communication / len(rows) if rows else 0.0
        
        return EvaluatorOutput(
            name="agent_communication",
            summary={
                "average_communication": avg_communication,
                "total_conversations": len(rows),
                "multi_agent_conversations": multi_agent_conversations,
                "single_agent_conversations": len(rows) - multi_agent_conversations
            },
            per_row=per_row_results
        )

    def _evaluate_single_row(self, row: DataModelRow) -> EvaluationResult:
        """Evaluate agent-to-agent communication."""
        if not row.conversation_history:
            return EvaluationResult(
                metric_name="agent_communication",
                metric_value=0.0,
                metadata={"reason": "no_conversation"}
            )
        
        messages = row.conversation_history
        
        # Identify unique agents
        agents = set(msg.agent_id for msg in messages if msg.agent_id)
        
        if len(agents) < 2:
            return EvaluationResult(
                metric_name="agent_communication",
                metric_value=0.0,
                metadata={"reason": "single_agent", "agents": list(agents)}
            )
        
        # Analyze communication patterns
        communication_score = self._analyze_communication_patterns(messages, agents)
        handoff_score = self._analyze_handoffs(messages)
        collaboration_score = self._analyze_collaboration(messages)
        
        overall_score = (communication_score + handoff_score + collaboration_score) / 3
        
        return EvaluationResult(
            metric_name="agent_communication",
            metric_value=overall_score,
            metadata={
                "unique_agents": len(agents),
                "communication_score": communication_score,
                "handoff_score": handoff_score,
                "collaboration_score": collaboration_score,
                "agent_ids": list(agents),
                "total_exchanges": len(messages),
                "multi_agent_turns": self._count_multi_agent_turns(messages)
            }
        )

    def _analyze_communication_patterns(self, messages: List, agents: set) -> float:
        """Analyze communication patterns between agents."""
        if len(messages) < 2:
            return 0.0
        
        # Check for balanced communication
        agent_message_counts = {}
        for msg in messages:
            if msg.agent_id:
                agent_message_counts[msg.agent_id] = agent_message_counts.get(msg.agent_id, 0) + 1
        
        if not agent_message_counts:
            return 0.0
        
        # Calculate balance (all agents should participate somewhat equally)
        counts = list(agent_message_counts.values())
        min_count = min(counts)
        max_count = max(counts)
        
        balance_score = min_count / max_count if max_count > 0 else 0.0
        
        return balance_score

    def _analyze_handoffs(self, messages: List) -> float:
        """Analyze the quality of handoffs between agents."""
        if len(messages) < 2:
            return 0.0
        
        handoffs = 0
        smooth_handoffs = 0
        
        for i in range(1, len(messages)):
            prev_msg = messages[i-1]
            curr_msg = messages[i]
            
            if prev_msg.agent_id != curr_msg.agent_id and prev_msg.agent_id and curr_msg.agent_id:
                handoffs += 1
                
                # Check if handoff is smooth (no abrupt topic changes)
                # This is a simplified check - in practice, you might use NLP
                if self._is_smooth_handoff(prev_msg.content, curr_msg.content):
                    smooth_handoffs += 1
        
        return smooth_handoffs / handoffs if handoffs > 0 else 1.0

    def _analyze_collaboration(self, messages: List) -> float:
        """Analyze collaborative behavior between agents."""
        collaboration_indicators = 0
        total_messages = len(messages)
        
        if total_messages == 0:
            return 0.0
        
        # Look for collaboration indicators
        for msg in messages:
            content = msg.content.lower()
            
            # Check for collaborative language
            if any(phrase in content for phrase in [
                "let me help", "working together", "collaborating",
                "building on", "continuing from", "following up"
            ]):
                collaboration_indicators += 1
            
            # Check for tool usage in collaborative context
            if msg.tool_calls and any(phrase in content for phrase in [
                "using", "calling", "invoking", "executing"
            ]):
                collaboration_indicators += 1
        
        return min(1.0, collaboration_indicators / (total_messages * 0.3))  # Up to 30% collaborative messages is ideal

    def _is_smooth_handoff(self, prev_content: str, curr_content: str) -> bool:
        """Check if a handoff between agents is smooth."""
        # Simplified implementation - in practice, use semantic similarity
        prev_words = set(prev_content.lower().split())
        curr_words = set(curr_content.lower().split())
        
        # Check for word overlap (indicates topic continuity)
        overlap = len(prev_words.intersection(curr_words))
        total_unique = len(prev_words.union(curr_words))
        
        return overlap / total_unique > 0.1 if total_unique > 0 else False

    def _count_multi_agent_turns(self, messages: List) -> int:
        """Count the number of multi-agent conversation turns."""
        if len(messages) < 2:
            return 0
        
        turns = 0
        for i in range(1, len(messages)):
            if messages[i-1].agent_id != messages[i].agent_id:
                turns += 1
        
        return turns