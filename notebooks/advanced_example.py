# Example Module for Advanced Experimentation

def run(input_text: str, context: dict = None) -> str:
    """
    Advanced example module with contextual responses.
    
    This module demonstrates more sophisticated processing patterns
    that data scientists might want to experiment with.
    
    Args:
        input_text: The input text to process
        context: Optional context dictionary with additional parameters
        
    Returns:
        Processed response string
    """
    
    # Initialize context if not provided
    if context is None:
        context = {}
    
    # Get processing mode from context
    mode = context.get('mode', 'helpful')
    temperature = context.get('temperature', 0.7)
    
    # Process based on input patterns
    input_lower = input_text.lower()
    
    # Question answering
    if '?' in input_text:
        if 'capital' in input_lower:
            return _answer_geography_question(input_text, mode)
        elif 'math' in input_lower or any(op in input_text for op in ['+', '-', '*', '/', '=']):
            return _answer_math_question(input_text, mode)
        elif 'science' in input_lower or 'photosynthesis' in input_lower:
            return _answer_science_question(input_text, mode)
        else:
            return _answer_general_question(input_text, mode)
    
    # Summarization requests
    elif any(word in input_lower for word in ['summarize', 'summary', 'brief']):
        return _create_summary(input_text, mode)
    
    # Translation requests
    elif any(word in input_lower for word in ['translate', 'translation']):
        return _translate_text(input_text, mode)
    
    # Default response
    else:
        return _generate_default_response(input_text, mode, temperature)


def _answer_geography_question(question: str, mode: str) -> str:
    """Handle geography-related questions."""
    question_lower = question.lower()
    
    if 'france' in question_lower:
        if mode == 'concise':
            return "Paris."
        elif mode == 'detailed':
            return "Paris is the capital and largest city of France, located in the north-central part of the country along the Seine River."
        else:
            return "The capital of France is Paris."
    
    elif 'japan' in question_lower:
        if mode == 'concise':
            return "Tokyo."
        elif mode == 'detailed':
            return "Tokyo is the capital of Japan and one of the world's most populous metropolitan areas."
        else:
            return "The capital of Japan is Tokyo."
    
    else:
        return f"I'd be happy to help with geography questions! Could you be more specific about {question}?"


def _answer_math_question(question: str, mode: str) -> str:
    """Handle mathematical questions."""
    import re
    
    # Simple arithmetic detection
    if '2 + 2' in question or '2+2' in question:
        if mode == 'concise':
            return "4"
        elif mode == 'detailed':
            return "2 + 2 = 4. This is basic addition where we combine two quantities of 2 to get 4."
        else:
            return "2 + 2 equals 4."
    
    # Look for other simple patterns
    math_pattern = r'(\d+)\s*([+\-*/])\s*(\d+)'
    match = re.search(math_pattern, question)
    
    if match:
        num1, operator, num2 = match.groups()
        try:
            a, b = int(num1), int(num2)
            if operator == '+':
                result = a + b
                operation = "addition"
            elif operator == '-':
                result = a - b
                operation = "subtraction"
            elif operator == '*':
                result = a * b
                operation = "multiplication"
            elif operator == '/':
                result = a / b if b != 0 else "undefined (division by zero)"
                operation = "division"
            
            if mode == 'concise':
                return str(result)
            elif mode == 'detailed':
                return f"{num1} {operator} {num2} = {result}. This is a {operation} operation."
            else:
                return f"{num1} {operator} {num2} = {result}"
                
        except (ValueError, ZeroDivisionError):
            pass
    
    return "I can help with basic math! Try asking something like 'What is 5 + 3?'"


def _answer_science_question(question: str, mode: str) -> str:
    """Handle science-related questions."""
    question_lower = question.lower()
    
    if 'photosynthesis' in question_lower:
        if mode == 'concise':
            return "Plants convert light energy to chemical energy using CO2 and water."
        elif mode == 'detailed':
            return ("Photosynthesis is the biological process by which plants, algae, and some bacteria "
                   "convert light energy (usually from sunlight) into chemical energy stored in glucose. "
                   "This process uses carbon dioxide from the air and water from the soil, producing "
                   "oxygen as a byproduct. The overall equation is: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2.")
        else:
            return "Photosynthesis is how plants make food using sunlight, water, and carbon dioxide."
    
    elif 'gravity' in question_lower:
        if mode == 'concise':
            return "Force that attracts objects toward each other."
        elif mode == 'detailed':
            return ("Gravity is a fundamental force of attraction between objects with mass. "
                   "On Earth, it gives weight to physical objects and causes them to fall toward the ground.")
        else:
            return "Gravity is the force that attracts objects toward each other, like keeping us on Earth."
    
    else:
        return "I can help explain scientific concepts! What would you like to know about?"


