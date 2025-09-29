#!/usr/bin/env python3
"""
Simple Chat Example

This example demonstrates:
- Basic chat functionality
- Simple conversation flow
- Response handling
- No function calling complexity
"""

import asyncio
import os
from datetime import datetime
from typing import Any

# Mock imports for testing without dependencies
try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

    MOCK_MODE = False
except ImportError:
    MOCK_MODE = True
    print("ℹ️  Running in mock mode (semantic-kernel not installed)")


class SimpleChatAgent:
    """A simple chat agent without function calling."""

    def __init__(self):
        self.kernel = None
        self.chat_service = None
        self.conversation = []

    async def setup(self):
        """Initialize the kernel for basic chat."""
        if MOCK_MODE:
            print("✅ Mock chat agent ready")
            return

        # Create kernel
        self.kernel = sk.Kernel()

        # Add OpenAI service
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")

        self.chat_service = OpenAIChatCompletion(ai_model_id="gpt-3.5-turbo", api_key=api_key)
        self.kernel.add_service(self.chat_service)

        print("✅ Chat agent ready")

    async def chat(self, message: str) -> dict[str, Any]:
        """Send a message and get a response."""
        start_time = datetime.now()

        # Add user message to conversation
        self.conversation.append(
            {"role": "user", "content": message, "timestamp": start_time.isoformat()}
        )

        if MOCK_MODE:
            # Generate mock response
            response_content = self._generate_mock_response(message)

            end_time = datetime.now()
            self.conversation.append(
                {
                    "role": "assistant",
                    "content": response_content,
                    "timestamp": end_time.isoformat(),
                }
            )

            return {
                "message": message,
                "response": response_content,
                "duration_ms": (end_time - start_time).total_seconds() * 1000,
                "success": True,
                "mock": True,
                "conversation_length": len(self.conversation),
            }

        try:
            # Create chat history
            chat_history = sk.ChatHistory()

            # Add recent conversation (last 10 messages)
            recent_messages = self.conversation[-20:]  # Keep context reasonable
            for msg in recent_messages[:-1]:  # Exclude the current message
                if msg["role"] == "user":
                    chat_history.add_user_message(msg["content"])
                else:
                    chat_history.add_assistant_message(msg["content"])

            # Add current message
            chat_history.add_user_message(message)

            # Get response
            execution_settings = sk.PromptExecutionSettings(
                service_id=self.chat_service.service_id, max_tokens=500, temperature=0.7
            )

            response = await self.chat_service.get_chat_message_content(
                chat_history=chat_history, settings=execution_settings, kernel=self.kernel
            )

            end_time = datetime.now()
            response_content = str(response.content) if response.content else ""

            # Add assistant response to conversation
            self.conversation.append(
                {
                    "role": "assistant",
                    "content": response_content,
                    "timestamp": end_time.isoformat(),
                }
            )

            return {
                "message": message,
                "response": response_content,
                "duration_ms": (end_time - start_time).total_seconds() * 1000,
                "success": True,
                "model": "gpt-3.5-turbo",
                "conversation_length": len(self.conversation),
                "token_usage": getattr(response, "usage", None),
            }

        except Exception as e:
            end_time = datetime.now()
            return {
                "message": message,
                "response": None,
                "duration_ms": (end_time - start_time).total_seconds() * 1000,
                "success": False,
                "error": str(e),
                "conversation_length": len(self.conversation),
            }

    def _generate_mock_response(self, message: str) -> str:
        """Generate a simple mock response."""
        message_lower = message.lower()

        if "hello" in message_lower or "hi" in message_lower:
            return "Hello! How can I help you today?"
        elif "how are you" in message_lower:
            return "I'm doing well, thank you for asking! I'm here to help."
        elif "weather" in message_lower:
            return "I don't have access to current weather data, but you could check a weather app or website."
        elif "time" in message_lower:
            return f"I don't have real-time access, but when I generated this response it was around {datetime.now().strftime('%I:%M %p')}."
        elif "help" in message_lower:
            return "I'm a simple chat assistant. I can have conversations with you, but I don't have any special functions enabled in this example."
        else:
            return f"That's interesting! You mentioned: '{message}'. What would you like to know more about?"

    def get_conversation_summary(self) -> dict[str, Any]:
        """Get a summary of the conversation."""
        user_messages = [msg for msg in self.conversation if msg["role"] == "user"]
        assistant_messages = [msg for msg in self.conversation if msg["role"] == "assistant"]

        return {
            "total_messages": len(self.conversation),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "conversation_start": self.conversation[0]["timestamp"] if self.conversation else None,
            "last_message": self.conversation[-1]["timestamp"] if self.conversation else None,
        }

    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation.clear()
        print("🧹 Conversation cleared")


async def main():
    """Run simple chat examples."""
    print("💬 Simple Chat Example")
    print("=" * 30)

    # Create and setup agent
    agent = SimpleChatAgent()
    await agent.setup()

    # Test messages
    test_messages = [
        "Hello!",
        "How are you doing today?",
        "Can you tell me about the weather?",
        "What time is it?",
        "I need some help with something",
        "Thank you for your help!",
    ]

    print("\n🗣️  Conversation:")
    print("-" * 30)

    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. User: {message}")

        result = await agent.chat(message)

        if result["success"]:
            print(f"   Agent: {result['response']}")
            print(f"   Duration: {result['duration_ms']:.1f}ms")
        else:
            print(f"   ❌ Error: {result['error']}")

        # Small delay for readability
        await asyncio.sleep(0.1)

    # Show conversation summary
    print("\n📊 Conversation Summary:")
    print("-" * 30)
    summary = agent.get_conversation_summary()
    print(f"Total messages: {summary['total_messages']}")
    print(f"User messages: {summary['user_messages']}")
    print(f"Assistant messages: {summary['assistant_messages']}")

    if summary["conversation_start"]:
        print(f"Started: {summary['conversation_start'][:19]}")
        print(f"Ended: {summary['last_message'][:19]}")

    print("\n✅ Chat example completed!")


if __name__ == "__main__":
    asyncio.run(main())
