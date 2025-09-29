"""Semantic Kernel specifclassclass SemanticKernelProcessor(BaseProcessor[dict]):
    \"\"\"Post-processor for Semantic Kernel agent interactions and tool calls.\"\"\"

    def run(self, data_model_row: DataModelRow, **kwargs) -> DataModelRow:
        \"\"\"Process a row to extract Semantic Kernel agent evaluation data.\"\"\"
        row = data_model_row
        try:ticKernelProcessor(BaseProcessor[dict]):
    \"\"\"Post-processor for Semantic Kernel agent interactions and tool calls.\"\"\"

    def run(self, data_model_row: DataModelRow, **kwargs) -> DataModelRow:
        \"\"\"Process a row to extract Semantic Kernel agent evaluation data.\"\"\"
        row = data_model_rowdef run(self, data_model_row: DataModelRow, **kwargs) -> DataModelRow:
        \"\"\"Process a row to extract Semantic Kernel agent evaluation data.\"\"\"
        row = data_model_rowpost-processor for agent evaluation."""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..models import (
    AgentFramework,
    AgentInteraction,
    AgentMessage,
    AgentRole,
    DataModelRow,
    SemanticKernelTrace,
    ToolCallDetails,
    ToolCallStatus,
)
from .base import BaseProcessor


class SemanticKernelProcessor(BaseProcessor):
    """Semantic Kernel specific post-processor for agent evaluation."""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..models import (
    AgentFramework,
    AgentInteraction,
    AgentMessage,
    AgentRole,
    DataModelRow,
    SemanticKernelTrace,
    ToolCallDetails,
    ToolCallStatus,
)
from .base import BaseProcessor


