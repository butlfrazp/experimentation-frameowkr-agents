"""
Simple echo module that imports and registers custom evaluators.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import custom evaluators to register them
import custom_evaluators

def run(**kwargs) -> str:
    """
    Simple echo processor that returns the input.
    
    Args:
        **kwargs: All data fields from the dataset row
        
    Returns:
        The processed output
    """
    # Extract the input field
    input_text = kwargs.get('input', 'No input provided')
    return f"Echo: {input_text}"