def _answer_general_question(question: str, mode: str) -> str:
    """Handle general questions."""
    if mode == 'concise':
        return f"Regarding: {question[:30]}... I'd need more context to provide a specific answer."
    elif mode == 'detailed':
        return (f"Thank you for your question: '{question}'. To provide you with the most accurate "
               f"and helpful response, I would need some additional context or clarification about "
               f"what specific aspect you're most interested in.")
    else:
        return f"That's an interesting question about {question}. Could you provide more details?"


def _create_summary(text: str, mode: str) -> str:
    """Create summaries of text."""
    # Extract the main content (remove "summarize" command words)
    import re
    content = re.sub(r'\b(summarize|summary|brief)\b', '', text, flags=re.IGNORECASE).strip()
    
    if len(content) < 10:
        return "Please provide more text to summarize."
    
    # Simple summarization approach
    sentences = content.split('.')
    key_sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    if mode == 'concise':
        return f"Summary: {key_sentences[0] if key_sentences else content[:50]}..."
    elif mode == 'detailed':
        summary_points = key_sentences[:3] if len(key_sentences) >= 3 else key_sentences
        return f"Summary:\n" + "\n".join(f"• {point.strip()}" for point in summary_points)
    else:
        return f"Key point: {key_sentences[0] if key_sentences else content[:100]}..."


def _translate_text(text: str, mode: str) -> str:
    """Handle translation requests."""
    # This is a mock translation function
    if 'hello' in text.lower():
        return "Bonjour (French), Hola (Spanish), Guten Tag (German)"
    elif 'goodbye' in text.lower():
        return "Au revoir (French), Adiós (Spanish), Auf Wiedersehen (German)"  
    else:
        return "I can provide basic translations for common phrases. Try 'hello' or 'goodbye'!"


def _generate_default_response(text: str, mode: str, temperature: float) -> str:
    """Generate default responses."""
    
    # Vary response based on temperature
    if temperature < 0.3:
        # Conservative response
        response_templates = [
            f"I understand you mentioned: {text[:50]}{'...' if len(text) > 50 else ''}",
            f"Thank you for sharing: {text[:50]}{'...' if len(text) > 50 else ''}"
        ]
    elif temperature > 0.8:
        # Creative response
        response_templates = [
            f"Interesting perspective on: {text[:50]}{'...' if len(text) > 50 else ''}! Tell me more.",
            f"That's a fascinating point about {text[:30]}{'...' if len(text) > 30 else ''}. What inspired this thought?"
        ]
    else:
        # Balanced response
        response_templates = [
            f"I see you're discussing: {text[:50]}{'...' if len(text) > 50 else ''}. How can I help?",
            f"Thanks for the input about: {text[:50]}{'...' if len(text) > 50 else ''}. What would you like to know?"
        ]
    
    # Select response based on text length (simple hash-like selection)
    response_index = len(text) % len(response_templates)
    return response_templates[response_index]


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Advanced Module Testing")
    print("=" * 40)
    
    test_cases = [
        # Questions
        ("What is the capital of France?", {"mode": "helpful"}),
        ("What is the capital of Japan?", {"mode": "detailed"}),
        ("What is 5 + 3?", {"mode": "concise"}),
        ("Explain photosynthesis", {"mode": "detailed"}),
        
        # Different modes
        ("What is gravity?", {"mode": "concise"}),
        ("What is gravity?", {"mode": "detailed"}),
        
        # Summaries
        ("Summarize this: Artificial intelligence is transforming many industries. It helps automate tasks and provides insights.", {"mode": "detailed"}),
        
        # Temperature variations
        ("Hello there!", {"mode": "helpful", "temperature": 0.2}),
        ("Hello there!", {"mode": "helpful", "temperature": 0.9}),
    ]
    
    for i, (test_input, context) in enumerate(test_cases, 1):
        print(f"\n{i}. Input: {test_input}")
        print(f"   Context: {context}")
        result = run(test_input, context)
        print(f"   Output: {result}")