class SemanticKernelProcessor(BaseProcessor[dict]):
    """Post-processor for Semantic Kernel agent interactions and tool calls."""

    def run(self, data_model_row: DataModelRow, **kwargs) -> DataModelRow:
        """Process a row to extract Semantic Kernel agent evaluation data."""
        row = data_model_row
        
        try:
            # Extract agent interaction from data_output if present
            if row.data_output and isinstance(row.data_output, dict):
                interaction = self._extract_agent_interaction(row.data_output)
                if interaction:
                    row.agent_interaction = interaction
                
                # Extract tool calls
                tool_calls = self._extract_tool_calls(row.data_output)
                if tool_calls:
                    row.tool_calls.extend(tool_calls)
                
                # Extract conversation history
                messages = self._extract_conversation_history(row.data_output)
                if messages:
                    row.conversation_history.extend(messages)
            
            # Process metadata for additional Semantic Kernel information
            if row.metadata:
                self._process_sk_metadata(row)
            
        except Exception as e:
            # Log error but don't fail the entire row
            row.metadata["sk_processor_error"] = str(e)
        
        return row

    def _extract_agent_interaction(
        self, data_output: Dict[str, Any]
    ) -> Optional[AgentInteraction]:
        """Extract agent interaction from data output."""
        # Look for common Semantic Kernel patterns
        if "kernel_result" in data_output or "function_result" in data_output:
            interaction_id = str(uuid4())
            
            # Extract basic interaction info
            interaction = AgentInteraction(
                interaction_id=interaction_id,
                framework=AgentFramework.SEMANTIC_KERNEL,
                metadata={}
            )
            
            # Extract semantic kernel trace
            sk_trace = self._extract_sk_trace(data_output)
            if sk_trace:
                interaction.semantic_kernel_trace = sk_trace
            
            # Extract timing information
            if "execution_time_ms" in data_output:
                interaction.duration_ms = data_output["execution_time_ms"]
            
            # Extract token usage
            if "token_usage" in data_output:
                token_data = data_output["token_usage"]
                if isinstance(token_data, dict):
                    interaction.total_tokens = token_data.get("total_tokens")
            
            # Extract cost information
            if "cost" in data_output:
                interaction.total_cost = data_output["cost"]
            
            return interaction
        
        return None

    def _extract_sk_trace(self, data_output: Dict[str, Any]) -> Optional[SemanticKernelTrace]:
        """Extract Semantic Kernel specific trace information."""
        trace = SemanticKernelTrace()
        
        # Extract kernel information
        if "kernel_id" in data_output:
            trace.kernel_id = data_output["kernel_id"]
        
        if "plugin_name" in data_output:
            trace.plugin_name = data_output["plugin_name"]
        
        if "function_name" in data_output:
            trace.function_name = data_output["function_name"]
        
        if "invocation_id" in data_output:
            trace.invocation_id = data_output["invocation_id"]
        
        # Extract execution settings
        if "execution_settings" in data_output:
            settings = data_output["execution_settings"]
            if isinstance(settings, dict):
                trace.execution_settings = settings
                # Extract common AI service settings
                trace.model_name = settings.get("model_id") or settings.get("model_name")
                trace.temperature = settings.get("temperature")
        
        # Extract token usage
        if "token_usage" in data_output:
            token_data = data_output["token_usage"]
            if isinstance(token_data, dict):
                trace.prompt_tokens = token_data.get("prompt_tokens")
                trace.completion_tokens = token_data.get("completion_tokens")
                trace.total_tokens = token_data.get("total_tokens")
        
        # Extract filter information
        if "filters_applied" in data_output:
            filters = data_output["filters_applied"]
            if isinstance(filters, list):
                trace.filters_applied = filters
        
        # Extract planner information
        if "planners_used" in data_output:
            planners = data_output["planners_used"]
            if isinstance(planners, list):
                trace.planners_used = planners
        
        return trace if any([
            trace.kernel_id,
            trace.plugin_name,
            trace.function_name,
            trace.invocation_id,
            trace.execution_settings,
            trace.filters_applied,
            trace.planners_used
        ]) else None

    def _extract_tool_calls(self, data_output: Dict[str, Any]) -> List[ToolCallDetails]:
        """Extract tool calls from data output."""
        tool_calls = []
        
        # Look for function calls in various formats
        if "function_calls" in data_output:
            calls = data_output["function_calls"]
            if isinstance(calls, list):
                for call in calls:
                    if isinstance(call, dict):
                        tool_call = self._parse_function_call(call)
                        if tool_call:
                            tool_calls.append(tool_call)
        
        # Look for kernel invocations
        if "kernel_invocations" in data_output:
            invocations = data_output["kernel_invocations"]
            if isinstance(invocations, list):
                for invocation in invocations:
                    if isinstance(invocation, dict):
                        tool_call = self._parse_kernel_invocation(invocation)
                        if tool_call:
                            tool_calls.append(tool_call)
        
        return tool_calls

    def _parse_function_call(self, call_data: Dict[str, Any]) -> Optional[ToolCallDetails]:
        """Parse a function call into a ToolCallDetails object."""
        if "name" not in call_data:
            return None
        
        # Determine status
        status = ToolCallStatus.SUCCESS
        if call_data.get("error"):
            status = ToolCallStatus.FAILED
        elif call_data.get("cancelled"):
            status = ToolCallStatus.CANCELLED
        elif call_data.get("timeout"):
            status = ToolCallStatus.TIMEOUT
        
        # Extract plugin and function names
        function_name = call_data["name"]
        tool_name = call_data.get("plugin_name", "unknown")
        
        # Parse plugin-function format (e.g., "math-add")
        if "-" in function_name and not tool_name or tool_name == "unknown":
            parts = function_name.split("-", 1)
            if len(parts) == 2:
                tool_name, function_name = parts
        
        return ToolCallDetails(
            tool_name=tool_name,
            function_name=function_name,
            arguments=call_data.get("arguments", {}),
            result=call_data.get("result"),
            status=status,
            execution_time_ms=call_data.get("execution_time_ms"),
            error_message=call_data.get("error"),
            metadata={
                "invocation_id": call_data.get("invocation_id"),
                "kernel_id": call_data.get("kernel_id"),
                **call_data.get("metadata", {})
            }
        )

    def _parse_kernel_invocation(self, invocation_data: Dict[str, Any]) -> Optional[ToolCallDetails]:
        """Parse a kernel invocation into a ToolCallDetails object."""
        plugin_name = invocation_data.get("plugin_name", "unknown")
        function_name = invocation_data.get("function_name", "unknown")
        
        if plugin_name == "unknown" and function_name == "unknown":
            return None
        
        # Determine status from result
        status = ToolCallStatus.SUCCESS
        if invocation_data.get("exception"):
            status = ToolCallStatus.FAILED
        
        return ToolCallDetails(
            tool_name=plugin_name,
            function_name=function_name,
            arguments=invocation_data.get("arguments", {}),
            result=invocation_data.get("result"),
            status=status,
            execution_time_ms=invocation_data.get("duration_ms"),
            error_message=str(invocation_data.get("exception")) if invocation_data.get("exception") else None,
            metadata={
                "kernel_id": invocation_data.get("kernel_id"),
                "invocation_id": invocation_data.get("invocation_id"),
                **invocation_data.get("metadata", {})
            }
        )

    def _extract_conversation_history(
        self, data_output: Dict[str, Any]
    ) -> List[AgentMessage]:
        """Extract conversation history from data output."""
        messages = []
        
        # Look for chat history
        if "chat_history" in data_output:
            history = data_output["chat_history"]
            if isinstance(history, list):
                for msg in history:
                    if isinstance(msg, dict):
                        message = self._parse_chat_message(msg)
                        if message:
                            messages.append(message)
        
        # Look for conversation messages
        if "messages" in data_output:
            msg_list = data_output["messages"]
            if isinstance(msg_list, list):
                for msg in msg_list:
                    if isinstance(msg, dict):
                        message = self._parse_chat_message(msg)
                        if message:
                            messages.append(message)
        
        return messages

    def _parse_chat_message(self, msg_data: Dict[str, Any]) -> Optional[AgentMessage]:
        """Parse a chat message into an AgentMessage object."""
        if "content" not in msg_data:
            return None
        
        # Determine role
        role_str = msg_data.get("role", "assistant").lower()
        role = AgentRole.ASSISTANT  # default
        
        try:
            role = AgentRole(role_str)
        except ValueError:
            # Handle custom roles or map them
            if role_str in ["ai", "bot", "agent"]:
                role = AgentRole.ASSISTANT
            elif role_str in ["human", "user"]:
                role = AgentRole.USER
            elif role_str in ["system"]:
                role = AgentRole.SYSTEM
        
        # Parse timestamp
        timestamp = datetime.utcnow()
        if "timestamp" in msg_data:
            try:
                timestamp = datetime.fromisoformat(msg_data["timestamp"])
            except (ValueError, TypeError):
                pass
        
        # Extract tool calls from message
        tool_calls = []
        if "tool_calls" in msg_data:
            calls = msg_data["tool_calls"]
            if isinstance(calls, list):
                for call in calls:
                    if isinstance(call, dict):
                        tool_call = self._parse_function_call(call)
                        if tool_call:
                            tool_calls.append(tool_call)
        
        return AgentMessage(
            role=role,
            content=str(msg_data["content"]),
            timestamp=timestamp,
            agent_id=msg_data.get("agent_id"),
            tool_calls=tool_calls,
            metadata=msg_data.get("metadata", {})
        )

    def _process_sk_metadata(self, row: DataModelRow) -> None:
        """Process Semantic Kernel specific metadata."""
        # Extract additional SK-specific information from metadata
        metadata = row.metadata
        
        # Look for kernel configuration
        if "kernel_config" in metadata:
            config = metadata["kernel_config"]
            if isinstance(config, dict):
                row.metadata["sk_kernel_services"] = list(config.get("services", {}).keys())
                row.metadata["sk_plugins_loaded"] = list(config.get("plugins", {}).keys())
        
        # Extract AI service information
        if "ai_service" in metadata:
            service = metadata["ai_service"]
            if isinstance(service, dict):
                row.metadata["sk_ai_service_type"] = service.get("type")
                row.metadata["sk_model_id"] = service.get("model_id")
        
        # Extract prompt information
        if "prompt_template" in metadata:
            row.metadata["sk_prompt_template"] = metadata["prompt_template"]
        
        # Extract semantic function information
        if "semantic_function" in metadata:
            func_info = metadata["semantic_function"]
            if isinstance(func_info, dict):
                row.metadata["sk_function_description"] = func_info.get("description")
                row.metadata["sk_function_parameters"] = list(func_info.get("parameters", {}).keys())

    def process(self, row: DataModelRow, **kwargs) -> DataModelRow:
        """Process a row to extract Semantic Kernel agent evaluation data."""
        try:
            # Extract agent interaction from data_output if present
            if row.data_output and isinstance(row.data_output, dict):
                interaction = self._extract_agent_interaction(row.data_output)
                if interaction:
                    row.agent_interaction = interaction
                
                # Extract tool calls
                tool_calls = self._extract_tool_calls(row.data_output)
                if tool_calls:
                    row.tool_calls.extend(tool_calls)
                
                # Extract conversation history
                messages = self._extract_conversation_history(row.data_output)
                if messages:
                    row.conversation_history.extend(messages)
            
            # Process metadata for additional Semantic Kernel information
            if row.metadata:
                self._process_sk_metadata(row)
            
        except Exception as e:
            # Log error but don't fail the entire row
            row.metadata["sk_processor_error"] = str(e)
        
        return row

    def _extract_agent_interaction(
        self, data_output: Dict[str, Any]
    ) -> Optional[AgentInteraction]:
        """Extract agent interaction from data output."""
        # Look for common Semantic Kernel patterns
        if "kernel_result" in data_output or "function_result" in data_output:
            interaction_id = str(uuid4())
            
            # Extract basic interaction info
            interaction = AgentInteraction(
                interaction_id=interaction_id,
                framework=AgentFramework.SEMANTIC_KERNEL,
                metadata={}
            )
            
            # Extract semantic kernel trace
            sk_trace = self._extract_sk_trace(data_output)
            if sk_trace:
                interaction.semantic_kernel_trace = sk_trace
            
            # Extract timing information
            if "execution_time_ms" in data_output:
                interaction.duration_ms = data_output["execution_time_ms"]
            
            # Extract token usage
            if "token_usage" in data_output:
                token_data = data_output["token_usage"]
                if isinstance(token_data, dict):
                    interaction.total_tokens = token_data.get("total_tokens")
            
            # Extract cost information
            if "cost" in data_output:
                interaction.total_cost = data_output["cost"]
            
            return interaction
        
        return None

    def _extract_sk_trace(self, data_output: Dict[str, Any]) -> Optional[SemanticKernelTrace]:
        """Extract Semantic Kernel specific trace information."""
        trace = SemanticKernelTrace()
        
        # Extract kernel information
        if "kernel_id" in data_output:
            trace.kernel_id = data_output["kernel_id"]
        
        if "plugin_name" in data_output:
            trace.plugin_name = data_output["plugin_name"]
        
        if "function_name" in data_output:
            trace.function_name = data_output["function_name"]
        
        if "invocation_id" in data_output:
            trace.invocation_id = data_output["invocation_id"]
        
        # Extract execution settings
        if "execution_settings" in data_output:
            settings = data_output["execution_settings"]
            if isinstance(settings, dict):
                trace.execution_settings = settings
                # Extract common AI service settings
                trace.model_name = settings.get("model_id") or settings.get("model_name")
                trace.temperature = settings.get("temperature")
        
        # Extract token usage
        if "token_usage" in data_output:
            token_data = data_output["token_usage"]
            if isinstance(token_data, dict):
                trace.prompt_tokens = token_data.get("prompt_tokens")
                trace.completion_tokens = token_data.get("completion_tokens")
                trace.total_tokens = token_data.get("total_tokens")
        
        # Extract filter information
        if "filters_applied" in data_output:
            filters = data_output["filters_applied"]
            if isinstance(filters, list):
                trace.filters_applied = filters
        
        # Extract planner information
        if "planners_used" in data_output:
            planners = data_output["planners_used"]
            if isinstance(planners, list):
                trace.planners_used = planners
        
        return trace if any([
            trace.kernel_id,
            trace.plugin_name,
            trace.function_name,
            trace.invocation_id,
            trace.execution_settings,
            trace.filters_applied,
            trace.planners_used
        ]) else None

    def _extract_tool_calls(self, data_output: Dict[str, Any]) -> List[ToolCallDetails]:
        """Extract tool calls from data output."""
        tool_calls = []
        
        # Look for function calls in various formats
        if "function_calls" in data_output:
            calls = data_output["function_calls"]
            if isinstance(calls, list):
                for call in calls:
                    if isinstance(call, dict):
                        tool_call = self._parse_function_call(call)
                        if tool_call:
                            tool_calls.append(tool_call)
        
        # Look for kernel invocations
        if "kernel_invocations" in data_output:
            invocations = data_output["kernel_invocations"]
            if isinstance(invocations, list):
                for invocation in invocations:
                    if isinstance(invocation, dict):
                        tool_call = self._parse_kernel_invocation(invocation)
                        if tool_call:
                            tool_calls.append(tool_call)
        
        # Look for plugin executions
        if "plugin_executions" in data_output:
            executions = data_output["plugin_executions"]
            if isinstance(executions, list):
                for execution in executions:
                    if isinstance(execution, dict):
                        tool_call = self._parse_plugin_execution(execution)
                        if tool_call:
                            tool_calls.append(tool_call)
        
        return tool_calls

    def _parse_function_call(self, call_data: Dict[str, Any]) -> Optional[ToolCallDetails]:
        """Parse a function call into a ToolCallDetails object."""
        if "name" not in call_data:
            return None
        
        # Determine status
        status = ToolCallStatus.SUCCESS
        if call_data.get("error"):
            status = ToolCallStatus.FAILED
        elif call_data.get("cancelled"):
            status = ToolCallStatus.CANCELLED
        elif call_data.get("timeout"):
            status = ToolCallStatus.TIMEOUT
        
        # Extract plugin and function names
        function_name = call_data["name"]
        tool_name = call_data.get("plugin_name", "unknown")
        
        # Parse plugin-function format (e.g., "math-add")
        if "-" in function_name and not tool_name or tool_name == "unknown":
            parts = function_name.split("-", 1)
            if len(parts) == 2:
                tool_name, function_name = parts
        
        return ToolCallDetails(
            tool_name=tool_name,
            function_name=function_name,
            arguments=call_data.get("arguments", {}),
            result=call_data.get("result"),
            status=status,
            execution_time_ms=call_data.get("execution_time_ms"),
            error_message=call_data.get("error"),
            metadata={
                "invocation_id": call_data.get("invocation_id"),
                "kernel_id": call_data.get("kernel_id"),
                **call_data.get("metadata", {})
            }
        )

    def _parse_kernel_invocation(self, invocation_data: Dict[str, Any]) -> Optional[ToolCallDetails]:
        """Parse a kernel invocation into a ToolCallDetails object."""
        plugin_name = invocation_data.get("plugin_name", "unknown")
        function_name = invocation_data.get("function_name", "unknown")
        
        if plugin_name == "unknown" and function_name == "unknown":
            return None
        
        # Determine status from result
        status = ToolCallStatus.SUCCESS
        if invocation_data.get("exception"):
            status = ToolCallStatus.FAILED
        
        return ToolCallDetails(
            tool_name=plugin_name,
            function_name=function_name,
            arguments=invocation_data.get("arguments", {}),
            result=invocation_data.get("result"),
            status=status,
            execution_time_ms=invocation_data.get("duration_ms"),
            error_message=str(invocation_data.get("exception")) if invocation_data.get("exception") else None,
            metadata={
                "kernel_id": invocation_data.get("kernel_id"),
                "invocation_id": invocation_data.get("invocation_id"),
                **invocation_data.get("metadata", {})
            }
        )

    def _parse_plugin_execution(self, execution_data: Dict[str, Any]) -> Optional[ToolCallDetails]:
        """Parse a plugin execution into a ToolCallDetails object."""
        return self._parse_kernel_invocation(execution_data)  # Same format

    def _extract_conversation_history(
        self, data_output: Dict[str, Any]
    ) -> List[AgentMessage]:
        """Extract conversation history from data output."""
        messages = []
        
        # Look for chat history
        if "chat_history" in data_output:
            history = data_output["chat_history"]
            if isinstance(history, list):
                for msg in history:
                    if isinstance(msg, dict):
                        message = self._parse_chat_message(msg)
                        if message:
                            messages.append(message)
        
        # Look for conversation messages
        if "messages" in data_output:
            msg_list = data_output["messages"]
            if isinstance(msg_list, list):
                for msg in msg_list:
                    if isinstance(msg, dict):
                        message = self._parse_chat_message(msg)
                        if message:
                            messages.append(message)
        
        return messages

    def _parse_chat_message(self, msg_data: Dict[str, Any]) -> Optional[AgentMessage]:
        """Parse a chat message into an AgentMessage object."""
        if "content" not in msg_data:
            return None
        
        # Determine role
        role_str = msg_data.get("role", "assistant").lower()
        role = AgentRole.ASSISTANT  # default
        
        try:
            role = AgentRole(role_str)
        except ValueError:
            # Handle custom roles or map them
            if role_str in ["ai", "bot", "agent"]:
                role = AgentRole.ASSISTANT
            elif role_str in ["human", "user"]:
                role = AgentRole.USER
            elif role_str in ["system"]:
                role = AgentRole.SYSTEM
        
        # Parse timestamp
        timestamp = datetime.utcnow()
        if "timestamp" in msg_data:
            try:
                timestamp = datetime.fromisoformat(msg_data["timestamp"])
            except (ValueError, TypeError):
                pass
        
        # Extract tool calls from message
        tool_calls = []
        if "tool_calls" in msg_data:
            calls = msg_data["tool_calls"]
            if isinstance(calls, list):
                for call in calls:
                    if isinstance(call, dict):
                        tool_call = self._parse_function_call(call)
                        if tool_call:
                            tool_calls.append(tool_call)
        
        return AgentMessage(
            role=role,
            content=str(msg_data["content"]),
            timestamp=timestamp,
            agent_id=msg_data.get("agent_id"),
            tool_calls=tool_calls,
            metadata=msg_data.get("metadata", {})
        )

    def _process_sk_metadata(self, row: DataModelRow) -> None:
        """Process Semantic Kernel specific metadata."""
        # Extract additional SK-specific information from metadata
        metadata = row.metadata
        
        # Look for kernel configuration
        if "kernel_config" in metadata:
            config = metadata["kernel_config"]
            if isinstance(config, dict):
                row.metadata["sk_kernel_services"] = list(config.get("services", {}).keys())
                row.metadata["sk_plugins_loaded"] = list(config.get("plugins", {}).keys())
        
        # Extract AI service information
        if "ai_service" in metadata:
            service = metadata["ai_service"]
            if isinstance(service, dict):
                row.metadata["sk_ai_service_type"] = service.get("type")
                row.metadata["sk_model_id"] = service.get("model_id")
        
        # Extract prompt information
        if "prompt_template" in metadata:
            row.metadata["sk_prompt_template"] = metadata["prompt_template"]
        
        # Extract semantic function information
        if "semantic_function" in metadata:
            func_info = metadata["semantic_function"]
            if isinstance(func_info, dict):
                row.metadata["sk_function_description"] = func_info.get("description")
                row.metadata["sk_function_parameters"] = list(func_info.get("parameters", {}).keys())