#!/usr/bin/env python3
"""
Simple Conversation Flow Example

This example demonstrates:
- Multi-turn conversation with context
- Conversation state management
- Context preservation across messages
- Simple conversation analysis
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


class ConversationAgent:
    """Agent focused on maintaining conversation context."""

    def __init__(self):
        self.kernel = None
        self.chat_service = None
        self.conversation_history = []
        self.conversation_metadata = {
            "start_time": None,
            "topic_changes": 0,
            "user_questions": 0,
            "agent_responses": 0,
        }

    async def setup(self):
        """Initialize the conversation agent."""
        if MOCK_MODE:
            print("✅ Mock conversation agent ready")
            return

        # Create kernel
        self.kernel = sk.Kernel()

        # Add OpenAI service
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")

        self.chat_service = OpenAIChatCompletion(ai_model_id="gpt-3.5-turbo", api_key=api_key)
        self.kernel.add_service(self.chat_service)

        print("✅ Conversation agent ready")

    async def start_conversation(self):
        """Start a new conversation."""
        self.conversation_history.clear()
        self.conversation_metadata = {
            "start_time": datetime.now(),
            "topic_changes": 0,
            "user_questions": 0,
            "agent_responses": 0,
        }
        print("🆕 New conversation started")

    async def send_message(self, message: str) -> dict[str, Any]:
        """Send a message and maintain conversation context."""
        start_time = datetime.now()

        # Initialize metadata if needed
        if not self.conversation_metadata["start_time"]:
            self.conversation_metadata["start_time"] = start_time

        # Track user message
        if "?" in message:
            self.conversation_metadata["user_questions"] += 1

        # Add to conversation history
        self.conversation_history.append(
            {
                "role": "user",
                "content": message,
                "timestamp": start_time,
                "turn": len(self.conversation_history) + 1,
            }
        )

        if MOCK_MODE:
            response_content = self._generate_contextual_mock_response(message)
        else:
            try:
                response_content = await self._get_ai_response(message)
            except Exception as e:
                return {
                    "message": message,
                    "response": None,
                    "success": False,
                    "error": str(e),
                    "turn": len(self.conversation_history),
                }

        end_time = datetime.now()

        # Add agent response to history
        self.conversation_history.append(
            {
                "role": "assistant",
                "content": response_content,
                "timestamp": end_time,
                "turn": len(self.conversation_history) + 1,
            }
        )

        # Update metadata
        self.conversation_metadata["agent_responses"] += 1

        return {
            "message": message,
            "response": response_content,
            "success": True,
            "turn": len(self.conversation_history) // 2,  # Conversation turns
            "duration_ms": (end_time - start_time).total_seconds() * 1000,
            "context_length": len(self.conversation_history),
        }

    async def _get_ai_response(self, message: str) -> str:
        """Get AI response with conversation context."""
        # Create chat history with context
        chat_history = sk.ChatHistory()

        # Add conversation context (last 10 exchanges to keep it manageable)
        recent_history = self.conversation_history[-20:]  # Last 20 messages (10 exchanges)
        for msg in recent_history[:-1]:  # Exclude current message
            if msg["role"] == "user":
                chat_history.add_user_message(msg["content"])
            else:
                chat_history.add_assistant_message(msg["content"])

        # Add current message
        chat_history.add_user_message(message)

        # Get response
        execution_settings = sk.PromptExecutionSettings(
            service_id=self.chat_service.service_id,
            max_tokens=300,
            temperature=0.8,  # Slightly higher for more conversational responses
        )

        response = await self.chat_service.get_chat_message_content(
            chat_history=chat_history, settings=execution_settings, kernel=self.kernel
        )

        return str(response.content) if response.content else "I'm not sure how to respond to that."

    def _generate_contextual_mock_response(self, message: str) -> str:
        """Generate mock response that considers conversation context."""
        message_lower = message.lower()
        turn_number = len(self.conversation_history) // 2 + 1

        # Check for context references
        context_words = ["that", "it", "this", "earlier", "before", "mentioned"]
        has_context_reference = any(word in message_lower for word in context_words)

        # Get recent conversation topics
        recent_topics = []
        for msg in self.conversation_history[-4:]:  # Last 4 messages
            if msg["role"] == "user":
                if "weather" in msg["content"].lower():
                    recent_topics.append("weather")
                elif "food" in msg["content"].lower() or "eat" in msg["content"].lower():
                    recent_topics.append("food")
                elif "work" in msg["content"].lower() or "job" in msg["content"].lower():
                    recent_topics.append("work")

        # Generate contextual response
        if turn_number == 1:
            # First message
            if "hello" in message_lower or "hi" in message_lower:
                return "Hello! It's nice to meet you. What would you like to talk about today?"
            else:
                return f"Thanks for starting our conversation with '{message[:30]}...' What else is on your mind?"

        elif has_context_reference and recent_topics:
            # Reference to previous context
            topic = recent_topics[-1]
            return f"Yes, regarding the {topic} we were discussing - that's a good point. Tell me more about your thoughts on that."

        elif "thanks" in message_lower or "thank you" in message_lower:
            return "You're welcome! I'm enjoying our conversation. Is there anything else you'd like to discuss?"

        elif "?" in message:
            # Question - be helpful
            if "weather" in message_lower:
                return "I don't have real-time weather data, but you could check a weather app. What's the weather like where you are?"
            elif "time" in message_lower:
                return f"I don't have access to the current time, but our conversation started around turn {turn_number}. Are you in a hurry for something?"
            else:
                return f"That's an interesting question about '{message[:40]}...'. I don't have specific information, but what made you curious about that?"

        else:
            # General conversational response
            return f"I see we're on turn {turn_number} of our conversation. That's {message[:30]}... is quite thought-provoking. What's your perspective on that?"

    def get_conversation_analysis(self) -> dict[str, Any]:
        """Analyze the current conversation."""
        if not self.conversation_history:
            return {"status": "No conversation yet"}

        user_messages = [msg for msg in self.conversation_history if msg["role"] == "user"]
        assistant_messages = [
            msg for msg in self.conversation_history if msg["role"] == "assistant"
        ]

        # Calculate conversation duration
        duration = None
        if len(self.conversation_history) >= 2:
            start_time = self.conversation_history[0]["timestamp"]
            end_time = self.conversation_history[-1]["timestamp"]
            duration = (end_time - start_time).total_seconds()

        # Analyze message lengths
        user_msg_lengths = [len(msg["content"]) for msg in user_messages]
        assistant_msg_lengths = [len(msg["content"]) for msg in assistant_messages]

        return {
            "total_messages": len(self.conversation_history),
            "conversation_turns": len(user_messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "duration_seconds": duration,
            "user_questions": self.conversation_metadata["user_questions"],
            "avg_user_message_length": sum(user_msg_lengths) / len(user_msg_lengths)
            if user_msg_lengths
            else 0,
            "avg_assistant_message_length": sum(assistant_msg_lengths) / len(assistant_msg_lengths)
            if assistant_msg_lengths
            else 0,
            "conversation_started": self.conversation_metadata["start_time"].isoformat()
            if self.conversation_metadata["start_time"]
            else None,
        }

    def get_conversation_transcript(self) -> str:
        """Get a formatted transcript of the conversation."""
        if not self.conversation_history:
            return "No conversation yet."

        transcript = []
        for msg in self.conversation_history:
            role = "User" if msg["role"] == "user" else "Agent"
            timestamp = msg["timestamp"].strftime("%H:%M:%S")
            transcript.append(f"[{timestamp}] {role}: {msg['content']}")

        return "\n".join(transcript)


async def main():
    """Run conversation flow example."""
    print("💭 Conversation Flow Example")
    print("=" * 35)

    # Create and setup agent
    agent = ConversationAgent()
    await agent.setup()
    await agent.start_conversation()

    # Simulate a multi-turn conversation
    conversation_script = [
        "Hello! How are you doing today?",
        "I'm curious about artificial intelligence. What do you think about it?",
        "That's interesting. Can you tell me more about that?",
        "I work in technology too. Have you heard about recent AI developments?",
        "What about the weather? It's been quite unpredictable lately.",
        "Thanks for the great conversation! This has been very helpful.",
    ]

    print("\n🗣️  Multi-turn Conversation:")
    print("-" * 40)

    for i, message in enumerate(conversation_script, 1):
        print(f"\nTurn {i}:")
        print(f"User: {message}")

        result = await agent.send_message(message)

        if result["success"]:
            print(f"Agent: {result['response']}")
            print(
                f"Duration: {result['duration_ms']:.1f}ms | Context: {result['context_length']} messages"
            )
        else:
            print(f"❌ Error: {result['error']}")

        # Small delay for readability
        await asyncio.sleep(0.2)

    # Show conversation analysis
    print("\n📊 Conversation Analysis:")
    print("-" * 30)
    analysis = agent.get_conversation_analysis()

    print(f"Total messages: {analysis['total_messages']}")
    print(f"Conversation turns: {analysis['conversation_turns']}")
    print(f"User questions: {analysis['user_questions']}")
    print(
        f"Duration: {analysis['duration_seconds']:.1f} seconds"
        if analysis["duration_seconds"]
        else "Duration: N/A"
    )
    print(f"Avg user message length: {analysis['avg_user_message_length']:.1f} chars")
    print(f"Avg agent message length: {analysis['avg_assistant_message_length']:.1f} chars")

    # Show transcript
    print("\n📜 Conversation Transcript:")
    print("-" * 30)
    transcript = agent.get_conversation_transcript()
    # Show just the first few lines to avoid too much output
    transcript_lines = transcript.split("\n")
    for line in transcript_lines[:6]:  # Show first 6 lines
        print(line)
    if len(transcript_lines) > 6:
        print(f"... and {len(transcript_lines) - 6} more messages")

    print("\n✅ Conversation flow example completed!")


if __name__ == "__main__":
    asyncio.run(main())
