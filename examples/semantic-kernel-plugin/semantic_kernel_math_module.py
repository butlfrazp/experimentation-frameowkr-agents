"""
Semantic Kernel Math Plugin for experimentation platform.
This demonstrates how to create SK plugins and use them in experiments.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# Import custom evaluators to register them

import asyncio
import json
from typing import Annotated

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatCompletion
from semantic_kernel.functions import kernel_function


class MathPlugin:
    """
    A Semantic Kernel plugin that provides mathematical operations.
    """

    @kernel_function(description="Add two numbers together", name="add_numbers")
    def add_numbers(
        self,
        first_number: Annotated[float, "The first number to add"] = 0,
        second_number: Annotated[float, "The second number to add"] = 0,
    ) -> Annotated[str, "The sum of the two numbers"]:
        """Add two numbers and return the result as a string."""
        result = first_number + second_number
        return f"The sum of {first_number} and {second_number} is {result}"

    @kernel_function(description="Multiply two numbers together", name="multiply_numbers")
    def multiply_numbers(
        self,
        first_number: Annotated[float, "The first number to multiply"] = 0,
        second_number: Annotated[float, "The second number to multiply"] = 0,
    ) -> Annotated[str, "The product of the two numbers"]:
        """Multiply two numbers and return the result as a string."""
        result = first_number * second_number
        return f"The product of {first_number} and {second_number} is {result}"

    @kernel_function(description="Calculate the square of a number", name="square_number")
    def square_number(
        self, number: Annotated[float, "The number to square"] = 0
    ) -> Annotated[str, "The square of the number"]:
        """Calculate the square of a number."""
        result = number**2
        return f"The square of {number} is {result}"


async def create_kernel_with_math_plugin():
    """Create a Semantic Kernel instance with the math plugin."""
    kernel = Kernel()

    # Add OpenAI service (you can also use Azure OpenAI)
    # For demo purposes, we'll use a mock service if no API key is available
    try:
        if os.getenv("OPENAI_API_KEY"):
            kernel.add_service(
                OpenAIChatCompletion(
                    ai_model_id="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY")
                )
            )
        elif os.getenv("AZURE_OPENAI_API_KEY"):
            kernel.add_service(
                AzureChatCompletion(
                    ai_model_id="gpt-35-turbo",
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                    api_version="2024-02-01",
                )
            )
        else:
            print("⚠️  No OpenAI API key found - using direct plugin calls only")
    except Exception as e:
        print(f"⚠️  AI service setup failed: {e} - using direct plugin calls only")

    # Import the math plugin
    math_plugin = MathPlugin()
    kernel.add_plugin(math_plugin, plugin_name="MathPlugin")

    return kernel


async def process_math_request(kernel: Kernel, request: str, operation_data: dict) -> str:
    """
    Process a math request using the Semantic Kernel and math plugin.

    Args:
        kernel: The Semantic Kernel instance
        request: The natural language request
        operation_data: Dictionary containing operation details

    Returns:
        The result of the math operation
    """
    try:
        # Extract operation details
        operation = operation_data.get("operation", "add")
        first_num = float(operation_data.get("first_number", 0))
        second_num = float(operation_data.get("second_number", 0))

        # Call the appropriate plugin function directly
        math_plugin = kernel.plugins["MathPlugin"]

        if operation == "add":
            result = await kernel.invoke(
                math_plugin["add_numbers"], first_number=first_num, second_number=second_num
            )
        elif operation == "multiply":
            result = await kernel.invoke(
                math_plugin["multiply_numbers"], first_number=first_num, second_number=second_num
            )
        elif operation == "square":
            result = await kernel.invoke(math_plugin["square_number"], number=first_num)
        else:
            return f"Unknown operation: {operation}"

        return str(result)

    except Exception as e:
        return f"Error processing math request: {str(e)}"


# Main processing function for the experiment
def run(**kwargs) -> str:
    """
    Main function called by the experimentation platform.

    Args:
        **kwargs: All data fields from the dataset row

    Returns:
        The result of processing the math operation
    """
    try:
        # Extract the input fields
        request = kwargs.get("request", "No request provided")
        operation_data_str = kwargs.get("operation_data", "{}")

        # Parse operation data if it's a string
        if isinstance(operation_data_str, str):
            try:
                operation_data = json.loads(operation_data_str)
            except json.JSONDecodeError:
                return f"Invalid operation data format: {operation_data_str}"
        else:
            operation_data = operation_data_str

        # Create kernel and process the request
        async def process():
            kernel = await create_kernel_with_math_plugin()
            return await process_math_request(kernel, request, operation_data)

        # Run the async function
        result = asyncio.run(process())
        return result

    except Exception as e:
        return f"Error in semantic kernel processing: {str(e)}"


# Demo function to test the plugin directly
async def demo_math_plugin():
    """Demonstrate the math plugin functionality."""
    print("🧮 Semantic Kernel Math Plugin Demo")
    print("=" * 40)

    kernel = await create_kernel_with_math_plugin()
    math_plugin = kernel.plugins["MathPlugin"]

    # Test addition
    print("\n➕ Testing Addition:")
    result = await kernel.invoke(math_plugin["add_numbers"], first_number=15, second_number=25)
    print(f"   Result: {result}")

    # Test multiplication
    print("\n✖️  Testing Multiplication:")
    result = await kernel.invoke(math_plugin["multiply_numbers"], first_number=7, second_number=8)
    print(f"   Result: {result}")

    # Test square
    print("\n🔢 Testing Square:")
    result = await kernel.invoke(math_plugin["square_number"], number=9)
    print(f"   Result: {result}")

    print("\n✅ All plugin functions working correctly!")


if __name__ == "__main__":
    asyncio.run(demo_math_plugin())
