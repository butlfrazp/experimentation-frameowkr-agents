# Semantic Kernel Agent Examples

Clean, focused examples for learning and evaluating Semantic Kernel agent functionality.

## 🎯 Quick Start (Recommended)

**Start with the simple examples** - they're designed for easy learning and evaluation:

```bash
cd simple_examples

# Run individual focused examples (no setup needed!)
python 01_basic_math.py       # Plugin basics
python 02_basic_chat.py       # Chat basics  
python 03_function_calling.py # Function calling
python 04_conversation_flow.py # Context management

# Or run all examples
python run_all.py
```

**Why start here?**
- ✅ **No dependencies** required (mock mode included)
- ✅ **Clear, focused** functionality 
- ✅ **Easy to understand** and modify
- ✅ **Perfect for evaluation** - clean metrics
- ✅ **Progressive learning** - build from simple to complex

## 📁 Directory Structure

```
semantic_kernel/
├── simple_examples/          # 🎯 START HERE - Clean, focused examples
│   ├── 01_basic_math.py      # Plugin setup and function calls
│   ├── 02_basic_chat.py      # Simple conversation
│   ├── 03_function_calling.py # Auto function calling
│   ├── 04_conversation_flow.py # Context management
│   ├── run_all.py           # Run all examples
│   └── README.md            # Detailed documentation
├── requirements.txt         # Dependencies
├── setup.py                # Environment checker
└── README.md               # This file
```

## 🚀 Full Setup (Optional)

If you want to use real OpenAI integration instead of mock mode:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Check setup
python setup.py

# 4. Run examples with real AI
cd simple_examples && python run_all.py
```

## 📊 What Each Example Teaches

| Example | Focus | Complexity | What You Learn |
|---------|--------|------------|----------------|
| 01_basic_math.py | Plugin mechanics | ⭐ | Setup, registration, function calls |
| 02_basic_chat.py | Conversation basics | ⭐⭐ | Chat, history, context |
| 03_function_calling.py | Auto function calling | ⭐⭐⭐ | When/how agents call functions |
| 04_conversation_flow.py | Context management | ⭐⭐⭐ | Multi-turn conversations |

## 🔬 For Evaluation

Each example provides **clean, focused metrics**:

```bash
# Get specific capability metrics
python 01_basic_math.py      # Plugin integration success rate
python 02_basic_chat.py      # Conversation quality metrics
python 03_function_calling.py # Function call accuracy
python 04_conversation_flow.py # Context preservation metrics
```

## 🎓 Learning Path

1. **Start**: `01_basic_math.py` - Learn the fundamentals
2. **Add**: `02_basic_chat.py` - Understand conversations  
3. **Enhance**: `03_function_calling.py` - See automatic tools
4. **Master**: `04_conversation_flow.py` - Handle complex context

## 📚 More Information

- **`simple_examples/README.md`** - Detailed documentation
- **Framework Integration** - Examples use same data structures as main platform

## 💡 Tips

- **Use mock mode** for instant testing (no API key needed)
- **Start simple** even if you want to do complex things
- **Modify examples** to test your own ideas
- **Read the code** - it's heavily commented for learning

Happy learning! 🚀