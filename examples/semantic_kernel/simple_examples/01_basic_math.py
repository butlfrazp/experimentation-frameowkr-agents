#!/usr/bin/env python3
"""
Simple Math Plugin Example

This example demonstrates:
- Basic Semantic Kernel setup
- Single math plugin usage
- Direct function invocation
- Simple result handling
"""

import asyncio
import os
from typing import Any

# Mock imports for testing without dependencies
try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.core_plugins.math_plugin import MathPlugin

    MOCK_MODE = False
except ImportError:
    MOCK_MODE = True
    print("ℹ️  Running in mock mode (semantic-kernel not installed)")


class SimpleMathAgent:
    """A very simple agent that only does math operations."""

    def __init__(self):
        self.kernel = None
        self.math_plugin = None
        self.results = []

    async def setup(self):
        """Initialize the kernel with just the math plugin."""
        if MOCK_MODE:
            print("✅ Mock setup complete - Math plugin ready")
            return

        # Create kernel
        self.kernel = sk.Kernel()

        # Add OpenAI service (only if API key available)
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            chat_service = OpenAIChatCompletion(ai_model_id="gpt-3.5-turbo", api_key=api_key)
            self.kernel.add_service(chat_service)

        # Add math plugin
        self.math_plugin = self.kernel.add_plugin(MathPlugin(), plugin_name="math")
        print(f"✅ Math plugin loaded with functions: {list(self.math_plugin.keys())}")

    async def add_numbers(self, a: float, b: float) -> dict[str, Any]:
        """Add two numbers using the math plugin."""
        if MOCK_MODE:
            result = a + b
            return {
                "operation": "add",
                "inputs": {"a": a, "b": b},
                "result": result,
                "success": True,
                "mock": True,
            }

        try:
            # Create arguments
            args = sk.KernelArguments(input=str(a), amount=str(b))

            # Call the Add function
            result = await self.math_plugin["Add"].invoke(self.kernel, args)

            return {
                "operation": "add",
                "inputs": {"a": a, "b": b},
                "result": float(result.value) if result.value else None,
                "success": True,
                "raw_result": str(result.value),
            }

        except Exception as e:
            return {
                "operation": "add",
                "inputs": {"a": a, "b": b},
                "result": None,
                "success": False,
                "error": str(e),
            }

    async def multiply_numbers(self, a: float, b: float) -> dict[str, Any]:
        """Multiply two numbers using the math plugin."""
        if MOCK_MODE:
            result = a * b
            return {
                "operation": "multiply",
                "inputs": {"a": a, "b": b},
                "result": result,
                "success": True,
                "mock": True,
            }

        try:
            args = sk.KernelArguments(input=str(a), amount=str(b))
            result = await self.math_plugin["Multiply"].invoke(self.kernel, args)

            return {
                "operation": "multiply",
                "inputs": {"a": a, "b": b},
                "result": float(result.value) if result.value else None,
                "success": True,
                "raw_result": str(result.value),
            }

        except Exception as e:
            return {
                "operation": "multiply",
                "inputs": {"a": a, "b": b},
                "result": None,
                "success": False,
                "error": str(e),
            }

    def get_results_summary(self) -> dict[str, Any]:
        """Get a summary of all operations performed."""
        return {
            "total_operations": len(self.results),
            "successful_operations": len([r for r in self.results if r["success"]]),
            "failed_operations": len([r for r in self.results if not r["success"]]),
            "operations": self.results.copy(),
        }


async def main():
    """Run simple math examples."""
    print("🧮 Simple Math Plugin Example")
    print("=" * 40)

    # Create and setup agent
    agent = SimpleMathAgent()
    await agent.setup()

    # Test cases
    test_cases = [(10, 5), (25, 3), (100, 0.5), (-5, 10)]

    print("\n📊 Addition Tests:")
    for a, b in test_cases:
        result = await agent.add_numbers(a, b)
        agent.results.append(result)

        status = "✅" if result["success"] else "❌"
        print(f"  {status} {a} + {b} = {result['result']}")

        if not result["success"]:
            print(f"    Error: {result['error']}")

    print("\n📊 Multiplication Tests:")
    for a, b in test_cases:
        result = await agent.multiply_numbers(a, b)
        agent.results.append(result)

        status = "✅" if result["success"] else "❌"
        print(f"  {status} {a} × {b} = {result['result']}")

        if not result["success"]:
            print(f"    Error: {result['error']}")

    # Show summary
    print("\n📈 Results Summary:")
    summary = agent.get_results_summary()
    print(f"  Total operations: {summary['total_operations']}")
    print(f"  Successful: {summary['successful_operations']}")
    print(f"  Failed: {summary['failed_operations']}")

    if summary["failed_operations"] > 0:
        print("\n❌ Failed Operations:")
        for result in summary["operations"]:
            if not result["success"]:
                print(f"  {result['operation']}: {result['error']}")

    print("\n✅ Math example completed!")


def process_row(question: str, **kwargs) -> dict[str, Any]:
    """Process a single row for experimentation."""
    if MOCK_MODE:
        # Simple mock math processing
        import re

        # Extract numbers and operation from question
        if "+" in question:
            numbers = re.findall(r"\d+", question)
            if len(numbers) >= 2:
                result = int(numbers[0]) + int(numbers[1])
                return {"data_output": str(result)}
        elif "*" in question:
            numbers = re.findall(r"\d+", question)
            if len(numbers) >= 2:
                result = int(numbers[0]) * int(numbers[1])
                return {"data_output": str(result)}
        elif "-" in question:
            numbers = re.findall(r"\d+", question)
            if len(numbers) >= 2:
                result = int(numbers[0]) - int(numbers[1])
                return {"data_output": str(result)}

        return {"data_output": "unknown"}
    else:
        # Use actual Semantic Kernel agent
        agent = SimpleMathAgent()
        try:
            result = asyncio.run(agent.process_question(question))
            return {"data_output": result.get("answer", "unknown")}
        except Exception as e:
            return {"data_output": "error", "error": str(e)}


if __name__ == "__main__":
    asyncio.run(main())
