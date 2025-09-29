"""
Simple conversation module for quickstart tutorial.
Simulates basic AI conversation responses.
"""


def run(input: str, context: str = None, **kwargs) -> str:
    """
    Simple conversation simulation for quickstart demo.

    Args:
        input: User input message
        context: Optional context for the conversation
        **kwargs: Additional arguments (e.g., expected_output)

    Returns:
        Simulated AI response
    """

    # Simple response patterns based on input
    input_lower = input.lower()

    if "hello" in input_lower or "hi" in input_lower:
        return "Hello! I'm doing great, thank you for asking. How can I assist you today?"

    elif "weather" in input_lower:
        return (
            "I don't have access to current weather data, but I can help you find "
            "weather resources for your area."
        )

    elif "python" in input_lower or "programming" in input_lower:
        return (
            "I'd be happy to help with Python programming! What specific topic or "
            "challenge are you working on?"
        )

    elif "help" in input_lower:
        return (
            "Of course! I'm here to help. Could you tell me more about what you need "
            "assistance with?"
        )

    else:
        # Default helpful response
        return (
            f"Thank you for your message. I understand you're asking about '{input}'. "
            f"How can I best help you with this?"
        )


# Optional: Add some conversation context handling
def get_response_quality_score(response: str) -> float:
    """
    Simple quality scoring for demonstration.
    In real applications, this would be more sophisticated.
    """
    quality_indicators = [
        len(response) > 20,  # Reasonable length
        "?" in response,  # Asks clarifying questions
        "help" in response.lower(),  # Offers assistance
        response.endswith((".", "!", "?")),  # Proper punctuation
    ]

    return sum(quality_indicators) / len(quality_indicators)


if __name__ == "__main__":
    # Test the module directly
    test_inputs = ["Hello, how are you?", "What's the weather like?", "Can you help with Python?"]

    for test_input in test_inputs:
        response = run(input=test_input)
        quality = get_response_quality_score(response)
        print(f"Input: {test_input}")
        print(f"Response: {response}")
        print(f"Quality Score: {quality:.2f}")
        print("-" * 50)
