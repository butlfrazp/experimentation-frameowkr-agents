"""
Simple echo module for demonstrating the experimentation platform.
This module simply echoes back the input as output.
"""

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