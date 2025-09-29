"""
Simple math module for demonstrating the experimentation platform.
This module handles basic math questions.
"""

def run(**kwargs) -> str:
    """
    Simple math processor that handles basic arithmetic.
    
    Args:
        **kwargs: All data fields from the dataset row
        
    Returns:
        The computed result
    """
    question = kwargs.get('question', 'No question provided')
    
    # Simple math evaluation
    try:
        # Extract numbers and operation from question
        if '+' in question:
            parts = question.replace('What is ', '').replace('?', '').split(' + ')
            if len(parts) == 2:
                result = int(parts[0].strip()) + int(parts[1].strip())
                return str(result)
        elif '*' in question:
            parts = question.replace('What is ', '').replace('?', '').split(' * ')
            if len(parts) == 2:
                result = int(parts[0].strip()) * int(parts[1].strip())
                return str(result)
        elif '-' in question:
            parts = question.replace('What is ', '').replace('?', '').split(' - ')
            if len(parts) == 2:
                result = int(parts[0].strip()) - int(parts[1].strip())
                return str(result)
        elif '/' in question:
            parts = question.replace('What is ', '').replace('?', '').split(' / ')
            if len(parts) == 2:
                result = int(parts[0].strip()) / int(parts[1].strip())
                return str(int(result) if result.is_integer() else result)
    except (ValueError, IndexError):
        pass
    
    return f"Cannot compute: {question}"