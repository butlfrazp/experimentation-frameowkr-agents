"""
Approach 1: Direct path manipulation and imports.
This module demonstrates loading evaluators from nested directories.
"""

import sys
import os
from pathlib import Path

# Method 1: Add nested paths to sys.path
def load_nested_evaluators_method1():
    """Load evaluators by adding nested paths to sys.path."""
    current_dir = Path(__file__).parent
    
    # Add nested evaluator directories to Python path
    basic_path = current_dir / "custom_evaluators" / "basic"
    advanced_path = current_dir / "custom_evaluators" / "advanced"
    
    sys.path.insert(0, str(basic_path))
    sys.path.insert(0, str(advanced_path))
    sys.path.insert(0, str(current_dir))
    
    # Import evaluators from nested locations
    try:
        import evaluators as basic_evaluators  # from basic/
        from custom_evaluators.advanced import evaluators as advanced_evaluators
        print("✅ Method 1: Successfully loaded nested evaluators via sys.path")
        return True
    except ImportError as e:
        print(f"❌ Method 1 failed: {e}")
        return False


# Method 2: Explicit module loading
def load_nested_evaluators_method2():
    """Load evaluators using explicit imports with package structure."""
    try:
        # Import from nested packages
        from custom_evaluators.basic.evaluators import BasicLengthEvaluator, BasicCompletenessEvaluator
        from custom_evaluators.advanced.evaluators import AdvancedQualityEvaluator, AdvancedCoherenceEvaluator
        print("✅ Method 2: Successfully loaded nested evaluators via package imports")
        return True
    except ImportError as e:
        print(f"❌ Method 2 failed: {e}")
        return False


# Method 3: Dynamic loading with importlib
def load_nested_evaluators_method3():
    """Load evaluators dynamically using importlib."""
    import importlib.util
    import importlib
    
    try:
        current_dir = Path(__file__).parent
        
        # Load basic evaluators
        basic_spec = importlib.util.spec_from_file_location(
            "basic_evaluators", 
            current_dir / "custom_evaluators" / "basic" / "evaluators.py"
        )
        basic_module = importlib.util.module_from_spec(basic_spec)
        basic_spec.loader.exec_module(basic_module)
        
        # Load advanced evaluators  
        advanced_spec = importlib.util.spec_from_file_location(
            "advanced_evaluators",
            current_dir / "custom_evaluators" / "advanced" / "evaluators.py"
        )
        advanced_module = importlib.util.module_from_spec(advanced_spec)
        advanced_spec.loader.exec_module(advanced_module)
        
        print("✅ Method 3: Successfully loaded nested evaluators via importlib")
        return True
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
        return False


def run(**kwargs) -> str:
    """
    Main function that loads nested evaluators and processes the request.
    
    Args:
        **kwargs: All data fields from the dataset row
        
    Returns:
        The processed response
    """
    # Try different methods to load evaluators
    success = False
    
    print("🔧 Loading nested evaluators...")
    
    # Try Method 1: sys.path manipulation
    if load_nested_evaluators_method1():
        success = True
    
    # Try Method 2: package imports  
    if not success and load_nested_evaluators_method2():
        success = True
        
    # Try Method 3: dynamic loading
    if not success and load_nested_evaluators_method3():
        success = True
    
    if success:
        response = "Successfully loaded and registered nested evaluators from multiple directories!"
    else:
        response = "Failed to load nested evaluators - check path configuration"
    
    # Process the actual input
    input_text = kwargs.get('input', 'No input provided')
    return f"{response} Processed input: '{input_text}'"


if __name__ == "__main__":
    print("🧪 Testing Nested Evaluator Loading Methods")
    print("=" * 50)
    load_nested_evaluators_method1()
    load_nested_evaluators_method2() 
    load_nested_evaluators_method3()