"""
Main processor that demonstrates python_path functionality.
This module can import from nested directories thanks to python_path configuration.
"""

import sys
from pathlib import Path

# Import evaluators from nested paths (made possible by python_path config)
try:
    # These imports work because the directories are added to sys.path
    import complex_evaluator  # from nested/deep/evaluators/
    import utility_eval       # from utils/helpers/
    from text_utils import calculate_readability_score, extract_keywords  # from shared/common/
    
    print("✅ Successfully imported from all nested directories via python_path!")
    print(f"📍 Current sys.path includes: {[p for p in sys.path if 'system-path-demo' in p]}")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print(f"📍 Current sys.path: {sys.path[:5]}...")  # Show first 5 entries


def run(**kwargs) -> str:
    """
    Process input using modules from custom python_path directories.
    
    Args:
        **kwargs: All data fields from the dataset row
        
    Returns:
        The processed response
    """
    input_text = kwargs.get('input', 'No input provided')
    
    # Use shared utilities
    readability = calculate_readability_score(input_text)
    keywords = extract_keywords(input_text)
    
    # Create enhanced response
    response = f"Processed: {input_text}"
    
    if keywords:
        response += f" | Keywords: {', '.join(keywords[:3])}"
    
    response += f" | Readability: {readability:.2f}"
    
    # Add system path info
    nested_paths = [p for p in sys.path if 'system-path-demo' in p]
    response += f" | Loaded from {len(nested_paths)} custom paths"
    
    return response


if __name__ == "__main__":
    # Test the system path functionality
    print("🧪 Testing System Path Demo")
    print("=" * 50)
    
    # Show current Python path
    print("📁 Added Python paths:")
    for path in sys.path:
        if 'system-path-demo' in path:
            print(f"   • {path}")
    
    # Test the processing
    test_result = run(input="Hello world! How are you today?")
    print(f"\n📋 Test Result: {test_result}")