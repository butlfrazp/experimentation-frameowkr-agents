# Simple Semantic Kernel Examples

This directory contains focused, easy-to-understand examples of Semantic Kernel agent functionality. Each example demonstrates a specific aspect without the complexity of the full framework.

## 📁 Examples Overview

### 1. Basic Math (`01_basic_math.py`)
**Focus**: Simple plugin usage and direct function calls
- ✅ Basic Semantic Kernel setup
- ✅ Math plugin registration
- ✅ Direct function invocation
- ✅ Result handling and error management
- ✅ Mock mode for testing without dependencies

**Key Learning**: How to set up a kernel, register plugins, and call functions directly.

### 2. Basic Chat (`02_basic_chat.py`)
**Focus**: Simple conversational interaction
- ✅ Chat functionality without function calling
- ✅ Conversation history management
- ✅ Basic response handling
- ✅ Simple conversation analysis

**Key Learning**: How to have basic conversations with context preservation.

### 3. Function Calling (`03_function_calling.py`)
**Focus**: Automatic function calling during chat
- ✅ Chat with automatic function calling enabled
- ✅ Function call detection and handling
- ✅ Integration of function results into responses
- ✅ Function call tracking and analysis

**Key Learning**: How the agent automatically decides when and how to call functions.

### 4. Conversation Flow (`04_conversation_flow.py`)
**Focus**: Multi-turn conversations with context
- ✅ Multi-turn conversation management
- ✅ Context preservation across turns
- ✅ Conversation analysis and metrics
- ✅ Conversation transcript generation

**Key Learning**: How to maintain context and analyze conversation patterns.

## 🚀 Quick Start

### Run All Examples
```bash
cd simple_examples
python run_all.py
```

### Run Individual Examples
```bash
# Basic math operations
python 01_basic_math.py

# Simple chat
python 02_basic_chat.py

# Function calling
python 03_function_calling.py

# Conversation flow
python 04_conversation_flow.py
```

## 🔧 Setup

### Option 1: With Semantic Kernel (Full Functionality)
```bash
# Install dependencies
pip install semantic-kernel openai

# Set API key
export OPENAI_API_KEY="your-api-key"

# Run examples
python 01_basic_math.py
```

### Option 2: Mock Mode (No Dependencies)
All examples include mock mode that runs without Semantic Kernel or OpenAI:
```bash
# No installation needed, just run:
python 01_basic_math.py
```

## 📊 Example Comparison

| Example | Dependencies | API Required | Function Calls | Conversation | Complexity |
|---------|--------------|--------------|----------------|--------------|------------|
| 01_basic_math | Optional | No | Direct only | No | ⭐ |
| 02_basic_chat | Optional | Yes* | No | Yes | ⭐⭐ |
| 03_function_calling | Optional | Yes* | Auto | Yes | ⭐⭐⭐ |
| 04_conversation_flow | Optional | Yes* | No | Multi-turn | ⭐⭐⭐ |

*API required for full functionality, but mock mode available

## 🎯 What Each Example Teaches

### 1. Basic Math - Core Concepts
```python
# Simple setup
agent = SimpleMathAgent()
await agent.setup()

# Direct function call
result = await agent.add_numbers(10, 5)
print(result['result'])  # 15.0
```

### 2. Basic Chat - Conversation Basics
```python
# Simple chat
agent = SimpleChatAgent()
response = await agent.chat("Hello!")
print(response['response'])  # AI response
```

### 3. Function Calling - Automatic Tools
```python
# Chat with automatic function calling
agent = FunctionCallingAgent()
result = await agent.chat_with_functions("What is 15 + 25?")
# Agent automatically calls math plugin and integrates result
```

### 4. Conversation Flow - Context Management
```python
# Multi-turn conversation
agent = ConversationAgent()
await agent.start_conversation()

# Each message builds on previous context
await agent.send_message("Hello!")
await agent.send_message("Tell me about that topic we discussed")
# Agent remembers previous context
```

## 🔍 Understanding the Progression

1. **Start with 01_basic_math.py** - Learn the fundamentals
2. **Move to 02_basic_chat.py** - Understand conversations
3. **Try 03_function_calling.py** - See automatic function integration
4. **Finish with 04_conversation_flow.py** - Master context management

## 🛠 Customization

Each example is designed to be easily modified:

### Add Your Own Functions
```python
# In any example, add custom functions
async def my_custom_function(self, input_data):
    # Your logic here
    return {"result": "processed", "success": True}
```

### Change Models
```python
# Modify the model used
agent = SimpleAgent(model_name="gpt-4")  # Use GPT-4 instead
```

### Adjust Settings
```python
# Modify AI behavior
execution_settings = sk.PromptExecutionSettings(
    temperature=0.9,  # More creative
    max_tokens=200    # Shorter responses
)
```

## 📈 Performance Expectations

### Mock Mode
- ⚡ Instant responses (< 1ms)
- 🔄 No external dependencies
- 🧪 Perfect for testing logic

### Full Mode (with OpenAI)
- ⏱️ Response times: 500-2000ms
- 💰 API costs: ~$0.001-0.01 per example run
- 🌐 Requires internet connection

## 🚨 Common Issues & Solutions

### "semantic_kernel not found"
- ✅ **Solution**: Run in mock mode or install: `pip install semantic-kernel`

### "OpenAI API key required"
- ✅ **Solution**: Set `OPENAI_API_KEY` environment variable or run mock mode

### "Function calls not working"
- ✅ **Check**: API key is set and model supports function calling (GPT-3.5-turbo+)

### "Responses are slow"
- ✅ **Try**: Use mock mode for testing, or reduce max_tokens setting

## 🔗 Integration with Main Framework

These examples use the same data structures and patterns as the main experimentation framework:

```python
# Convert simple example results for framework use
framework_data = {
    "data_output": {
        "result": example_result["result"],
        "success": example_result["success"],
        "duration_ms": example_result.get("duration_ms", 0)
    },
    "metadata": example_result.get("metadata", {})
}
```

## 📚 Next Steps

After mastering these examples:

1. **Combine Concepts**: Mix function calling with conversation flow
2. **Add Custom Plugins**: Create your own Semantic Kernel plugins
3. **Scale Up**: Use the full framework for complex experiments
4. **Deploy**: Turn examples into production services

## 💡 Tips for Learning

- **Start Simple**: Begin with 01_basic_math.py even if you want to do complex things
- **Use Mock Mode**: Test your understanding without API costs
- **Read the Code**: Each example is heavily commented
- **Modify Examples**: Change inputs and see what happens
- **Compare Outputs**: Run with and without mock mode to see differences

Happy learning! 🚀