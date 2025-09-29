#!/usr/bin/env python3
"""
Simple Function Calling Example

This example demonstrates:
- Chat with automatic function calling
- How the agent decides when to call functions
- Function call results integration
- Clean separation of concerns
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any, List

# Mock imports for testing without dependencies
try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.core_plugins.math_plugin import MathPlugin
    MOCK_MODE = False
except ImportError:
    MOCK_MODE = True
    print("ℹ️  Running in mock mode (semantic-kernel not installed)")


class FunctionCallingAgent:
    """Agent that demonstrates automatic function calling."""
    
    def __init__(self):
        self.kernel = None
        self.chat_service = None
        self.function_calls = []
    
    async def setup(self):
        """Initialize with function calling capability."""
        if MOCK_MODE:
            print("✅ Mock function calling agent ready")
            return
        
        # Create kernel
        self.kernel = sk.Kernel()
        
        # Add OpenAI service
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")
        
        self.chat_service = OpenAIChatCompletion(
            ai_model_id="gpt-3.5-turbo",
            api_key=api_key
        )
        self.kernel.add_service(self.chat_service)
        
        # Add math plugin for function calling
        math_plugin = self.kernel.add_plugin(MathPlugin(), plugin_name="math")
        print(f"✅ Function calling agent ready with math functions: {list(math_plugin.keys())}")
    
    async def chat_with_functions(self, message: str) -> Dict[str, Any]:
        """Chat with automatic function calling enabled."""
        start_time = datetime.now()
        
        if MOCK_MODE:
            return self._mock_function_calling_response(message, start_time)
        
        try:
            # Create chat history
            chat_history = sk.ChatHistory()
            chat_history.add_user_message(message)
            
            # Enable automatic function calling
            execution_settings = sk.PromptExecutionSettings(
                service_id=self.chat_service.service_id,
                max_tokens=500,
                temperature=0.7,
                function_call_behavior=sk.FunctionCallBehavior.AutoInvokeKernelFunctions()
            )
            
            # Get response with function calling
            response = await self.chat_service.get_chat_message_content(
                chat_history=chat_history,
                settings=execution_settings,
                kernel=self.kernel
            )
            
            end_time = datetime.now()
            
            # Extract function call information
            function_calls = self._extract_function_calls(response)
            
            result = {
                "message": message,
                "response": str(response.content) if response.content else "",
                "function_calls": function_calls,
                "duration_ms": (end_time - start_time).total_seconds() * 1000,
                "success": True,
                "model": "gpt-3.5-turbo"
            }
            
            # Store for analysis
            self.function_calls.extend(function_calls)
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            return {
                "message": message,
                "response": None,
                "function_calls": [],
                "duration_ms": (end_time - start_time).total_seconds() * 1000,
                "success": False,
                "error": str(e)
            }
    
    def _mock_function_calling_response(self, message: str, start_time: datetime) -> Dict[str, Any]:
        """Generate mock response with function calling simulation."""
        message_lower = message.lower()
        function_calls = []
        response_content = ""
        
        # Simulate function calling based on message content
        if any(word in message_lower for word in ["add", "plus", "+", "sum"]):
            # Mock math function call
            function_calls.append({
                "plugin_name": "math",
                "function_name": "Add",
                "arguments": {"input": "15", "amount": "25"},
                "result": "40",
                "success": True,
                "duration_ms": 12.5
            })
            response_content = "I calculated that for you using the math plugin. The result is 40."
            
        elif any(word in message_lower for word in ["multiply", "times", "×", "*"]):
            function_calls.append({
                "plugin_name": "math",
                "function_name": "Multiply",
                "arguments": {"input": "8", "amount": "7"},
                "result": "56",
                "success": True,
                "duration_ms": 15.2
            })
            response_content = "I used the math plugin to multiply those numbers. The answer is 56."
            
        else:
            response_content = f"I understand you said: '{message}'. I don't see any math operations to perform, so no functions were called."
        
        end_time = datetime.now()
        
        return {
            "message": message,
            "response": response_content,
            "function_calls": function_calls,
            "duration_ms": (end_time - start_time).total_seconds() * 1000,
            "success": True,
            "mock": True
        }
    
    def _extract_function_calls(self, response) -> List[Dict[str, Any]]:
        """Extract function call information from response."""
        function_calls = []
        
        # Check if response has metadata with function calls
        if hasattr(response, 'metadata') and response.metadata:
            if 'function_calls' in response.metadata:
                calls = response.metadata['function_calls']
                if isinstance(calls, list):
                    for call in calls:
                        function_calls.append({
                            "plugin_name": call.get("plugin_name", "unknown"),
                            "function_name": call.get("function_name", "unknown"),
                            "arguments": call.get("arguments", {}),
                            "result": call.get("result"),
                            "success": call.get("success", True),
                            "duration_ms": call.get("duration_ms", 0)
                        })
        
        return function_calls
    
    def get_function_call_summary(self) -> Dict[str, Any]:
        """Get summary of all function calls made."""
        if not self.function_calls:
            return {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "plugins_used": [],
                "functions_used": []
            }
        
        successful_calls = [call for call in self.function_calls if call.get("success", True)]
        failed_calls = [call for call in self.function_calls if not call.get("success", True)]
        
        plugins_used = list(set(call.get("plugin_name", "unknown") for call in self.function_calls))
        functions_used = list(set(f"{call.get('plugin_name', 'unknown')}.{call.get('function_name', 'unknown')}" for call in self.function_calls))
        
        return {
            "total_calls": len(self.function_calls),
            "successful_calls": len(successful_calls),
            "failed_calls": len(failed_calls),
            "plugins_used": plugins_used,
            "functions_used": functions_used,
            "all_calls": self.function_calls.copy()
        }


async def main():
    """Run function calling examples."""
    print("🔧 Function Calling Example")
    print("=" * 35)
    
    # Create and setup agent
    agent = FunctionCallingAgent()
    await agent.setup()
    
    # Test messages that should trigger function calls
    test_messages = [
        "What is 15 plus 25?",
        "Can you multiply 8 times 7?",
        "Please add 100 and 200 together",
        "Hello, how are you?",  # Should not trigger functions
        "Calculate 50 minus 30",  # May or may not work depending on plugin
        "What's 12 × 4?"
    ]
    
    print("\n🤖 Chat with Function Calling:")
    print("-" * 40)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. User: {message}")
        
        result = await agent.chat_with_functions(message)
        
        if result["success"]:
            print(f"   Agent: {result['response']}")
            
            if result["function_calls"]:
                print(f"   📞 Functions called: {len(result['function_calls'])}")
                for call in result["function_calls"]:
                    status = "✅" if call.get("success", True) else "❌"
                    plugin = call.get("plugin_name", "unknown")
                    func = call.get("function_name", "unknown")
                    args = call.get("arguments", {})
                    result_val = call.get("result", "N/A")
                    print(f"      {status} {plugin}.{func}({args}) → {result_val}")
            else:
                print("   📞 No functions called")
                
            print(f"   ⏱️  Duration: {result['duration_ms']:.1f}ms")
        else:
            print(f"   ❌ Error: {result['error']}")
        
        # Small delay for readability
        await asyncio.sleep(0.1)
    
    # Show function call summary
    print("\n📊 Function Call Summary:")
    print("-" * 30)
    summary = agent.get_function_call_summary()
    print(f"Total function calls: {summary['total_calls']}")
    print(f"Successful calls: {summary['successful_calls']}")
    print(f"Failed calls: {summary['failed_calls']}")
    print(f"Plugins used: {', '.join(summary['plugins_used']) if summary['plugins_used'] else 'None'}")
    print(f"Functions used: {', '.join(summary['functions_used']) if summary['functions_used'] else 'None'}")
    
    if summary['failed_calls'] > 0:
        print("\n❌ Failed Function Calls:")
        for call in summary['all_calls']:
            if not call.get("success", True):
                print(f"  {call.get('plugin_name')}.{call.get('function_name')}: {call.get('error', 'Unknown error')}")
    
    print("\n✅ Function calling example completed!")


if __name__ == "__main__":
    asyncio.run(main())